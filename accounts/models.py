from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

STREAM_CHOICES = [
    ("BCA", "BCA"),
    ("BTECH", "B.Tech"),
    ("MTECH", "M.Tech"),
    ("MSCIT", "MSc IT"),
    ("MBA", "MBA"),
    ("BBA", "BBA"),
    ("MCA", "MCA"),
]

ROLE_CHOICES = [
    ("STUDENT", "Student"),
    ("FACULTY", "Faculty"),
    ("HOD", "HOD"),
    ("ADMIN", "Admin"),
]

class User(AbstractUser):
    # Common fields
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="STUDENT")
    phone = models.CharField(max_length=15, blank=True)
    department = models.CharField(max_length=20, blank=True)  # e.g., BCA, MCA

    # Student-specific
    enrollment_number = models.CharField(max_length=50, blank=True, unique=False)
    stream = models.CharField(max_length=10, choices=STREAM_CHOICES, blank=True)
    credits = models.PositiveIntegerField(default=20)
    last_complaint_at = models.DateTimeField(null=True, blank=True)

    # Staff-specific
    college_id = models.CharField(max_length=100, blank=True)

    def can_raise_again(self) -> bool:
        if not self.last_complaint_at:
            return True
        return timezone.now() >= self.last_complaint_at + timezone.timedelta(days=5)

    def __str__(self):
        return f"{self.username} ({self.role})"

from django.db import models

# Create your models here.
