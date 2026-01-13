from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings

class Tag(models.Model):
    #  Tags können nur von Superusern erstellt werden
    name = models.CharField(max_length=50, unique=True)
    erstellt_am = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name


class Produkt(models.Model):

    verkaeufer_profil = models.ForeignKey(
        'profil.UserProfile',
        on_delete=models.CASCADE,
        related_name="produkte",
        null = True, #  WICHTIG, AM ENDE MUSS DAS WEG!
        blank = True
    )

    name = models.CharField(max_length=200)
    beschreibung = models.TextField()
    bild = models.ImageField(upload_to="product/images/", blank=True, null=True, help_text="Produktbild (optional)")

    tags = models.ManyToManyField(Tag, blank=True, related_name="produkte")

    mindestpreis = models.DecimalField(max_digits=8, decimal_places=2)
    auktionsdauer = models.DurationField(help_text="Dauer der Auktion (z. B. 7 Tage)")

    anzahlListungen = models.PositiveSmallIntegerField(default=0, editable=False, help_text="Interner Counter - wird automatisch erhöht")
    istArchiviert = models.BooleanField(default=False)
    erstelltAm = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-erstelltAm']
        verbose_name = 'Produkt'
        verbose_name_plural = 'Produkte'

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
    def auktion_endet(self):
        return self.erstelltAm + self.auktionsdauer

    #  Listungscounter erhöht sich nach Auktionsende
    def increment_listings(self):
        if self.anzahlListungen < 3:
            self.anzahlListungen += 1
            self.save(update_fields=['anzahlListungen'])
            return True
        return False

    #  Archivierung verkaufter Produkte
    def archive(self):
        self.istArchiviert = True
        self.save(update_fields=["istArchiviert"])

    def __str__(self):
        return self.name