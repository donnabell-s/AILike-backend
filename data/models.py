from django.db import models
from django.contrib.auth.models import AbstractUser
import json


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

class UserEmbedding(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='embedding')
    embedding_json = models.TextField(help_text="JSON-encoded embedding vector")

    def set_embedding(self, vector):
        """Store embedding vector as JSON string."""
        self.embedding_json = json.dumps(vector)
        self.save()

    def get_embedding(self):
        """Return embedding vector as Python list."""
        return json.loads(self.embedding_json)

    def __str__(self):
        return f"Embedding for {self.user.username}"


class UserMatch(models.Model):
    user = models.ForeignKey(User, related_name='matches', on_delete=models.CASCADE)
    matched_user = models.ForeignKey(User, related_name='matched_by', on_delete=models.CASCADE)
    similarity_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'matched_user')
        ordering = ['-similarity_score']

    def __str__(self):
        return f"{self.user.username} matched with {self.matched_user.username} ({self.similarity_score:.3f})"