from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Complaint, CATEGORY_CHOICES, STATUS_CHOICES, LEVEL_CHOICES, ValidationLog, CreditTransaction
from accounts.models import User

@login_required
def list_complaints(request):
    if request.user.role == 'STUDENT':
        qs = Complaint.objects.filter(student=request.user).order_by('-created_at')
        context = {'complaints': qs, 'is_staff_view': False}
    else:
        qs = Complaint.objects.all().select_related('student').order_by('-created_at')
        context = {'complaints': qs, 'is_staff_view': True}
    return render(request, 'complaints/list.html', context)

@login_required
def select_category(request):
    user: User = request.user
    if user.role != 'STUDENT':
        messages.error(request, 'Only students can raise complaints.')
        return redirect('dashboard')

    # Build selection tiles with emoji icons
    labels = dict(CATEGORY_CHOICES)
    tiles = [
        {'value': 'INFRA', 'title': 'Infra Complaint', 'emoji': '🏗️', 'label': labels.get('INFRA', 'Infrastructure')},
        {'value': 'FACULTY', 'title': 'Teaching Complaint', 'emoji': '🎓', 'label': labels.get('FACULTY', 'Teaching Faculty')},
        {'value': 'STAFF', 'title': 'Staff Behaviour', 'emoji': '🧑\u200d🔧', 'label': labels.get('STAFF', 'Staff Behavior')},
        {'value': 'STUDENT', 'title': 'Student Behaviour', 'emoji': '🧑\u200d🎓', 'label': labels.get('STUDENT', 'Student Behavior')},
        {'value': 'CLEANING', 'title': 'Cleaning Complaint', 'emoji': '🧹', 'label': labels.get('CLEANING', 'Cleaning')},
    ]
    return render(request, 'complaints/select_category.html', {'tiles': tiles})


@login_required
def create_complaint(request, category=None):
    user: User = request.user
    if user.role != 'STUDENT':
        messages.error(request, 'Only students can create complaints.')
        return redirect('dashboard')

    # Validate/normalize category
    valid_values = set(dict(CATEGORY_CHOICES).keys())
    if request.method == 'GET' and not category:
        # If no category chosen, go to selection page
        return redirect('select_complaint_category')

    if category and category not in valid_values:
        messages.error(request, 'Please choose a valid section.')
        return redirect('select_complaint_category')

    if request.method == 'POST':
        category = request.POST.get('category') or category
        # Enforce 5-day cooldown per category
        last = Complaint.objects.filter(student=user, category=category).order_by('-created_at').first()
        if last and timezone.now() < last.created_at + timezone.timedelta(days=5):
            messages.error(request, 'You can raise a new complaint in this section after 5 days.')
            return redirect('create_complaint', category=category)
        title = request.POST.get('title')
        description = request.POST.get('description')
        media = request.FILES.get('media')
        complaint = Complaint.objects.create(
            student=user, category=category, title=title, description=description, media=media
        )
        user.last_complaint_at = timezone.now()
        user.save(update_fields=['last_complaint_at'])
        messages.success(request, 'Complaint submitted!')
        return redirect('complaint_detail', complaint_id=complaint.id)

    # GET: show form for selected category
    label = dict(CATEGORY_CHOICES).get(category, category)
    return render(request, 'complaints/create.html', {
        'categories': CATEGORY_CHOICES,
        'selected_category': category,
        'selected_label': label,
    })


@login_required
def complaint_detail(request, complaint_id):
    c = get_object_or_404(Complaint, id=complaint_id)
    # Ensure anonymity: staff can't see student identity; only their department
    student_dept = c.student.department
    context = {'complaint': c, 'student_dept': student_dept if request.user.role != 'STUDENT' else None}
    return render(request, 'complaints/detail.html', context)


@login_required
def validate_complaint(request, complaint_id):
    # Allow all staff roles to validate (FACULTY, HOD, ADMIN, STAFF)
    if request.user.role not in ['FACULTY', 'HOD', 'ADMIN', 'STAFF']:
        messages.error(request, 'Not authorized to validate complaints.')
        return redirect('dashboard')
    c = get_object_or_404(Complaint, id=complaint_id)
    valid = request.POST.get('valid') == 'true'
    note = request.POST.get('note', '')
    c.is_valid = valid
    c.save(update_fields=['is_valid'])
    ValidationLog.objects.create(complaint=c, reviewer=request.user, valid=valid, note=note)
    if valid:
        c.student.credits += 5
        c.student.save(update_fields=['credits'])
        CreditTransaction.objects.create(user=c.student, amount=5, reason='Valid Complaint Reward')
    messages.success(request, 'Validation recorded.')
    return redirect('complaint_detail', complaint_id=complaint_id)


@login_required
def update_status(request, complaint_id):
    # Allow all staff roles to update status as well
    if request.user.role not in ['FACULTY', 'HOD', 'ADMIN', 'STAFF']:
        messages.error(request, 'Not authorized to update status.')
        return redirect('dashboard')
    c = get_object_or_404(Complaint, id=complaint_id)
    status = request.POST.get('status')
    level = request.POST.get('level', c.level)
    if status in dict(STATUS_CHOICES):
        c.status = status
    if level in dict(LEVEL_CHOICES):
        c.level = level
    c.save(update_fields=['status', 'level'])
    messages.success(request, 'Status updated.')
    return redirect('complaint_detail', complaint_id=complaint_id)

