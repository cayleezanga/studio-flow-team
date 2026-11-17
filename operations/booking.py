"""Business rules for Studio Flow bookings.

Payment records are bookkeeping only, not real charges. An optional booking
checkbox creates a reservation and pending payment together in ONE transaction.

Keep capacity checks in this module instead of only in HTML/form validation:
a browser form can be bypassed and two staff members can book simultaneously.
"""
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import ClassSession, Payment, Reservation


@transaction.atomic
def create_booking(*, member, session, create_pending_payment=False):
    """Book member into session, safely reactivating a cancelled booking.

    A PostgreSQL row lock on the session serializes concurrent bookings for
    that session. Session availability is calculated; it is not stored.
    """
    session = ClassSession.objects.select_related('class_type').select_for_update().get(pk=session.pk)

    previous = (
        Reservation.objects.select_for_update()
        .filter(member=member, session=session).first()
    )
    if previous and previous.booking_status != 'Cancelled':
        raise ValidationError('This member already has a reservation for this class.')

    taken = Reservation.objects.filter(
        session=session, booking_status='Booked'
    ).count()
    if taken >= session.capacity:
        raise ValidationError('This class is full. Please choose another session.')

    if previous and create_pending_payment and Payment.objects.filter(reservation=previous).exists():
        raise ValidationError('This reservation already has a payment record. Uncheck the payment option.')

    if previous:
        previous.booking_status = 'Booked'
        previous.booking_date = timezone.localdate()
        previous.save(update_fields=['booking_status', 'booking_date'])
        reservation, reactivated = previous, True
    else:
        reservation = Reservation.objects.create(
            member=member,
            session=session,
            booking_date=timezone.localdate(),
            booking_status='Booked',
        )
        reactivated = False

    # A single transaction now writes TWO related business rows, or rolls both
    # back on any error. This is the course's multi-change transaction demo.
    if create_pending_payment:
        Payment.objects.create(
            reservation=reservation,
            amount=session.class_type.price,
            payment_status='Pending',
            payment_method=None,
            payment_date=None,
        )

    return reservation, reactivated


@transaction.atomic
def change_booking_status(*, reservation_id, new_status):
    """Update status; re-booking must respect class capacity."""
    if new_status not in {'Booked', 'Cancelled', 'Attended'}:
        raise ValidationError('Please choose a valid reservation status.')

    # Consistent lock order with create_booking: session, then reservation.
    original = Reservation.objects.only('session_id').get(pk=reservation_id)
    session = ClassSession.objects.select_for_update().get(pk=original.session_id)
    reservation = Reservation.objects.select_for_update().get(pk=reservation_id)

    if reservation.booking_status == new_status:
        return reservation
    if new_status == 'Booked':
        taken = Reservation.objects.filter(
            session=session, booking_status='Booked'
        ).exclude(pk=reservation.pk).count()
        if taken >= session.capacity:
            raise ValidationError('This class is full, so the reservation cannot be rebooked.')
    reservation.booking_status = new_status
    reservation.save(update_fields=['booking_status'])
    return reservation


@transaction.atomic
def delete_unpaid_booking(*, reservation_id):
    """Delete only reservations with no payment row; protect payment history."""
    original = Reservation.objects.only('session_id').get(pk=reservation_id)
    ClassSession.objects.select_for_update().get(pk=original.session_id)
    reservation = Reservation.objects.select_for_update().get(pk=reservation_id)
    if Payment.objects.filter(reservation=reservation).exists():
        raise ValidationError(
            'This reservation has a payment record. Cancel it instead of deleting it.'
        )
    reservation.delete()
