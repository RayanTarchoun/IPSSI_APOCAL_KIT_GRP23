import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="DataRequest",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "request_type",
                    models.CharField(
                        choices=[
                            ("access", "Accès (Art. 15)"),
                            ("portability", "Portabilité (Art. 20)"),
                            ("erasure", "Effacement (Art. 17)"),
                        ],
                        default="access",
                        max_length=20,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("received", "Reçue"),
                            ("in_progress", "En cours"),
                            ("answered", "Répondue"),
                        ],
                        default="received",
                        max_length=20,
                    ),
                ),
                (
                    "export_format",
                    models.CharField(
                        default="json",
                        help_text="Format du fichier remis (json / csv).",
                        max_length=10,
                    ),
                ),
                (
                    "file_sha256",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Empreinte SHA-256 du fichier exporté (preuve d'intégrité).",
                        max_length=64,
                    ),
                ),
                ("requested_at", models.DateTimeField(auto_now_add=True)),
                ("answered_at", models.DateTimeField(blank=True, null=True)),
                (
                    "user",
                    models.ForeignKey(
                        help_text="Personne concernée par la demande.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="data_requests",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Demande RGPD",
                "verbose_name_plural": "Demandes RGPD",
                "ordering": ["-requested_at"],
            },
        ),
    ]
