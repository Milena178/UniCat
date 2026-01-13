from django.urls import path
from . import views

urlpatterns = [
    # ===== Registrierung =====
    path('signup/', views.SignUp.as_view(), name='signup'),

    # ===== Profil anzeigen =====
    path('<int:pk>/', views.ProfileDetailView.as_view(), name='profil_detail'),

    # ===== Bewertungen =====
    path('<int:pk>/review/add/', views.review_create, name='review_add'),  # Neue Bewertung schreiben
    path('review/<int:pk>/edit/', views.ReviewUpdateView.as_view(), name='review_edit'),  # Bewertung bearbeiten
    path('review/<int:pk>/delete/', views.ReviewDeleteView.as_view(), name='review_delete'),  # Bewertung löschen
    path('review/<int:pk>/vote/<str:direction>/', views.review_vote, name='review_vote'),  # Upvote/Downvote

    # ===== Profil bearbeiten =====
    path('<int:pk>/edit/', views.ProfileUpdateView.as_view(), name='profil_edit'),
]
