from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Review
from django.views.generic import DetailView
from django.shortcuts import get_object_or_404
from .models import UserProfile


class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

@login_required
def review_vote(request, pk, direction):
    review = get_object_or_404(Review, pk=pk)
    review.vote(request.user, direction)
    return redirect('profil_detail', pk=review.profile.pk)

class ProfileDetailView(DetailView):
    model = UserProfile
    template_name = 'profil_detail.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviews'] = self.object.reviews.all()
        return context
