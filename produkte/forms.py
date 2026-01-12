from django import forms
from .models import Produkte

class ProductForm(forms.ModelForm):
    class Meta:
        model = Produkte
        fields = [
            "name",
            "beschreibung",
            # "bild",
            # "tags",
            "mindestpreis",
            "auktionsdauer",
        ]