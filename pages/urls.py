from django.urls import path
from . import views, payment_views

urlpatterns = [
    path('', views.home, name='home'),
    path('schedule/', views.schedule, name='schedule'),
    path('reservations/', views.reservations, name='reservations'),
    path('reservations/new/', views.book_class, name='book_class'),
    path('reservations/<int:pk>/', views.reservation_detail, name='reservation_detail'),
    path('reservations/<int:pk>/edit/', views.reservation_edit, name='reservation_edit'),
    path('reservations/<int:pk>/delete/', views.reservation_delete, name='reservation_delete'),
    path('payments/', payment_views.payments, name='payments'),
    path('payments/new/', payment_views.payment_new, name='payment_new'),
    path('payments/<int:pk>/', payment_views.payment_detail, name='payment_detail'),
    path('payments/<int:pk>/edit/', payment_views.payment_edit, name='payment_edit'),
    path('about/', views.about, name='about'),
]
