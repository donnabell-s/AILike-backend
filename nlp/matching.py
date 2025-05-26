from data.models import User, UserMatch, UserEmbedding,Post
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity as cosine_similarity
import numpy as np
from django.core.exceptions import ObjectDoesNotExist
from transformers import pipeline
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




embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

#EMBEDDING PROCESS
def auto_profile_embedding(user_id):  # MAIN CALL
    print("AUTO- Embedding in progress")
    try:
        user = User.objects.get(id=user_id)
        user_posts = Post.objects.filter(author=user_id)
    except User.DoesNotExist:
        return {"error": "User not found."}

    # Aggregate all (topic name, sentiment_score, sentiment) from the user's posts
    all_topics = []
    for post in user_posts.prefetch_related("topics"):
        for topic in post.topics.all():
            if topic.sentiment_score is not None and topic.sentiment:
                all_topics.append((topic.name, topic.sentiment_score, topic.sentiment.lower()))

    # Build sentiment phrases from all topics
    phrased_topics = [sentiment_to_phrase(t, s, sen) for t, s, sen in all_topics]

    # Create new embedding from phrased topics
    embedding_vector = profile_embedding(all_topics)
    if embedding_vector is None:
        return {"error": "No topics found to embed."}

    # Save/update UserEmbedding
    user_embedding, created = UserEmbedding.objects.get_or_create(user=user)
    user_embedding.set_embedding(embedding_vector.tolist())
    user_embedding.save()

    return {
        "status": "success",
        "user_id": user.id,
        "username": user.username,
        "created": created,
        "all_topics": all_topics,
        "phrased_topics": phrased_topics,
        "embedding": embedding_vector.tolist()
    }



def profile_embedding(topics):
    phrases = [sentiment_to_phrase(topic, score, sentiment) for topic, score, sentiment in topics]
    vectors = [embedding_model.encode(p) for p in phrases]
    return np.mean(vectors, axis=0) if vectors else None

def sentiment_to_phrase(topic, intensity, sentiment):
    if sentiment == "positive":
        if intensity >= 0.95:
            return f"I'm absolutely passionate about {topic}."
        elif intensity >= 0.90:
            return f"I truly love {topic}."
        elif intensity >= 0.85:
            return f"I'm really into {topic}."
        elif intensity >= 0.80:
            return f"I really enjoy {topic}."
        elif intensity >= 0.75:
            return f"I definitely like {topic}."
        elif intensity >= 0.70:
            return f"I enjoy {topic}."
        elif intensity >= 0.65:
            return f"I like {topic}."
        elif intensity >= 0.60:
            return f"I’m mildly interested in {topic}."
        elif intensity >= 0.55:
            return f"I have some interest in {topic}."
        elif intensity >= 0.50:
            return f"I have mixed feelings about {topic}."
        else:
            return f"I'm neutral about {topic}."

    elif sentiment == "negative":
        if intensity >= 0.95:
            return f"I absolutely can't stand {topic}."
        elif intensity >= 0.90:
            return f"I truly hate {topic}."
        elif intensity >= 0.85:
            return f"I really dislike {topic}."
        elif intensity >= 0.80:
            return f"I'm not a fan of {topic}."
        elif intensity >= 0.75:
            return f"I definitely don't like {topic}."
        elif intensity >= 0.70:
            return f"I tend to avoid {topic}."
        elif intensity >= 0.65:
            return f"I dislike {topic}."
        elif intensity >= 0.60:
            return f"I'm mildly put off by {topic}."
        elif intensity >= 0.55:
            return f"I have some negative thoughts about {topic}."
        elif intensity >= 0.50:
            return f"I have mixed feelings about {topic}."
        else:
            return f"I'm neutral about {topic}."

    return f"I'm neutral about {topic}."  # fallback


#MATCHING PROCESS
def top_10_matches_and_save(user_id):  # MAIN CALL
    try:
        # Get this user's embedding
        user_embedding_obj = UserEmbedding.objects.get(user__id=user_id)
        user_emb = np.array(user_embedding_obj.get_embedding()).reshape(1, -1)

        similarities = []

        # Compare with all other users
        other_users = UserEmbedding.objects.exclude(user__id=user_id).select_related('user').order_by('user__id')
        for other_embedding in other_users:
            other_user = other_embedding.user
            other_emb = np.array(other_embedding.get_embedding()).reshape(1, -1)

            # Use sklearn's cosine similarity
            sim = cosine_similarity(user_emb, other_emb)[0][0]  # float between 0 and 1
            similarity_score = round(sim, 4)
            compatibility_percent = f"{round(sim * 100)}%"

            similarities.append({
                "user": other_user,
                "similarity": similarity_score,
                "compatibility": compatibility_percent
            })

        # Sort by similarity, descending
        top_matches = sorted(similarities, key=lambda x: x["similarity"], reverse=True)[:10]

        # Remove old matches and save new ones
        UserMatch.objects.filter(user_id=user_id).delete()
        for match in top_matches:
            UserMatch.objects.create(
                user_id=user_id,
                matched_user=match["user"],
                similarity_score=match["similarity"]
            )

        # Return list of top matches
        return [{
            "user_id": match["user"].id,
            "username": match["user"].username,
            "similarity": match["similarity"],
            "compatibility": match["compatibility"]
        } for match in top_matches]

    except UserEmbedding.DoesNotExist:
        return {"error": "User embedding not found."}

# ✅ Compute cosine similarity between two user IDs for testing
def cosine_similarity_between_users(user1_id, user2_id):
    try:
        user1_emb = UserEmbedding.objects.get(user__id=user1_id)
        user2_emb = UserEmbedding.objects.get(user__id=user2_id)

        emb1 = np.array(user1_emb.get_embedding()).reshape(1, -1)
        emb2 = np.array(user2_emb.get_embedding()).reshape(1, -1)

        similarity = cosine_similarity(emb1, emb2)[0][0]
        return round(similarity, 4)

    except UserEmbedding.DoesNotExist:
        return "One or both user embeddings not found."
