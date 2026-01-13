from django.urls import path
from . import views

app_name = "gebot"

urlpatterns = [
    path("meine/", views.meine_gebote, name="meine_gebote"),
]