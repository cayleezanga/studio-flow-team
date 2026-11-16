"""URL -> view -> template, following the Scarlet Roasters starter."""
from django.shortcuts import render
from .sample_data import SAMPLE_SESSIONS


def home(request):
    return render(request, 'pages/home.html', {'featured': SAMPLE_SESSIONS[:3]})


def schedule(request):
    return render(request, 'pages/schedule.html', {'sessions': SAMPLE_SESSIONS})


def reservations(request):
    # Placeholder only: no booking saved yet. We will add this after Neon + models.
    return render(request, 'pages/reservations.html')


def about(request):
    return render(request, 'pages/about.html')
