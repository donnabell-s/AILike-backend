@api_view(["GET"])
def all_post_analysis(request):
    from transformers import pipeline
    from nlp.matching import topic_classifier
    from data.models import Post

    sentiment_pipeline = pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english"
    )

    result = []

    for post in Post.objects.all():
        sentiment_result = sentiment_pipeline(post.content)[0]
        sentiment = sentiment_result["label"].lower()  # e.g. 'positive'
        score = round(sentiment_result["score"], 3)
        topics = topic_classifier(post.id)

        #save sa datbase
        post.sentiment = sentiment
        post.sentiment_score = score
        post.topics = topics
        post.save()

        result.append([
            post.id,
            topics,
            sentiment,
            score
        ])

    return Response(result)
