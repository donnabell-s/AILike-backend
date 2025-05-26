from django.shortcuts import render
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from data.models import Post, User,UserEmbedding
from .matching import auto_profile_embedding, cosine_similarity,top_10_matches_and_save
from rest_framework import status



# Create your views here.
class TestEmbeddingView(APIView):
    def get(self, request, user_id):
        try:
            user_embedding = UserEmbedding.objects.get(user__id=user_id)
            result = auto_profile_embedding(user_id)
        except UserEmbedding.DoesNotExist:
            return Response({"error": "User embedding not found"}, status=404)

        return Response({
            "user_id": user_embedding.user.id,
            "username": user_embedding.user.username,
            "phrases": result["phrased_topics"],
            "embedding": user_embedding.get_embedding()  # Already a list
        }, status=200)
    
class TestCosineSimilarityView(APIView):
    def get(self, request, user1_id, user2_id):
        try:
            user1_embedding = UserEmbedding.objects.get(user__id=user1_id)
            user2_embedding = UserEmbedding.objects.get(user__id=user2_id)
        except UserEmbedding.DoesNotExist:
            return Response({"error": "One or both user embeddings not found."}, status=404)

        similarity = cosine_similarity(user1_id, user2_id)

        return Response({
            "user1": user1_embedding.user.username,
            "user2": user2_embedding.user.username,
            "similarity": similarity
        }, status=200)

class TestGetMatches(APIView):
    def get(self, request, user_id):
        try:
            # Ensure the user embedding exists first
            if not UserEmbedding.objects.filter(user__id=user_id).exists():
                return Response({"error": "User embedding not found."}, status=404)

            # Compute and save matches
            matches = top_10_matches_and_save(user_id)

            return Response({
                "user_id": user_id,
                "matches": matches
            }, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=500)