# Réponse à l'audit de sécurité automatisé (SecureScan / semgrep)

**Équipe 23 — EduTutor IA** · Perturbation J3 (Conformité) · v1.0

- **Rapport audité** : SecureScan (semgrep) — 1er juillet 2026, 10:38
- **Findings** : 11 au total (1 HIGH, 10 MEDIUM, 0 LOW)
- **Auteur de l'audit** : membre de l'équipe (revue croisée)

> **Démarche.** Un scanner statique produit du **bruit** : il faut trier, pas
> « corriger aveuglément ». On classe chaque finding en **faux positif**,
> **risque assumé (POC)** ou **à corriger**, avec justification. Bilan : **aucun
> finding n'est exploitable** dans le POC ; 2 vrais durcissements ont été appliqués.

## Triage des 11 findings

| # | Finding | Fichier(s) | Verdict | Justification |
|---|---------|-----------|---------|---------------|
| 1-3 | `set_password()` signalé | `accounts/views.py:225,297` · `accounts/serializers.py:84` | 🟢 Faux positif | API **correcte** de Django : hachage **PBKDF2**. semgrep flague le motif « password », mais c'est la bonne pratique attendue (la reco « utiliser PBKDF2 » est déjà satisfaite). |
| 4-5 | Mot de passe en dur | `quizzes/.../seed.py:27` · `quizzes/.../bootstrap_demo.py:92` | 🟡 Accepté (dev) | Fixtures de **démo** (`motdepasse123`), créées uniquement par `seed`/`bootstrap_demo`. Jamais des identifiants de production. |
| 6-9 | Actions CI non épinglées (A08) | `.github/workflows/ci.yml:63,66,104,107` | ✅ **Corrigé** | Actions épinglées à un **SHA de commit** vérifié (voir ci-dessous). |
| 10 | Conteneur en root (A04, **HIGH**) | `docker/frontend.Dockerfile` | 🟡 Accepté (dev) + ✅ **Corrigé (prod)** | Dockerfile de **dev** (local uniquement). L'image **backend de prod** tourne désormais en utilisateur non-root ; le frontend de prod est servi par **nginx** (workers non-root par défaut). |
| 11 | Path Traversal | (non localisé par le rapport) | 🟢 Faux positif probable | Aucun chemin contrôlé par l'utilisateur : PDF lu via `pypdf`, nom de fichier d'export = `user.id` (entier) + `fmt` validé (`json`/`csv`). |
| 12 | Cryptographic Failures (A05) | `backend/apocal/settings.py` | 🟡 Accepté (dev) | `SECRET_KEY` a un défaut de dev, `DEBUG=True`, `ALLOWED_HOSTS='*'` — **tous surchargés en production** via `.env` et le bloc `if SECURE_PROD:` (HTTPS, HSTS, cookies sécurisés). |

**Synthèse : 5 faux positifs · 4 risques dev assumés · 2 vrais durcissements → corrigés.**

## Corrections appliquées

### 1. Épinglage des actions GitHub Actions à un SHA (A08 — intégrité supply-chain)
Les actions étaient référencées par tag mobile (`@v5`), qui peut être re-pointé.
Elles sont désormais épinglées à un **SHA de commit immuable** (tag conservé en
commentaire), dans `ci.yml` **et** `security.yml` :

| Action | SHA épinglé |
|--------|-------------|
| `actions/checkout` | `93cb6efe18208431cddfb8368fd83d5badbf9bfd` (# v5) |
| `actions/setup-python` | `ece7cb06caefa5fff74198d8649806c4678c61a1` (# v6) |
| `actions/setup-node` | `a0853c24544627f65ddf259abe73b1d18a591444` (# v5) |

### 2. Exécution non-root de l'image backend de production (A04)
`docker/backend.prod.Dockerfile` crée un utilisateur `appuser` (uid 1000),
lui attribue `/app`, et bascule `USER appuser` avant le lancement de gunicorn.

## Risques résiduels assumés (POC)

Cohérent avec la [Note de sécurité](equipe-23-note-securite.docx) §4 :

- **Conteneurs de dev en root** : acceptable, exécution **locale** uniquement.
- **Défauts de dev dans `settings.py`** (`SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`) :
  neutralisés en production par `.env` + `SECURE_PROD` (déjà en place).
- **Clés API LLM en clair** dans `LLMConfig` (cf. Note de sécurité §4.4) : à
  chiffrer (Fernet) pour un vrai déploiement.

## Conclusion

L'audit ne révèle **aucune vulnérabilité exploitable** dans le POC. Les 5 faux
positifs sont documentés, les 4 risques dev sont assumés et gated pour la prod,
et les 2 vrais durcissements (supply-chain CI + non-root prod) sont **corrigés**.
Cette réponse complète le volet **conformité** de la perturbation J3.

> Voir aussi : [Note de sécurité](equipe-23-note-securite.docx) ·
> [Tests adversariaux](equipe-23-tests-adversariaux.md) ·
> [Démo injection réelle](equipe-23-demo-injection-reelle.md) ·
> [ADR Prompt Injection](../../adr/equipe-23-adr-prompt-injection.md)
