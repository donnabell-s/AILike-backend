from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from data.models import Post, User
from .summarizer import summarize_bio, patch_bio


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
    