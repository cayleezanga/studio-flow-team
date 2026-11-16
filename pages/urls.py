from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('schedule/', views.schedule, name='schedule'),
    path('reservations/', views.reservations, name='reservations'),
    path('about/', views.about, name='about'),
]
