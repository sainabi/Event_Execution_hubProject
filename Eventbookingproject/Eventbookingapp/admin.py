from django.contrib import admin
from .models import*



class UserProfileAdmin(admin.ModelAdmin):
    search_fields=['first_name']

class BookingInline(admin.TabularInline):
    model=Booking
    fields=('user',)
    extra=0
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    
    search_fields=('event',)
    list_filter=('price',)
    inlines=[BookingInline]
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display=('user','event','booking_date','booking_for_date')

    

admin.site.register(UserProfile,UserProfileAdmin)

admin.site.register(Advance)
admin.site.register(Feedback)
