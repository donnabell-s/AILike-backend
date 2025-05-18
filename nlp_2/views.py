from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from transformers import pipeline
from nlp.matching import topic_classifier
from data.models import Post

# Load once
sentiment_pipeline = pipeline("sentiment-analysis")

@api_view(["POST"])
def analyze_post(request):
    post_id = request.data.get("post_id")
    if not post_id:
        return Response({"error": "Missing post_id"}, status=400)

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=404)

    sentiment_result = sentiment_pipeline(post.content)[0]
    sentiment = sentiment_result["label"].lower()
    score = round(sentiment_result["score"], 3)

    topics = topic_classifier(post_id)

    return Response({
        "sentiment": sentiment,
        "score": score,
        "topics": topics  
    })
