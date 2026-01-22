from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.utils import timezone
from datetime import timedelta

from django.views.decorators.http import require_POST

from gebot.models import Gebot
from gebot.views import GebotForm
from .models import Produkt
from .forms import ProduktForm, ProduktFilterForm
from .utils import generate_produkt_pdf

#  Produkt anlegen
@login_required
def produkt_erstellen(request):
    if not hasattr(request.user, 'profile'):
        messages.warning(request, "Bitte vervollständigen Sie zuerst Ihr Profil.")
        return redirect("profil:profil_erstellen")  # ✅ GEÄNDERT: Angepasst an deine URL

    user_profile = request.user.profile

    if request.method == "POST":
        form = ProduktForm(request.POST, request.FILES)
        if form.is_valid():
            produkt = form.save(commit=False)
            produkt.verkaeufer_profil = user_profile
            produkt.save()
            form.save_m2m()  # Tags speichern
            messages.success(request, "Produkt erfolgreich erstellt!")
            return redirect("produkt:produkt_detail", pk=produkt.pk)
    else:
        form = ProduktForm()

    return render(request, "produkt/produkt_erstellen.html", {
        "form": form
    })


#  Produkt anzeigen
def produkt_detail(request, pk):
    produkt = get_object_or_404(Produkt, pk=pk)

    # Archiviere nur wenn Auktion beendet ist
    # Die archive() Methode entscheidet selbst, ob archiviert wird
    if produkt.auktion_beendet():
        produkt.archive()

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
                    return redirect("produkt:produkt_detail", pk=produkt.pk)
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


# Öffentliche Produktliste
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

        jetzt = timezone.now()
        for produkt in produkte:
            ende = produkt.auktion_ende()
            if produkt.auktion_aktiv() and (ende - jetzt) <= timedelta(hours=3):
                produkt.endet_sehr_bald = True
            else:
                produkt.endet_sehr_bald = False

    return render(request, "produkt/produkt_liste.html", {
        "produkte": produkte,
        "filter_form": form,
    })


@login_required
def meine_produkte(request):
    if not hasattr(request.user, 'profile'):
        messages.warning(request, "Bitte erstellen Sie zuerst Ihr Profil.")
        return redirect("profil:profil_erstellen")

    user_profile = request.user.profile

    zeige_archiviert = request.GET.get('archiviert', 'false') == 'true'

    if zeige_archiviert:
        # Archivierte Produkte
        produkte = Produkt.objects.filter(
            verkaeufer_profil=user_profile,
            istArchiviert=True
        )
        archivierte_produkte = produkte
        aktive_produkte = []
        unverkaufte_produkte = []
        verkaufte_produkte = []
    else:
        # Aktive und unverkaufte Produkte
        alle_produkte = Produkt.objects.filter(
            verkaeufer_profil=user_profile,
            istArchiviert=False
        )

        aktive_produkte = []
        unverkaufte_produkte = []

        for produkt in alle_produkte:
            if produkt.auktion_aktiv():
                aktive_produkte.append(produkt)
            elif produkt.ist_unverkauft():
                unverkaufte_produkte.append(produkt)

        # Verkaufte Produkte (kauf_bestaetigt=True), egal ob archiviert oder nicht
        verkaufte_gebote = Gebot.objects.filter(
            produkt__verkaeufer_profil=user_profile,
            kauf_bestaetigt=True
        ).select_related('produkt', 'bieter')

        verkaufte_produkte = []
        for gebot in verkaufte_gebote:
            verkaufte_produkte.append({
                'produkt': gebot.produkt,
                'gebot': gebot,
                'kaeufer': gebot.bieter
            })

        archivierte_produkte = []

    return render(request, "produkt/meine_produkte.html", {
        "aktive_produkte": aktive_produkte,
        "unverkaufte_produkte": unverkaufte_produkte,
        "verkaufte_produkte": verkaufte_produkte,
        "archivierte_produkte": archivierte_produkte,
        "zeige_archiviert": zeige_archiviert
    })


# Produkt bearbeiten für Relisting
@login_required
def produkt_bearbeiten(request, pk):
    produkt = get_object_or_404(Produkt, pk=pk, verkaeufer_profil=request.user.profile)

    # Nur unverkaufte Produkte dürfen bearbeitet werden
    if not produkt.ist_unverkauft():
        messages.error(request, "Dieses Produkt kann nicht mehr bearbeitet werden.")
        return redirect("produkt:meine_produkte")

    if not produkt.kann_relistet_werden():
        messages.error(request, "Dieses Produkt kann nicht mehr erneut eingestellt werden (maximale Anzahl erreicht).")
        return redirect("produkt:meine_produkte")

    if request.method == "POST":
        form = ProduktForm(request.POST, request.FILES, instance=produkt)
        if form.is_valid():
            produkt = form.save(commit=False)
            # Relisting durchführen
            produkt.relisten()
            form.save_m2m()  # Tags speichern
            messages.success(request, f"Produkt erfolgreich erneut eingestellt! (Listung {produkt.anzahlListungen}/3)")
            return redirect("produkt:produkt_detail", pk=produkt.pk)
    else:
        form = ProduktForm(instance=produkt)

    return render(request, "produkt/produkt_bearbeiten.html", {
        "form": form,
        "produkt": produkt
    })


# Produkt endgültig archivieren
@login_required
@require_POST
def produkt_archivieren(request, pk):
    produkt = get_object_or_404(Produkt, pk=pk, verkaeufer_profil=request.user.profile)

    if not produkt.ist_unverkauft():
        messages.error(request, "Nur unverkaufte Produkte können archiviert werden.")
        return redirect("produkt:meine_produkte")

    produkt.archive()
    messages.success(request, f"Produkt '{produkt.name}' wurde archiviert.")
    return redirect("produkt:meine_produkte")


@login_required
def produkt_report(request, pk):
    produkt = get_object_or_404(Produkt, pk=pk)

    if request.method == "POST":
        produkt.gemeldet = True
        produkt.save()

    return redirect('produkt:produkt_detail', pk=produkt.pk)


@staff_member_required
def support_produkt_list(request):
    produkte = Produkt.objects.filter(gemeldet=True).order_by('-erstelltAm')
    return render(request, "admin/support_produkt_list.html", {
        "produkte": produkte
    })


@staff_member_required
@require_POST
def support_produkt_unreport(request, pk):
    produkt = get_object_or_404(Produkt, pk=pk)
    produkt.gemeldet = False
    produkt.save()
    return redirect('produkt:support_produkt_list')


@staff_member_required
@require_POST
def support_produkt_delete(request, pk):
    produkt = get_object_or_404(Produkt, pk=pk)
    produkt.delete()
    return redirect('produkt:support_produkt_list')