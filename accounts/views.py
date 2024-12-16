from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from management.models import EmployeeForm
from . models import User

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('login') 
        else:
            print(form.errors)
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Login successful!')
                return redirect('home') 
            else:
                messages.error(request, 'Invalid email or password.')
        else:
            messages.error(request, 'Invalid form submission.')
    else:
        form = UserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('login')

@login_required(login_url='login/')
def home_view(request):
    try:
        form = EmployeeForm.objects.get(created_by=request.user)
    except EmployeeForm.DoesNotExist:
        form = None

    return render(request, 'accounts/home.html', {'form': form})


@login_required
def profile(request):
    user = User.objects.get(id=request.user.id)
    return render(request, 'accounts/profile.html', {'user': user})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Your password has been changed successfully!')
            return redirect('profile')
        else:
            messages.error(request,form.errors)
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'accounts/profile.html', {'form': form})