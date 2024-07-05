from django.urls import path
from .import views


urlpatterns = [
    


path('',views.signup,name='signup'),
path('login',views.user_login,name='login'),
path('logout',views.user_logout,name='logout'),
path('reset',views.Resethome,name='reset'),
path('passwordreset',views.resetpassword),

]