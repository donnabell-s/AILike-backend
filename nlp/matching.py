from data.models import Post, User
from django.core.exceptions import ObjectDoesNotExist
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine_similarity
from transformers import pipeline
import numpy as np
import os


os.environ["TRANSFORMERS_NO_TF"] = "1"

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
sentiment_pipeline = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")
topic_pipeline = pipeline("zero-shot-classification", model="MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli")

topic_labels = [
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

def topic_classifier(post_id, threshold=0.5):
    try:
        post = Post.objects.get(id=post_id)
        content = post.content

        result = topic_pipeline(content, candidate_labels=topic_labels, multi_label=True)

        filtered_topics = [
            label for label, score in zip(result["labels"], result["scores"]) if score >= threshold
        ]

        return filtered_topics if filtered_topics else ["No strong topic match"]

    except Post.DoesNotExist:
        return "Post not found."

def sentiment_analyzer(post_id):
    try:
        post = Post.objects.get(id=post_id)
        sentiment = sentiment_pipeline(post.content)
        return sentiment[0]['label']
    except Post.DoesNotExist:
        return "Post not found."


def vector_embedding(post_id):
    try:
        post = Post.objects.get(id=post_id)
        return embedding_model.encode(post.content)
    except Post.DoesNotExist:
        return "Post not found."


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



def cosine_similarity():
    try:
        embedding1 = vector_embedding(1)
        embedding2 = vector_embedding(2)
        similarity = sklearn_cosine_similarity(
            np.array(embedding1).reshape(1, -1),
            np.array(embedding2).reshape(1, -1)
        )
        return similarity[0][0]
    except:
        return "One or both posts not found."