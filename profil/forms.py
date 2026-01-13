from django import forms
from .models import UserProfile, Review


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'username',
            'bio',
            'street',
            'house_number',
            'zip_code',
            'city',
            'country',
            'profile_picture',
        ]

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['sterne', 'text']
