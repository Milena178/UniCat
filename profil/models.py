from datetime import date
from django.db import models
from django.conf import settings


class UserProfile(models.Model):
    USER_TYPES = [
        ('K', 'Käufer'),
        ('V', 'Verkäufer'),
        ('B', 'Beides'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    username = models.CharField(max_length=50)  # optional, zur Anzeige
    bio = models.TextField(blank=True)
    user_type = models.CharField(max_length=1, choices=USER_TYPES, default='K')
    erstellt_am = models.DateField(default=date.today)

    class Meta:
        ordering = ['user_type', 'username']
        verbose_name = 'User Profil'
        verbose_name_plural = 'User Profile'

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

    def __repr__(self):
        return f"{self.username} / {self.get_user_type_display()}"


class Review(models.Model):
    STERNE_CHOICES = [(i, str(i)) for i in range(1, 6)]

    bewerteter = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='reviews')
    bewertender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    sterne = models.IntegerField(choices=STERNE_CHOICES)
    text = models.TextField()
    erstellt_am = models.DateField(default=date.today)
    gemeldet = models.BooleanField(default=False)

    class Meta:
        ordering = ['-erstellt_am']
        verbose_name = 'Bewertung'
        verbose_name_plural = 'Bewertungen'

    def __str__(self):
        return f"Review von {self.bewertender.username} ({self.sterne} Sterne) an {self.bewerteter.username}"

    def __repr__(self):
        return f"{self.bewertender.username} -> {self.bewerteter.username}: {self.sterne} Sterne"
