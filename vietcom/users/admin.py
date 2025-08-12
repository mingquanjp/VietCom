from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User

# Register your models here.

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Fields displayed in the list
    list_display = [
        'username', 
        'email', 
        'full_name', 
        'phone', 
        'gender_display',
        'status_display',
        'status',
        'level',
        'date_joined'
    ]
    
    # Searchable fields
    search_fields = ['username', 'email', 'full_name', 'phone']
    
    # Filters on the right side
    list_filter = [
        'gender', 
        'status', 
        'level',
        'is_active', 
        'date_joined'
    ]
    
    # Default ordering
    ordering = ['-date_joined']
    
    # Fields that can be edited directly in the list
    list_editable = ['status', 'level']
    
    # Items per page
    list_per_page = 25
    
    # Add to BaseUserAdmin fieldsets
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Personal Information', {
            'fields': ('full_name', 'phone', 'hometown', 'date_of_birth', 'gender', 'bio', 'avatar')
        }),
        ('Application Settings', {
            'fields': ('status', 'interests', 'latitude', 'longitude', 'search_radius', 'level', 'is_admin')
        }),
    )
    
    # Fieldsets for adding new user
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Information', {
            'fields': ('email', 'full_name', 'phone', 'gender')
        }),
    )
    
    def gender_display(self, obj):
        """Display gender with colors"""
        if obj.gender == 'M':
            return format_html('<span style="color: blue;">♂ Male</span>')
        elif obj.gender == 'F':
            return format_html('<span style="color: pink;">♀ Female</span>')
        elif obj.gender == 'O':
            return format_html('<span style="color: purple;">⚲ Other</span>')
        return '-'
    gender_display.short_description = 'Gender'
    
    def status_display(self, obj):
        """Display status with colors"""
        status_colors = {
            'online': 'green',
            'offline': 'gray',
        }
        color = status_colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {};">● {}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = 'Status'
    
    # Custom actions
    actions = ['make_online', 'make_offline', 'reset_level']
    
    def make_online(self, request, queryset):
        """Set status to online for selected users"""
        updated = queryset.update(status='online')
        self.message_user(request, f'{updated} user(s) have been set to online status.')
    make_online.short_description = "Set status to Online"
    
    def make_offline(self, request, queryset):
        """Set status to offline for selected users"""
        updated = queryset.update(status='offline')
        self.message_user(request, f'{updated} user(s) have been set to offline status.')
    make_offline.short_description = "Set status to Offline"
    
    def reset_level(self, request, queryset):
        """Reset level to 1 for selected users"""
        updated = queryset.update(level=1)
        self.message_user(request, f'{updated} user(s) have been reset to level 1.')
    reset_level.short_description = "Reset Level to 1"
