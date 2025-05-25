@api_view(["GET"])
def all_post_analysis(request):
    sentiment_pipeline = pipeline(
        "sentiment-analysis", 
        model="nlptown/bert-base-multilingual-uncased-sentiment"
    )

    result = []

    for post in Post.objects.all():
        sentiment_result = sentiment_pipeline(post.content)[0]
        sentiment = sentiment_result["label"]
        topics = topic_classifier(post.id)

      
        post.sentiment = sentiment
        post.topics = topics
        post.save()

        result.append([
            post.id,
            topics,
            sentiment
        ])

    return Response(result) 