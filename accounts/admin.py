from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'phone', 'department', 'enrollment_number', 'stream', 'credits', 'last_complaint_at', 'college_id')
        }),
    )
    list_display = ('username', 'email', 'role', 'department', 'stream', 'credits')
    list_filter = ('role', 'department', 'stream', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'enrollment_number', 'college_id')

from django.contrib import admin

# Register your models here.
