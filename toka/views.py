# views.py
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from django.conf import settings
from .forms import LoginForm, SignupForm, ContactForm
from .models import *

def home(request):
    # Query top 4 items
    top_four_health_plans = HealthPlan.objects.all()[:4]
    top_four_workout_plans = WorkoutPlan.objects.all()[:4]
    top_four_workouts = WorkoutClass.objects.all()[:4]

    context = {
        'top_four_health_plans': top_four_health_plans,
        'top_four_workout_plans': top_four_workout_plans,
        'top_four_workouts': top_four_workouts
    }

    if request.user.is_authenticated:
        # Fetch or create a membership for the user
        membership, created = Membership.objects.get_or_create(
            user=request.user,
            defaults={'membership_type': 'free', 'price': 0.00}
        )
        context['membership'] = membership

        # Determine if the user is a paid member (anything other than 'free')
        context['is_member'] = (membership.membership_type != 'free')

        # Optionally check for a membership message stored in the session
        if 'membership_message' in request.session:
            context['message'] = request.session.pop('membership_message')

    return render(request, 'index.html', context)






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
    is_member = False
    if request.user.is_authenticated:
        membership, created = Membership.objects.get_or_create(
            user=request.user,
            defaults={'membership_type': 'free', 'price': 0.00}
        )
        is_member = (membership.membership_type != 'free')
    return render(request, 'workoutclass.html', {'workouts': workouts, 'is_member': is_member})


def workout_detail(request, id):
    workout = get_object_or_404(WorkoutClass, id=id)
    return render(request, "workoutclassindividual.html", {"workout": workout})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Membership

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
        # Store message in session so it can be displayed on the home page
        request.session['membership_message'] = message
        return redirect('home')  # Redirect back to the home page
    # For GET requests, simply redirect back to home (since the membership form is embedded on home)
    return redirect('home')


def about_us(request):
    return render(request, 'aboutus.html')


def workoutplan_list(request):
    plans = WorkoutPlan.objects.all()
    filter_type = request.GET.get('filter', 'all')  # Default filter: 'all'

    if request.user.is_authenticated:
        purchased_plan_ids = WorkoutPlanPurchase.objects.filter(
            user=request.user
        ).values_list('workout_plan_id', flat=True)
        if filter_type == 'purchased':
            plans = plans.filter(id__in=purchased_plan_ids)
        elif filter_type == 'not_purchased':
            plans = plans.exclude(id__in=purchased_plan_ids)
        # Else, if 'all', do nothing
    else:
        # Optionally, if not logged in you can show all or force login to filter.
        pass

    context = {
        'plans': plans,
        'filter': filter_type
    }
    return render(request, 'workoutplan_list.html', context)


def workoutplan_detail(request, id):
    plan = get_object_or_404(WorkoutPlan, id=id)
    purchased = False
    if request.user.is_authenticated:
        purchased = WorkoutPlanPurchase.objects.filter(
            user=request.user, workout_plan=plan
        ).exists()
    context = {
        'plan': plan,
        'purchased': purchased
    }
    return render(request, 'workoutplan_detail.html', context)




@login_required
def purchase_workoutplan(request, id):
    plan = get_object_or_404(WorkoutPlan, id=id)
    # Check if the plan has already been purchased
    if WorkoutPlanPurchase.objects.filter(user=request.user, workout_plan=plan).exists():
        return redirect('workoutplan_detail', id=plan.id)  # Redirect if already purchased

    # Integrate your payment gateway here. For now, assume payment is successful.
    WorkoutPlanPurchase.objects.create(user=request.user, workout_plan=plan)
    return redirect('workoutplan_detail', id=plan.id)



@login_required
def plan_purchase_list(request):
    purchases = WorkoutPlanPurchase.objects.filter(user=request.user)
    return render(request, 'plan_purchase_list.html', {'purchases': purchases})




def healthplan_list(request):
    plans = HealthPlan.objects.all()
    filter_type = request.GET.get('filter', 'all')  # Default filter is "all"
    
    if request.user.is_authenticated:
        purchased_plan_ids = HealthPlanPurchase.objects.filter(
            user=request.user
        ).values_list('health_plan_id', flat=True)
        
        if filter_type == 'purchased':
            plans = plans.filter(id__in=purchased_plan_ids)
        elif filter_type == 'not_purchased':
            plans = plans.exclude(id__in=purchased_plan_ids)
        # If filter is 'all', do nothing
    # Optionally, you could enforce login for filtering
    context = {
        'plans': plans,
        'filter': filter_type,
    }
    return render(request, 'healthplan_list.html', context)

def healthplan_detail(request, id):
    plan = get_object_or_404(HealthPlan, id=id)
    purchased = False
    if request.user.is_authenticated:
        purchased = HealthPlanPurchase.objects.filter(user=request.user, health_plan=plan).exists()
    context = {
        'plan': plan,
        'purchased': purchased
    }
    return render(request, 'healthplan_detail.html', context)



@login_required
def purchase_healthplan(request, id):
    plan = get_object_or_404(HealthPlan, id=id)
    # Check if already purchased
    if HealthPlanPurchase.objects.filter(user=request.user, health_plan=plan).exists():
        return redirect('healthplan_detail', id=plan.id)
    # Payment integration goes here. For now, assume success.
    HealthPlanPurchase.objects.create(user=request.user, health_plan=plan)
    return redirect('healthplan_detail', id=plan.id)

@login_required
def healthplan_purchase_list(request):
    purchases = HealthPlanPurchase.objects.filter(user=request.user)
    return render(request, 'healthplan_purchase_list.html', {'purchases': purchases})


def contact(request):
    return render(request, 'contact.html')

def privacy(request):
    return render(request, 'privacy.html')

def terms(request):
    return render(request, 'terms.html')

def cookies(request):
    return render(request, 'cookies.html')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save form data to the database
            submission = form.save()
            
            # Prepare the email content
            subject = f'ShieldSenseAI: New Contact Submission from {submission.company}'
            message = (
                f"Name: {submission.name}\n"
                f"Email: {submission.email}\n"
                f"Company: {submission.company}\n"
            )
            recipient = settings.ADMIN_EMAIL  # Defined in settings.py
            
            # Send the email
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [recipient],
                fail_silently=False,
            )
            
            # If the request is AJAX, return a JSON response
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Success, thanks!'})
            else:
                # Fallback: you could redirect or render the same template
                return render(request, 'contact.html', {'form': ContactForm(), 'success': True})
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = ContactForm()

    
    return render(request, 'contact.html', {'form': form})



 












