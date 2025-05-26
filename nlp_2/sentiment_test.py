# from transformers import pipeline

# sentiment_pipeline = pipeline(
#     "sentiment-analysis",
#     model="cardiffnlp/twitter-roberta-base-sentiment-latest"
# )

# CARDIFF_LABEL_MAP = {
#     "LABEL_0": "negative",
#     "LABEL_1": "neutral",
#     "LABEL_2": "positive"
# }

# examples = [
#     "I love fries!",
#     "I hate fries!",
#     "Fries are okay.",
#     "I am so happy about this!",
#     "This is terrible."
# ]

# for text in examples:
#     result = sentiment_pipeline(text)[0]
#     label = CARDIFF_LABEL_MAP.get(result["label"], "neutral")
#     print(f"Text: {text}\nSentiment: {label}, Score: {result['score']}\n")


from transformers import pipeline

pipeline_model = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
print(pipeline_model("I love this!"))
print(pipeline_model("I hate this!"))
