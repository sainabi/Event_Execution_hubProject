from django import forms
from .models import UserProfile,Booking,Feedback
from .models import Event

class EventForm(forms.ModelForm):

    class Meta:
        model=Event
        fields=['event','description','image','price']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model=UserProfile
        fields='__all__'
       
        
    

class BookingForm(forms.ModelForm):
    VENUE_CHOICES=[
        ('beachside','Beachside'),
        ('riverside','Riverside'),
        ('garden','Garden'),
        ('banquet_hall','Banquet Hall'),
        ('park', 'Park'),
        ('hotel', 'Hotel'),
        ('island', 'Island'),
        ('resort', 'Resort'),
        ('countryside', 'Countryside'),

    ]

    venue=forms.ChoiceField(choices=VENUE_CHOICES,widget=forms.Select(attrs={'class':'form-control'}))
    


    class Meta:
        model=Booking
        fields=['user','userprofile','event','booking_for_date','setup_time','location','number_of_members','location','suggestion','venue']
        widgets = {
            'booking_for_date': forms.DateInput(attrs={'type': 'date'})
        }
        labels={
            'suggestion':'Suggestions (Any additional decoration needed or special requests for decor)'
        }

    def clean(self):
        cleaned_data=super().clean()
        event=cleaned_data.get("event")
        booking_for_date=cleaned_data.get("booking_for_date")
        user=cleaned_data.get("user")
        if event and booking_for_date:
            existing_booking=Booking.objects.filter(event=event,booking_for_date=booking_for_date).exclude(user=user).first()
            if existing_booking:
                raise forms.ValidationError(f"A booking already exists for {event} on {booking_for_date}.Could You Please Reschedule it. ")
        return cleaned_data
       

class ContactForm(forms.Form):
    name=forms.CharField(max_length=100)
    email=forms.EmailField()
    phone_number=forms.CharField(max_length=15)
    event=forms.ModelChoiceField(queryset=Event.objects.all())
    rating=forms.IntegerField(label='Rating (1-5)',min_value=1,max_value=5)
    feedback=forms.CharField(widget=forms.Textarea)
      
    def save(self,user):
        name=self.cleaned_data['name']
        email=self.cleaned_data['email']
        phone_number=self.cleaned_data['phone_number']
        event=self.cleaned_data['event']
        rating=self.cleaned_data['rating']
        feedback_text=self.cleaned_data['feedback']

        feedback,_ =Feedback.objects.update_or_create(
            user=user,
            event=event,
            defaults={
           
            'rating':rating,
            'feedback_text':feedback_text
            
            }

            
        )
        return feedback





    
 