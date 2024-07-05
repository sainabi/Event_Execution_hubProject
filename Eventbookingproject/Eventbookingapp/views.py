from django.shortcuts import render,redirect
from .models import Event,UserProfile,Booking
from .forms import UserProfileForm
from.forms import BookingForm
from.forms import ContactForm,EventForm
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.db import transaction
from django.core.exceptions import ValidationError
from.models import Advance
import json
import razorpay
from django.conf import settings
from django.shortcuts import get_object_or_404,reverse
from razorpay.errors import BadRequestError, GatewayError
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import JsonResponse
from django.db import IntegrityError
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.html import strip_tags
from decimal import Decimal
from django.core.paginator import Paginator





def home(request):
    user_groups=request.user.groups.values_list('name',flat=True)
    
    if 'Admin' in user_groups:
        return redirect('/admin/')
    
    is_organiser='Organisers' in user_groups
    context={'is_organiser':is_organiser}
    return render(request,'home.html',context)

def is_organiser(user):
    return user.groups.filter(name='Organisers').exists()



def about(request):
    return render(request,'about.html')


def events(request):
    events=Event.objects.all()
    search_query=request.GET.get('search_query')
    price_filter=request.GET.get('price_filter')
    
    if search_query:
        events=events.filter(event__icontains=search_query)

    if price_filter:
       if price_filter =='lt_20000':
           events=events.filter(price__lt=20000)
       elif price_filter =='20000_40000':
           events=events.filter(price__range=(20000, 40000))
       elif price_filter=='gt_60000':
           events=events.filter(price__gt=60000)
    
   
    
    paginator= Paginator(events,9)
    page_number=request.GET.get('page',1)
    page_obj=paginator.get_page(page_number)

    
    if request.headers.get('X-requested-with')=='XMLHttpRequest':
        events_html=render_to_string('events_list.html',{'page_obj':page_obj})
        return JsonResponse({'events_html':events_html,'has_next':page_obj.has_next()})
    
    context={'page_obj':page_obj,'events':Event.objects.all(),'search_query':search_query,'price_filter':price_filter}
    return render(request,'events.html',context)




def event_detail(request,event_id):
    event=get_object_or_404(Event,pk=event_id)
    return render(request,'eventdetails.html',{'event':event})

def services(request):
    return render(request,'services.html')

@login_required
def add_event(request):
    success_message=None
    if not is_organiser(request.user):
        return redirect('home')
    if request.method=='POST':
        form=EventForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()

            print("Form is valid and event has been saved.")
            success_message="Event added succesfully"
            form=EventForm()
        else:
            print("Form is invalid:",form.errors)
        
           
    else:
        form=EventForm()
    return render(request,'add_event.html',{'form':form,'success_message':success_message})


@login_required
def update_event_list(request):
    if not is_organiser(request.user):
        return redirect('home')
    events=Event.objects.all()
    return render(request,'update_event_list.html',{'events':events})


@login_required
def update_event(request,event_id):
    success_message=None
    if not is_organiser(request.user):
        return redirect('home')
    event=get_object_or_404(Event,id=event_id)
    if request.method=='POST':
        form=EventForm(request.POST,request.FILES,instance=event)
        if form.is_valid():
            form.save()
            success_message="Event Updated successfully"
            form=EventForm()
            
        else:
            print("Form is invalid",form.errors)
    else:
        form=EventForm(instance=event)
    return render(request,'update_event.html',{'form':form,'event':event,'success_message':success_message})


@login_required
def delete_event_list(request):
    if not is_organiser(request.user):
        return redirect('home')
    events=Event.objects.all()
    return render(request,'delete_event_list.html',{'events':events})

@login_required
def delete_event(request,event_id):
    success_message=None
    if not is_organiser(request.user):
        return redirect('home')
    event=get_object_or_404(Event,id=event_id)
    if request.method=='POST':
        event.delete()
        success_message="Event deleted successfully"
        return redirect('events')
    return render(request,'delete_event.html',{'event':event,'success_message':success_message})




@login_required
def contact(request):
    if request.method=="POST":
        form=ContactForm(request.POST)
        if form.is_valid():
            try:
                form.save(request.user)
                return redirect('feedback')
            except IntegrityError as e:
                if 'UNIQUE constraint' in str(e):
                    form.add_error(None,'Feedback for this user already exists.')
                else:
                    form.add_error(None,'An unexpected error occured.')
        else:
            print("Form is Invalid",form.errors)
    else:
        form=ContactForm()
    return render(request,'contact.html',{'form':form})

def feedback(request):
    print("Feedback page accessed")
    return render(request,'feedback.html')



@login_required
def profile(request):
    if request.method=="POST":
        form=UserProfileForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('booking')
    else:
        form=UserProfileForm()
    return render(request,'profile.html',{'form':form})

 
      
       
@login_required
def booking(request):
    event=None
   
    if request.method=="POST":
        form=BookingForm(request.POST)
        if form.is_valid():
            form.instance.user=request.user
            
            form.save()
            event_id=form.cleaned_data.get("event").id
            return redirect('payment',event_id=event_id)
       
    else:  
        event_id=request.GET.get('event_id')
        
        if event_id:
            event=Event.objects.filter(id=event_id).first()
         
                
        form=BookingForm(initial={'event':event,'user':request.user})
    return render(request,'booking.html',{'form':form,'event':event})






@login_required
def payment(request,event_id):

    event=get_object_or_404(Event,pk=event_id)
    total_amount=float(event.price)
    gst_amount=total_amount*0.05
    total_sum=total_amount+gst_amount

    if request.method=="POST":
        
        name=request.POST.get("name")
        amount=request.POST.get("amount")
        email=request.POST.get("email")

        if not amount:
            return render(request,'payment.html',{'error':"Amount is required"})
        
        try:
            amount=int(amount) * 100
        except ValueError:
            return render(request,'payment.html',{'error':"Invalid amount value"})
        
        client=razorpay.Client(auth=(settings.RAZORPAY_API_KEY,settings.RAZORPAY_API_SECRET))

        DATA={
            "amount":amount,
            "currency":"INR",
            "receipt":"receipt#1",
            "notes":{
                "name":name
            }
        }

        try:
            payment=client.order.create(data=DATA)
        except razorpay.errors.BadRequestError as e:
            return render(request,'payment.html',{'error':f'BadRequestError: {str(e)}'})
        except razorpay.errors.GatewayError as e:
            return render(request,'payment.html',{'error':f'GatewayError:{str(e)}'})
        except Exception as e:
            return render(request,'payment.html',{'error':f'Error:{str(e)}',})
        booking = Booking.objects.filter(event=event, user=request.user).first()

        if booking:
            advance = Advance.objects.create(
                booking=booking,
                name=name,
                amount=amount,
                email=email,
                payment_id=payment['id']
                )
        
    
        context={
            'payment':payment,
            'name':name,
            'amount':amount //100,
            'total_amount':total_amount,
            'gst_amount':gst_amount,
            'total_sum':total_sum,
            'user':request.user
        }
        return render(request,'payment.html',context)
    return render(request, 'payment.html', {'total_amount':total_amount,'gst_amount':gst_amount,'total_sum':total_sum,})

    


@csrf_exempt
def success(request):
    if request.method=="POST":
        a=request.POST
        payment_id=""
        data={}
        for key,val in a.items():
            if key=="razorpay_order_id":
                data['razorpay_order_id']=val
                payment_id=val
            elif key=='razorpay_payment_id':
                data['razorpay_payment_id']=val
            elif key=='razorpay_signature':
                data['razorpay_signature']=val
        
        user_advance=Advance.objects.filter(payment_id=payment_id).first()

        if user_advance:
            client=razorpay.Client(auth=(settings.RAZORPAY_API_KEY,settings.RAZORPAY_API_SECRET))
            check=client.utility.verify_payment_signature(data)
            if not check:
                return render(request,'error.html')
           
            user_advance.paid=True
            user_advance.save()
            
            booking=user_advance.booking
            user=booking.user
            event=booking.event
            event_price=event.price
            
            gst=event_price * Decimal('0.05')
            total_amount=event_price+gst
            advance_paid=Decimal(user_advance.amount)
            balance_amount=total_amount-advance_paid

            event_price = format(event_price, '.2f')
            gst = format(gst, '.2f')
            total_amount = format(total_amount, '.2f')
            advance_paid = format(advance_paid, '.2f')
            balance_amount = format(balance_amount, '.2f')

           
            context={
                'user':user,
                'event':event,
                'event_price':event_price,
                'gst':gst,
                'amount':advance_paid,
                'total_amount':total_amount,
                'balance_amount':balance_amount,
               
                'booking':booking
            }
         
            msg_plain=render_to_string('email.txt',context)
            msg_html=render_to_string('email.html',context)
            send_mail("your payment has been received",msg_plain,settings.EMAIL_HOST_USER,[user_advance.email],html_message=msg_html)
           
        
        
        else:
           return render(request,'error.html')
        return render(request,'success.html',{'payment_data':a})  


@login_required
def booking_details(request):
    bookings=Booking.objects.select_related('event').all()
    return render(request,'bookingdetails.html',{'bookings':bookings})
   

        

def booking_update(request,booking_id):
    booking=get_object_or_404(Booking,pk=booking_id)
    form=BookingForm(instance=booking)
    if request.method=='POST':
        form=BookingForm(request.POST,instance=booking)
        if form.is_valid():
            form.save()
            return redirect('booking_details')
    return render(request,'booking_update.html',{'form':form})


def booking_delete(request,booking_id):
    booking=get_object_or_404(Booking,pk=booking_id)
    if request.method=='POST':
        booking.delete()
        return redirect('booking_details')
    return render(request,'booking_delete.html',{'booking':booking})

            
 