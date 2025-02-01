# views.py
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from .forms import LoginForm, SignupForm
from .models import WorkoutClass, Membership

def home(request):
    return render(request, 'index.html')

def signup(request):
    if request.method == "POST":
        signup_form = SignupForm(request.POST)
        if signup_form.is_valid():
            if User.objects.filter(username=signup_form.cleaned_data.get("username")).first():
                return render(request, 'signup.html')
            user = User.objects.create_user(
                signup_form.cleaned_data.get("username"),
                password=signup_form.cleaned_data.get("password")
            )
            # Assign user to the "basic" group
            basic_group = Group.objects.get(name='basic')
            user.groups.add(basic_group)

            authenticated_user = authenticate(
                request, 
                username=signup_form.cleaned_data.get("username"), 
                password=signup_form.cleaned_data.get("password")
            )
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
        if login_form.is_valid():
            authenticated_user = authenticate(
                request, 
                username=login_form.cleaned_data.get("username"), 
                password=login_form.cleaned_data.get("password")
            )
            if authenticated_user is not None:
                login(request=request, user=authenticated_user)
            return HttpResponseRedirect("/")
    return render(request, 'login.html')

def workout_list(request):
    workouts = WorkoutClass.objects.all()
    is_member = request.user.is_authenticated and request.user.groups.filter(name='Members').exists()  # Check membership
    return render(request, 'workoutclass.html', {'workouts': workouts, 'is_member': is_member})

def workout_detail(request, id):
    workout = get_object_or_404(WorkoutClass, id=id)
    return render(request, "workoutclassindividual.html", {"workout": workout})

@login_required
def membership_options(request):
    user = request.user
    # Get or create a default Free membership for the user
    membership, created = Membership.objects.get_or_create(
        user=user, 
        defaults={'membership_type': 'free', 'price': 0.00}
    )
    message = ""
    if request.method == "POST":
        if 'upgrade' in request.POST:
            new_type = request.POST.get("membership_type")
            if new_type not in ['free', 'student', 'premium']:
                message = "Invalid membership type selected."
            else:
                if membership.membership_type == new_type:
                    message = "You already have this membership."
                else:
                    membership.membership_type = new_type
                    if new_type == 'free':
                        membership.price = 0.00
                    elif new_type == 'student':
                        membership.price = 5.99
                    elif new_type == 'premium':
                        membership.price = 19.99
                    membership.save()
                    message = f"Membership upgraded to {new_type.capitalize()}."
        elif 'cancel' in request.POST:
            if membership.membership_type != 'free':
                membership.membership_type = 'free'
                membership.price = 0.00
                membership.save()
                message = "Your membership has been cancelled. You are now on a Free membership."
            else:
                message = "You are already on a Free membership."
    context = {
        'membership': membership,
        'message': message,
    }
    return render(request, 'member.html', context)
