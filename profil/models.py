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
