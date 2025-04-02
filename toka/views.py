# views.py
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from django.conf import settings
from .forms import *
from .models import *
from django.contrib import messages
from datetime import datetime, time, date, timedelta

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
            subject = f'Toka Fitness: New Contact Submission from {submission.company}'
            message = (
                f"Name: {submission.name}\n"
                f"Email: {submission.email}\n"
                f"Company: {submission.company}\n"
            )
            recipient = settings.ADMIN_EMAIL  # Defined in settings.py
            
            print(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

            # Send the email
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [recipient],
                auth_user=settings.EMAIL_HOST_USER,
                auth_password=settings.EMAIL_HOST_PASSWORD,
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


@login_required
def book_facility(request):
    # 1) Determine which week to display
    try:
        week_offset = int(request.GET.get('week_offset', 0))
    except ValueError:
        week_offset = 0

    today = datetime.date.today()
    # Monday of the current week
    monday = today - datetime.timedelta(days=today.weekday())
    # Apply offset
    monday += datetime.timedelta(weeks=week_offset)

    # Generate days for this week
    week_days = []
    for i in range(7):
        day = monday + datetime.timedelta(days=i)
        formatted = day.strftime("%a %d")  # e.g., "Mon 12"
        # Disable if day is in the past for the current week_offset=0
        disabled = (week_offset == 0 and day < today)
        week_days.append({
            'date': day,
            'formatted': formatted,
            'disabled': disabled,
        })

    # 2) Create a list of time slots (9:00 to 17:00)
    time_slots = [
        "09:00", "10:00", "11:00", "12:00", 
        "13:00", "14:00", "15:00", "16:00", "17:00"
    ]

    # 3) Handle the booking form
    if request.method == 'POST':
        form = FacilityBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user

            # Retrieve date/time from hidden fields in the form
            str_date = request.POST.get('date')
            str_time = request.POST.get('time')
            if not str_date or not str_time:
                messages.error(request, "No date/time selected.")
                return redirect('book_facility')

            # Convert date/time strings to Python objects
            try:
                booking.date = datetime.datetime.strptime(str_date, "%Y-%m-%d").date()
                booking.time = datetime.datetime.strptime(str_time, "%H:%M").time()
            except ValueError:
                messages.error(request, "Invalid date/time format.")
                return redirect('book_facility')

            # --- Double-booking prevention ---
            if FacilityBooking.objects.filter(
                facility_type=booking.facility_type,
                location=booking.location,
                date=booking.date,
                time=booking.time
            ).exists():
                messages.error(request, "This time slot is already booked. Please select another time.")
                return redirect('book_facility')
            # ---------------------------------

            booking.save()
            messages.success(request, "Booking submitted!")
            return redirect('dashboard')
    else:
        form = FacilityBookingForm()

    context = {
        'form': form,
        'week_days': week_days,
        'week_offset': week_offset,
        'time_slots': time_slots,
    }
    return render(request, 'book_facility.html', context)


@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(FacilityBooking, id=booking_id, user=request.user)
    if request.method == "POST":
        booking.delete()
        messages.success(request, "Booking cancelled successfully.")
        return redirect('dashboard')
    return render(request, 'cancel_booking_confirm.html', {'booking': booking})



@login_required
def dashboard(request):
    bookings = FacilityBooking.objects.filter(user=request.user).order_by('-date', '-time')
    fitness_result = None
    calorie_result = None
    weekly_logs = None
    weekly_status = None

    if request.method == "POST":
        # Check if the calorie counter form is submitted (by checking for calorie_goal in POST)
        if 'calorie_goal' in request.POST:
            try:
                calorie_goal = float(request.POST.get('calorie_goal'))
                calories_consumed = float(request.POST.get('calories_consumed', 0))
                now = datetime.now()
                start_of_day = datetime.combine(date.today(), time.min)
                hours_elapsed = (now - start_of_day).seconds / 3600.0
                # Prevent division by zero if the day has just started
                if hours_elapsed == 0:
                    predicted_total = calories_consumed
                else:
                    predicted_total = (calories_consumed / hours_elapsed) * 24
                calorie_diff = calorie_goal - predicted_total
                calorie_result = {
                    'goal': calorie_goal,
                    'consumed': calories_consumed,
                    'predicted': round(predicted_total),
                    'difference': round(calorie_diff)
                }
                # Save or update the CalorieLog for today
                today = date.today()
                calorie_log, created = CalorieLog.objects.get_or_create(
                    user=request.user,
                    date=today,
                    defaults={
                        'calorie_goal': calorie_goal,
                        'calories_consumed': calories_consumed,
                        'predicted': predicted_total,
                        'difference': calorie_diff
                    }
                )
                if not created:
                    calorie_log.calorie_goal = calorie_goal
                    calorie_log.calories_consumed = calories_consumed
                    calorie_log.predicted = predicted_total
                    calorie_log.difference = calorie_diff
                    calorie_log.save()
            except ValueError:
                calorie_result = None
        else:
            # Process the fitness questionnaire submission
            try:
                question1 = int(request.POST.get('question1', 0))
                question2 = int(request.POST.get('question2', 0))
                question3 = int(request.POST.get('question3', 0))
            except ValueError:
                question1, question2, question3 = 0, 0, 0

            total_score = question1 + question2 + question3

            if total_score <= 2:
                level = "Beginner"
                message = "You are just starting out. Consider adding more regular activity."
            elif total_score <= 5:
                level = "Intermediate"
                message = "You have a moderate fitness level. Keep challenging yourself!"
            else:
                level = "Advanced"
                message = "Great job! You are in excellent shape. Maintain your workout regimen."

            fitness_result = FitnessAssessment.objects.create(
                user=request.user,
                level=level,
                message=message,
                total_score=total_score
            )
    else:
        fitness_result = FitnessAssessment.objects.filter(user=request.user).order_by('-created_at').first()

    # Retrieve calorie logs for the past 7 days (including today)
    week_start = date.today() - timedelta(days=6)
    weekly_logs = CalorieLog.objects.filter(user=request.user, date__gte=week_start).order_by('date')
    total_weekly_diff = sum(log.difference for log in weekly_logs)
    if total_weekly_diff >= 0:
        weekly_status = f"Great job! You're under your calorie goal by a total of {round(total_weekly_diff)} calories this week."
    else:
        weekly_status = f"This week, you've exceeded your calorie goal by {abs(round(total_weekly_diff))} calories. Consider adjustments."

    context = {
        'bookings': bookings,
        'fitness_result': fitness_result,
        'calorie_result': calorie_result,
        'weekly_logs': weekly_logs,
        'weekly_status': weekly_status,
    }
    return render(request, 'dashboard.html', context)

@login_required
def retake_fitness_questionnaire(request):
    return redirect('dashboard')
