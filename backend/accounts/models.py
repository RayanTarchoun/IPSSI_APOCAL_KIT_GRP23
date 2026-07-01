"""
Modèles de l'app accounts.

[Note pédagogique] On garde le modèle User standard de Django (simple et
robuste), et on lui ajoute un Profil 1-pour-1 pour les infos métier qui ne sont
pas dans User — ici `email_verified` (l'utilisateur a-t-il cliqué le lien de
confirmation envoyé par email ?).

Choix d'architecture « email = identifiant » : à l'inscription, on met
username = email (voir SignupSerializer). Le login se fait donc par email, sans
backend d'authentification custom. C'est le compromis le plus simple pour un
kit pédagogique (un vrai produit utiliserait souvent un User personnalisé avec
USERNAME_FIELD = 'email').
"""

from django.conf import settings
from django.db import models


class Profile(models.Model):
    """Informations complémentaires attachées à un utilisateur."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    # Validation "soft" : le compte fonctionne même si l'email n'est pas vérifié,
    # mais un bandeau invite l'utilisateur à cliquer le lien de confirmation.
    email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Profile<{self.user.email or self.user.username}>"


def get_or_create_profile(user) -> Profile:
    """Récupère (ou crée) le profil d'un utilisateur.

    Pratique pour les comptes créés AVANT l'ajout du modèle Profile (ils n'ont
    pas encore de profil) : on le crée à la volée plutôt que de planter.
    """
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile


class DataRequest(models.Model):
    """Journal (audit trail) des demandes RGPD — perturbation J3-bis.

    [Note pédagogique] Une demande d'accès (SAR — Subject Access Request, RGPD
    Article 15) doit être TRAÇABLE : qui a demandé, quand, sous quel statut, et
    quelle a été la réponse. Chaque export déclenché par un utilisateur crée un
    enregistrement ici, avec l'empreinte SHA-256 du fichier remis (preuve
    d'intégrité). Répond au critère CA-J3B-6.
    """

    TYPE_ACCESS = "access"  # Art. 15 — droit d'accès
    TYPE_PORTABILITY = "portability"  # Art. 20 — portabilité
    TYPE_ERASURE = "erasure"  # Art. 17 — effacement
    TYPE_CHOICES = [
        (TYPE_ACCESS, "Accès (Art. 15)"),
        (TYPE_PORTABILITY, "Portabilité (Art. 20)"),
        (TYPE_ERASURE, "Effacement (Art. 17)"),
    ]

    STATUS_RECEIVED = "received"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_ANSWERED = "answered"
    STATUS_CHOICES = [
        (STATUS_RECEIVED, "Reçue"),
        (STATUS_IN_PROGRESS, "En cours"),
        (STATUS_ANSWERED, "Répondue"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="data_requests",
        help_text="Personne concernée par la demande.",
    )
    request_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_ACCESS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_RECEIVED)
    export_format = models.CharField(
        max_length=10, default="json", help_text="Format du fichier remis (json / csv)."
    )
    file_sha256 = models.CharField(
        max_length=64,
        blank=True,
        default="",
        help_text="Empreinte SHA-256 du fichier exporté (preuve d'intégrité).",
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-requested_at"]
        verbose_name = "Demande RGPD"
        verbose_name_plural = "Demandes RGPD"

    def __str__(self) -> str:
        return f"DataRequest<{self.user.username} · {self.request_type} · {self.status}>"
