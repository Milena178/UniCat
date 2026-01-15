from django import forms
from datetime import timedelta
from .models import Produkt, Tag


class ProduktForm(forms.ModelForm):
    # Separate Felder für Stunden und Minuten
    auktionsdauer_stunden = forms.IntegerField(
        min_value=0,
        max_value=168,  # max 1 Woche (7 Tage)
        initial=0,
        label="Stunden",
        help_text="0-168 Stunden",
        widget=forms.NumberInput(attrs={
            'placeholder': '0',
            'style': 'width: 80px;'
        })
    )

    auktionsdauer_minuten = forms.IntegerField(
        min_value=0,
        max_value=59,
        initial=1,
        label="Minuten",
        help_text="0-59 Minuten",
        widget=forms.NumberInput(attrs={
            'placeholder': '1',
            'style': 'width: 80px;'
        })
    )

    class Meta:
        model = Produkt
        fields = [
            "name",
            "beschreibung",
            "bild",
            "tags",
            "mindestpreis",
            # auktionsdauer wird nicht direkt verwendet
        ]

        widgets = {
            'tags': forms.CheckboxSelectMultiple(),
            'beschreibung': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Nur bestehende Tags zur Auswahl
        self.fields['tags'].queryset = Tag.objects.all()
        self.fields['tags'].required = False

        # Wenn Produkt bearbeitet wird, Stunden/Minuten aus auktionsdauer extrahieren
        if self.instance and self.instance.pk and hasattr(self.instance,
                                                          'auktionsdauer') and self.instance.auktionsdauer:
            total_seconds = int(self.instance.auktionsdauer.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60

            self.fields['auktionsdauer_stunden'].initial = hours
            self.fields['auktionsdauer_minuten'].initial = minutes

    def clean(self):
        cleaned_data = super().clean()
        stunden = cleaned_data.get('auktionsdauer_stunden', 0)
        minuten = cleaned_data.get('auktionsdauer_minuten', 0)

        # Validierung: Mindestens 1 Minute Auktionsdauer
        total_minutes = (stunden * 60) + minuten

        if total_minutes < 1:
            raise forms.ValidationError(
                "Die Auktionsdauer muss mindestens 1 Minute betragen."
            )

        # Timedelta erstellen und im cleaned_data speichern
        cleaned_data['auktionsdauer'] = timedelta(
            hours=stunden,
            minutes=minuten
        )

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Auktionsdauer aus den separaten Feldern setzen
        instance.auktionsdauer = self.cleaned_data['auktionsdauer']

        if commit:
            instance.save()
            self.save_m2m()  # Tags speichern

        return instance