from django import forms
from .models import UserProfile, Review, SupportRequest
from django import forms
from django.contrib.auth import get_user_model


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

class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Passwort",
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label="Passwort bestätigen",
        widget=forms.PasswordInput
    )

    class Meta:
        model = get_user_model()
        fields = ('username', 'first_name', 'last_name', 'email')
        help_texts = {
            'username': '',
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 != password2:
            raise forms.ValidationError(
                "Die Passwörter stimmen nicht überein."
            )

        return password2
