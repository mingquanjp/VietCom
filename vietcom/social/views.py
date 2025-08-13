from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
import json

from .models import Post, PostLike, PostComment, Friendship, FriendRequest, Message
from users.models import User
from events.models import Event

@login_required
def wall(request):
    """Main wall/timeline view"""
    # Get friends for posts feed
    friends_ids = []
    friendships1 = Friendship.objects.filter(user1=request.user).values_list('user2_id', flat=True)
    friendships2 = Friendship.objects.filter(user2=request.user).values_list('user1_id', flat=True)
    friends_ids = list(friendships1) + list(friendships2)
    
    # Get posts from user and friends
    posts = Post.objects.filter(
        Q(author=request.user) | Q(author_id__in=friends_ids)
    ).select_related('author').prefetch_related(
        'likes', 'comments', 'comments__author'
    )
    
    # Add user_liked property to each post
    for post in posts:
        post.is_liked_by_user = post.user_liked(request.user)
    
    # Get online friends
    online_friends = User.objects.filter(
        Q(id__in=friends_ids),
        status__in=['online', 'available']
    ).exclude(id=request.user.id)[:10]
    
    # Get upcoming events
    upcoming_events = Event.objects.filter(
        Q(creator=request.user) | Q(participations__user=request.user),
        time__gte=timezone.now()
    ).distinct()[:5]
    
    # Get statistics
    friends_count = len(friends_ids)
    posts_count = Post.objects.filter(author=request.user).count()
    
    # Get notifications count (placeholder)
    notifications_count = FriendRequest.objects.filter(
        receiver=request.user, 
        status='pending'
    ).count()
    
    # Get unread messages count
    unread_messages_count = Message.objects.filter(
        receiver=request.user,
        # Add is_read field if you have it
    ).count()
    
    context = {
        'posts': posts[:20],  # Limit to 20 posts initially
        'online_friends': online_friends,
        'upcoming_events': upcoming_events,
        'friends_count': friends_count,
        'posts_count': posts_count,
        'notifications_count': notifications_count,
        'unread_messages_count': unread_messages_count,
        'notifications': [],  # Add actual notifications if needed
    }
    
    return render(request, 'wall.html', context)

@login_required
@require_http_methods(["POST"])
def create_post(request):
    """Create a new post"""
    content = request.POST.get('content', '').strip()
    image = request.FILES.get('image')
    location = request.POST.get('location', '')
    
    if not content:
        messages.error(request, 'Nội dung bài đăng không được để trống!')
        return redirect('wall')
    
    post = Post.objects.create(
        author=request.user,
        content=content,
        image=image,
        location=location
    )
    
    # Track mission progress
    try:
        from gamification.views import track_post_created
        track_post_created(request.user)
    except ImportError:
        pass
    
    return redirect('wall')

@login_required
@require_http_methods(["POST"])
def toggle_like(request, post_id):
    """Toggle like on a post"""
    post = get_object_or_404(Post, id=post_id)
    
    like, created = PostLike.objects.get_or_create(
        post=post,
        user=request.user
    )
    
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
        # Track mission progress
        try:
            from gamification.views import track_post_liked
            track_post_liked(request.user)
        except ImportError:
            pass
    
    return JsonResponse({
        'success': True,
        'liked': liked,
        'likes_count': post.likes_count
    })

@login_required
@require_http_methods(["POST"])
def add_comment(request, post_id):
    """Add a comment to a post"""
    post = get_object_or_404(Post, id=post_id)
    content = request.POST.get('content', '').strip()
    
    if not content:
        messages.error(request, 'Nội dung bình luận không được để trống!')
        return redirect('wall')
    
    PostComment.objects.create(
        post=post,
        author=request.user,
        content=content
    )
    
    # Track mission progress
    try:
        from gamification.views import track_post_commented
        track_post_commented(request.user)
    except ImportError:
        pass
    
    return redirect('wall')

@login_required
def chat_list(request):
    """List of chat conversations"""
    # Get friends for chat list
    friends_ids = []
    friendships1 = Friendship.objects.filter(user1=request.user).values_list('user2_id', flat=True)
    friendships2 = Friendship.objects.filter(user2=request.user).values_list('user1_id', flat=True)
    friends_ids = list(friendships1) + list(friendships2)
    
    friends = User.objects.filter(id__in=friends_ids)
    
    context = {
        'friends': friends
    }
    
    return render(request, 'chat_list.html', context)

@login_required
def chat_detail(request, friend_id):
    """Chat with a specific friend"""
    friend = get_object_or_404(User, id=friend_id)
    
    # Check if they are friends
    is_friend = Friendship.objects.filter(
        Q(user1=request.user, user2=friend) |
        Q(user1=friend, user2=request.user)
    ).exists()
    
    if not is_friend:
        messages.error(request, 'Bạn chỉ có thể chat với bạn bè!')
        return redirect('wall')
    
    # Handle sending message
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            message = Message.objects.create(
                sender=request.user,
                receiver=friend,
                content=content
            )
            
            # Track mission progress
            try:
                from gamification.views import track_message_sent
                track_message_sent(request.user)
            except ImportError:
                pass
            
            # If it's an AJAX request, return JSON response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': {
                        'id': message.id,
                        'sender_id': message.sender.id,
                        'sender_name': message.sender.get_display_name(),
                        'content': message.content,
                        'created_at': message.created_at.strftime('%H:%M'),
                        'is_sent': True
                    }
                })
                
            return redirect('chat_detail', friend_id=friend_id)
    
    # Get messages between users
    messages_list = Message.objects.filter(
        Q(sender=request.user, receiver=friend) |
        Q(sender=friend, receiver=request.user)
    ).order_by('created_at')
    
    context = {
        'friend': friend,
        'messages': messages_list
    }
    
    return render(request, 'chat_detail.html', context)

@login_required
def get_messages_api(request, friend_id):
    """API endpoint to get messages between current user and friend"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    friend = get_object_or_404(User, id=friend_id)
    
    # Check if they are friends
    is_friend = Friendship.objects.filter(
        Q(user1=request.user, user2=friend) |
        Q(user1=friend, user2=request.user)
    ).exists()
    
    if not is_friend:
        return JsonResponse({'error': 'Not friends'}, status=403)
    
    # Get messages since last_message_id if provided
    last_message_id = request.GET.get('last_message_id', 0)
    
    messages_query = Message.objects.filter(
        Q(sender=request.user, receiver=friend) |
        Q(sender=friend, receiver=request.user)
    )
    
    if last_message_id:
        messages_query = messages_query.filter(id__gt=last_message_id)
    
    messages_list = messages_query.order_by('created_at')
    
    # Convert messages to JSON format
    messages_data = []
    for message in messages_list:
        messages_data.append({
            'id': message.id,
            'sender_id': message.sender.id,
            'sender_name': message.sender.get_display_name(),
            'content': message.content,
            'created_at': message.created_at.strftime('%H:%M'),
            'is_sent': message.sender == request.user
        })
    
    return JsonResponse({
        'messages': messages_data,
        'friend_name': friend.get_display_name()
    })

@login_required
def search(request):
    """Search functionality"""
    query = request.GET.get('q', '').strip()
    
    if not query:
        return redirect('wall')
    
    # Search users and events
    users = User.objects.filter(
        Q(full_name__icontains=query) |
        Q(username__icontains=query) |
        Q(email__icontains=query)
    ).exclude(id=request.user.id)[:10]
    
    events = Event.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(location_desc__icontains=query)
    )[:10]
    
    context = {
        'query': query,
        'users': users,
        'events': events
    }
    
    return render(request, 'search_results.html', context)

# Placeholder views for URLs in base template
@login_required
def profile(request):
    """User profile view"""
    return render(request, 'profile.html')

@login_required
def settings(request):
    """User settings view"""
    return render(request, 'settings.html')

@login_required
def friend_requests(request):
    """Friend requests view"""
    received_requests = FriendRequest.objects.filter(
        receiver=request.user,
        status='pending'
    )
    sent_requests = FriendRequest.objects.filter(
        sender=request.user,
        status='pending'
    )
    
    context = {
        'received_requests': received_requests,
        'sent_requests': sent_requests
    }
    
    return render(request, 'friend_requests.html', context)

@login_required
def all_notifications(request):
    """All notifications view"""
    return render(request, 'notifications.html')

@login_required
@require_http_methods(["POST"])
def send_friend_request(request):
    """Send friend request"""
    try:
        data = json.loads(request.body)
        receiver_id = data.get('user_id')
        
        if not receiver_id:
            return JsonResponse({'success': False, 'message': 'User ID is required'})
        
        receiver = get_object_or_404(User, id=receiver_id)
        
        # Check if it's the same user
        if receiver == request.user:
            return JsonResponse({'success': False, 'message': 'Cannot send friend request to yourself'})
        
        # Check if they are already friends
        if are_friends(request.user, receiver):
            return JsonResponse({'success': False, 'message': 'You are already friends'})
        
        # Check if request already exists
        existing_request = FriendRequest.objects.filter(
            Q(sender=request.user, receiver=receiver) |
            Q(sender=receiver, receiver=request.user)
        ).first()
        
        if existing_request:
            if existing_request.sender == request.user:
                return JsonResponse({'success': False, 'message': 'Friend request already sent'})
            else:
                return JsonResponse({'success': False, 'message': 'This user has already sent you a friend request'})
        
        # Create friend request
        friend_request = FriendRequest.objects.create(
            sender=request.user,
            receiver=receiver
        )
        
        return JsonResponse({
            'success': True, 
            'message': f'Friend request sent to {receiver.get_display_name()}'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@require_http_methods(["POST"])
def respond_friend_request(request):
    """Accept or reject friend request"""
    try:
        data = json.loads(request.body)
        request_id = data.get('request_id')
        action = data.get('action')  # 'accept' or 'reject'
        
        if not request_id or action not in ['accept', 'reject']:
            return JsonResponse({'success': False, 'message': 'Invalid request'})
        
        friend_request = get_object_or_404(FriendRequest, id=request_id, receiver=request.user)
        
        if action == 'accept':
            # Create friendship
            Friendship.objects.create(
                user1=friend_request.sender,
                user2=friend_request.receiver
            )
            friend_request.status = 'accepted'
            friend_request.save()
            
            # Track mission progress for both users
            try:
                from gamification.views import track_friend_added
                track_friend_added(friend_request.sender)
                track_friend_added(friend_request.receiver)
            except ImportError:
                pass
            
            message = f'You are now friends with {friend_request.sender.get_display_name()}'
        else:
            friend_request.status = 'rejected'
            friend_request.save()
            message = 'Friend request rejected'
        
        return JsonResponse({'success': True, 'message': message})
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@require_http_methods(["POST"])
def cancel_friend_request(request):
    """Cancel sent friend request"""
    try:
        data = json.loads(request.body)
        request_id = data.get('request_id')
        
        if not request_id:
            return JsonResponse({'success': False, 'message': 'Request ID is required'})
        
        friend_request = get_object_or_404(FriendRequest, id=request_id, sender=request.user)
        friend_request.delete()
        
        return JsonResponse({'success': True, 'message': 'Friend request cancelled'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

def are_friends(user1, user2):
    """Check if two users are friends"""
    return Friendship.objects.filter(
        Q(user1=user1, user2=user2) | Q(user1=user2, user2=user1)
    ).exists()

def get_friend_request_status(sender, receiver):
    """Get friend request status between two users"""
    request = FriendRequest.objects.filter(
        Q(sender=sender, receiver=receiver) | Q(sender=receiver, receiver=sender)
    ).first()
    
    if not request:
        return None
    
    return {
        'id': request.id,
        'status': request.status,
        'is_sender': request.sender == sender
    }

@login_required
def edit_post(request, post_id):
    """Edit an existing post"""
    post = get_object_or_404(Post, id=post_id)

    # Only allow editing own posts
    if post.author != request.user:
        messages.error(request, 'Bạn không có quyền chỉnh sửa bài đăng này!')
        return redirect('wall')

    if request.method == "POST":
        content = request.POST.get('content', '').strip()
        image = request.FILES.get('image')
        location = request.POST.get('location', '')

        if not content:
            messages.error(request, 'Nội dung bài đăng không được để trống!')
            return render(request, 'edit_post.html', {'post': post})

        post.content = content
        if image:
            post.image = image
        post.location = location
        post.save()

        return redirect('wall')

    return render(request, 'edit_post.html', {'post': post})

@login_required
def delete_post(request, post_id):
    """Delete a post"""
    post = get_object_or_404(Post, id=post_id)

    # Only allow deleting own posts
    if post.author != request.user:
        messages.error(request, 'Bạn không có quyền xóa bài đăng này!')
        return redirect('wall')

    if request.method == "POST":
        post.delete()
        return redirect('wall')

    return render(request, 'delete_post_confirm.html', {'post': post})