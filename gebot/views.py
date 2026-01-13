from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib import messages
from .models import Gebot
from .models import Produkt
from .forms import GebotForm

@login_required
def bieten(request, product_id):
    produkt = get_object_or_404(Produkt, pk=product_id, istArchiviert=False)

    if not produkt.auktion_aktiv():
        return HttpResponseForbidden("Auktion beendet")

    form = GebotForm(request.POST)

    if form.is_valid():
        gebot = form.save(commit=False)
        gebot.produkt = produkt
        gebot.bieter = request.user

        hoechstes = produkt.hoechstgebot()

        min_benoetigt = (
            hoechstes.biethoehe if hoechstes else produkt.mindestpreis
        )

        if gebot.biethoehe <= min_benoetigt:
            form.add_error(
                "biethoehe",
                "Gebot muss höher als das aktuelle Höchstgebot sein."
            )
        else:
            gebot.save()
            return redirect("product_detail", pk=produkt.pk)

    return render(request, "gebot/bieten.html", {
        "form": form,
        "produkt": produkt
    })