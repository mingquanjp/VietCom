from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from users.models import User

class Event(models.Model):
    name = models.CharField(max_length=255)
    time = models.DateTimeField()
    location_desc = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True, help_text="Vĩ độ sự kiện")
    longitude = models.FloatField(null=True, blank=True, help_text="Kinh độ sự kiện")
    description = models.TextField(blank=True)
    creator = models.ForeignKey(User, related_name='created_events', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-time']
        verbose_name = 'Event'
        verbose_name_plural = 'Events'

    def clean(self):
        """Validate event data"""
        if self.time and self.time <= timezone.now():
            raise ValidationError("Event time must be in the future.")

    def __str__(self):
        return f"{self.name} - {self.time.strftime('%Y-%m-%d %H:%M')}"

    @property
    def participant_count(self):
        """Get total number of participants"""
        return self.participations.filter(status='joined').count()

    @property
    def interested_count(self):
        """Get number of interested users"""
        return self.participations.filter(status='interested').count()

    @property
    def is_past(self):
        """Check if event is in the past"""
        return self.time <= timezone.now()

    def can_user_join(self, user):
        """Check if user can join this event"""
        if self.is_past:
            return False, "Event is in the past"
        
        if self.creator == user:
            return False, "You are the creator of this event"
            
        if self.participations.filter(user=user).exists():
            return False, "You are already participating in this event"
            
        return True, "You can join this event"

class EventParticipation(models.Model):
    STATUS_CHOICES = (('joined', 'Joined'), ('interested', 'Interested'))
    event = models.ForeignKey(Event, related_name='participations', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='event_participations', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='joined')
    joined_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('event', 'user')
        ordering = ['-joined_at']
        verbose_name = 'Event Participation'
        verbose_name_plural = 'Event Participations'

    def clean(self):
        """Validate participation"""
        if self.event and self.user:
            # Check if event is in the past
            if self.event.is_past:
                raise ValidationError("Cannot join/show interest in past events.")
            
            # Check if user is the creator
            if self.event.creator == self.user:
                raise ValidationError("Event creator cannot participate in their own event.")

    def __str__(self):
        return f"{self.user.username} - {self.event.name} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        """Override save to run validation"""
        self.clean()
        super().save(*args, **kwargs)