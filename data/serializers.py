from rest_framework import serializers
from .models import User, FriendRequest, Post, PostLike, Notification


class UserSerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()
    friend_count = serializers.SerializerMethodField()
    post_like_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'pronouns', 'date_of_birth', 'bio', 'post_count', 'friend_count', 'post_like_count']

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


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'pronouns', 'date_of_birth']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            pronouns=validated_data.get('pronouns', ''),
            date_of_birth=validated_data.get('date_of_birth', None),
        )
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
