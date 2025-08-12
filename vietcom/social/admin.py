from django.contrib import admin
from django.utils.html import format_html
from .models import Post, PostLike, PostComment, FriendRequest, Friendship, Message, Group, GroupMembership

# Register your models here.

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['author', 'content_preview', 'likes_count_display', 'comments_count_display', 'created_at']
    list_filter = ['created_at']
    search_fields = ['author__username', 'author__full_name', 'content']
    ordering = ['-created_at']
    list_per_page = 25
    
    def content_preview(self, obj):
        if len(obj.content) > 50:
            return obj.content[:50] + '...'
        return obj.content
    content_preview.short_description = 'Content'
    
    def likes_count_display(self, obj):
        count = obj.likes_count
        return format_html('<span style="color: red;">❤️ {}</span>', count)
    likes_count_display.short_description = 'Likes'
    
    def comments_count_display(self, obj):
        count = obj.comments_count
        return format_html('<span style="color: blue;">💬 {}</span>', count)
    comments_count_display.short_description = 'Comments'

@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'post__content']
    ordering = ['-created_at']
    
    def post_preview(self, obj):
        return f"{obj.post.author.username}: {obj.post.content[:30]}..."
    post_preview.short_description = 'Post'

@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post_preview', 'content_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['author__username', 'content', 'post__content']
    ordering = ['-created_at']
    
    def post_preview(self, obj):
        return f"{obj.post.author.username}: {obj.post.content[:20]}..."
    post_preview.short_description = 'Post'
    
    def content_preview(self, obj):
        if len(obj.content) > 30:
            return obj.content[:30] + '...'
        return obj.content
    content_preview.short_description = 'Comment'

@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'status_display', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['sender__username', 'receiver__username', 'sender__email', 'receiver__email']
    ordering = ['-created_at']
    list_per_page = 25
    
    def status_display(self, obj):
        """Display status with colors"""
        status_colors = {
            'pending': 'orange',
            'accepted': 'green',
            'rejected': 'red',
        }
        color = status_colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">● {}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = 'Status'
    
    actions = ['accept_requests', 'reject_requests']
    
    def accept_requests(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='accepted')
        self.message_user(request, f'{updated} friend request(s) have been accepted.')
    accept_requests.short_description = "Accept selected requests"
    
    def reject_requests(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, f'{updated} friend request(s) have been rejected.')
    reject_requests.short_description = "Reject selected requests"


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ['user1', 'user2', 'since']
    search_fields = ['user1__username', 'user2__username', 'user1__email', 'user2__email']
    list_filter = ['since']
    ordering = ['-since']
    list_per_page = 25


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver_or_group', 'type_display', 'content_preview', 'created_at']
    list_filter = ['type', 'created_at']
    search_fields = ['sender__username', 'receiver__username', 'content']
    ordering = ['-created_at']
    list_per_page = 30
    
    def receiver_or_group(self, obj):
        if obj.group:
            return format_html('<strong>Group:</strong> {}', obj.group.name)
        elif obj.receiver:
            return obj.receiver.username
        return '-'
    receiver_or_group.short_description = 'To'
    
    def type_display(self, obj):
        """Display message type with icons"""
        type_icons = {
            'text': '💬',
            'image': '🖼️',
            'sticker': '😀',
            'location': '📍',
        }
        icon = type_icons.get(obj.type, '📝')
        return format_html('{} {}', icon, obj.get_type_display())
    type_display.short_description = 'Type'
    
    def content_preview(self, obj):
        """Show content preview"""
        if len(obj.content) > 50:
            return obj.content[:50] + '...'
        return obj.content
    content_preview.short_description = 'Content'


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['topic', 'creator', 'member_count', 'created_at']
    search_fields = ['topic', 'creator__username']
    list_filter = ['created_at']
    ordering = ['-created_at']
    list_per_page = 25
    
    def member_count(self, obj):
        count = obj.memberships.count()
        return format_html('<span style="font-weight: bold;">{} members</span>', count)
    member_count.short_description = 'Members'


class GroupMembershipInline(admin.TabularInline):
    model = GroupMembership
    extra = 0
    fields = ['user', 'role', 'joined_at']
    readonly_fields = ['joined_at']


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'group', 'role_display', 'joined_at']
    list_filter = ['role', 'joined_at']
    search_fields = ['user__username', 'group__name']
    ordering = ['-joined_at']
    list_per_page = 30
    
    def role_display(self, obj):
        """Display role with colors"""
        if obj.role == 'admin':
            return format_html('<span style="color: red; font-weight: bold;">👑 Admin</span>')
        return format_html('<span style="color: blue;">👤 Member</span>')
    role_display.short_description = 'Role'
    
    actions = ['make_admin', 'make_member']
    
    def make_admin(self, request, queryset):
        updated = queryset.update(role='admin')
        self.message_user(request, f'{updated} member(s) have been promoted to admin.')
    make_admin.short_description = "Promote to Admin"
    
    def make_member(self, request, queryset):
        updated = queryset.update(role='member')
        self.message_user(request, f'{updated} admin(s) have been demoted to member.')
    make_member.short_description = "Demote to Member"


# Add inline to Group admin
GroupAdmin.inlines = [GroupMembershipInline]
