from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    PRONOUN_CHOICES = [
        ('he/him', 'He/Him'),
        ('she/her', 'She/Her'),
        ('they/them', 'They/Them')
    ]

    pronouns = models.CharField(max_length=20, choices=PRONOUN_CHOICES, default='they/them', blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    
    profile_picture_blob = models.BinaryField(null=True, blank=True)
    header_picture_blob = models.BinaryField(null=True, blank=True)


class FriendRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    from_user = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    timestamp = models.DateTimeField(auto_now_add=True)


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    topics = models.JSONField(default=list, blank=True)  # Works with MySQL 5.7+ and Django 4.0+
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', through='PostLike')


class PostLike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    liked_at = models.DateTimeField(auto_now_add=True)


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')  # Sender
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    TYPE_CHOICES = [
        ('like', 'Like'),
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    topics = models.JSONField(default=list, blank=True)
    sentiment = models.CharField(max_length=20, blank=True, null=True)  # 👈 ADD THIS
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', through='PostLike')

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    topics = models.JSONField(default=list, blank=True)
    sentiment = models.CharField(max_length=20, blank=True, null=True)        # already added
    sentiment_score = models.FloatField(blank=True, null=True)                # 👈 ADD THIS
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', through='PostLike')
