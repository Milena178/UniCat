from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path("create/", views.product_create, name="product_create"),
    path('my/', views.my_products, name='my_products'),
    path("<int:pk>/", views.product_detail, name="product_detail"),
    path('<int:pk>/pdf/', views.product_pdf_download, name='product_pdf'),
]