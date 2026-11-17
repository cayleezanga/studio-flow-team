"""Small login redirect customization for the staff demonstration."""
from django.contrib.auth.views import LoginView
from django.urls import reverse


class StaffLoginView(LoginView):
    template_name = 'registration/login.html'

    def get_default_redirect_url(self):
        return reverse('reservations')
