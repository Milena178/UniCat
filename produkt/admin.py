from django.contrib import admin
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
    list_display = ['name', 'verkaeufer_profil', 'mindestpreis', 'anzahlListungen', 'erstelltAm', 'istArchiviert']
    list_filter = ['istArchiviert', 'tags', 'erstelltAm']
    search_fields = ['name', 'beschreibung', 'verkaeufer_profil__username']
    readonly_fields = ['erstelltAm']
    filter_horizontal = ['tags']