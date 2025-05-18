from data.models import User, UserMatch, UserEmbedding
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine_similarity
import numpy as np

# Load embedding model once
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# ✅ Convert sentiment score into descriptive phrase
def sentiment_to_phrase(topic, intensity):
    if intensity >= 0.90:
        return f"I absolutely love {topic}."
    elif intensity >= 0.70:
        return f"I really enjoy {topic}."
    elif intensity >= 0.50:
        return f"I like {topic}."
    elif intensity >= 0.30:
        return f"I feel okay about {topic}."
    else:
        return f"{topic} is alright."

# ✅ Convert a user's topic-sentiment dictionary into a vector
def user_profile_embedding(user_topics: dict):
    phrases = [sentiment_to_phrase(topic, score) for topic, score in user_topics.items()]
    vectors = [embedding_model.encode(p) for p in phrases]
    return np.mean(vectors, axis=0)  # Averaged user vector

# ✅ Compute cosine similarity between two user IDs (for debug/testing)
def cosine_similarity(user1_id, user2_id):
    try:
        user1 = User.objects.get(id=user1_id)
        user2 = User.objects.get(id=user2_id)

        profile1 = user1.profile_data  # Replace with actual data source
        profile2 = user2.profile_data

        emb1 = user_profile_embedding(profile1).reshape(1, -1)
        emb2 = user_profile_embedding(profile2).reshape(1, -1)

        similarity = sklearn_cosine_similarity(emb1, emb2)
        return round(similarity[0][0], 4)

    except User.DoesNotExist:
        return "One or both users not found."

# ✅ Compute and store top 10 matches in UserMatch table
def top_10_matches_and_save(user_id):
    try:
        # Get this user's embedding
        user_embedding_obj = UserEmbedding.objects.get(user__id=user_id)
        user_emb = np.array(user_embedding_obj.get_embedding()).reshape(1, -1)

        similarities = []

        # Compare to all other users
        for other_embedding in UserEmbedding.objects.exclude(user__id=user_id).select_related('user').order_by('user__id'):
            other_user = other_embedding.user
            other_emb = np.array(other_embedding.get_embedding()).reshape(1, -1)
            sim = sklearn_cosine_similarity(user_emb, other_emb)[0][0]

            similarities.append({
                "user": other_user,
                "similarity": round(sim, 4)
            })

        # Sort and get top 10
        top_matches = sorted(similarities, key=lambda x: x["similarity"], reverse=True)[:10]

        # Clear existing matches first
        UserMatch.objects.filter(user_id=user_id).delete()

        # Save each top match
        for match in top_matches:
            UserMatch.objects.create(
                user_id=user_id,
                matched_user=match["user"],
                similarity_score=match["similarity"]
            )

        return [{
            "user_id": match["user"].id,
            "username": match["user"].username,
            "similarity": match["similarity"]
        } for match in top_matches]

    except UserEmbedding.DoesNotExist:
        return "User embedding not found."
