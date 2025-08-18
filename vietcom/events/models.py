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
    max_participants = models.PositiveIntegerField(default=50, help_text="Số người tối đa có thể tham gia")
    image = models.ImageField(upload_to='events/', blank=True, null=True, help_text="Ảnh sự kiện")
    
    class Meta:
        ordering = ['-time']
        verbose_name = 'Event'
        verbose_name_plural = 'Events'

    def clean(self):
        """Validate event data"""
        if self.time and self.time <= timezone.now():
            raise ValidationError("Event time must be in the future.")
        
        if self.max_participants <= 0:
            raise ValidationError("Max participants must be greater than 0.")

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
    
    @property
    def is_full(self):
        """Check if event is full"""
        return self.participant_count >= self.max_participants
    
    @property
    def available_spots(self):
        """Get number of available spots"""
        return max(0, self.max_participants - self.participant_count)

    def can_user_join(self, user):
        """Check if user can join this event"""
        if self.is_past:
            return False, "Sự kiện đã kết thúc"
        
        if self.is_full:
            return False, "Sự kiện đã đủ người tham gia"
        
        if self.creator == user:
            return False, "Bạn là người tạo sự kiện này"
            
        if self.participations.filter(user=user).exists():
            return False, "Bạn đã tham gia sự kiện này rồi"
            
        return True, "Bạn có thể tham gia sự kiện này"

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
                raise ValidationError("Không thể tham gia sự kiện đã kết thúc.")
            
            # Check if event is full
            if self.event.is_full and not self.pk:  # Only check for new participations
                raise ValidationError("Sự kiện đã đủ người tham gia.")
            
            # Check if user is the creator
            if self.event.creator == self.user:
                raise ValidationError("Người tạo sự kiện không thể tham gia sự kiện của chính mình.")

    def __str__(self):
        return f"{self.user.username} - {self.event.name} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        """Override save to run validation"""
        self.clean()
        super().save(*args, **kwargs)