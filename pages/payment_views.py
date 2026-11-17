"""Staff-only payment management; all amounts and statuses live in Neon."""
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from operations.models import Payment
from operations.payments import change_payment_status, record_payment
from .payment_forms import NewPaymentForm, UpdatePaymentForm


def payment_query():
    return Payment.objects.select_related(
        'reservation__member', 'reservation__session__class_type'
    )


@staff_member_required(login_url='/accounts/login/')
def payments(request):
    return render(request, 'pages/payments.html', {
        'payments': payment_query().order_by('-payment_id')
    })


@staff_member_required(login_url='/accounts/login/')
@require_http_methods(['GET', 'POST'])
def payment_new(request):
    form = NewPaymentForm(request.POST or None)
    if request.method == 'GET':
        reservation_id = request.GET.get('reservation')
        if reservation_id and reservation_id.isdecimal():
            form.fields['reservation'].initial = reservation_id
    if request.method == 'POST' and form.is_valid():
        try:
            payment = record_payment(**form.cleaned_data)
        except ValidationError as exc:
            form.add_error(None, exc)
        except IntegrityError:
            form.add_error(None, 'This reservation already has a payment. Refresh and try again.')
        else:
            messages.success(request, 'Payment record created (no money was charged).')
            return redirect('payment_detail', pk=payment.pk)
    return render(request, 'pages/payment_form.html', {'form': form})


@staff_member_required(login_url='/accounts/login/')
def payment_detail(request, pk):
    payment = get_object_or_404(payment_query(), pk=pk)
    return render(request, 'pages/payment_detail.html', {'payment': payment})


@staff_member_required(login_url='/accounts/login/')
@require_http_methods(['GET', 'POST'])
def payment_edit(request, pk):
    payment = get_object_or_404(payment_query(), pk=pk)
    form = UpdatePaymentForm(request.POST or None, initial={
        'payment_status': payment.payment_status,
        'payment_method': payment.payment_method or '',
    })
    if request.method == 'POST' and form.is_valid():
        try:
            change_payment_status(
                payment_id=pk,
                new_status=form.cleaned_data['payment_status'],
                payment_method=form.cleaned_data['payment_method'],
            )
        except ValidationError as exc:
            form.add_error(None, exc)
        else:
            messages.success(request, 'Payment record updated (no real transfer).')
            return redirect('payment_detail', pk=pk)
    return render(request, 'pages/payment_edit.html', {
        'payment': payment, 'form': form,
    })
