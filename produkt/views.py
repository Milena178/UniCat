from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.utils import timezone
from datetime import timedelta
from gebot.models import Gebot
from gebot.views import GebotForm
from .models import Produkt
from .forms import ProduktForm, ProduktFilterForm
from .utils import generate_produkt_pdf
from profil.models import Review

#  Produkt anlegen
@login_required
def produkt_erstellen(request):
    # Prüfe ob User ein Profil hat, falls nicht -> erstellen lassen
    try:
        user_profile = request.user.profile
    except:
        messages.warning(request, "Bitte erstellen Sie zuerst Ihr Profil.")
        return redirect("profil_create")

    if request.method == "POST":
        form = ProduktForm(request.POST, request.FILES)
        if form.is_valid():
            produkt = form.save(commit=False)
            produkt.verkaeufer_profil = user_profile
            produkt.save()
            form.save_m2m()  # Tags speichern
            messages.success(request, "Produkt erfolgreich erstellt!")
            return redirect("produkt_detail", pk=produkt.pk)
    else:
        form = ProduktForm()

    return render(request, "produkt/produkt_erstellen.html", {
        "form": form
    })

#  Produkt anzeigen
def produkt_detail(request, pk):
    produkt = get_object_or_404(Produkt, pk=pk)
    produkt.archive() if produkt.auktion_beendet() else None

    gebot_form = None
    error = None

    if request.user.is_authenticated and produkt.auktion_aktiv():
        if request.method == "POST":
            gebot_form = GebotForm(request.POST)
            if gebot_form.is_valid():
                gebot = gebot_form.save(commit=False)
                gebot.produkt = produkt
                gebot.bieter = request.user.profile

                hoechst = produkt.hoechstgebot()
                mindest = hoechst.biethoehe if hoechst else produkt.mindestpreis

                if gebot.biethoehe <= mindest:
                    error = f"Gebot muss höher als {mindest} € sein."
                else:
                    gebot.save()
                    return redirect("produkt_detail", pk=produkt.pk)
        else:
            gebot_form = GebotForm()

    return render(request, "produkt/produkt_detail.html", {
        "produkt": produkt,
        "gebot_form": gebot_form,
        "error": error,
    })


# PDF Download
@login_required
def produkt_pdf_download(request, pk):
    produkt = get_object_or_404(Produkt, pk=pk)

    # Generiere PDF
    pdf_buffer = generate_produkt_pdf(produkt)

    # Sende als Download
    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="produkt_{produkt.pk}_{produkt.name}.pdf"'
    return response


# Öffentliche Produktliste (wie bei Kleinanzeigen)
def produkt_liste(request):
    produkte = Produkt.objects.filter(istArchiviert=False).select_related('verkaeufer_profil')

    produkte = produkte.annotate(
        durchschnitt_bewertung=Avg('verkaeufer_profil__reviews__sterne')
    )

    form = ProduktFilterForm(request.GET or None)

    if form.is_valid():
        # Textsuche im Produktnamen
        suche = form.cleaned_data.get('suche')
        if suche:
            produkte = produkte.filter(
                Q(name__icontains=suche) | Q(beschreibung__icontains=suche)
            )

        # Tag-Filter
        tags = form.cleaned_data.get('tags')
        if tags:
            produkte = produkte.filter(tags__in=tags).distinct()

        # Bewertungsfilter
        min_bewertung = form.cleaned_data.get('min_bewertung')
        if min_bewertung:
            min_sterne = int(min_bewertung)
            produkte = produkte.filter(durchschnitt_bewertung__gte=min_sterne)

        # "Endet bald" Filter (nächste 3 Stunden)
        endet_bald = form.cleaned_data.get('endet_bald')
        if endet_bald:
            jetzt = timezone.now()
            grenze = jetzt + timedelta(hours=3)

            # Filtere Produkte, deren Auktionsende in den nächsten 3 Stunden liegt
            gefilterte_ids = []
            for p in produkte:
                ende = p.auktion_ende()
                if jetzt < ende <= grenze:
                    gefilterte_ids.append(p.pk)

            produkte = produkte.filter(pk__in=gefilterte_ids)

        # Sortierung
        sortierung = form.cleaned_data.get('sortierung')
        if sortierung == 'neueste':
            produkte = produkte.order_by('-erstelltAm')
        elif sortierung == 'aelteste':
            produkte = produkte.order_by('erstelltAm')
        elif sortierung == 'preis_aufsteigend':
            produkte = produkte.order_by('mindestpreis')
        elif sortierung == 'preis_absteigend':
            produkte = produkte.order_by('-mindestpreis')
        elif sortierung == 'endet_bald':
            # Für "Endet bald" sortieren wir manuell
            produkte_mit_ende = []
            for p in produkte:
                produkte_mit_ende.append((p, p.auktion_ende()))
            produkte_mit_ende.sort(key=lambda x: x[1])
            produkte = [p[0] for p in produkte_mit_ende]

    return render(request, "produkt/produkt_liste.html", {
        "produkte": produkte,
        "filter_form": form,
    })

@login_required
def meine_produkte(request):
    try:
        user_profile = request.user.profile
        produkte = Produkt.objects.filter(
            verkaeufer_profil=user_profile,
            istArchiviert=False
        )
        return render(request, "produkt/meine_produkte.html", {
            "produkte": produkte
        })
    except:
        messages.warning(request, "Bitte erstellen Sie zuerst Ihr Profil.")
        return redirect("profil_create")