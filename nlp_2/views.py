from rest_framework.decorators import api_view
from rest_framework.response import Response


# @api_view(["GET"])
# def all_post_analysis(request):
#     from transformers import pipeline
#     from nlp.matching import topic_classifier
#     from data.models import Post

#     sentiment_pipeline = pipeline(
#         "sentiment-analysis",
#         model="distilbert-base-uncased-finetuned-sst-2-english"
#     )

#     result = []

#     for post in Post.objects.all():
#         sentiment_result = sentiment_pipeline(post.content)[0]
#         sentiment = sentiment_result["label"].lower()  # e.g. 'positive'
#         score = round(sentiment_result["score"], 3)
#         topics = topic_classifier(post.id)

#         #save sa datbase
#         post.sentiment = sentiment
#         post.sentiment_score = score
#         post.topics = topics
#         post.save()

#         result.append([
#             post.id,
#             topics,
#             sentiment,
#             score
#         ])

#     return Response(result)




# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from transformers import pipeline
# from nlp.matching import topic_classifier  # this returns a list of topic names
# from data.models import Post, Topic


# @api_view(["GET"])
# def all_post_analysis(request):
#     sentiment_pipeline = pipeline(
#         "sentiment-analysis",
#         model="distilbert-base-uncased-finetuned-sst-2-english"
#     )

#     result = []

#     for post in Post.objects.all():
#         # Run sentiment analysis on full post content
#         sentiment_result = sentiment_pipeline(post.content)[0]
#         sentiment = sentiment_result["label"].lower()
#         score = round(sentiment_result["score"], 3)

#         # Get topic names (limit to 5)
#         topic_names = topic_classifier(post.id)[:5]

#         topic_instances = []
#         for name in topic_names:
#             # Run sentiment on the individual topic name (or use post's sentiment if you prefer)
#             topic_sentiment = sentiment_pipeline(name)[0]
#             topic_obj, _ = Topic.objects.get_or_create(
#                 name=name,
#                 defaults={
#                     "sentiment": topic_sentiment["label"].lower(),
#                     "sentiment_score": round(topic_sentiment["score"], 3)
#                 }
#             )

#             # Optional: update sentiment if it changed
#             if topic_obj.sentiment is None or topic_obj.sentiment_score is None:
#                 topic_obj.sentiment = topic_sentiment["label"].lower()
#                 topic_obj.sentiment_score = round(topic_sentiment["score"], 3)
#                 topic_obj.save()

#             topic_instances.append(topic_obj)

#         # Assign topics to the post
#         post.topics.set(topic_instances)
#         post.save()

#         result.append({
#             "post_id": post.id,
#             "topics": [t.name for t in topic_instances],
#             "sentiment": sentiment,
#             "sentiment_score": score
#         })

#     return Response(result)


def analyze_post_content(post):
    from transformers import pipeline
    from nlp.matching import topic_classifier
    from data.models import Topic

    sentiment_pipeline = pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english"
    )

    # Run sentiment on post content
    sentiment_result = sentiment_pipeline(post.content)[0]
    sentiment = sentiment_result["label"].lower()
    score = round(sentiment_result["score"], 3)

    # Generate topics
    topic_names = topic_classifier(post.id)[:5]

    topic_instances = []
    for name in topic_names:
        topic_sentiment = sentiment_pipeline(name)[0]
        topic_obj, _ = Topic.objects.get_or_create(
            name=name,
            defaults={
                "sentiment": topic_sentiment["label"].lower(),
                "sentiment_score": round(topic_sentiment["score"], 3)
            }
        )

        if topic_obj.sentiment is None or topic_obj.sentiment_score is None:
            topic_obj.sentiment = topic_sentiment["label"].lower()
            topic_obj.sentiment_score = round(topic_sentiment["score"], 3)
            topic_obj.save()

        topic_instances.append(topic_obj)

    # Link topics to post
    post.topics.set(topic_instances)
    post.save()


