from django.db import models

class Book(models.Model):
    BookID = models.AutoField(primary_key=True)
    BookName = models.CharField(max_length=256, db_index=True)
    NumberOfCopies = models.PositiveIntegerField(default=0)

    class Meta:
        db_table='books'
        verbose_name = 'Books'
        verbose_name_plural = 'Books'

class Member(models.Model):
    MemberID = models.AutoField(primary_key=True)
    MemberName = models.CharField(max_length=256)
    
    class Meta:
        db_table='members'
        verbose_name = 'Members'
        verbose_name_plural = 'Members'

class Circulation(models.Model):
    event_type_choices = [
        (1, 'Checkout'),
        (2, 'Return')
    ]
    book = models.ForeignKey(Book, on_delete=models.CASCADE, db_index=True)
    event_type = models.SmallIntegerField(choices=event_type_choices)
    time_stamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table='circulation'
        verbose_name = 'Circulation'
        verbose_name_plural = 'Circulations'

class Reservation(models.Model):
    reservation_choices = [
        ('PENDING', 'Pending'),
        ('FULFILLED', 'Fulfilled'),
        ('CANCELLED', 'Cancelled'),
    ]
    book = models.ForeignKey(Book, on_delete=models.CASCADE, db_index=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, db_index=True)
    status = models.CharField(max_length=10, choices=reservation_choices, default='PENDING', db_index=True)
    time_stamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table='reservation'
        verbose_name = 'Reservation'
        verbose_name_plural = 'Reservations'