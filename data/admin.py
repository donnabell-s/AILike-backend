from django.contrib import admin
from .models import User, Post, FriendRequest, PostLike, Notification
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username','bio', 'email', 'first_name', 'last_name', 'pronouns', 'date_of_birth', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'email')
    ordering = ('username',)

admin.site.register(User, CustomUserAdmin)

admin.site.register(Post)
admin.site.register(FriendRequest)
admin.site.register(PostLike)
admin.site.register(Notification)
