from django.db import models
from django.conf import settings
from django.utils import timezone

CATEGORY_CHOICES = [
    ('CLEANING', 'Cleaning'),
    ('FACULTY', 'Teaching Faculty'),
    ('STAFF', 'Staff Behavior'),
    ('INFRA', 'Infrastructure'),
    ('STUDENT', 'Student Behavior'),
]

STATUS_CHOICES = [
    ('OPEN', 'Open'),
    ('IN_PROCESS', 'In Process'),
    ('CLOSED', 'Closed'),
]

LEVEL_CHOICES = [
    ('CLASS', 'Class Mentor'),
    ('HOD', 'Head of Department'),
    ('ADMIN', 'Admin Office'),
]

class Complaint(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='complaints')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    media = models.FileField(upload_to='complaints/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='CLASS')
    is_valid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_category_display()}: {self.title} ({self.get_status_display()})"

class ValidationLog(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='validations')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='reviews')
    valid = models.BooleanField()
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class CreditTransaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='credit_transactions')
    amount = models.IntegerField()
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

from django.db import models

# Create your models here.
