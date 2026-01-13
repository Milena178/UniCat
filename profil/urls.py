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
    path('review/<int:pk>/report/', views.review_report, name='review_report'),
    path('cs/reviews/', views.cs_review_list, name='cs_review_list'),
    path('cs/review/<int:pk>/delete/', views.cs_review_disable, name='cs_review_disable'),
    path('cs/review/<int:pk>/delete/', views.cs_review_disable, name='cs_review_disable'),
    path('cs/review/<int:pk>/unreport/', views.cs_review_unreport, name='cs_review_unreport'),

    # Profil erstellen für neue User
    path('create/', views.ProfileCreateView.as_view(), name='profil_create'),

]
