from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login, logout 
from .forms import LoginForm, SignupForm
from django.contrib.auth.models import User
from .models import WorkoutClass

def home(request):
     return render(request, 'index.html')

def signup(request):
    if request.method == "POST":
        signup_form = SignupForm(request.POST)
        if signup_form.is_valid():
            if User.objects.filter(username = signup_form.cleaned_data.get("username")).first():
                return render(request, 'signup.html')
            

            user = User.objects.create_user(signup_form.cleaned_data.get("username"), password=signup_form.cleaned_data.get("password"))

            authenticated_user = authenticate(request, username=signup_form.cleaned_data.get("username"), password=signup_form.cleaned_data.get("password"))
            if authenticated_user is not None:
                login(request, authenticated_user)

            return HttpResponseRedirect("/")
        else:
            print(signup_form.errors)

    return render(request, 'signup.html')

def signout_view(request):
    logout(request)
    return HttpResponseRedirect("/") 

def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("/")
    
    if request.method == "POST":
        login_form = LoginForm(request.POST)
        print("testing")
        if login_form.is_valid():
            print("valid")
            print(login_form.cleaned_data.get("username"))
            print(login_form.cleaned_data.get("password"))
            authenticated_user = authenticate(request, username=login_form.cleaned_data.get("username"), password=login_form.cleaned_data.get("password"))
            print(authenticated_user)
            if authenticated_user is not None:
                login(request=request, user=authenticated_user)
                print("logged in")
            return HttpResponseRedirect("/")


    return render(request, 'login.html')

def workout_list(request):
    workouts = WorkoutClass.objects.all()
    return render(request, 'workoutclass.html', {'workouts': workouts})

def workout_detail(request, id):
    workout = get_object_or_404(WorkoutClass, id=id)
    return render(request, "workouts/detail.html",{"workout":workout})