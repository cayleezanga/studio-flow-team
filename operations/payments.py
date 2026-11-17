"""Recordkeeping only: no real charges, card numbers, or processor API.

A single payment is associated with a reservation. The price is saved at the
moment the payment record is made so later edits to the class price do not
rewrite the historical payment amount.
"""
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import Payment, Reservation


@transaction.atomic
def record_payment(*, reservation, payment_status, payment_method=None):
    """Create a payment record for a confirmed or attended reservation."""
    if payment_status not in ('Pending', 'Paid'):
        raise ValidationError('Choose Pending or Paid for a new payment.')
    if payment_status == 'Paid' and payment_method not in ('Card', 'Cash', 'Other'):
        raise ValidationError('Choose a payment method when marking a payment Paid.')

    current = (
        Reservation.objects.select_for_update()
        .select_related('session__class_type')
        .get(pk=reservation.pk)
    )
    if current.booking_status == 'Cancelled':
        raise ValidationError('Cannot record a new payment for a cancelled reservation.')
    if Payment.objects.filter(reservation=current).exists():
        raise ValidationError('This reservation already has a payment record.')

    return Payment.objects.create(
        reservation=current,
        amount=current.session.class_type.price,
        payment_status=payment_status,
        payment_method=payment_method if payment_status == 'Paid' else None,
        payment_date=timezone.localdate() if payment_status == 'Paid' else None,
    )


@transaction.atomic
def change_payment_status(*, payment_id, new_status, payment_method=None):
    """A pending payment can be marked paid; a paid payment can be refunded.

    Historical payment records are never deleted or replaced by real charges.
    A Refund is a status marker for the demo, not a transfer of money.
    """
    payment = Payment.objects.select_for_update().get(pk=payment_id)
    allowed = {
        'Pending': {'Pending', 'Paid'},
        'Paid': {'Paid', 'Refunded'},
        'Refunded': {'Refunded'},
    }
    if new_status not in allowed.get(payment.payment_status, set()):
        raise ValidationError(
            f'Cannot change a {payment.payment_status} payment to {new_status}. '
            'Allowed steps: Pending → Paid → Refunded.'
        )
    if new_status == 'Paid':
        # New Paid entries must be supplied with a method; when already
        # Paid, the existing method is used unless staff corrects it.
        method = payment_method or payment.payment_method
        if method not in ('Card', 'Cash', 'Other'):
            raise ValidationError('Select Card, Cash, or Other before marking Paid.')
        payment.payment_method = method
        if payment.payment_status == 'Pending':
            payment.payment_date = timezone.localdate()
    payment.payment_status = new_status
    payment.save(update_fields=['payment_status', 'payment_method', 'payment_date'])
    return payment
