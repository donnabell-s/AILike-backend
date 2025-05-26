import os
import requests
from data.models import Post, User
from django.core.exceptions import ObjectDoesNotExist
import re

CHUTES_API_KEY = os.getenv("CHUTES_API_KEY")  

CHUTES_API_URL = "https://llm.chutes.ai/v1/chat/completions"
MODEL_ID = "deepseek-ai/DeepSeek-V3-0324"  


def patch_bio(user_id):
    """Helper function to summarize the bio and update the user's bio field."""
    try:
        summarized_bio = summarize_bio(user_id)
        user = User.objects.get(id=user_id)
        user.bio = summarized_bio
        user.save() 
        
        return summarized_bio 

    except ObjectDoesNotExist:
        raise Exception(f"User with ID {user_id} does not exist.")
    except Exception as e:
        raise Exception(f"Error while updating bio for user {user_id}: {e}")
    

def summarize_bio(user_id):
    """Send concatenated user posts to Chutes API for summarization."""

    user_posts = Post.objects.filter(author__id=user_id)
    user = User.objects.get(id=user_id)
    pronouns = user.pronouns
    bday = user.date_of_birth
    full_name = f"{user.first_name} {user.last_name}"
    posts_content = "\n".join([post.content for post in user_posts])
    
    prompt = (
      f"""Based on the following user-generated posts, write a witty, slightly roasty, first-person social media app bio under 30 words.
        Highlight what they like, their personality traits, and any funny quirks or contradictions — but do **not invent** anything that isn't clearly stated in the posts or biography.

        Use only the following verifiable information:
        - Pronouns: {pronouns}
        - Birthday: {bday}
        - Full name: {full_name}
        - Posts: {posts_content}

        You may include the user's name **only if it fits naturally into the tone and flow** of the bio — avoid forced or robotic use.

        Integrate pronouns naturally into the sentence structure. Keep the tone playful, insightful, and accurate. Output only the final bio text."""

    )
    # print(f"Generated Prompt for Summarization: \n{prompt}\n")


    headers = {
        "Authorization": f"Bearer {CHUTES_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL_ID,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False,
        "max_tokens": 1024,
        "temperature": 0.7
    }

    response = requests.post(CHUTES_API_URL, headers=headers, json=payload)

    if response.status_code == 200:
            raw_bio = response.json()["choices"][0]["message"]["content"]
            
            cleaned_bio = re.sub(r"[^a-zA-Z0-9\s\.\,\!\?\'\-]", '', raw_bio)


            return cleaned_bio
    else:
        raise Exception(f"Chutes API Error: {response.status_code}, {response.text}")

    