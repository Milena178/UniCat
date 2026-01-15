from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from .models import Gebot
from produkt.models import Produkt
from django import forms

class GebotForm(forms.ModelForm):
    class Meta:
        model = Gebot
        fields = ["biethoehe"]

@login_required
def bieten(request, product_id):
    produkt = get_object_or_404(Produkt, pk=product_id, istArchiviert=False)

    if not produkt.auktion_aktiv():
        return HttpResponseForbidden("Auktion beendet")

    if produkt.verkaeufer_profil == request.user.profile:
        return HttpResponseForbidden(
            "Du kannst nicht auf dein eigenes Produkt bieten."
        )

    if request.method == "POST":
        form = GebotForm(request.POST)

        if form.is_valid():
            gebot = form.save(commit=False)
            gebot.produkt = produkt
            gebot.bieter = request.user.profile

            hoechstgebot = produkt.hoechstgebot()

            if hoechstgebot:
                mindestgebot = hoechstgebot.biethoehe
            else:
                mindestgebot = produkt.mindestpreis

            if gebot.biethoehe <= mindestgebot:
                form.add_error(
                    "biethoehe",
                    f"Dein Gebot muss höher als {mindestgebot} € sein."
                )
            else:
                gebot.save()
                return redirect(
                    "produkt_detail",
                    pk=produkt.pk
                )
    else:
        form = GebotForm()

    return render(request, "gebot/gebot_form.html", {
        "form": form,
        "produkt": produkt
    })

@login_required
def meine_gebote(request):
    gebote = Gebot.objects.filter(
        bieter=request.user.profile
    ).select_related("produkt")

    return render(request, "gebot/meine_gebote.html", {
        "gebote": gebote
    })