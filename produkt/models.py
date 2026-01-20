from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

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
    auktionsdauer = models.DurationField(help_text="Dauer der Auktion", null=False, blank=False)

    anzahlListungen = models.PositiveSmallIntegerField(default=1, editable=False, help_text="Wie oft das Produkt insgesamt gelistet wurde")
    istArchiviert = models.BooleanField(default=False)
    erstelltAm = models.DateTimeField(auto_now_add=True)

    # Produkt melden
    gemeldet = models.BooleanField(default=False)

    class Meta:
        ordering = ['-erstelltAm']
        verbose_name = 'Produkt'
        verbose_name_plural = 'Produkte'

    #  Validierung
    def clean(self):
        errors = {}

        if self.anzahlListungen > 3:
            errors["anzahl_listungen"] = (
                "Ein Produkt darf maximal 3 Mal gelistet werden."
            )

        if self.mindestpreis <= 0:
            errors["mindestpreis"] = (
                "Der Mindestpreis muss größer als 0 sein."
            )

        if errors:
            raise ValidationError(errors)

    #  Validierungen erzwingen
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    #  Aktuelles Höchstgebot ermitteln
    def hoechstgebot(self):
        return self.gebote.order_by("-biethoehe").first()

    #  Auktion endet
    def auktion_ende(self):
        return self.erstelltAm + self.auktionsdauer

    #  Auktion läuft
    def auktion_aktiv(self):
        return (
            not self.istArchiviert and
            timezone.now() < self.auktion_ende()
        )

    #  Auktionsende erreicht?
    def auktion_beendet(self):
        return timezone.now() >= self.auktion_ende()

    #  wurde das Produkt verkauft?
    def ist_unverkauft(self):
        """Auktion beendet, aber kein Gebot oder Gebot nicht bestätigt"""
        if not self.auktion_beendet():
            return False

        hoechstgebot = self.hoechstgebot()

        # Kein Gebot abgegeben
        if not hoechstgebot:
            return True

        # Gebot vorhanden, aber nicht bestätigt
        return not hoechstgebot.kauf_bestaetigt

    # Kann das Produkt erneut gelistet werden?
    def kann_relistet_werden(self):
        return self.anzahlListungen < 3

    def archive(self):
        """
        WICHTIG: Archiviert nur wenn:
        1. Produkt wurde verkauft (Gebot bestätigt), ODER
        2. Produkt wurde bereits 3x gelistet und ist immer noch unverkauft
        """
        hoechstgebot = self.hoechstgebot()

        # Fall 1: Produkt wurde verkauft
        if hoechstgebot and hoechstgebot.kauf_bestaetigt:
            self.istArchiviert = True
            self.save(update_fields=["istArchiviert"])
            return

        # Fall 2: Maximale Listungen erreicht UND unverkauft
        if self.anzahlListungen >= 3:
            self.istArchiviert = True
            self.save(update_fields=["istArchiviert"])
            return

    def relisten(self):
        """Produkt erneut einstellen - NUR Counter erhöhen und Status zurücksetzen"""
        if self.anzahlListungen >= 3:
            return False

        self.anzahlListungen += 1
        self.istArchiviert = False
        self.erstelltAm = timezone.now()
        self.save()
        return True

    def __str__(self):
        return self.name

