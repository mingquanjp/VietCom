from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from users.models import User

class Badge(models.Model):
    CATEGORY_CHOICES = [
        ('social', 'Social'),
        ('event', 'Event'),
        ('activity', 'Activity'),
        ('special', 'Special'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='activity')
    icon = models.CharField(max_length=50, blank=True, help_text="Emoji or icon class")
    required_points = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['category', 'required_points']
        verbose_name = 'Badge'
        verbose_name_plural = 'Badges'
    
    def clean(self):
        if self.required_points < 0:
            raise ValidationError("Required points cannot be negative.")
    
    def __str__(self):
        return f"{self.icon} {self.name}" if self.icon else self.name

class UserBadge(models.Model):
    user = models.ForeignKey(User, related_name='user_badges', on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    awarded_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('user', 'badge')
        ordering = ['-awarded_at']
        verbose_name = 'User Badge'
        verbose_name_plural = 'User Badges'
    
    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"


class UserPoints(models.Model):
    ACTION_CHOICES = [
        ('login', 'Daily Login'),
        ('event_create', 'Create Event'),
        ('event_join', 'Join Event'),
        ('friend_add', 'Add Friend'),
        ('message_send', 'Send Message'),
        ('profile_complete', 'Complete Profile'),
    ]
    
    user = models.ForeignKey(User, related_name='points', on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    points = models.IntegerField()
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User Points'
        verbose_name_plural = 'User Points'
    
    def clean(self):
        if self.points == 0:
            raise ValidationError("Points cannot be zero.")
    
    def __str__(self):
        sign = "+" if self.points > 0 else ""
        return f"{self.user.username}: {sign}{self.points} pts ({self.get_action_display()})"