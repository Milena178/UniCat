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
    erstelltAm = models.DateTimeField(auto_now_add=True)

    kauf_bestaetigt = models.BooleanField(default=False)
    kauf_bestaetigt_am = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-biethoehe']
        verbose_name = 'Gebot'
        verbose_name_plural = 'Gebote'

    def __str__(self):
        return f"{self.biethoehe} € auf {self.produkt}"

    def ist_gewonnen(self):
        return (
                not self.produkt.auktion_aktiv() and
                self == self.produkt.hoechstgebot()
        )
