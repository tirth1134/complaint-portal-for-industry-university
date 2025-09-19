from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from .models import User, STREAM_CHOICES, ROLE_CHOICES
from complaints.models import Complaint, CATEGORY_CHOICES
import math
import re


def _normalize_phone(raw: str) -> str:
    """Strip non-digits and return just the digits."""
    return re.sub(r"\D", "", raw or "")


def _is_valid_mobile(digits: str) -> bool:
    """Basic 10-digit mobile validation after normalization."""
    return len(digits) == 10 and digits.isdigit()


def home(request):
    return render(request, 'accounts/home.html')


def register_student(request):
    if request.method == 'POST':
        data = request.POST
        username = (data.get('enrollment_number') or "").strip()
        email = (data.get('email') or "").strip()
        phone_digits = _normalize_phone(data.get('phone'))
        password = data.get('password') or ""

        # Username/enrollment uniqueness
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Enrollment number already registered.')
            return redirect('register_student')

        # Mobile number validation
        if not _is_valid_mobile(phone_digits):
            messages.error(request, 'Enter a valid 10-digit mobile number.')
            return redirect('register_student')

        # Email validation + uniqueness
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Enter a valid email address.')
            return redirect('register_student')
        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'Email already registered.')
            return redirect('register_student')

        # Password strength validation using Django validators
        try:
            temp_user = User(username=username, email=email, first_name=data.get('first_name', ''))
            validate_password(password, user=temp_user)
        except ValidationError as e:
            messages.error(request, ' '.join(e.messages))
            return redirect('register_student')

        # Create the user on success
        User.objects.create_user(
            username=username,
            password=password,
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            phone=phone_digits,
            email=email,
            role='STUDENT',
            enrollment_number=username,
            stream=data.get('stream'),
            department=data.get('stream'),
        )
        messages.success(request, 'Registration successful. You can login now.')
        return redirect('login')
    return render(request, 'accounts/register_student.html', {'streams': STREAM_CHOICES})


def register_staff(request):
    if request.method == 'POST':
        data = request.POST
        username = (data.get('college_id') or "").strip()
        email = (data.get('email') or "").strip()
        phone_digits = _normalize_phone(data.get('phone'))
        password = data.get('password') or ""
        confirm_password = data.get('confirm_password') or ""

        # Username/college_id uniqueness
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Member ID already registered.')
            return redirect('register_staff')

        # Mobile validation
        if not _is_valid_mobile(phone_digits):
            messages.error(request, 'Enter a valid 10-digit mobile number.')
            return redirect('register_staff')

        # Email format + uniqueness
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Enter a valid email address.')
            return redirect('register_staff')
        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'Email already registered.')
            return redirect('register_staff')

        # Password validation & confirmation
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('register_staff')
        try:
            temp_user = User(username=username, email=email, first_name=data.get('first_name', ''))
            validate_password(password, user=temp_user)
        except ValidationError as e:
            messages.error(request, ' '.join(e.messages))
            return redirect('register_staff')

        # Map working_at to existing role for permissions
        working_at = (data.get('working_at') or '').strip()
        role_map = {
            'teachingFaculty': 'FACULTY',
            'hod': 'HOD',
            'adminOffice': 'ADMIN',
            'staffMember': 'STAFF',
            'infraManager': 'STAFF',
            'studentCommittee': 'STAFF',
        }
        resolved_role = role_map.get(working_at, 'STAFF')

        # Normalize department selections
        faculty_department = data.get('faculty_department') or ''
        if faculty_department:
            faculty_department = faculty_department.upper()
            if faculty_department == 'COMPUTING':
                dept_label = 'Computing'
            elif faculty_department == 'SST':
                dept_label = 'SST'
            else:
                dept_label = faculty_department
        else:
            dept_label = ''

        hod_department = data.get('hod_department') or ''
        if hod_department:
            hod_department = hod_department.upper()

        # Streams list (can be empty)
        streams = data.getlist('faculty_streams')

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            phone=phone_digits,
            email=email,
            role=resolved_role,
            department=dept_label,
            college_id=username,
            working_at={
                'teachingFaculty': 'TEACHING_FACULTY',
                'hod': 'HOD',
                'adminOffice': 'ADMIN_OFFICE',
                'staffMember': 'STAFF_MEMBER',
                'infraManager': 'INFRA_MANAGER',
                'studentCommittee': 'STUDENT_COMMITTEE',
            }.get(working_at, ''),
            faculty_department=faculty_department,
            faculty_streams=streams,
            staff_description=data.get('staff_description', ''),
            infra_building=(data.get('infra_building') or '').upper(),
            hod_department=hod_department,
        )
        messages.success(request, 'Staff registration successful. You can login now.')
        return redirect('login')
    return render(request, 'accounts/register_staff.html', {})


def login_view(request):
    # If the user is already authenticated (e.g., visits "/" or "/login/"), send them to the dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')

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
    # After logout, send users directly to the login page
    return redirect('login')


@login_required
def dashboard(request):
    if request.user.role == 'STUDENT':
        # Student metrics and recent items for a richer dashboard UI
        qs = Complaint.objects.filter(student=request.user)
        my_count = qs.count()
        open_count = qs.filter(status='OPEN').count()
        in_process_count = qs.filter(status='IN_PROCESS').count()
        closed_count = qs.filter(status='CLOSED').count()
        recent = list(qs.order_by('-created_at')[:5])

        # Cooldown days remaining based on last_complaint_at (global hint)
        days_remaining = 0
        if request.user.last_complaint_at:
            remaining = request.user.last_complaint_at + timezone.timedelta(days=5) - timezone.now()
            if remaining.total_seconds() > 0:
                days_remaining = math.ceil(remaining.total_seconds() / 86400)

        context = {
            'my_count': my_count,
            'open_count': open_count,
            'in_process_count': in_process_count,
            'closed_count': closed_count,
            'recent_complaints': recent,
            'days_remaining': days_remaining,
        }
        return render(request, 'accounts/dashboard_student.html', context)
    else:
        # Build staff dashboard context (global view across all complaints)
        qs = Complaint.objects.all()
        total = qs.count()
        stats = {
            'total': total,
            'open': qs.filter(status='OPEN').count(),
            'in_process': qs.filter(status='IN_PROCESS').count(),
            'closed': qs.filter(status='CLOSED').count(),
            'validated': qs.filter(is_valid=True).count(),
        }
        # Recent complaints, newest first
        recent = list(qs.order_by('-created_at')[:5])
        # Category breakdown with percentage bar widths
        labels = dict(CATEGORY_CHOICES)
        by_cat = []
        emoji_map = {
            'CLEANING': '🧹',
            'FACULTY': '🎓',
            'STAFF': '🧑‍🔧',
            'INFRA': '🏗️',
            'STUDENT': '🧑‍🎓',
        }
        for key, label in CATEGORY_CHOICES:
            by_cat.append({
                'key': key,
                'label': label,
                'count': qs.filter(category=key).count(),
                'emoji': emoji_map.get(key, '•'),
            })
        max_count = max([c['count'] for c in by_cat] + [0])
        for item in by_cat:
            item['pct'] = 0 if max_count == 0 else round(item['count'] * 100 / max_count, 2)
        context = {
            'stats': stats,
            'recent_complaints': recent,
            'category_breakdown': by_cat,
        }
        return render(request, 'accounts/dashboard_staff.html', context)

from django.shortcuts import render

# Create your views here.
