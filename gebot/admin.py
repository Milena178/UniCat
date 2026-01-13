from django.contrib import admin
from .models import Gebot


@admin.register(Gebot)
class GebotAdmin(admin.ModelAdmin):

    list_display = ("produkt", "bieter", "biethoehe", "erstelltAm", "auktion_status",)

    list_filter = ("produkt", "bieter")

    search_fields = ("produkt__name", "bieter__user__username")

    readonly_fields = ("produkt", "bieter", "biethoehe", "erstelltAm")

    ordering = ("-erstelltAm",)

    @admin.display(description="Auktion aktiv?", boolean=True)
    def auktion_status(self, obj):
        return obj.produkt.auktion_aktiv()