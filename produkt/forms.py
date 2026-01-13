from django import forms
from .models import Produkt, Tag

class ProduktForm(forms.ModelForm):
    class Meta:
        model = Produkt
        fields = [
            "name",
            "beschreibung",
            "bild",
            "tags",
            "mindestpreis",
            "auktionsdauer",
        ]

        widgets = {
            'tags': forms.CheckboxSelectMultiple(),  # Mehrfachauswahl
            'beschreibung': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Nur bestehende Tags zur Auswahl
        self.fields['tags'].queryset = Tag.objects.all()
        self.fields['tags'].required = False