from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db import models
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Q
import json
import math
from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm
from social.models import Friendship, FriendRequest
# Remove this import if gamification app doesn't exist yet
# from gamification.models import UserPoints

def firstpage(request):
    """Landing page with authentication options"""
    return render(request, 'firstpage.html')

@login_required
def temp_page(request):
    """Temporary welcome page after login/register"""
    return render(request, 'temp.html')

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula"""
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

@login_required
def nearby_users(request):
    """Display nearby users page with a mini-map"""
    current_user = request.user
    
    nearby_users_data = []
    if current_user.latitude and current_user.longitude:
        nearby_users_data = get_nearby_users_data(current_user)
    
    # Chuẩn bị dữ liệu JSON cho bản đồ
    # Chỉ lấy các thông tin cần thiết để tránh lộ dữ liệu nhạy cảm
    map_users_data = []
    for user_data in nearby_users_data:
        map_users_data.append({
            'id': user_data['user'].id,
            'full_name': user_data['user'].get_display_name(),
            'avatar_url': user_data['user'].avatar.url if user_data['user'].avatar else '/static/default-avatar.png',
            'latitude': user_data['user'].latitude,
            'longitude': user_data['user'].longitude,
            'distance': round(user_data['distance'], 1),
            'friend_status': user_data['friend_status'],
            'request_id': user_data['request_id']
        })

    # Get current user's search radius based on level
    current_search_radius = current_user.get_search_radius_by_level()
    next_level_radius = 5 + current_user.level * 2  # Next level radius

    context = {
        'current_user': current_user,
        'nearby_users': nearby_users_data,
        'user_level': current_user.level,
        'search_radius': current_search_radius,
        'next_level': current_user.level + 1,
        'next_level_radius': next_level_radius,
        # Chuyển đổi dữ liệu sang chuỗi JSON và đưa vào context
        'map_users_json': json.dumps(map_users_data),
        'current_user_json': json.dumps({
            'latitude': current_user.latitude,
            'longitude': current_user.longitude,
            'search_radius': current_search_radius,
            'level': current_user.level
        })
    }
    
    # Sửa lại đường dẫn template nếu cần, ví dụ: 'users/nearby_users.html'
    return render(request, 'nearby_users.html', context)

def get_nearby_users_data(current_user):
    """Get nearby users with distance calculation based on user level"""
    if not current_user.latitude:
        return []
    
    # Get search radius based on user level: 5 + (level-1) * 2
    search_radius = current_user.get_search_radius_by_level()
    
    # Get all users with location data
    users_with_location = User.objects.exclude(
        id=current_user.id
    ).exclude(
        latitude__isnull=True
    ).exclude(
        longitude__isnull=True
    )
    
    # Calculate distances and filter by search radius
    nearby_users = []
    for user in users_with_location:
        distance = calculate_distance(
            current_user.latitude,
            current_user.longitude,
            user.latitude,
            user.longitude
        )
        
        if distance <= search_radius:
            # Check friendship status
            is_friend = Friendship.objects.filter(
                Q(user1=current_user, user2=user) | Q(user1=user, user2=current_user)
            ).exists()
            
            # Check friend request status
            friend_request = FriendRequest.objects.filter(
                Q(sender=current_user, receiver=user) | Q(sender=user, receiver=current_user)
            ).first()
            
            friend_status = 'none'  # none, sent, received, friends
            request_id = None
            
            if is_friend:
                friend_status = 'friends'
            elif friend_request:
                request_id = friend_request.id
                if friend_request.sender == current_user:
                    friend_status = 'sent'
                else:
                    friend_status = 'received'
            
            nearby_users.append({
                'user': user,
                'distance': distance,
                'friend_status': friend_status,
                'request_id': request_id
            })
    
    # Sort by distance and limit to 20
    nearby_users.sort(key=lambda x: x['distance'])
    return nearby_users[:20]

@login_required
@require_http_methods(["POST"])
def update_location(request):
    """Update user's current location"""
    try:
        data = json.loads(request.body)
        latitude = float(data.get('latitude'))
        longitude = float(data.get('longitude'))
        
        # Update user location
        request.user.latitude = latitude
        request.user.longitude = longitude
        request.user.save(update_fields=['latitude', 'longitude'])
        
        # Award points for location update - uncomment when gamification is ready
        # UserPoints.objects.create(
        #     user=request.user,
        #     action='profile_complete',
        #     points=2,
        #     description='Updated location for nearby search'
        # )
        
        return JsonResponse({
            'success': True,
            'message': 'Location updated successfully'
        })
        
    except (ValueError, KeyError) as e:
        return JsonResponse({
            'success': False,
            'message': 'Invalid location data'
        }, status=400)

@login_required
@require_http_methods(["POST"])
def update_search_radius(request):
    """Update user's search radius"""
    try:
        data = json.loads(request.body)
        radius = float(data.get('radius'))
        
        # Validate radius (1-100 km)
        if not 1 <= radius <= 100:
            return JsonResponse({
                'success': False,
                'message': 'Radius must be between 1 and 100 km'
            }, status=400)
        
        # Update search radius
        request.user.search_radius = radius
        request.user.save(update_fields=['search_radius'])
        
        return JsonResponse({
            'success': True,
            'message': 'Search radius updated successfully'
        })
        
    except (ValueError, KeyError):
        return JsonResponse({
            'success': False,
            'message': 'Invalid radius data'
        }, status=400)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                
                # Track first login mission
                try:
                    from gamification.views import track_first_login
                    track_first_login(user)
                except ImportError:
                    pass
                
                messages.success(request, 'Đăng ký thành công!')
                return redirect('temp_page')
            except Exception as e:
                messages.error(request, f'Đăng ký thất bại: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def profile_update(request):
    """Update user profile"""
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            old_avatar = request.user.avatar
            user = form.save()
            
            # Track avatar upload mission
            if 'avatar' in form.changed_data and user.avatar:
                try:
                    from gamification.views import track_avatar_uploaded
                    track_avatar_uploaded(user)
                except ImportError:
                    pass
            
            # Track profile completion mission
            try:
                from gamification.views import track_profile_completed
                track_profile_completed(user)
            except ImportError:
                pass
            
            messages.success(request, 'Cập nhật hồ sơ thành công!')
            return redirect('profile_update')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CustomUserChangeForm(instance=request.user)
    
    return render(request, 'users/profile_update.html', {'form': form})


