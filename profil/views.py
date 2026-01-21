from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied

from django.urls import reverse_lazy
from django.shortcuts import redirect, render
from django.views import generic
from django.views.generic import UpdateView, DeleteView

from gebot.models import Gebot
from .models import Review, SupportRequest, SupportMessage
from .forms import UserProfileForm, ReviewForm, SupportRequestForm

from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST

from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from django.db.models import Avg
from .models import UserProfile
from django.contrib.auth import get_user_model
from produkt.models import Produkt

# Custom Form für UserCreation
class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Passwort", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Passwort bestätigen", widget=forms.PasswordInput)
    first_name = forms.CharField(label="Vorname", max_length=30, required=True)
    last_name = forms.CharField(label="Nachname", max_length=30, required=True)
    email = forms.EmailField(label="E-Mail", required=True)

    class Meta:
        model = get_user_model()
        fields = ('username', 'first_name', 'last_name', 'email')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Die Passwörter stimmen nicht überein.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

# SignUp View
class SignUp(generic.CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        user = form.save()

        profile = UserProfile.objects.create(
            user=user,
            username=user.username
        )

        # User einloggen
        login(self.request, user)

        # Direkt zur Profil-Bearbeitung weiterleiten
        return redirect('profil:profil_detail', pk=profile.pk)

#Eigenes Profil bearbeiten
class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'profil/profil_edit.html'

#Nur der Profilbesitzer darf dieses Profil bearbeiten
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != request.user:
            raise PermissionDenied("Du darfst dieses Profil nicht bearbeiten.")
        return super().dispatch(request, *args, **kwargs)

#Nach erfolgreichem Speichern wird man zu Profil-Detailseite geleitet
    def get_success_url(self):
        return reverse_lazy('profil:profil_detail', kwargs={'pk': self.object.pk})

#User automatisch setzten und doppelte Profile verhindern
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

#Profil anzeigen nach der erstellung
    def get_success_url(self):
        # Nach Erstellung auf Profil-Detail weiterleiten
        return reverse_lazy('profil:profil_detail', kwargs={'pk': self.object.pk})

#Bewertungen
@login_required
def review_vote(request, pk, direction):
    review = get_object_or_404(Review, pk=pk)
    review.vote(request.user, direction)
    return redirect('profil:profil_detail', pk=review.profile.pk)

@login_required
def review_create(request, gebot_id):
    gebot = get_object_or_404(
        Gebot,
        pk=gebot_id,
        bieter=request.user.profile,
        kauf_bestaetigt=True
    )

    profile = gebot.produkt.verkaeufer_profil

    # Verkäufer darf sich nicht selbst bewerten
    if profile.user == request.user:
        return redirect('profil:profil_detail', pk=profile.pk)

    # Schon bewertet?
    if hasattr(gebot, 'review'):
        messages.warning(request, "Dieser Kauf wurde bereits bewertet.")
        return redirect('profil:profil_detail', pk=profile.pk)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.profile = profile
            review.author = request.user
            review.gebot = gebot
            review.save()
            return redirect('profil:profil_detail', pk=profile.pk)
    else:
        form = ReviewForm()

    return render(request, 'bewertung/review_form.html', {
        'form': form,
        'profile': profile,
        'gebot': gebot
    })

class ProfileDetailView(DetailView):
    model = UserProfile
    template_name = 'profil/profil_detail.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        profile_id = self.kwargs.get('pk')
        profile = get_object_or_404(UserProfile, pk=profile_id)
        return profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Bewertungen
        context['reviews'] = self.object.reviews.all()
        durchschnitt = self.object.reviews.aggregate(avg_sterne=Avg('sterne'))['avg_sterne']
        context['profil_durchschnitt'] = round(durchschnitt or 0, 2)

        # Private Daten sichtbar?
        user = self.request.user
        context['darf_private_daten_sehen'] = False

        if user.is_authenticated:
            if user == self.object.user:
                # Profilbesitzer
                context['darf_private_daten_sehen'] = True
                context['darf_email_sehen'] = True
            else:
                # Käufer?
                hat_gekauft = Gebot.objects.filter(
                    produkt__verkaeufer_profil=self.object,
                    bieter__user=user,
                    kauf_bestaetigt=True
                ).exists()

                if hat_gekauft:
                    context['darf_email_sehen'] = True

        # Produkte nur bei fremden Profilen anzeigen
            produkte = Produkt.objects.filter(
                verkaeufer_profil=self.object
            )

            if user == self.object.user:
                # Eigener Nutzer: alles sehen
                context['user_produkte'] = produkte
            else:
                # Fremde Nutzer: nur aktive, nicht archivierte Produkte
                context['user_produkte'] = [
                    p for p in produkte
                    if p.auktion_aktiv() and not p.istArchiviert
                ]

        return context

#Bewertungen melden von dem User
@login_required
@require_POST
def review_report(request, pk):
    review = get_object_or_404(Review, pk=pk)
    review.gemeldet = True
    review.save()
    return redirect('profil:profil_detail', pk=review.profile.pk)

#Kunden-Service Meldungen Ansehen
@staff_member_required
def cs_review_list(request):
    """Liste aller gemeldeten Reviews"""
    reviews = Review.objects.filter(gemeldet=True).order_by('-erstellt_am')
    return render(request, 'admin/cs_review_list.html', {'reviews': reviews})

@staff_member_required
def cs_review_disable(request, pk):
    review = get_object_or_404(Review, pk=pk)
    review.delete()  # Review löschen
    return redirect('profil:cs_review_list')

@staff_member_required
def cs_review_unreport(request, pk):
    review = get_object_or_404(Review, pk=pk)
    review.gemeldet = False
    review.save()
    return redirect('profil:cs_review_list')

#Review bearbeiten/löschen
class ReviewUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Review
    fields = ['sterne', 'text']
    template_name = 'bewertung/review_edit.html'

    def test_func(self):
        return self.get_object().author == self.request.user

    def get_success_url(self):
        return reverse_lazy('profil:profil_detail', kwargs={'pk': self.object.profile.pk})


class ReviewDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Review
    template_name = 'bewertung/review_delete.html'

    def test_func(self):
        return self.get_object().author == self.request.user

    def get_success_url(self):
        review = self.get_object()
        return reverse_lazy('profil:profil_detail', kwargs={'pk': review.profile.pk})

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
        return redirect('profil:support_request_list')

    return render(
        request,
        'anfragen/support_request_answer.html',
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

            return redirect('profil:support_user_list')
    else:
        form = SupportRequestForm()

    return render(request, 'anfragen/support_request_form.html', {'form': form})

@login_required
def support_user_list(request):
    anfragen = SupportRequest.objects.filter(user=request.user)
    return render(request, 'anfragen/support_user_list.html', {'anfragen': anfragen})

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
        'anfragen/support_request_detail.html',
        {'anfrage': anfrage}
    )

@staff_member_required
def support_request_list(request):
    anfragen = SupportRequest.objects.exclude(
        status=SupportRequest.STATUS_CLOSED
    ).order_by('-created_at')

    return render(
        request,
        'admin/support_request_list.html',
        {'anfragen': anfragen}
    )

@staff_member_required
@require_POST
def support_close(request, pk):
    anfrage = get_object_or_404(SupportRequest, pk=pk)
    anfrage.status = SupportRequest.STATUS_CLOSED
    anfrage.save()
    return redirect('profil:support_detail', pk=pk)

@staff_member_required
@require_POST
def support_delete(request, pk):
    anfrage = get_object_or_404(SupportRequest, pk=pk)
    anfrage.delete()
    return redirect('profil:support_request_list')

@staff_member_required
def admin_dashboard(request):
    return render(request, "admin/admin_dashboard.html")
