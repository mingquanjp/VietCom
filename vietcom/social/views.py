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
    
    messages.success(request, 'Đã đăng bài thành công!')
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
    
    messages.success(request, 'Đã thêm bình luận!')
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
            Message.objects.create(
                sender=request.user,
                receiver=friend,
                content=content
            )
            messages.success(request, 'Đã gửi tin nhắn!')
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
