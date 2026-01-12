from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.product_create, name="product_create"),
    path("<int:pk>/", views.product_detail, name="product_detail"),
]