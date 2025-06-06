from .forms import OverloadForm
from .models import Overload, Workout, WorkoutEntry
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from .forms import UserLoginForm, UserRegistrationForm

User = get_user_model()


@login_required(login_url='login')
def home(request):
    # Get the latest overload for the current user
    overloads = Overload.objects.filter(user=request.user).order_by(
        '-date')[:1]  # Get only the most recent overload

    # For each overload, get its workouts
    overload_data = []
    for overload in overloads:
        workouts = WorkoutEntry.objects.filter(
            overload=overload).select_related('workout')
        overload_data.append({
            'overload': overload,
            'workouts': workouts
        })

    context = {
        'user': request.user,
        'overload_data': overload_data
    }
    return render(request, 'local_screen/home_page.html', context=context)


@login_required(login_url='login')
def profile(request):
    # Get total overloads for the user
    total_overloads = Overload.objects.filter(user=request.user).count()

    # Get current month's overloads
    from datetime import datetime, timedelta
    today = datetime.now()
    first_day_of_month = today.replace(
        day=1, hour=0, minute=0, second=0, microsecond=0)
    this_month_overloads = Overload.objects.filter(
        user=request.user,
        date__gte=first_day_of_month
    ).count()

    # Get this week's overloads
    first_day_of_week = today - timedelta(days=today.weekday())
    first_day_of_week = first_day_of_week.replace(
        hour=0, minute=0, second=0, microsecond=0)
    this_week_overloads = Overload.objects.filter(
        user=request.user,
        date__gte=first_day_of_week
    ).count()

    # Get last workout date
    last_overload = Overload.objects.filter(
        user=request.user).order_by('-date').first()
    last_workout_date = last_overload.date if last_overload else None

    context = {
        'user': request.user,
        'total_overloads': total_overloads,
        'this_month_overloads': this_month_overloads,
        'this_week_overloads': this_week_overloads,
        'last_workout_date': last_workout_date
    }
    return render(request, 'local_screen/profile.html', context=context)


def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            try:
                user = User.objects.get(email=email)
                if user.check_password(password):
                    login(request, user)
                    return redirect('home')
                else:
                    messages.error(request, 'Invalid password.')
            except User.DoesNotExist:
                messages.error(
                    request, 'No account found with this email address.')
    else:
        form = UserLoginForm()

    return render(request, 'auth_files/login.html', {'form': form})


def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserRegistrationForm()

    return render(request, 'auth_files/register.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')


@login_required(login_url='login')
def create_overload(request):
    if request.method == "POST":
        form = OverloadForm(request.POST)
        if form.is_valid():
            user = request.user
            overload = Overload.objects.create(user=user)

            # Get all workout rows from the form
            workout_rows = request.POST.getlist('workout')
            rep_counts = request.POST.getlist('reps')

            # Create workout entries for each workout
            for workout_id, rep_count in zip(workout_rows, rep_counts):
                if workout_id:  # Only create entry if workout is selected
                    WorkoutEntry.objects.create(
                        overload=overload,
                        workout_id=workout_id,
                        reps=rep_count
                    )

            messages.success(request, "Overload created successfully!")
            return redirect("home")
    else:
        form = OverloadForm()

    return render(request, 'crud_operation_files/overload_creation.html', {
        'form': form
    })


@login_required(login_url='login')
def progress(request):
    # Get all overloads for the current user
    overloads = Overload.objects.filter(user=request.user).order_by('-date')

    # For each overload, get its workouts
    overload_data = []
    for overload in overloads:
        workouts = WorkoutEntry.objects.filter(
            overload=overload).select_related('workout')
        overload_data.append({
            'overload': overload,
            'workouts': workouts
        })

    context = {
        'overload_data': overload_data
    }
    return render(request, 'local_screen/progress.html', context=context)


@login_required
def settings(request):
    return render(request, 'local_screen/settings.html')
