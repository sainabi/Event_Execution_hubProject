from django.urls import path
from.import views


urlpatterns = [
    path('',views.home,name='home'),
    path('about/',views.about,name='aboutus'),
    path('events/',views.events,name='events'),
    
    path('event/<int:event_id>/',views.event_detail,name='event_detail'),
    path('services/',views.services,name='services'),
    path('add_event/',views.add_event,name='add_event'),
    path('update_event_list/',views.update_event_list,name='update_event_list'),
    path('update_event/<int:event_id>/',views.update_event,name='update_event'),
    path('delete_event_list/',views.delete_event_list,name='delete_event_list'),
    path('delete_event/<int:event_id>/',views.delete_event,name='delete_event'),
    path('contact/',views.contact,name='contact'),
    path('feedback/',views.feedback,name='feedback'),
    path('profile/',views.profile,name='profile'),
    path('booking/',views.booking,name='booking'),
    path('payment/<int:event_id>/',views.payment,name='payment'),
    path('payment/success',views.success,name='success'),
    path('booking_details/',views.booking_details,name='booking_details'),
    path('booking_update/<int:booking_id>/',views.booking_update,name='booking_update'),
    path('booking_delete<int:booking_id>/',views.booking_delete,name='booking_delete'),

   

   
    
    
    ]
    



