from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from users.models import User

class Mission(models.Model):
    MISSION_TYPE_CHOICES = [
        ('first_login', 'Lần đầu đăng nhập'),
        ('daily_login', 'Đăng nhập hàng ngày'),
        ('add_friend', 'Kết bạn'),
        ('send_message', 'Gửi tin nhắn'),
        ('create_post', 'Tạo bài viết'),
        ('like_post', 'Thích bài viết'),
        ('comment_post', 'Bình luận bài viết'),
        ('share_post', 'Chia sẻ bài viết'),
        ('complete_profile', 'Hoàn thiện hồ sơ'),
        ('upload_avatar', 'Tải ảnh đại diện'),
        ('join_event', 'Tham gia sự kiện'),
        ('create_event', 'Tạo sự kiện'),
        ('streak_login', 'Đăng nhập liên tiếp'),
        ('level_up', 'Lên cấp'),
        ('earn_points', 'Tích lũy điểm'),
    ]
    
    FREQUENCY_CHOICES = [
        ('once', 'Một lần'),
        ('daily', 'Hàng ngày'),
        ('weekly', 'Hàng tuần'),
        ('monthly', 'Hàng tháng'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    mission_type = models.CharField(max_length=20, choices=MISSION_TYPE_CHOICES)
    target_count = models.IntegerField(default=1, help_text="Số lần cần thực hiện")
    points_reward = models.IntegerField()
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default='once')
    icon = models.CharField(max_length=10, default='🎯')
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0, help_text="Thứ tự hiển thị")
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['order', 'points_reward']
        
    def __str__(self):
        return f"{self.icon} {self.title} (+{self.points_reward} điểm)"

class UserMission(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'Đang thực hiện'),
        ('completed', 'Hoàn thành'),
        ('claimed', 'Đã nhận thưởng'),
    ]
    
    user = models.ForeignKey(User, related_name='user_missions', on_delete=models.CASCADE)
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    current_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    completed_at = models.DateTimeField(null=True, blank=True)
    claimed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('user', 'mission')
        
    def __str__(self):
        return f"{self.user.full_name} - {self.mission.title} ({self.status})"
    
    def check_completion(self):
        """Kiểm tra xem nhiệm vụ đã hoàn thành chưa"""
        if self.current_count >= self.mission.target_count and self.status == 'in_progress':
            self.status = 'completed'
            self.completed_at = timezone.now()
            self.save()
            return True
        return False
    
    def claim_reward(self):
        """Nhận thưởng nhiệm vụ"""
        if self.status == 'completed':
            # Cộng điểm cho user
            self.user.add_points(self.mission.points_reward)
            
            # Tạo lịch sử điểm
            UserPoints.objects.create(
                user=self.user,
                action='mission_complete',
                points=self.mission.points_reward,
                description=f'Hoàn thành nhiệm vụ: {self.mission.title}'
            )
            
            # Cập nhật trạng thái
            self.status = 'claimed'
            self.claimed_at = timezone.now()
            self.save()
            return True
        return False
    
    def increment_progress(self, count=1):
        """Tăng tiến độ nhiệm vụ"""
        self.current_count += count
        self.save()
        return self.check_completion()
    
    @property
    def progress_percentage(self):
        """Tính phần trăm hoàn thành"""
        return min((self.current_count / self.mission.target_count) * 100, 100)

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
        ('mission_complete', 'Complete Mission'),
        ('post_create', 'Create Post'),
        ('post_like', 'Like Post'),
        ('post_comment', 'Comment Post'),
        ('avatar_upload', 'Upload Avatar'),
    ]
    
    user = models.ForeignKey(User, related_name='point_history', on_delete=models.CASCADE)
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
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