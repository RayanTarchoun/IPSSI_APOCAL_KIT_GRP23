"""
Client Ollama — appel HTTP vers le service LLM LOCAL (gratuit).

[Note pédagogique] Ollama fait tourner un modèle open-source (Llama, Phi,
Mistral…) en local, sans clé API ni coût. C'est le backend par DÉFAUT du kit :
souveraineté des données + zéro coût. Sa contrepartie est la latence sur CPU
(cf. perturbation J2). Le prompt et la validation sont mutualisés dans
quiz_prompt.py et partagés avec les clients OpenAI / Claude.
"""

import requests
from django.conf import settings

from .base import LLMClient, LLMError
from .quiz_prompt import build_full_prompt, generate_quiz_resilient


class OllamaLLMClient(LLMClient):
    """Client HTTP minimal pour Ollama (/api/generate)."""

    def __init__(
        self, *, model: str | None = None, host: str | None = None, timeout: int | None = None
    ) -> None:
        # Overrides éventuels (config admin en base, Lot 8) sinon valeurs .env.
        self.host = (host or settings.OLLAMA_HOST).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL
        # Configurable via OLLAMA_TIMEOUT (.env). Défaut 600 s : une génération
        # 8B sur CPU peut dépasser largement 120 s (cf. perturbation J2 latence).
        self.timeout = timeout or settings.OLLAMA_TIMEOUT

    def generate_quiz(self, source_text: str, title: str) -> list[dict]:
        # Ollama /api/generate attend UN prompt unique (pas de séparation
        # system/user native) : la séparation est assurée par des DÉLIMITEURS
        # explicites autour du cours (build_full_prompt) + l'instruction
        # défensive du system prompt (J3, couche 1). Re-prompt auto si la
        # validation échoue (couche 4).
        return generate_quiz_resilient(
            lambda strict: self._call_ollama(build_full_prompt(source_text, title, strict))
        )

    # ----- internals -----

    def _call_ollama(self, prompt: str) -> str:
        try:
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.4},  # peu de créativité : on veut du factuel
                    "format": "json",  # mode JSON strict d'Ollama si supporté
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise LLMError(f"Ollama injoignable : {exc}") from exc

        data = response.json()
        raw = data.get("response", "")
        if not raw:
            raise LLMError("Ollama a renvoyé une réponse vide.")
        return raw
