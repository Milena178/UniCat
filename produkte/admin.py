from django.contrib import admin
from .models import Produkte

@admin.register(Produkte)
class ProdukteAdmin(admin.ModelAdmin):
    list_display = ['name', 'mindestpreis', 'anzahlListungen', 'erstelltAm', 'istArchiviert']
    list_filter = ['istArchiviert', 'erstelltAm']
    search_fields = ['name', 'beschreibung']
    readonly_fields = ['erstelltAm']