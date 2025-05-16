from data.models import Post, User
from django.core.exceptions import ObjectDoesNotExist
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine_similarity
import numpy as np
from transformers import pipeline
import os
sentiment_pipeline = pipeline("sentiment-analysis")  # ✅ loaded once



# Avoid using TensorFlow if unnecessary (since Keras 3 is incompatible)
os.environ["TRANSFORMERS_NO_TF"] = "1"

# ✅ Load models ONCE and reuse them (they’ll load from cache if already downloaded)
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
topic_classifier_pipeline = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
sentiment_pipeline = pipeline("sentiment-analysis")

# ✅ Topic classifier
def topic_classifier(post_id):
    try:
        post = Post.objects.get(id=post_id)
        content = post.content

        candidate_labels = [
            "Technology", "Health", "Politics", "Sports", "Entertainment",
            "Education", "Business", "Environment", "Fashion", "Travel",
            "Food", "Science", "Gaming", "Finance", "Relationships",
            "Art", "History", "Music", "Movies", "Television",
            "Literature", "Psychology", "Philosophy", "Religion", "Parenting",
            "Career", "Productivity", "Self-Improvement", "Mental Health", "Fitness",
            "Spirituality", "Pets", "Automotive", "Real Estate", "Marketing",
            "Entrepreneurship", "Economics", "Law", "Medicine", "AI",
            "Machine Learning", "Data Science", "Programming", "Cybersecurity", "Cryptocurrency",
            "Social Media", "Memes", "News", "Climate Change", "Politics (Global)",
            "Politics (Local)", "Startups", "Investing", "Photography", "Writing",
            "Poetry", "Comics", "Languages", "DIY", "Design", "Cats", "Dogs",
            "Birds", "Reptiles", "Fish", "Rodents", "Animals", "Humor", "Emotions",
            "Mental Health", "Education", "School Life", "Rants",
            "Frustration", "Student Experience", "Classmates", "Venting", "Conflict",
        ]

        result = topic_classifier_pipeline(content, candidate_labels)
        return result['labels'][:5]  # Return top predicted label

    except Post.DoesNotExist:
        return "Post not found."

# ✅ Sentiment analyzer
def sentiment_analyzer(post_id):
    try:
        post = Post.objects.get(id=post_id)
        post_text = post.content

        sentiment = sentiment_pipeline(post_text)
        return sentiment[0]['label']  # e.g., 'POSITIVE', 'NEGATIVE', etc.

    except Post.DoesNotExist:
        return "Post not found."

# ✅ Embedding function
def vector_embedding(post_id):
    try:
        post = Post.objects.get(id=post_id)
        post_text = post.content

        embedding = embedding_model.encode(post_text)
        return embedding

    except Post.DoesNotExist:
        return "Post not found."

# ✅ Convert sentiment intensity to phrase
def sentiment_to_phrase(topic, intensity):
    if intensity >= 90:
        return f"I absolutely love {topic}."
    elif intensity >= 70:
        return f"I really enjoy {topic}."
    elif intensity >= 50:
        return f"I like {topic}."
    elif intensity >= 30:
        return f"I feel okay about {topic}."
    else:
        return f"{topic} is alright."

# ✅ Cosine similarity
def cosine_similarity():
    user1 = User.objects.get(id=1)
    User2 = User.objects.get(id=2)
    try:
        embedding1 = vector_embedding(post_id1)
        embedding2 = vector_embedding(post_id2)

        embedding1 = np.array(embedding1).reshape(1, -1)
        embedding2 = np.array(embedding2).reshape(1, -1)

        similarity = sklearn_cosine_similarity(embedding1, embedding2)
        return similarity[0][0]

    except Post.DoesNotExist:
        return "One or both posts not found."
