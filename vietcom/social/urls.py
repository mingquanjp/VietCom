from django.urls import path
from . import views

urlpatterns = [
    # Wall/Timeline
    path('', views.wall, name='wall'),
    path('create-post/', views.create_post, name='create_post'),
    path('toggle-like/<int:post_id>/', views.toggle_like, name='toggle_like'),
    path('add-comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('edit-post/<int:post_id>/', views.edit_post, name='edit_post'),
    path('delete-post/<int:post_id>/', views.delete_post, name='delete_post'),
    
    # Chat
    path('chat/', views.chat_list, name='chat_list'),
    path('chat/<int:friend_id>/', views.chat_detail, name='chat_detail'),
    path('api/chat/<int:friend_id>/messages/', views.get_messages_api, name='get_messages_api'),
    
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
    path('cancel-friend-request-by-user/', views.cancel_friend_request_by_user, name='cancel_friend_request_by_user'),
    
    # Call APIs
    path('call/initiate/', views.initiate_call, name='initiate_call'),
    path('call/answer/', views.answer_call, name='answer_call'),
    path('call/reject/', views.reject_call, name='reject_call'),
    path('call/end/', views.end_call, name='end_call'),
    path('call/<int:call_id>/status/', views.get_call_status, name='get_call_status'),
    path('call/check-incoming/', views.check_incoming_calls, name='check_incoming_calls'),
]
