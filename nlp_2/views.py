from transformers import pipeline
from nlp.matching import topic_classifier
from data.models import Topic
import re

def preprocess_tweet(text):
    text = text.lower()
    text = re.sub(r'https?:\/\/\S+', 'http', text)
    text = re.sub(r'@\w+', '@user', text)
    text = re.sub(r'#', '', text)
    return text

# Cardiff sentiment model
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest"
)

CARDIFF_LABEL_MAP = {
    "LABEL_0": "negative",
    "LABEL_1": "neutral",
    "LABEL_2": "positive"
}


def analyze_post_content(post):
    topic_results = topic_classifier(post.content, threshold=0.75)

    if topic_results == "Post not found." or not topic_results:
        return  # exit early if no valid topics

    topic_instances = []

    for name, topic_score in topic_results[:3]:
        # Preprocess + sentiment
        sentence = preprocess_tweet(f"{post.content} This is about {name}.")
        sentiment_result = sentiment_pipeline(sentence)[0]
        sentiment_raw = sentiment_result["label"]
        sentiment_score = round(sentiment_result["score"], 3)


        final_score = round(topic_score * sentiment_score, 3)

        topic_obj = Topic.objects.create(
            name=name,
            sentiment=sentiment_raw,
            sentiment_score=final_score
        )

        topic_instances.append(topic_obj)
        print(f"Topics created for post {post.id}: {[t.name for t in topic_instances]}")

    post.topics.set(topic_instances)
    post.save()
