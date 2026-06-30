"""
Commande `python manage.py benchmark_llm`
=========================================
Harness de benchmark REPRODUCTIBLE pour la perturbation J2 (latence de
génération des QCM).

Mesure, pour chaque modèle passé en argument et sur le MÊME cours de référence :
  - la latence de génération (toutes les durées, p50 = médiane, p95) ;
  - le taux de succès (générations valides / total) ;
  - la taille disque du modèle local (best-effort via l'API Ollama /api/tags).

Il sauvegarde aussi UN quiz généré par modèle (JSON) pour permettre la
notation qualité /5 « à l'aveugle » par les testeurs (le nom du modèle n'est
pas dans le contenu du quiz).

Exemples
--------
  # 3 modèles locaux Ollama, 5 runs chacun, 1 run de chauffe ignoré :
  python manage.py benchmark_llm \
      --models ollama:llama3.1:8b ollama:llama3.2:3b ollama:phi3:mini \
      --runs 5 --warmup 1 \
      --course docs/perturbations/j2/equipe-23-cours-reference-algorithmique.md

  # Comparer un cloud rapide (clé GROQ_API_KEY requise dans .env) :
  python manage.py benchmark_llm \
      --models ollama:llama3.2:3b groq:llama-3.3-70b-versatile cerebras:llama-3.3-70b \
      --runs 5

Le tableau Markdown final est à reporter dans equipe-23-benchmark-modeles.xlsx.
"""

from __future__ import annotations

import json
import statistics
import time
from pathlib import Path

import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from llm.providers import PROVIDERS
from llm.services.base import LLMError
from llm.services.factory import _BACKENDS

# Cours de référence par défaut (relatif à la racine du repo).
DEFAULT_COURSE = "docs/perturbations/j2/equipe-23-cours-reference-algorithmique.md"
DEFAULT_TITLE = "Algorithmique — cours de référence (benchmark J2)"


def _percentile(values: list[float], pct: float) -> float:
    """Centile par méthode du rang le plus proche (nearest-rank).

    Simple et défendable en démo : p95 = la valeur telle que 95 % des runs
    sont en dessous. Sur 5 runs, p95 ≈ la valeur max (c'est attendu et honnête).
    """
    if not values:
        return float("nan")
    ordered = sorted(values)
    rank = max(1, int(round(pct / 100.0 * len(ordered))))
    return ordered[min(rank, len(ordered)) - 1]


def _make_client(backend: str, model: str):
    """Instancie un client pour (backend, model) sans passer par la config DB.

    On veut tester un modèle PRÉCIS, indépendamment de ce qui est branché en
    base ou dans le .env. La clé API cloud est lue depuis settings (.env).
    """
    cls = _BACKENDS.get(backend)
    if cls is None:
        raise CommandError(f"Backend inconnu : {backend!r} (voir llm/providers.py).")

    if backend == "mock":
        return cls()
    if backend == "ollama":
        return cls(model=model)

    # Cloud / compatibles OpenAI + Anthropic + Gemini : (api_key=, model=).
    prov = PROVIDERS.get(backend)
    api_key = getattr(settings, prov.settings_key_attr, "") if (prov and prov.settings_key_attr) else ""
    return cls(api_key=api_key, model=model)


def _ollama_disk_size(model: str) -> str:
    """Taille disque d'un modèle Ollama (best-effort, '' si indisponible)."""
    try:
        host = settings.OLLAMA_HOST.rstrip("/")
        resp = requests.get(f"{host}/api/tags", timeout=5)
        resp.raise_for_status()
        for m in resp.json().get("models", []):
            if m.get("name") == model:
                gb = m.get("size", 0) / (1024**3)
                return f"{gb:.1f} Go"
    except Exception:
        pass
    return ""


class Command(BaseCommand):
    help = "Benchmark de latence des modèles de génération de QCM (perturbation J2)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--models",
            nargs="+",
            required=True,
            metavar="backend:model",
            help="Liste 'backend:model' (ex: ollama:llama3.2:3b groq:llama-3.3-70b-versatile).",
        )
        parser.add_argument("--runs", type=int, default=5, help="Nombre de runs mesurés (défaut 5).")
        parser.add_argument(
            "--warmup",
            type=int,
            default=1,
            help="Runs de chauffe NON mesurés (charge le modèle en VRAM). Défaut 1.",
        )
        parser.add_argument("--course", default=DEFAULT_COURSE, help="Chemin du cours de référence.")
        parser.add_argument(
            "--out",
            default="docs/perturbations/j2/runs",
            help="Dossier de sortie pour les quiz générés + le JSON brut.",
        )

    def handle(self, *args, **opts):
        course_path = Path(opts["course"])
        if not course_path.exists():
            raise CommandError(f"Cours de référence introuvable : {course_path}")
        source_text = course_path.read_text(encoding="utf-8")

        out_dir = Path(opts["out"])
        out_dir.mkdir(parents=True, exist_ok=True)

        specs = []
        for raw in opts["models"]:
            backend, _, model = raw.partition(":")
            if not model:
                raise CommandError(f"Format attendu 'backend:model', reçu : {raw!r}")
            specs.append((backend, model))

        runs, warmup = opts["runs"], opts["warmup"]
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f"Benchmark J2 — {len(specs)} modèle(s) × {runs} run(s) "
                f"(+{warmup} chauffe) — cours : {course_path}\n"
            )
        )

        rows = []
        for backend, model in specs:
            label = f"{backend}:{model}"
            self.stdout.write(f"▶ {label}")
            try:
                client = _make_client(backend, model)
            except (LLMError, CommandError) as exc:
                self.stdout.write(self.style.WARNING(f"  ⏭  ignoré : {exc}\n"))
                rows.append({"label": label, "skipped": str(exc)})
                continue

            # Chauffe (non mesurée) : charge le modèle en mémoire.
            for _ in range(warmup):
                try:
                    client.generate_quiz(source_text, DEFAULT_TITLE)
                except Exception as exc:  # noqa: BLE001 — on tolère un échec de chauffe
                    self.stdout.write(self.style.WARNING(f"  chauffe en échec : {exc}"))

            durations, ok, first_quiz = [], 0, None
            for i in range(runs):
                start = time.perf_counter()
                try:
                    quiz = client.generate_quiz(source_text, DEFAULT_TITLE)
                    elapsed = time.perf_counter() - start
                    ok += 1
                    durations.append(elapsed)
                    if first_quiz is None:
                        first_quiz = quiz
                    self.stdout.write(f"  run {i + 1}/{runs} : {elapsed:6.1f} s ✅")
                except Exception as exc:  # noqa: BLE001 — un échec compte dans le taux
                    elapsed = time.perf_counter() - start
                    self.stdout.write(self.style.WARNING(f"  run {i + 1}/{runs} : {elapsed:6.1f} s ❌ {exc}"))

            # Sauvegarde d'un quiz pour notation qualité à l'aveugle.
            if first_quiz is not None:
                safe = label.replace(":", "_").replace("/", "_")
                (out_dir / f"quiz_{safe}.json").write_text(
                    json.dumps(first_quiz, ensure_ascii=False, indent=2), encoding="utf-8"
                )

            p50 = statistics.median(durations) if durations else float("nan")
            p95 = _percentile(durations, 95)
            disk = _ollama_disk_size(model) if backend == "ollama" else "cloud (N/A)"
            rows.append(
                {
                    "label": label,
                    "p50": p50,
                    "p95": p95,
                    "ok": ok,
                    "runs": runs,
                    "disk": disk,
                    "durations": [round(d, 1) for d in durations],
                }
            )
            self.stdout.write(
                self.style.SUCCESS(f"  → p50={p50:.1f}s  p95={p95:.1f}s  succès={ok}/{runs}\n")
            )

        # JSON brut (traçabilité / reproductibilité).
        (out_dir / "benchmark_raw.json").write_text(
            json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        # Tableau Markdown prêt à coller dans l'ADR / le benchmark xlsx.
        self.stdout.write(self.style.MIGRATE_HEADING("\n=== Tableau récapitulatif (Markdown) ===\n"))
        self.stdout.write("| Modèle | p50 (médiane) | p95 | Succès | Disque | Qualité /5 |")
        self.stdout.write("|---|---|---|---|---|---|")
        for r in rows:
            if "skipped" in r:
                self.stdout.write(f"| `{r['label']}` | — | — | ignoré | — | — |")
                continue
            self.stdout.write(
                f"| `{r['label']}` | {r['p50']:.1f} s | {r['p95']:.1f} s | "
                f"{r['ok']}/{r['runs']} | {r['disk']} | _(à noter)_ |"
            )
        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Quiz générés + JSON brut dans : {out_dir}\n"
                "   → fais noter quiz_*.json /5 par ≥ 3 testeurs (à l'aveugle), "
                "puis reporte le tableau dans equipe-23-benchmark-modeles.xlsx."
            )
        )
