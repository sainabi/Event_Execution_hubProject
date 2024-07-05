from django.db import models
from django.contrib.auth.models import User
import datetime


class Event(models.Model):
   
    event=models.CharField(max_length=100,default="New event")
    description=models.TextField()
    image=models.ImageField(upload_to='images',default=None)
    price=models.DecimalField(max_digits=10,decimal_places=2)

    class Meta:
        verbose_name_plural= 'Events'
    def __str__(self):
        return self.event
    
class UserProfile(models.Model):

    first_name=models.CharField(max_length=20,verbose_name="First Name")
    last_name=models.CharField(max_length=20,verbose_name="Last Name",blank=True)
    address=models.TextField(max_length=20)
    phno=models.BigIntegerField(default=0,verbose_name="Phone Number")
    email=models.EmailField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class Booking(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    userprofile=models.ForeignKey(UserProfile,on_delete=models.CASCADE,related_name='bookings')
    event=models.ForeignKey(Event,on_delete=models.CASCADE)
    booking_date=models.DateTimeField(auto_now=True)
    booking_for_date=models.DateField()
    setup_time=models.TimeField(default=datetime.time(9,0))
    suggestion=models.TextField(default='')
    number_of_members=models.PositiveIntegerField(default=1)
    location=models.CharField(max_length=100)
    venue=models.CharField(max_length=100)

    
    def __str__(self):
        return f"{self.event} booked by {self.user} for {self.booking_for_date}"
class Advance(models.Model):
    booking=models.ForeignKey(Booking,on_delete=models.CASCADE)
    name=models.CharField(max_length=100,default='please provide your name')
    amount=models.CharField(max_length=100,default='')
    email=models.CharField(max_length=100)
    payment_id=models.CharField(max_length=100)
    paid=models.BooleanField(default=False)
    
    
    def __str__(self):
        return f"Advance {self.amount} paid by {self.name}"


class Feedback(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    event=models.ForeignKey(Event,on_delete=models.CASCADE)
    rating=models.IntegerField(choices=[(i, i)for i in range(1,6)])
    feedback_text=models.TextField()

    class Meta:
        unique_together = ('user','event')
    def __str__(self):
        return f"{self.user.username} - {self.event.event} -Rating:{self.rating}"
       
      

