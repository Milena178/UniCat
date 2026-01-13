from django import forms
from .models import Gebot

class GebotForm(forms.ModelForm):
    class Meta:
        model = Gebot
        fields = ['biethoehe']
