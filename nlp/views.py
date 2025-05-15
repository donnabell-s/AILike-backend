from django.shortcuts import render
from django.views import View
from grpc import Status
from rest_framework.views import APIView
from rest_framework.response import Response
from data.models import Post, User
from .summarizer import summarize_bio, patch_bio
from .matching import topic_classifier
from rest_framework import status


# Create your views here.
    
class TestSummarizerView(APIView):

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except user.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        summary = patch_bio(user_id)
        return Response({
            "username": user.username,
            "summary": summary
        }) 
class TestTopicClassifier(APIView):
    def get(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
            content = post.content

            topic = topic_classifier(post_id)
            # sentiment = sentiment_analyzer(post_id)

            return Response({
                "post_id": post_id,
                "content": content,
                "topic": topic,
                # "sentiment": sentiment,
            }, status=status.HTTP_200_OK)

        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)