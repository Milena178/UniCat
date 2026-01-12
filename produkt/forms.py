from django import forms
from .models import Produkt

class ProductForm(forms.ModelForm):
    class Meta:
        model = Produkt
        fields = [
            "name",
            "beschreibung",
            # "bild",
            # "tags",
            "mindestpreis",
            "auktionsdauer",
        ]