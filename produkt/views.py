from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from .models import Produkt
from .forms import ProductForm
from .utils import generate_product_pdf

#  Produkt anlegen
@login_required
def product_create(request):
    # Prüfe ob User ein Profil hat, falls nicht -> erstellen lassen
    try:
        user_profile = request.user.userprofile
    except:
        messages.warning(request, "Bitte erstellen Sie zuerst Ihr Profil.")
        return redirect("profile_create")

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.verkaeufer_profil = user_profile
            product.save()
            form.save_m2m()  # Tags speichern
            messages.success(request, "Produkt erfolgreich erstellt!")
            return redirect("product_detail", pk=product.pk)
    else:
        form = ProductForm()

    return render(request, "produkt/product_form.html", {
        "form": form
    })

#  Produkt anzeigen
def product_detail(request, pk):
    produkt = get_object_or_404(Produkt, pk=pk, istArchiviert=False)
    return render(request, "produkt/product_detail.html", {
        "product": produkt
    })


# PDF Download
@login_required
def product_pdf_download(request, pk):
    produkt = get_object_or_404(Produkt, pk=pk)

    # Generiere PDF
    pdf_buffer = generate_product_pdf(produkt)

    # Sende als Download
    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="produkt_{produkt.pk}_{produkt.name}.pdf"'
    return response


# Öffentliche Produktliste (wie bei Kleinanzeigen)
def product_list(request):
    produkte = Produkt.objects.filter(istArchiviert=False).select_related('verkaeufer_profil')

    # Optional: Filter nach Tags
    tag_filter = request.GET.get('tag')
    if tag_filter:
        produkte = produkte.filter(tags__name=tag_filter)

    return render(request, "produkt/product_list.html", {
        "produkte": produkte,
        "tag_filter": tag_filter
    })

@login_required
def my_products(request):
    try:
        user_profile = request.user.userprofile
        produkte = Produkt.objects.filter(
            verkaeufer_profil=user_profile,
            istArchiviert=False
        )
        return render(request, "produkt/my_products.html", {
            "produkte": produkte
        })
    except:
        messages.warning(request, "Bitte erstellen Sie zuerst Ihr Profil.")
        return redirect("profile_create")