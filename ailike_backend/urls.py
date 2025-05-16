"""
URL configuration for ailike_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from data.views import UserDetailView, UserListView, CurrentUserView, UserProfilePictureView, UserHeaderPictureView ,RegisterView, FriendRequestView, FriendsListView, PostListCreateView, LikePostView, NotificationListView
from nlp.views import TestSummarizerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/users/', UserListView.as_view(), name='user-list'), 
    path('api/users/<int:pk>/', UserDetailView.as_view(), name='user-detail-id'),  
    path('api/user/', CurrentUserView.as_view(), name='current-user'),
    path('api/users/<int:pk>/profile_picture/', UserProfilePictureView.as_view(), name='user-profile-picture'),
    path('api/users/<int:pk>/header_picture/', UserHeaderPictureView.as_view(), name='user-header-picture'),
    path('api/friends/requests/', FriendRequestView.as_view(), name='friend-request'),
    path('api/friends/requests/<int:pk>/', FriendRequestView.as_view(), name='friend-request-respond'),
    path('api/friends/', FriendsListView.as_view(), name='friend-list'),
    path('api/posts/', PostListCreateView.as_view(), name='post-list-create'),
    path('api/posts/<int:post_id>/like/', LikePostView.as_view(), name='like-post'),
    path('api/notifications/', NotificationListView.as_view(), name='notification-list'),
    path('api/notifications/<int:pk>/', NotificationListView.as_view(), name='notification-update-delete'),
    path('api/notifications/<int:pk>/', NotificationListView.as_view(), name='notification-update'),

    path('api/summarize/<int:user_id>', TestSummarizerView.as_view(), name='test-summarizer'),
    path('api/nlp/', include('nlp_2.urls')),
]
INSTALLED_APPS = [
    'nlp',
]