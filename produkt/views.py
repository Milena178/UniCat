from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from .models import Produkt
from .forms import ProduktForm
from .utils import generate_produkt_pdf

#  Produkt anlegen
@login_required
def produkt_erstellen(request):
    # Prüfe ob User ein Profil hat, falls nicht -> erstellen lassen
    try:
        user_profile = request.user.userprofile
    except:
        messages.warning(request, "Bitte erstellen Sie zuerst Ihr Profil.")
        return redirect("profile_create")

    if request.method == "POST":
        form = ProduktForm(request.POST, request.FILES)
        if form.is_valid():
            produkt = form.save(commit=False)
            produkt.verkaeufer_profil = user_profile
            produkt.save()
            form.save_m2m()  # Tags speichern
            messages.success(request, "Produkt erfolgreich erstellt!")
            return redirect("product_detail", pk=produkt.pk)
    else:
        form = ProduktForm()

    return render(request, "produkt/produkt_erstellen.html", {
        "form": form
    })

#  Produkt anzeigen
def produkt_detail(request, pk):
    produkt = get_object_or_404(Produkt, pk=pk, istArchiviert=False)
    return render(request, "produkt/produkt_detail.html", {
        "produkt": produkt
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

    # Optional: Filter nach Tags
    tag_filter = request.GET.get('tag')
    if tag_filter:
        produkte = produkte.filter(tags__name=tag_filter)

    return render(request, "produkt/produkt_liste.html", {
        "produkte": produkte,
        "tag_filter": tag_filter
    })

@login_required
def meine_produkte(request):
    try:
        user_profile = request.user.userprofile
        produkte = Produkt.objects.filter(
            verkaeufer_profil=user_profile,
            istArchiviert=False
        )
        return render(request, "produkt/meine_produkte.html", {
            "produkte": produkte
        })
    except:
        messages.warning(request, "Bitte erstellen Sie zuerst Ihr Profil.")
        return redirect("profile_create")