from datetime import date
from django.db import models
from django.conf import settings

def user_directory_path(instance, filename):
    # Profilbilder landen unter: media/profile_pictures/user_<id>/<filename>
    return f'profile_pictures/user_{instance.user.id}/{filename}'

class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    # Anzeige-Daten
    username = models.CharField(max_length=50)
    bio = models.TextField(blank=True)

    # Adresse
    street = models.CharField("Straße", max_length=100, blank=True)
    house_number = models.CharField("Hausnummer", max_length=10, blank=True)
    zip_code = models.CharField("PLZ", max_length=10, blank=True)
    city = models.CharField("Ort", max_length=50, blank=True)
    country = models.CharField("Land", max_length=50, blank=True)

    # Profilbild
    profile_picture = models.ImageField(
        upload_to=user_directory_path,
        blank=True,
        null=True
    )

    erstellt_am = models.DateField(default=date.today)

    class Meta:
        ordering = ['username']
        verbose_name = 'User Profil'
        verbose_name_plural = 'User Profile'

    def __str__(self):
        return self.username

class Review(models.Model):
    STERNE_CHOICES = [(i, str(i)) for i in range(1, 6)]

    profile = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    sterne = models.IntegerField(choices=STERNE_CHOICES)
    text = models.TextField()
    erstellt_am = models.DateTimeField(auto_now_add=True)
    gemeldet = models.BooleanField(default=False)

    class Meta:
        ordering = ['-erstellt_am']
        verbose_name = 'Bewertung'
        verbose_name_plural = 'Bewertungen'

    # ===== Voting-Logik =====

    def get_upvotes(self):
        return ReviewVote.objects.filter(
            vote_type='U',
            review=self
        )

    def get_upvotes_count(self):
        return self.get_upvotes().count()

    def get_downvotes(self):
        return ReviewVote.objects.filter(
            vote_type='D',
            review=self
        )

    def get_downvotes_count(self):
        return self.get_downvotes().count()

    def score(self):
        return self.get_upvotes_count() - self.get_downvotes_count()

    def vote(self, user, direction):
        vote_value = 'U'
        if direction == 'down':
            vote_value = 'D'

        existing_vote = ReviewVote.objects.filter(
            user=user,
            review=self
        ).first()

        # Gleiches Vote → entfernen
        if existing_vote and existing_vote.vote_type == vote_value:
            existing_vote.delete()
            return

        # Vote wechseln
        if existing_vote:
            existing_vote.vote_type = vote_value
            existing_vote.save()
            return

        # Neues Vote
        ReviewVote.objects.create(
            vote_type=vote_value,
            user=user,
            review=self
        )

    def __str__(self):
        return f"{self.author.username} → {self.profile.username}"

class ReviewVote(models.Model):
    VOTE_TYPES = [
        ('U', 'Upvote'),
        ('D', 'Downvote'),
    ]

    vote_type = models.CharField(
        max_length=1,
        choices=VOTE_TYPES
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='votes'
    )

    class Meta:
        unique_together = ('user', 'review')
        verbose_name = 'Bewertungs-Vote'
        verbose_name_plural = 'Bewertungs-Votes'

    def __str__(self):
        return f"{self.user.username} → {self.vote_type}"
