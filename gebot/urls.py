from django.urls import path
from . import views

app_name = "gebot"

urlpatterns = [
    path("meine/", views.meine_gebote, name="meine_gebote"),
    path('kauf-bestaetigen/<int:gebot_id>/', views.kauf_bestaetigen, name='kauf_bestaetigen'),
]