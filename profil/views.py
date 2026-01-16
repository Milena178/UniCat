from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied

from django.urls import reverse_lazy
from django.shortcuts import redirect, render, get_object_or_404
from django.views import generic
from django.views.generic import DetailView, UpdateView, DeleteView

from .models import UserProfile, Review, SupportRequest, SupportMessage
from .forms import UserProfileForm, ReviewForm, SupportRequestForm

from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST

#Signup-View
from .models import UserProfile

class SignUp(generic.CreateView):
    form_class = UserCreationForm
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        user = form.save()

        # Leeres Profil direkt anlegen
        UserProfile.objects.create(
            user=user,
            username=user.username  # sinnvoll vorbelegen
        )

        # User einloggen
        login(self.request, user)

        # Direkt zur Profil-Bearbeitung
        return redirect('profil_edit', pk=user.profile.pk)

#Eigenes Profil bearbeiten
class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'profil_edit.html'

#Nur der Profilbesitzer darf dieses Profil bearbeiten
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != request.user:
            raise PermissionDenied("Du darfst dieses Profil nicht bearbeiten.")
        return super().dispatch(request, *args, **kwargs)

#Nach erfolgreichem Speichern wird man zu Profil-Detailseite geleitet
    def get_success_url(self):
        return reverse_lazy('profil_detail', kwargs={'pk': self.object.pk})

#User automatisch setzten und doppelte Profile verhindern
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

#Profil anzeigen nach der erstellung
    def get_success_url(self):
        # Nach Erstellung auf Profil-Detail weiterleiten
        return reverse_lazy('profil_detail', kwargs={'pk': self.object.pk})

#Profil anzeigen
class ProfileDetailView(DetailView):
    model = UserProfile
    template_name = 'profil_detail.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviews'] = self.object.reviews.all()
        return context

#Bewertungen
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

#Bewertungen melden von dem User
@login_required
@require_POST
def review_report(request, pk):
    review = get_object_or_404(Review, pk=pk)
    review.gemeldet = True
    review.save()
    return redirect('profil_detail', pk=review.profile.pk)

#Kunden-Service Meldungen Ansehen
@staff_member_required
def cs_review_list(request):
    """Liste aller gemeldeten Reviews"""
    reviews = Review.objects.filter(gemeldet=True).order_by('-erstellt_am')
    return render(request, 'cs_review_list.html', {'reviews': reviews})

@staff_member_required
def cs_review_disable(request, pk):
    """Customer-Service kann Review deaktivieren (z.B. gemeldet = False / löschen)"""
    review = get_object_or_404(Review, pk=pk)
    review.delete()  # Review löschen
    return redirect('cs_review_list')

@staff_member_required
def cs_review_unreport(request, pk):
    """Customer-Service kann Meldung zurücksetzen, wenn Review in Ordnung ist"""
    review = get_object_or_404(Review, pk=pk)
    review.gemeldet = False
    review.save()
    return redirect('cs_review_list')

#Review bearbeiten/löschen
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

@staff_member_required
def support_request_answer(request, pk):
    anfrage = get_object_or_404(SupportRequest, pk=pk)

    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            SupportMessage.objects.create(
                request=anfrage,
                sender=request.user,
                text=text
            )
            anfrage.status = SupportRequest.STATUS_ANSWERED
            anfrage.save()

        # zurück zur Tabelle
        return redirect('support_request_list')

    return render(
        request,
        'support_request_answer.html',
        {'anfrage': anfrage}
    )


@login_required
def support_request_create(request):
    if request.method == 'POST':
        form = SupportRequestForm(request.POST)
        message_text = request.POST.get('message')

        if form.is_valid() and message_text:
            anfrage = form.save(commit=False)
            anfrage.user = request.user
            anfrage.status = SupportRequest.STATUS_OPEN
            anfrage.save()

            SupportMessage.objects.create(
                request=anfrage,
                sender=request.user,
                text=message_text
            )

            return redirect('support_user_list')
    else:
        form = SupportRequestForm()

    return render(request, 'support_request_form.html', {'form': form})

@login_required
def support_user_list(request):
    anfragen = SupportRequest.objects.filter(user=request.user)
    return render(request, 'support_user_list.html', {'anfragen': anfragen})

@login_required
def support_request_detail(request, pk):
    anfrage = get_object_or_404(SupportRequest, pk=pk)

    # Zugriffsschutz
    if not request.user.is_staff and anfrage.user != request.user:
        raise PermissionDenied

    if request.method == 'POST' and anfrage.status != SupportRequest.STATUS_CLOSED:
        text = request.POST.get('text')
        if text:
            SupportMessage.objects.create(
                request=anfrage,
                sender=request.user,
                text=text
            )

            #Status setzen nach Admin Antwort
            if request.user.is_staff:
                anfrage.status = SupportRequest.STATUS_ANSWERED
                anfrage.save()

            # gleiche Seite neu rendern
    return render(
        request,
        'support_request_detail.html',
        {'anfrage': anfrage}
    )

@staff_member_required
def support_request_list(request):
    anfragen = SupportRequest.objects.exclude(
        status=SupportRequest.STATUS_CLOSED
    ).order_by('-created_at')

    return render(
        request,
        'support_request_list.html',
        {'anfragen': anfragen}
    )

@staff_member_required
@require_POST
def support_close(request, pk):
    anfrage = get_object_or_404(SupportRequest, pk=pk)
    anfrage.status = SupportRequest.STATUS_CLOSED
    anfrage.save()
    return redirect('support_detail', pk=pk)

@staff_member_required
@require_POST
def support_delete(request, pk):
    anfrage = get_object_or_404(SupportRequest, pk=pk)
    anfrage.delete()
    return redirect('support_request_list')
