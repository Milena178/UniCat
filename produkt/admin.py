from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Produkt, Tag

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'erstellt_am']
    search_fields = ['name']

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

@admin.register(Produkt)
class ProduktAdmin(admin.ModelAdmin):
    list_display = ['name', 'verkaeufer_profil', 'mindestpreis', 'anzahlListungen', 'erstelltAm', 'istArchiviert', "auktion_status"]
    list_filter = ['istArchiviert', 'tags', 'erstelltAm']
    search_fields = ['name', 'beschreibung', 'verkaeufer_profil__username']
    readonly_fields = ["anzahlListungen", 'erstelltAm', "auktion_ende"]
    filter_horizontal = ['tags']
    actions = ["produkte_archivieren"]

    @admin.display(description="Auktion", boolean=True)
    def auktion_status(self, obj):
        return obj.auktion_aktiv()

    @admin.display(description="Auktionsende")
    def auktion_ende(self, obj):
        return obj.auktion_ende()

    @admin.display(description="Verbleibende Zeit", ordering='erstelltAm')
    def verbleibende_zeit(self, obj):
        """Zeigt die verbleibende Zeit neutral an"""
        if obj.istArchiviert:
            return "Archiviert"

        if not obj.auktion_aktiv():
            return "Beendet"

        delta = obj.auktion_ende() - timezone.now()

        days = delta.days
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        seconds = delta.seconds % 60

        parts = []
        if days > 0:
            parts.append(f"{days}T")
        if hours > 0 or days > 0:
            parts.append(f"{hours}h")
        parts.append(f"{minutes}min")

        return " ".join(parts)

    @admin.action(description="Ausgewählte Produkte archivieren")
    def produkte_archivieren(self, request, queryset):
        count = queryset.update(ist_archiviert=True)
        self.message_user(request, f"{count} Produkt(e) wurden archiviert.")