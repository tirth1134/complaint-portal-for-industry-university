from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, STREAM_CHOICES, ROLE_CHOICES


def home(request):
    return render(request, 'accounts/home.html')


def register_student(request):
    if request.method == 'POST':
        data = request.POST
        username = data.get('enrollment_number')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Enrollment number already registered.')
            return redirect('register_student')
        user = User.objects.create_user(
            username=username,
            password=data.get('password'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            phone=data.get('phone'),
            role='STUDENT',
            enrollment_number=data.get('enrollment_number'),
            stream=data.get('stream'),
            department=data.get('stream'),
        )
        messages.success(request, 'Registration successful. You can login now.')
        return redirect('login')
    return render(request, 'accounts/register_student.html', {'streams': STREAM_CHOICES})


def register_staff(request):
    if request.method == 'POST':
        data = request.POST
        username = data.get('college_id')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'College ID already registered.')
            return redirect('register_staff')
        user = User.objects.create_user(
            username=username,
            password=data.get('password'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            phone=data.get('phone'),
            email=data.get('email'),
            role=data.get('role', 'FACULTY'),
            department=data.get('department'),
            college_id=data.get('college_id'),
        )
        messages.success(request, 'Staff registration successful. You can login now.')
        return redirect('login')
    return render(request, 'accounts/register_staff.html', {'roles': ROLE_CHOICES})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Invalid credentials')
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def dashboard(request):
    if request.user.role == 'STUDENT':
        return render(request, 'accounts/dashboard_student.html')
    else:
        return render(request, 'accounts/dashboard_staff.html')

from django.shortcuts import render

# Create your views here.
