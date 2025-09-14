from django.contrib import admin
from .models import Complaint, ValidationLog, CreditTransaction

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'title', 'status', 'level', 'is_valid', 'created_at')
    list_filter = ('category', 'status', 'level', 'is_valid')
    search_fields = ('title', 'description')

@admin.register(ValidationLog)
class ValidationLogAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'reviewer', 'valid', 'created_at')
    list_filter = ('valid',)

@admin.register(CreditTransaction)
class CreditTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'reason', 'created_at')
    list_filter = ('amount',)

from django.contrib import admin

# Register your models here.
