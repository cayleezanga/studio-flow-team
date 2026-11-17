"""Studio Flow pages. Public schedule; staff-only reservation management."""
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError
from django.db.models import Count, F, Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from operations.booking import create_booking, change_booking_status, delete_unpaid_booking
from operations.models import ClassSession, Reservation
from .forms import BookClassForm, StatusForm


# User-facing browsing is public, but member details and booking actions are
# staff-only until customer authentication is built in a later step.
def session_list():
    return (
        ClassSession.objects
        .select_related('class_type', 'instructor', 'room')
        .annotate(
            booked_count=Count(
                'reservations', filter=Q(reservations__booking_status='Booked'),
            ),
        )
        .annotate(spots_remaining=F('capacity') - F('booked_count'))
        .order_by('session_date', 'start_time', 'session_id')
    )


def home(request):
    return render(request, 'pages/home.html', {'featured': session_list()[:3]})


def schedule(request):
    return render(request, 'pages/schedule.html', {'sessions': session_list()})


@staff_member_required(login_url='/accounts/login/')
def reservations(request):
    rows = (
        Reservation.objects
        .select_related('member', 'session__class_type', 'session__instructor')
        .order_by('-booking_date', '-reservation_id')
    )
    return render(request, 'pages/reservations.html', {'reservations': rows})


@staff_member_required(login_url='/accounts/login/')
@require_http_methods(['GET', 'POST'])
def book_class(request):
    form = BookClassForm(request.POST or None)
    if request.method == 'GET':
        session_id = request.GET.get('session')
        if session_id and session_id.isdecimal():
            form.fields['session'].initial = session_id
    if request.method == 'POST' and form.is_valid():
        try:
            reservation, reactivated = create_booking(**form.cleaned_data)
        except ValidationError as exc:
            form.add_error(None, exc)
        else:
            messages.success(
                request, 'Reservation reactivated.' if reactivated else 'Reservation created.'
            )
            return redirect('reservation_detail', pk=reservation.pk)
    return render(request, 'pages/book_class.html', {'form': form})


@staff_member_required(login_url='/accounts/login/')
def reservation_detail(request, pk):
    reservation = get_object_or_404(
        Reservation.objects.select_related('member', 'session__class_type',
                                           'session__instructor', 'session__room'),
        pk=pk,
    )
    return render(request, 'pages/reservation_detail.html', {'reservation': reservation})


@staff_member_required(login_url='/accounts/login/')
@require_http_methods(['GET', 'POST'])
def reservation_edit(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    form = StatusForm(request.POST or None, initial={
        'booking_status': reservation.booking_status
    })
    if request.method == 'POST' and form.is_valid():
        try:
            change_booking_status(
                reservation_id=pk, new_status=form.cleaned_data['booking_status']
            )
        except ValidationError as exc:
            form.add_error(None, exc)
        else:
            messages.success(request, 'Reservation updated.')
            return redirect('reservation_detail', pk=pk)
    return render(request, 'pages/reservation_edit.html', {
        'reservation': reservation, 'form': form,
    })


@staff_member_required(login_url='/accounts/login/')
@require_http_methods(['GET', 'POST'])
def reservation_delete(request, pk):
    reservation = get_object_or_404(
        Reservation.objects.select_related('member', 'session__class_type'), pk=pk
    )
    if request.method == 'POST':
        try:
            delete_unpaid_booking(reservation_id=pk)
        except ValidationError as exc:
            messages.error(request, exc.messages[0])
            return redirect('reservation_detail', pk=pk)
        else:
            messages.success(request, 'Unpaid reservation deleted.')
            return redirect('reservations')
    return render(request, 'pages/reservation_delete.html', {'reservation': reservation})


def about(request):
    return render(request, 'pages/about.html')
