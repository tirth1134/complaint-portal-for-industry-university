from typing import Dict
from django.contrib.auth.models import AnonymousUser
from django.db.models import Q

from complaints.models import Complaint


def notifications(request) -> Dict[str, int]:
    """Provide notifications_count for staff roles.
    Counts OPEN complaints in the staff member's department (plus admins see all).
    """
    user = getattr(request, 'user', None)
    if not user or isinstance(user, AnonymousUser) or not user.is_authenticated:
        return {}

    role = getattr(user, 'role', 'STUDENT')
    dept = (getattr(user, 'department', '') or '').strip()

    qs = Complaint.objects.filter(status='OPEN')
    if role in ['FACULTY', 'HOD']:
        if dept:
            qs = qs.filter(Q(student__department__iexact=dept) | Q(student__department__isnull=True) | Q(student__department__exact=''))
        count = qs.count()
    elif role == 'ADMIN':
        count = qs.count()
    else:
        return {}

    return {'notifications_count': int(count)}
