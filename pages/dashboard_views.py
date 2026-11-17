"""Studio Flow staff dashboard.

All figures are read directly from the seven existing Neon business tables.
The class popularity and payment breakdown queries use SQL GROUP BY via
.values(...).annotate(...), matching the course dashboard requirement.
Nothing on this page writes to or changes the database.
"""
from decimal import Decimal

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, F, Q, Sum
from django.shortcuts import render
from django.utils import timezone

from operations.models import ClassSession, ClassType, Member, Payment, Reservation


@staff_member_required(login_url='/accounts/login/')
def dashboard(request):
    today = timezone.localdate()

    reservation_totals = Reservation.objects.aggregate(
        total=Count('reservation_id'),
        booked=Count('reservation_id', filter=Q(booking_status='Booked')),
        attended=Count('reservation_id', filter=Q(booking_status='Attended')),
        cancelled=Count('reservation_id', filter=Q(booking_status='Cancelled')),
    )

    # GROUP BY class name / difficulty, joining the class type, session,
    # and reservation tables. Cancelled reservations do not count as
    # a successful booking; attended and currently booked ones do.
    popular_classes = (
        ClassType.objects
        .values('class_name', 'difficulty_level')
        .annotate(
            current_bookings=Count(
                'sessions__reservations',
                filter=Q(sessions__reservations__booking_status='Booked'),
            ),
            attended=Count(
                'sessions__reservations',
                filter=Q(sessions__reservations__booking_status='Attended'),
            ),
            total_noncancelled=Count(
                'sessions__reservations',
                filter=Q(sessions__reservations__booking_status__in=['Booked', 'Attended']),
            ),
        )
        .order_by('-total_noncancelled', 'class_name')
    )

    # GROUP BY payment_status, showing how many records and how much value
    # is recorded in each status. These are sample records, not transactions
    # handled by a payment processor.
    payment_groups = (
        Payment.objects
        .values('payment_status')
        .annotate(payment_count=Count('payment_id'), amount_total=Sum('amount'))
        .order_by('payment_status')
    )
    by_status = {row['payment_status']: row for row in payment_groups}
    payment_breakdown = []
    for status in ('Pending', 'Paid', 'Refunded'):
        record = by_status.get(status, {})
        payment_breakdown.append({
            'status': status,
            'count': record.get('payment_count', 0),
            'amount': record.get('amount_total') or Decimal('0.00'),
        })
    paid_total = next(p['amount'] for p in payment_breakdown if p['status'] == 'Paid')

    # Count available places from capacity - live Booked reservations;
    # the schema intentionally does not store a duplicate spots value.
    upcoming = list(
        ClassSession.objects
        .filter(session_date__gte=today)
        .select_related('class_type', 'instructor', 'room')
        .annotate(
            booked_count=Count(
                'reservations', filter=Q(reservations__booking_status='Booked')
            ),
            spots_remaining=F('capacity') - F('booked_count'),
        )
        .order_by('session_date', 'start_time', 'session_id')[:5]
    )

    return render(request, 'pages/dashboard.html', {
        'today': today,
        'members_count': Member.objects.count(),
        'upcoming_sessions_count': ClassSession.objects.filter(session_date__gte=today).count(),
        'reservation_totals': reservation_totals,
        'paid_total': paid_total,
        'popular_classes': popular_classes,
        'payment_breakdown': payment_breakdown,
        'upcoming': upcoming,
    })
