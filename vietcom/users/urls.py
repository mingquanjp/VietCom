from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    
    # Existing URLs
    path('nearby/', views.nearby_users, name='nearby_users'),
    path('update-location/', views.update_location, name='update_location'),
    path('update-search-radius/', views.update_search_radius, name='update_search_radius'),
]
