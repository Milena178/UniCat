from django.urls import path
from. import views

urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('<int:pk>/', views.ProfileDetailView.as_view(), name='profil_detail'),

    path(
        'review/<int:pk>/vote/<str:direction>/',
        views.review_vote,
        name='review_vote'
    ),
]