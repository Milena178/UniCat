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

        # Wenn Produkt bearbeitet wird, Stunden und Minuten aus auktionsdauer extrahieren
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

        # Mindestens 1 Minute Auktionsdauer
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


class ProduktFilterForm(forms.Form):
    BEWERTUNG_CHOICES = [
        ('', 'Alle Bewertungen'),
        ('5', '5 Sterne'),
        ('4', '4+ Sterne'),
        ('3', '3+ Sterne'),
    ]

    SORTIERUNG_CHOICES = [
        ('neueste', 'Neueste zuerst'),
        ('aelteste', 'Älteste zuerst'),
        ('preis_aufsteigend', 'Preis aufsteigend'),
        ('preis_absteigend', 'Preis absteigend'),
        ('endet_bald', 'Endet bald'),
    ]

    suche = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Produktname durchsuchen...',
            'class': 'search-input'
        })
    )

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Tags'
    )

    min_bewertung = forms.ChoiceField(
        choices=BEWERTUNG_CHOICES,
        required=False,
        label='Mindestbewertung Verkäufer'
    )

    endet_bald = forms.BooleanField(
        required=False,
        label='Endet in den nächsten 3 Stunden'
    )

    sortierung = forms.ChoiceField(
        choices=SORTIERUNG_CHOICES,
        required=False,
        initial='neueste',
        label='Sortierung'
    )