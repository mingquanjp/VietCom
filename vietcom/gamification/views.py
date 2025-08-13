from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import Mission, UserMission, Badge, UserBadge, UserPoints
from users.models import User

@login_required
def mission_list(request):
    """Hiển thị danh sách nhiệm vụ"""
    # Lấy tất cả missions đang hoạt động
    missions = Mission.objects.filter(is_active=True).order_by('order', 'points_reward')
    
    # Lấy progress của user cho từng mission
    user_missions = {}
    for mission in missions:
        user_mission, created = UserMission.objects.get_or_create(
            user=request.user,
            mission=mission
        )
        user_missions[mission.id] = user_mission
    
    # Thống kê user
    user_stats = {
        'total_points': request.user.points,
        'level': request.user.level,
        'points_for_next_level': request.user.get_points_for_next_level(),
        'progress_to_next_level': request.user.get_progress_to_next_level(),
        'completed_missions': UserMission.objects.filter(
            user=request.user, 
            status__in=['completed', 'claimed']
        ).count(),
        'total_missions': missions.count(),
    }
    
    context = {
        'missions': missions,
        'user_missions': user_missions,
        'user_stats': user_stats,
    }
    
    return render(request, 'gamification/mission_list.html', context)

@login_required
def claim_mission_reward(request, mission_id):
    """Nhận thưởng nhiệm vụ"""
    if request.method == 'POST':
        mission = get_object_or_404(Mission, id=mission_id, is_active=True)
        user_mission = get_object_or_404(UserMission, user=request.user, mission=mission)
        
        if user_mission.status == 'completed':
            if user_mission.claim_reward():
                messages.success(
                    request, 
                    f'🎉 Chúc mừng! Bạn đã nhận được {mission.points_reward} điểm từ nhiệm vụ "{mission.title}"!'
                )
                
                # Kiểm tra level up
                old_level = request.user.level
                request.user.refresh_from_db()  # Refresh để lấy points mới nhất
                if request.user.level > old_level:
                    messages.success(
                        request,
                        f'🎊 Tuyệt vời! Bạn đã lên level {request.user.level}!'
                    )
            else:
                messages.error(request, 'Không thể nhận thưởng cho nhiệm vụ này.')
        else:
            messages.error(request, 'Nhiệm vụ chưa hoàn thành hoặc đã nhận thưởng.')
    
    return redirect('gamification:mission_list')

@login_required
def user_progress(request):
    """Hiển thị tiến độ của user"""
    # Lấy lịch sử điểm
    recent_points = UserPoints.objects.filter(user=request.user).order_by('-created_at')[:10]
    
    # Lấy badges đã đạt được
    user_badges = UserBadge.objects.filter(user=request.user).select_related('badge')
    
    # Thống kê
    total_missions = Mission.objects.filter(is_active=True).count()
    completed_missions = UserMission.objects.filter(
        user=request.user,
        status__in=['completed', 'claimed']
    ).count()
    claimed_missions = UserMission.objects.filter(
        user=request.user,
        status='claimed'
    ).count()
    
    completion_rate = (completed_missions / total_missions * 100) if total_missions > 0 else 0
    
    stats = {
        'total_points': request.user.points,
        'current_level': request.user.level,
        'points_for_next_level': request.user.get_points_for_next_level(),
        'progress_percentage': request.user.get_progress_to_next_level(),
        'completed_missions': completed_missions,
        'claimed_missions': claimed_missions,
        'total_missions': total_missions,
        'completion_rate': round(completion_rate, 1),
    }
    
    context = {
        'recent_points': recent_points,
        'user_badges': user_badges,
        'stats': stats,
    }
    
    return render(request, 'gamification/user_progress.html', context)

def update_mission_progress(user, mission_type, count=1):
    """Helper function để cập nhật tiến độ nhiệm vụ"""
    missions = Mission.objects.filter(mission_type=mission_type, is_active=True)
    
    for mission in missions:
        user_mission, created = UserMission.objects.get_or_create(
            user=user,
            mission=mission
        )
        
        if user_mission.status == 'in_progress':
            completed = user_mission.increment_progress(count)
            if completed:
                # Tự động check completion cho missions đặc biệt
                if mission_type == 'level_up':
                    if user.level >= mission.target_count:
                        user_mission.check_completion()
                elif mission_type == 'earn_points':
                    if user.points >= mission.target_count:
                        user_mission.check_completion()

# Signal handlers để tự động cập nhật progress
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in

@receiver(user_logged_in)
def handle_login_missions(sender, user, request, **kwargs):
    """Xử lý missions khi user đăng nhập"""
    # Check first login
    if user.last_login is None or UserMission.objects.filter(
        user=user, 
        mission__mission_type='first_login',
        status='claimed'
    ).count() == 0:
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

# Helper functions cho các app khác
def track_friend_added(user):
    """Track khi user kết bạn"""
    update_mission_progress(user, 'add_friend')
    # Cộng điểm và tạo lịch sử điểm cho hoạt động kết bạn
    user.add_points(2)
    UserPoints.objects.create(
        user=user,
        action='friend_add',
        points=2,
        description='Kết bạn với người dùng mới'
    )

def track_message_sent(user):
    """Track khi user gửi tin nhắn"""
    update_mission_progress(user, 'send_message')
    # Cộng điểm và tạo lịch sử điểm cho hoạt động gửi tin nhắn
    user.add_points(1)
    UserPoints.objects.create(
        user=user,
        action='message_send',
        points=1,
        description='Gửi tin nhắn'
    )

def track_post_created(user):
    """Track khi user tạo bài viết"""
    update_mission_progress(user, 'create_post')
    # Cộng điểm và tạo lịch sử điểm cho hoạt động tạo bài viết
    user.add_points(3)
    UserPoints.objects.create(
        user=user,
        action='post_create',
        points=3,
        description='Tạo bài viết mới'
    )

def track_post_liked(user):
    """Track khi user thích bài viết"""
    update_mission_progress(user, 'like_post')
    # Cộng điểm và tạo lịch sử điểm cho hoạt động thích bài viết (ít điểm hơn)
    user.add_points(1)
    UserPoints.objects.create(
        user=user,
        action='post_like',
        points=1,
        description='Thích bài viết'
    )

def track_post_commented(user):
    """Track khi user bình luận"""
    update_mission_progress(user, 'comment_post')
    # Cộng điểm và tạo lịch sử điểm cho hoạt động bình luận
    user.add_points(2)
    UserPoints.objects.create(
        user=user,
        action='post_comment',
        points=2,
        description='Bình luận bài viết'
    )

def track_avatar_uploaded(user):
    """Track khi user upload avatar"""
    update_mission_progress(user, 'upload_avatar')
    # Cộng điểm và tạo lịch sử điểm cho hoạt động upload avatar
    user.add_points(5)
    UserPoints.objects.create(
        user=user,
        action='avatar_upload',
        points=5,
        description='Tải lên ảnh đại diện'
    )

def track_daily_login(user):
    """Track daily login"""
    update_mission_progress(user, 'daily_login')
    # Cộng điểm và tạo lịch sử điểm cho hoạt động đăng nhập hàng ngày
    user.add_points(2)
    UserPoints.objects.create(
        user=user,
        action='login',
        points=2,
        description='Đăng nhập hàng ngày'
    )

def track_event_joined(user):
    """Track khi user tham gia sự kiện"""
    update_mission_progress(user, 'join_event')

def track_event_created(user):
    """Track khi user tạo sự kiện"""
    update_mission_progress(user, 'create_event')

def track_profile_completed(user):
    """Track khi user hoàn thiện profile"""
    # Check if profile is complete
    if (user.first_name and user.last_name and user.date_of_birth and 
        user.gender != 'not_specified' and user.bio):
        update_mission_progress(user, 'complete_profile')
