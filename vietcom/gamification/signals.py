from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from users.models import User
from .models import Mission, UserMission, UserPoints


@receiver(post_save, sender=User)
def handle_user_level_change(sender, instance, created, **kwargs):
    """Xử lý khi user level thay đổi"""
    if not created:  # Chỉ xử lý khi update, không phải create
        # Kiểm tra level up missions
        from .views import update_mission_progress
        update_mission_progress(instance, 'level_up')
        update_mission_progress(instance, 'earn_points')


@receiver(user_logged_in)
def handle_login_missions(sender, user, request, **kwargs):
    """Xử lý missions khi user đăng nhập"""
    from .views import track_daily_login
    
    # Check first login
    if user.last_login is None or UserMission.objects.filter(
        user=user, 
        mission__mission_type='first_login',
        status='claimed'
    ).count() == 0:
        from .views import update_mission_progress
        update_mission_progress(user, 'first_login')
    
    # Daily login - chỉ tính một lần mỗi ngày
    from django.utils import timezone
    today = timezone.now().date()
    
    # Kiểm tra xem đã login hôm nay chưa
    today_login_points = UserPoints.objects.filter(
        user=user,
        action='login',
        created_at__date=today
    ).exists()
    
    if not today_login_points:
        track_daily_login(user)
