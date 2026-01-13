from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django.urls import reverse_lazy
from django.shortcuts import redirect, render, get_object_or_404
from django.views import generic
from django.views.generic import DetailView, UpdateView, DeleteView

from .models import UserProfile, Review
from .forms import UserProfileForm, ReviewForm


#class ProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
#    model = UserProfile
#    form_class = UserProfileForm
#    template_name = 'profil_edit.html'

#    def test_func(self):
#        return self.get_object().user == self.request.user

#    def get_success_url(self):
#        return reverse_lazy('profil_detail', kwargs={'pk': self.object.pk})

class ProfileUpdateView(UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'profil_edit.html'

    # nur eigener Nutzer darf bearbeiten
#    def test_func(self):
#        return self.get_object().user == self.request.user

    # zum Testen: kein Login, jeder kann das Profil bearbeiten
    def get_success_url(self):
        return reverse_lazy('profil_detail', kwargs={'pk': self.object.pk})


class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

@login_required
def review_vote(request, pk, direction):
    review = get_object_or_404(Review, pk=pk)
    review.vote(request.user, direction)
    return redirect('profil_detail', pk=review.profile.pk)

@login_required
def review_create(request, pk):
    profile = get_object_or_404(UserProfile, pk=pk)

    if profile.user == request.user:
        return redirect('profil_detail', pk=pk)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.profile = profile
            review.author = request.user
            review.save()
            return redirect('profil_detail', pk=pk)
    else:
        form = ReviewForm()

    return render(request, 'review_form.html', {
        'form': form,
        'profile': profile
    })

class ProfileDetailView(DetailView):
    model = UserProfile
    template_name = 'profil_detail.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviews'] = self.object.reviews.all()
        return context

class ReviewUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Review
    fields = ['sterne', 'text']
    template_name = 'review_edit.html'

    def test_func(self):
        return self.get_object().author == self.request.user

    def get_success_url(self):
        return reverse_lazy(
            'profil_detail',
            kwargs={'pk': self.object.profile.pk}
        )

class ReviewDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Review
    template_name = 'review_delete.html'

    def test_func(self):
        return self.get_object().author == self.request.user

    def get_success_url(self):
        return reverse_lazy(
            'profil_detail',
            kwargs={'pk': self.object.profile.pk}
        )

