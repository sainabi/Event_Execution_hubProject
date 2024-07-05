from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from django.contrib import messages
from django.contrib.auth.models import User,Group




def signup(request):
    if request.method=="POST":
        username=request.POST['username']
        email=request.POST['email']
        password=request.POST['password1']
        RepeatPassword=request.POST['password2']
   
        if User.objects.filter(email=email).exists():
            messages.info(request,"Email already exists")
            return redirect('signup')
        elif User.objects.filter(username=username).exists():
            messages.info(request,"Username already exists")
            return redirect('signup')
        elif password!=RepeatPassword:
            messages.error(request,"Password do not match")
            return redirect('signup')
         
    
        else:
            try:
                validate_password(password)
                user=User.objects.create_user(username=username,email=email,password=password)
                user.save()
                return redirect('login')
            except ValidationError as e:
                for error in e:
                    messages.error(request,error)
                return redirect('signup')

          
    else:
        return render(request,'signup.html')
        

    
def user_login(request):
    if request.method=="POST":
        uname=request.POST.get('username')
        pwd=request.POST.get('password')
        user=authenticate(request,username=uname,password=pwd)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            return render(request,"login.html",{'msg':'Invalid login'})
    
    else:
        return render(request,'login.html')


def user_logout(request):
    logout(request)
    return redirect('home')
  


def Resethome(request):
    return render(request,'resetpassword.html')

def resetpassword(request):
    if request.method=='POST':
        uname=request.POST['uname']
        newpwd=request.POST['password']
        try:
            user=User.objects.get(username=uname)
            validate_password(newpwd,user)
            user.password=make_password(newpwd)
            user.save()
            return render(request,'resetpassword.html',{"msg":"Password reset successfully"})
        except User.DoesNotExist:
            return render(request,'resetpassword.html',{'msg':'Username does not exist'})
        except ValidationError as e:
            for error in e:
                messages.error(request,error)
            return render(request,'resetpassword.html')
    return render(request,'resetpassword.html')    