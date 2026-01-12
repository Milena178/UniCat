from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

class Produkte(models.Model):

    verkaeufer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="products")

    name = models.CharField(max_length=200)
    beschreibung = models.TextField()
    bild = models.ImageField(upload_to="product/images/")
    tags = models.ManyToManyField("Tag", blank=True)

    mindestpreis = models.DecimalField(max_digits=8, decimal_places=2)
    auktionsdauer = models.DurationField(help_text="Dauer der Auktion (z. B. 7 Tage)")

    anzahlListungen = models.PositiveSmallIntegerField(default=1)
    istArchiviert = models.BooleanField(default=False)

    erstelltAm = models.DateTimeField(auto_now_add=True)

    infoPdf = models.FileField(upload_to="product/pdfs/", blank=True, null=True)

    #  Validierung
    def clean(self):
        if self.anzahlListungen > 3:
            raise ValidationError(
                "Ein Produkt darf maximal 3 Mal gelistet werden."
            )

        if self.mindestpreis <= 0:
            raise ValidationError(
                "Der Mindestpreis muss größer als 0 sein."
            )

    #  Berechnung des Enddatums der Auktion
    def auction_end(self):
        return self.erstelltAm + self.auktionsdauer

    def __str__(self):
        return self.name