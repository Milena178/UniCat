from django.db import models
from django.utils import timezone
from produkt.models import Produkt


class Gebot(models.Model):

    produkt = models.ForeignKey(
        Produkt,
        on_delete=models.CASCADE,
        related_name="gebote"
    )

    bieter = models.ForeignKey(
        'profil.UserProfile',
        on_delete=models.CASCADE,
        related_name="gebote",
    )

    biethoehe = models.DecimalField(max_digits=8, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-biethoehe']
        verbose_name = 'Gebot'
        verbose_name_plural = 'Gebote'

    #  Aktuelles Höchstgebot ermitteln
    def hoechstgebot(self):
        return self.gebote.order_by("-biethoehe").first()

    #  Auktion läuft
    def auktion_aktiv(self):
        return (
            not self.istArchiviert and
            timezone.now() < self.auktion_endet()
        )

    #  Auktion endet
    def auktion_endet(self):
        return timezone.now() >= self.auktion_endet()