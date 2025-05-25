@api_view(["GET"])
def all_post_analysis(request):
    from transformers import pipeline

    sentiment_pipeline = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")
    from nlp.matching import topic_classifier
    from data.models import Post

    result = []

    for post in Post.objects.all():
        sentiment_result = sentiment_pipeline(post.content)[0]
        sentiment = sentiment_result["label"]
        topics = topic_classifier(post.id)

        result.append([
            post.id,
            topics,
            sentiment
        ])

    return Response(result)
