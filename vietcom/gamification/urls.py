from django.urls import path
from . import views

app_name = 'gamification'

urlpatterns = [
    path('missions/', views.mission_list, name='mission_list'),
    path('missions/<int:mission_id>/claim/', views.claim_mission_reward, name='claim_mission_reward'),
    path('progress/', views.user_progress, name='user_progress'),
]
