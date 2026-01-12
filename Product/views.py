from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product
from .forms import ProductForm

#  Produkt anlegen
@login_required
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES) #  nutzt das Formular auf forms.py
        if form.is_valid():
            product = form.save(commit=False)
            product.verkaeufer = request.user
            product.save()
            form.save_m2m()
            return redirect("product_detail", pk=product.pk)
    else:
        form = ProductForm()

    return render(request, "products/product_form.html", {
        "form": form
    })

#  Produkt anzeigen
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, is_archived=False)
    return render(request, "products/product_detail.html", {
        "product": product
    })