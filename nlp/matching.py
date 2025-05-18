from data.models import User, UserMatch, UserEmbedding,Post
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity as cosine_similarity
import numpy as np

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

#EMBEDDING PROCESS
def auto_profile_embedding(user_id): #MAIN CALL
    try:
        user = User.objects.get(id=user_id)
        user_posts = Post.objects.filter(author=user_id)
    except User.DoesNotExist:
        return {"error": "User not found."}

    # Aggregate all topics from all posts
    all_topics = []
    for post in user_posts:
        all_topics.extend(post.topics)  # topics is a list of [topic, score]

    # Create new embedding from combined topics cuz unfortunately cant embed on existinf vectors
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
        "embedding": embedding_vector.tolist()
    }


def profile_embedding(topics):
    #process: get 2d array of topics and scores then reformat to sentences for embedding
    #vector is the embedded date then save to Userembedding model of that user
    phrases = [sentiment_to_phrase(topic, score) for topic, score in topics]
    vectors = [embedding_model.encode(p) for p in phrases]
    return np.mean(vectors, axis=0) if vectors else None

def sentiment_to_phrase(topic, intensity):
    if intensity >= 0.95:
        return f"I absolutely love {topic}."
    elif intensity >= 0.80:
        return f"I really enjoy {topic}."
    elif intensity >= 0.60:
        return f"I like {topic}."
    elif intensity >= 0.45:
        return f"I'm neutral about {topic}."
    elif intensity >= 0.30:
        return f"I'm indifferent to {topic}."
    elif intensity >= 0.15:
        return f"I really dislike {topic}."
    else:
        return f"I loathe {topic}."
    
 


#MATCHING PROCESS
def top_10_matches_and_save(user_id): #MAIN CALL
    try:
        # Get this user's embedding
        user_embedding_obj = UserEmbedding.objects.get(user__id=user_id)
        user_emb = np.array(user_embedding_obj.get_embedding()).reshape(1, -1)

        similarities = []

        # Compare to all other users
        for other_embedding in UserEmbedding.objects.exclude(user__id=user_id).select_related('user').order_by('user__id'):
            other_user = other_embedding.user
            other_emb = np.array(other_embedding.get_embedding()).reshape(1, -1)
            sim = cosine_similarity(user_emb, other_emb)[0][0]

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

# ✅ Compute cosine similarity between two user IDs
def cosine_similarity(user1_id, user2_id):
    try:
        user1_emb = UserEmbedding.objects.get(user__id=user1_id)
        user2_emb = UserEmbedding.objects.get(user__id=user2_id)

        emb1 = np.array(user1_emb.get_embedding()).reshape(1, -1)
        emb2 = np.array(user2_emb.get_embedding()).reshape(1, -1)

        similarity = cosine_similarity(emb1, emb2)[0][0]
        return round(similarity, 4)

    except UserEmbedding.DoesNotExist:
        return "One or both user embeddings not found."

