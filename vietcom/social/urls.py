from django.urls import path
from . import views

urlpatterns = [
    # Wall/Timeline
    path('', views.wall, name='wall'),
    path('create-post/', views.create_post, name='create_post'),
    path('toggle-like/<int:post_id>/', views.toggle_like, name='toggle_like'),
    path('add-comment/<int:post_id>/', views.add_comment, name='add_comment'),
    
    # Chat
    path('chat/', views.chat_list, name='chat_list'),
    path('chat/<int:friend_id>/', views.chat_detail, name='chat_detail'),
    
    # Search
    path('search/', views.search, name='search'),
    
    # Profile & Settings
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings, name='settings'),
    path('friend-requests/', views.friend_requests, name='friend_requests'),
    path('notifications/', views.all_notifications, name='all_notifications'),
    
    # Friend Request APIs
    path('send-friend-request/', views.send_friend_request, name='send_friend_request'),
    path('respond-friend-request/', views.respond_friend_request, name='respond_friend_request'),
    path('cancel-friend-request/', views.cancel_friend_request, name='cancel_friend_request'),
]
