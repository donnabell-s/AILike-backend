from rest_framework import serializers
from .models import User, FriendRequest, Post, PostLike, Notification
from django.core.files.base import ContentFile
from django.core.files import File
from django.conf import settings
import os


class UserSerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()
    friend_count = serializers.SerializerMethodField()
    post_like_count = serializers.SerializerMethodField()

    profile_picture = serializers.ImageField(write_only=True, required=False)
    header_picture = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'pronouns', 'first_name', 'last_name', 'date_of_birth', 'bio', 'profile_picture', 'header_picture', 'post_count', 'friend_count', 'post_like_count', 'is_staff']

    def get_post_count(self, obj):
        return obj.posts.count()

    def get_friend_count(self, obj):
        from django.db.models import Q
        accepted_friends = FriendRequest.objects.filter(
            status='accepted'
        ).filter(
            Q(from_user=obj) | Q(to_user=obj)
        )
        return accepted_friends.count()
    
    def get_post_like_count(self, obj):
        return PostLike.objects.filter(post__author=obj).count()
    
    def get_profile_picture_url(self, obj):
        return f'/api/users/{obj.id}/profile_picture/' if obj.profile_picture_blob else None

    def get_header_picture_url(self, obj):
        return f'/api/users/{obj.id}/header_picture/' if obj.header_picture_blob else None
    
    def update(self, instance, validated_data):
        if 'profile_picture' in validated_data:
            picture = validated_data.pop('profile_picture')
            instance.profile_picture_blob = picture.read()

        if 'header_picture' in validated_data:
            header = validated_data.pop('header_picture')
            instance.header_picture_blob = header.read()

        # Save after assigning blobs
        instance.save()

        return super().update(instance, validated_data)



# class RegisterSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'pronouns', 'date_of_birth']

#     def create(self, validated_data):
#         user = User.objects.create_user(
#             username=validated_data['username'],
#             email=validated_data.get('email'),
#             password=validated_data['password'],
#             first_name=validated_data.get('first_name', ''),
#             last_name=validated_data.get('last_name', ''),
#             pronouns=validated_data.get('pronouns', ''),
#             date_of_birth=validated_data.get('date_of_birth', None),
#         )
#         return user




class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'pronouns', 'date_of_birth', 'profile_picture_blob', 'header_picture_blob', 'bio']



    def create(self, validated_data):

        # Create the user
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            pronouns=validated_data.get('pronouns', ''),
            date_of_birth=validated_data.get('date_of_birth', None),
            bio=validated_data.get('bio', "Welcome to my profile! Let's be friends :)"),
        )

        # Set default profile and header pictures if not provided
        if 'profile_picture_blob' not in validated_data:
            default_profile_picture_path = os.path.join(settings.MEDIA_ROOT, 'profile_picture.png')
            with open(default_profile_picture_path, 'rb') as f:
                user.profile_picture_blob = f.read()

        if 'header_picture_blob' not in validated_data:
            default_header_picture_path = os.path.join(settings.MEDIA_ROOT, 'header_picture.png')
            with open(default_header_picture_path, 'rb') as f:
                user.header_picture_blob = f.read()


        user.save()  # Save the user instance with the new pictures
        return user



class FriendRequestSerializer(serializers.ModelSerializer):
    from_user = UserSerializer(read_only=True)
    to_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = FriendRequest
        fields = ['id', 'from_user', 'to_user', 'status', 'timestamp']


class PostLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostLike
        fields = ['id', 'post', 'user', 'liked_at']


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'topics', 'created_at', 'likes']
        read_only_fields = ['author', 'likes']


class NotificationSerializer(serializers.ModelSerializer):
    from_user_id = serializers.IntegerField(source='from_user.id', read_only=True)
    from_user_username = serializers.CharField(source='from_user.username', read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'user', 'from_user_id', 'from_user_username', 'message', 'is_read', 'created_at', 'type']
