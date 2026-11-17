"""Forms used by studio staff to create and update reservations."""
from django import forms
from operations.models import Member, ClassSession, Reservation


class BookClassForm(forms.Form):
    member = forms.ModelChoiceField(
        queryset=Member.objects.order_by('last_name', 'first_name'),
        empty_label='Choose a member',
    )
    session = forms.ModelChoiceField(
        queryset=ClassSession.objects.select_related('class_type', 'instructor')
        .order_by('session_date', 'start_time'),
        empty_label='Choose a class session',
    )

    create_pending_payment = forms.BooleanField(
        label='Also create a Pending payment record (no real charge)',
        required=False,
        initial=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = (
                'form-check-input' if name == 'create_pending_payment' else 'form-select'
            )


class StatusForm(forms.Form):
    booking_status = forms.ChoiceField(choices=[
        ('Booked', 'Booked'),
        ('Cancelled', 'Cancelled'),
        ('Attended', 'Attended'),
    ])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['booking_status'].widget.attrs['class'] = 'form-select'
