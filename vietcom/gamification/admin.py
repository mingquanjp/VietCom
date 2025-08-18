from django.contrib import admin
from .models import Badge, UserBadge, UserPoints, Mission, UserMission

@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ['title', 'mission_type', 'target_count', 'points_reward', 'frequency', 'is_active', 'order']
    list_filter = ['mission_type', 'frequency', 'is_active']
    search_fields = ['title', 'description']
    ordering = ['order', 'points_reward']
    list_editable = ['is_active', 'order']

@admin.register(UserMission)
class UserMissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'mission', 'current_count', 'status', 'completed_at', 'claimed_at']
    list_filter = ['status', 'mission__mission_type', 'completed_at']
    search_fields = ['user__username', 'user__email', 'mission__title']
    readonly_fields = ['created_at', 'completed_at', 'claimed_at']

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'required_points', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'description']

@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ['user', 'badge', 'awarded_at']
    list_filter = ['badge__category', 'awarded_at']
    search_fields = ['user__username', 'badge__name']

@admin.register(UserPoints)
class UserPointsAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'points', 'description', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['user__username', 'description']
    readonly_fields = ['created_at']
