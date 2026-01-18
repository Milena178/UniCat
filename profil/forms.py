from django import forms
from .models import UserProfile, Review, SupportRequest


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

class SupportRequestForm(forms.ModelForm):
    class Meta:
        model = SupportRequest
        fields = ['subject']

class LieferadresseForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['street', 'house_number', 'zip_code', 'city', 'country']
        widgets = {
            'street': forms.TextInput(attrs={'placeholder': 'Straße'}),
            'house_number': forms.TextInput(attrs={'placeholder': 'Hausnummer'}),
            'zip_code': forms.TextInput(attrs={'placeholder': 'PLZ'}),
            'city': forms.TextInput(attrs={'placeholder': 'Stadt'}),
            'country': forms.TextInput(attrs={'placeholder': 'Land'}),
        }