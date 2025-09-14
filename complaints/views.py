from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Complaint, CATEGORY_CHOICES, STATUS_CHOICES, LEVEL_CHOICES, ValidationLog, CreditTransaction
from accounts.models import User

@login_required
def create_complaint(request):
    user: User = request.user
    if user.role != 'STUDENT':
        messages.error(request, 'Only students can create complaints.')
        return redirect('dashboard')
    if request.method == 'POST':
        if not user.can_raise_again():
            messages.error(request, 'You can raise a new complaint in a section after 5 days.')
            return redirect('create_complaint')
        category = request.POST.get('category')
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

    return render(request, 'complaints/create.html', {
        'categories': CATEGORY_CHOICES,
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
    if request.user.role not in ['FACULTY', 'HOD', 'ADMIN']:
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
    if request.user.role not in ['FACULTY', 'HOD', 'ADMIN']:
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

from django.shortcuts import render

# Create your views here.
