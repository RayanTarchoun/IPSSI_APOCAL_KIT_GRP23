"""Admin de l'app accounts.

L'admin Django par défaut suffit pour User. On expose en lecture seule le
journal des demandes RGPD (DataRequest) pour que l'animateur / DPO puisse
consulter l'audit trail des exports (perturbation J3-bis).
"""

from django.contrib import admin

from .models import DataRequest


@admin.register(DataRequest)
class DataRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "request_type",
        "status",
        "export_format",
        "requested_at",
        "answered_at",
    )
    list_filter = ("request_type", "status", "export_format")
    search_fields = ("user__username", "user__email", "file_sha256")
    readonly_fields = (
        "user",
        "request_type",
        "status",
        "export_format",
        "file_sha256",
        "requested_at",
        "answered_at",
    )

    def has_add_permission(self, request):
        # Les demandes sont créées par l'endpoint d'export, pas à la main.
        return False
