from django.contrib import admin
from .models import Produkt

@admin.register(Produkt)
class ProduktAdmin(admin.ModelAdmin):
    list_display = ['name', 'mindestpreis', 'anzahlListungen', 'erstelltAm', 'istArchiviert']
    list_filter = ['istArchiviert', 'erstelltAm']
    search_fields = ['name', 'beschreibung']
    readonly_fields = ['erstelltAm']