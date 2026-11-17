"""Studio Flow's seven PostgreSQL business tables.

The tables were created by sql/schema.sql in Neon first, so these models
are unmanaged. Changing a model here does NOT update the SQL table.
"""
from django.db import models


class Member(models.Model):
    member_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    email = models.CharField(max_length=255, unique=True)
    phone = models.CharField(max_length=25, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'members'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Instructor(models.Model):
    instructor_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    email = models.CharField(max_length=255, unique=True)
    specialty = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'instructors'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class ClassType(models.Model):
    class_type_id = models.AutoField(primary_key=True)
    class_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    duration_minutes = models.IntegerField()
    difficulty_level = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'class_types'

    def __str__(self):
        return self.class_name


class Room(models.Model):
    room_id = models.AutoField(primary_key=True)
    room_name = models.CharField(max_length=80, unique=True)
    max_capacity = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'rooms'

    def __str__(self):
        return self.room_name


class ClassSession(models.Model):
    session_id = models.AutoField(primary_key=True)
    class_type = models.ForeignKey(
        ClassType, on_delete=models.PROTECT, db_column='class_type_id',
        related_name='sessions'
    )
    instructor = models.ForeignKey(
        Instructor, on_delete=models.PROTECT, db_column='instructor_id',
        related_name='sessions'
    )
    room = models.ForeignKey(
        Room, on_delete=models.PROTECT, db_column='room_id',
        related_name='sessions'
    )
    session_date = models.DateField()
    start_time = models.TimeField()
    capacity = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'class_sessions'
        unique_together = (
            ('room', 'session_date', 'start_time'),
            ('instructor', 'session_date', 'start_time'),
        )

    def __str__(self):
        return f'{self.class_type} on {self.session_date} at {self.start_time}'


class Reservation(models.Model):
    reservation_id = models.AutoField(primary_key=True)
    member = models.ForeignKey(
        Member, on_delete=models.PROTECT, db_column='member_id',
        related_name='reservations'
    )
    session = models.ForeignKey(
        ClassSession, on_delete=models.PROTECT, db_column='session_id',
        related_name='reservations'
    )
    booking_date = models.DateField()
    booking_status = models.CharField(max_length=20, default='Booked')

    class Meta:
        managed = False
        db_table = 'reservations'
        unique_together = (('member', 'session'),)

    def __str__(self):
        return f'{self.member} — {self.session} ({self.booking_status})'


class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    reservation = models.OneToOneField(
        Reservation, on_delete=models.PROTECT, db_column='reservation_id',
        related_name='payment'
    )
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    payment_date = models.DateField(blank=True, null=True)
    payment_method = models.CharField(max_length=20, blank=True, null=True)
    payment_status = models.CharField(max_length=20, default='Pending')

    class Meta:
        managed = False
        db_table = 'payments'

    def __str__(self):
        return f'Payment {self.payment_id}: {self.payment_status}'
