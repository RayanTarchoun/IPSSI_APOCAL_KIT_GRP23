"""
Export des données personnelles d'un utilisateur — RGPD Art. 15 (perturbation J3-bis).

[Note pédagogique] Point de vigilance RGPD n°1 : n'exporter QUE les données de la
personne concernée. Toutes les requêtes sont donc filtrées par `user` — jamais de
`.objects.all()`. Le résultat est un dict structuré (machine-readable), sérialisable
en JSON (complet) ou CSV (tabulaire) — jamais en PDF.

Les 6 catégories couvertes (CA-J3B-2) :
  1. compte utilisateur          4. réponses & scores
  2. documents importés          5. signalements émis (non implémenté — POC)
  3. quiz générés                6. logs d'audit (journal des demandes RGPD)
"""

import csv
import hashlib
import io
import json
from datetime import UTC, datetime


def _iso(dt) -> str | None:
    return dt.isoformat() if dt else None


def build_user_export(user) -> dict:
    """Construit l'export complet des données personnelles de `user`.

    Toutes les collections sont filtrées par `user` (aucune fuite inter-comptes).
    """
    from quizzes.models import Quiz

    from .models import DataRequest, get_or_create_profile

    profile = get_or_create_profile(user)
    quizzes = Quiz.objects.filter(user=user).prefetch_related("questions").order_by("created_at")

    documents: list[dict] = []
    quiz_list: list[dict] = []
    reponses: list[dict] = []

    for quiz in quizzes:
        # 2. Document importé = le texte source ayant servi à générer le quiz.
        documents.append(
            {
                "quiz_id": quiz.id,
                "titre": quiz.title,
                "contenu_source": quiz.source_text,
                "importe_le": _iso(quiz.created_at),
            }
        )

        questions = []
        for q in quiz.questions.all():
            questions.append(
                {
                    "index": q.index,
                    "enonce": q.prompt,
                    "options": q.options,
                    "correct_index": q.correct_index,
                    "reponse_choisie_index": q.selected_index,
                }
            )
            # 4. Réponse & score : seulement si l'utilisateur a répondu.
            if q.selected_index is not None:
                reponses.append(
                    {
                        "quiz_id": quiz.id,
                        "quiz_titre": quiz.title,
                        "question_index": q.index,
                        "reponse_choisie_index": q.selected_index,
                        "correct_index": q.correct_index,
                        "correcte": q.selected_index == q.correct_index,
                    }
                )

        # 3. Quiz généré.
        quiz_list.append(
            {
                "id": quiz.id,
                "titre": quiz.title,
                "score_sur_10": quiz.score,
                "cree_le": _iso(quiz.created_at),
                "modifie_le": _iso(quiz.updated_at),
                "questions": questions,
            }
        )

    # 6. Logs d'audit = journal des demandes RGPD de CET utilisateur.
    logs = [
        {
            "type": dr.get_request_type_display(),
            "statut": dr.get_status_display(),
            "format": dr.export_format,
            "demande_le": _iso(dr.requested_at),
            "repondu_le": _iso(dr.answered_at),
            "empreinte_sha256": dr.file_sha256,
        }
        for dr in DataRequest.objects.filter(user=user)
    ]

    return {
        "meta": {
            "genere_le": datetime.now(UTC).isoformat(),
            "base_legale": "RGPD Article 15 — droit d'accès de la personne concernée",
            "plateforme": "EduTutor IA",
            "utilisateur_id": user.id,
        },
        # 1. Compte utilisateur.
        "compte": {
            "id": user.id,
            "identifiant": user.username,
            "email": user.email,
            "prenom": user.first_name,
            "nom": user.last_name,
            "inscrit_le": _iso(user.date_joined),
            "derniere_connexion": _iso(user.last_login),
            "email_verifie": profile.email_verified,
            "compte_cree_le": _iso(profile.created_at),
            "administrateur": user.is_staff,
        },
        "documents_importes": documents,
        "quiz_generes": quiz_list,
        "reponses_et_scores": reponses,
        # 5. Signalements : pas de modèle dans le POC (prévu J4) — catégorie
        # présente mais vide, pour l'exhaustivité de l'export.
        "signalements_emis": [],
        "logs_audit": logs,
        "_notes": {
            "signalements_emis": "Aucun modèle de signalement dans le POC (prévu J4).",
            "logs_audit": "Journal des demandes RGPD (SAR) de cet utilisateur.",
        },
    }


def export_to_json_bytes(data: dict) -> bytes:
    return json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")


def export_to_csv_bytes(data: dict) -> bytes:
    """Sérialise l'export en CSV multi-sections (lisible et machine-readable)."""
    buf = io.StringIO()
    writer = csv.writer(buf)

    def section(title: str) -> None:
        writer.writerow([])
        writer.writerow([f"=== {title} ==="])

    section("COMPTE")
    compte = data["compte"]
    writer.writerow(list(compte.keys()))
    writer.writerow([compte[k] for k in compte])

    section("DOCUMENTS IMPORTES")
    writer.writerow(["quiz_id", "titre", "importe_le", "contenu_source"])
    for d in data["documents_importes"]:
        writer.writerow([d["quiz_id"], d["titre"], d["importe_le"], d["contenu_source"]])

    section("QUIZ GENERES")
    writer.writerow(["id", "titre", "score_sur_10", "cree_le", "modifie_le"])
    for q in data["quiz_generes"]:
        writer.writerow([q["id"], q["titre"], q["score_sur_10"], q["cree_le"], q["modifie_le"]])

    section("REPONSES ET SCORES")
    writer.writerow(
        [
            "quiz_id",
            "quiz_titre",
            "question_index",
            "reponse_choisie_index",
            "correct_index",
            "correcte",
        ]
    )
    for r in data["reponses_et_scores"]:
        writer.writerow(
            [
                r["quiz_id"],
                r["quiz_titre"],
                r["question_index"],
                r["reponse_choisie_index"],
                r["correct_index"],
                r["correcte"],
            ]
        )

    section("SIGNALEMENTS EMIS")
    writer.writerow(["(aucun — fonctionnalité non implémentée dans le POC, prévu J4)"])

    section("LOGS AUDIT (demandes RGPD)")
    writer.writerow(["type", "statut", "format", "demande_le", "repondu_le", "empreinte_sha256"])
    for lg in data["logs_audit"]:
        writer.writerow(
            [
                lg["type"],
                lg["statut"],
                lg["format"],
                lg["demande_le"],
                lg["repondu_le"],
                lg["empreinte_sha256"],
            ]
        )

    return buf.getvalue().encode("utf-8")


def sha256_hex(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()
