"""
Tests de l'export RGPD (perturbation J3-bis) — GET /api/accounts/me/export/.

Vérifie les critères d'acceptation :
  - CA-J3B-1 : 200 + données structurées
  - CA-J3B-2 : les 6 catégories sont présentes
  - CA-J3B-3 : formats JSON et CSV
  - CA-J3B-6 : audit trail (DataRequest) créé, avec empreinte SHA-256
  - Sécurité RGPD : aucune fuite inter-comptes (filtrage par request.user)
"""

import json

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from accounts.models import DataRequest
from quizzes.models import Question, Quiz

pytestmark = pytest.mark.django_db


@pytest.fixture
def alice() -> User:
    return User.objects.create_user(
        username="alice@example.com", email="alice@example.com", password="motdepasse123"
    )


@pytest.fixture
def alice_client(alice) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=alice)
    return client


def _make_quiz(user: User, title: str, answered: bool = True) -> Quiz:
    quiz = Quiz.objects.create(
        user=user, title=title, source_text="Contenu du cours " * 20, score=8
    )
    Question.objects.create(
        quiz=quiz,
        index=1,
        prompt="Q1 ?",
        options=["A", "B", "C", "D"],
        correct_index=1,
        selected_index=1 if answered else None,
    )
    return quiz


def test_export_requires_auth():
    resp = APIClient().get("/api/accounts/me/export/")
    assert resp.status_code in (401, 403)


def test_export_json_returns_structured_data(alice, alice_client):
    _make_quiz(alice, "Mon cours d'algèbre")
    resp = alice_client.get("/api/accounts/me/export/")
    assert resp.status_code == 200
    assert resp["Content-Type"].startswith("application/json")
    assert "attachment" in resp["Content-Disposition"]

    data = json.loads(resp.content)
    # CA-J3B-2 : les 6 catégories présentes.
    for key in (
        "compte",
        "documents_importes",
        "quiz_generes",
        "reponses_et_scores",
        "signalements_emis",
        "logs_audit",
    ):
        assert key in data
    assert data["compte"]["email"] == "alice@example.com"
    assert data["quiz_generes"][0]["titre"] == "Mon cours d'algèbre"
    assert data["reponses_et_scores"][0]["correcte"] is True


def test_export_csv_format(alice, alice_client):
    _make_quiz(alice, "Cours CSV")
    resp = alice_client.get("/api/accounts/me/export/", {"fmt": "csv"})
    assert resp.status_code == 200
    assert resp["Content-Type"].startswith("text/csv")
    body = resp.content.decode("utf-8")
    assert "=== COMPTE ===" in body
    assert "=== QUIZ GENERES ===" in body


def test_export_does_not_leak_other_users_data(alice, alice_client):
    """RGPD : l'export d'Alice ne doit JAMAIS contenir les données de Bob."""
    bob = User.objects.create_user(username="bob@example.com", password="x")
    _make_quiz(alice, "Cours d'Alice")
    _make_quiz(bob, "Cours SECRET de Bob")

    resp = alice_client.get("/api/accounts/me/export/")
    body = resp.content.decode("utf-8")
    assert "Cours d'Alice" in body
    assert "Bob" not in body
    assert "SECRET" not in body


def test_export_creates_audit_trail(alice, alice_client):
    assert DataRequest.objects.filter(user=alice).count() == 0
    resp = alice_client.get("/api/accounts/me/export/")
    assert resp.status_code == 200

    dr = DataRequest.objects.filter(user=alice).first()
    assert dr is not None
    assert dr.status == DataRequest.STATUS_ANSWERED
    assert dr.request_type == DataRequest.TYPE_ACCESS
    assert dr.answered_at is not None
    # Empreinte SHA-256 (64 hexadigits) présente et cohérente avec l'en-tête.
    assert len(dr.file_sha256) == 64
    assert resp["X-Export-SHA256"] == dr.file_sha256


def test_export_rejects_unknown_format(alice_client):
    resp = alice_client.get("/api/accounts/me/export/", {"fmt": "pdf"})
    assert resp.status_code == 400
