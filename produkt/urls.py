from django.urls import path
from . import views

app_name = 'produkt'
urlpatterns = [
    path('', views.produkt_liste, name='produkt_liste'),
    path("erstellen/", views.produkt_erstellen, name="produkt_erstellen"),
    path('meine/', views.meine_produkte, name='meine_produkte'),
    path("<int:pk>/", views.produkt_detail, name="produkt_detail"),
    path('<int:pk>/pdf/', views.produkt_pdf_download, name='produkt_pdf'),
    path('admin/gemeldete-produkte/', views.support_produkt_list, name='support_produkt_list'),
    path('produkt/<int:pk>/melden/', views.produkt_report, name='produkt_report'),
    path('admin/gemeldete-produkte/<int:pk>/unreport/', views.support_produkt_unreport, name='support_produkt_unreport'),
    path('admin/gemeldete-produkte/<int:pk>/delete/', views.support_produkt_delete, name='support_produkt_delete'),
]