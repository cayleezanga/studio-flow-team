"""Small Django forms for staff-only manual payment recordkeeping."""
from django import forms
from operations.models import Reservation

METHODS = [('', 'Select a method'), ('Card', 'Card (record only)'),
           ('Cash', 'Cash'), ('Other', 'Other')]


class NewPaymentForm(forms.Form):
    reservation = forms.ModelChoiceField(
        queryset=Reservation.objects.none(), empty_label='Choose a reservation',
    )
    payment_status = forms.ChoiceField(
        choices=[('Pending', 'Pending'), ('Paid', 'Paid')], initial='Pending',
    )
    payment_method = forms.ChoiceField(choices=METHODS, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # No second payment per reservation; exclude cancelled bookings.
        self.fields['reservation'].queryset = (
            Reservation.objects.select_related('member', 'session__class_type')
            .filter(payment__isnull=True)
            .exclude(booking_status='Cancelled')
            .order_by('-reservation_id')
        )
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-select'

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('payment_status') == 'Paid' and not cleaned.get('payment_method'):
            self.add_error('payment_method', 'Choose a method for a Paid payment.')
        return cleaned


class UpdatePaymentForm(forms.Form):
    payment_status = forms.ChoiceField(choices=[
        ('Pending', 'Pending'), ('Paid', 'Paid'), ('Refunded', 'Refunded'),
    ])
    payment_method = forms.ChoiceField(choices=METHODS, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-select'

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('payment_status') == 'Paid' and not cleaned.get('payment_method'):
            self.add_error('payment_method', 'Choose a method for a Paid payment.')
        return cleaned
