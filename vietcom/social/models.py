from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from users.models import User  # Import từ app users

class Post(models.Model):
    author = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    location = models.CharField(max_length=255, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'

    def __str__(self):
        return f"{self.author.get_display_name()}: {self.content[:50]}..."

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def comments_count(self):
        return self.comments.count()

    def user_liked(self, user):
        return self.likes.filter(user=user).exists()

    def recent_comments(self, limit=3):
        return self.comments.all()[:limit]

class PostLike(models.Model):
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='post_likes', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('post', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_display_name()} liked {self.post.author.get_display_name()}'s post"

class PostComment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='post_comments', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.author.get_display_name()} commented on {self.post.author.get_display_name()}'s post"

class FriendRequest(models.Model):
    STATUS_CHOICES = (('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected'))
    sender = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('sender', 'receiver')
        ordering = ['-created_at']

    def clean(self):
        if self.sender == self.receiver:
            raise ValidationError("Cannot send friend request to yourself.")

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username} ({self.status})"

class Friendship(models.Model):
    user1 = models.ForeignKey(User, related_name='friends1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='friends2', on_delete=models.CASCADE)
    since = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('user1', 'user2')
        ordering = ['-since']

    def clean(self):
        if self.user1 == self.user2:
            raise ValidationError("Cannot be friends with yourself.")

    def __str__(self):
        return f"{self.user1.username} & {self.user2.username}"

class Message(models.Model):
    TYPE_CHOICES = (('text', 'Text'), ('image', 'Image'), ('sticker', 'Sticker'), ('location', 'Location'))
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.SET_NULL, null=True, blank=True)
    group = models.ForeignKey('Group', on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField(blank=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='text')
    image = models.ImageField(upload_to='messages/', blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True, help_text="Vĩ độ vị trí")
    longitude = models.FloatField(null=True, blank=True, help_text="Kinh độ vị trí")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        if self.group:
            return f"{self.sender.username} in {self.group.topic}: {self.content[:50]}"
        return f"{self.sender.username} to {self.receiver.username}: {self.content[:50]}"

class Group(models.Model):
    topic = models.CharField(max_length=255, blank=True)
    creator = models.ForeignKey(User, related_name='created_groups', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.topic


class GroupMembership(models.Model):
    ROLE_CHOICES = (('member', 'Member'), ('admin', 'Admin'))
    group = models.ForeignKey(Group, related_name='memberships', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='group_memberships', on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('group', 'user')
        ordering = ['-joined_at']

    def __str__(self):
        return f"{self.user.username} in {self.group.topic} ({self.role})"

class Call(models.Model):
    STATUS_CHOICES = (
        ('initiating', 'Initiating'),
        ('ringing', 'Ringing'),
        ('active', 'Active'),
        ('ended', 'Ended'),
        ('missed', 'Missed'),
        ('rejected', 'Rejected')
    )
    
    caller = models.ForeignKey(User, related_name='calls_made', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='calls_received', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='initiating')
    started_at = models.DateTimeField(default=timezone.now)
    answered_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(default=0, help_text="Duration in seconds")
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.caller.username} -> {self.receiver.username} ({self.status})"
    
    @property
    def duration_formatted(self):
        """Return duration in MM:SS format"""
        if self.duration:
            minutes = self.duration // 60
            seconds = self.duration % 60
            return f"{minutes:02d}:{seconds:02d}"
        return "00:00"