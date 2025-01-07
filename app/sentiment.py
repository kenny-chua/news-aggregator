from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from sqlmodel import Session, select
from models import TopHeadline
from textblob import TextBlob

sql_stmt = select(TopHeadline).where(TopHeadline.sentiment.is_(None))


def sentiment_analysis(engine):
    with Session(engine) as session:
        rows = session.exec(sql_stmt).all()
        for row in rows:
            analysis = TextBlob(row.content)
            polarity = analysis.sentiment.polarity

            if polarity < 0:
                sentiment = "negative"
            elif polarity == 0:
                sentiment = "neutral"
            else:
                sentiment = "positive"

            row.sentiment = sentiment
        session.commit()


# Pre-filter for political relevance
def prefilter_political_articles(headlines):
    topic_tokenizer = AutoTokenizer.from_pretrained("dell-research-harvard/topic-politics")
    topic_model = AutoModelForSequenceClassification.from_pretrained("dell-research-harvard/topic-politics")
    topic_classifier = pipeline("text-classification", model=topic_model, tokenizer=topic_tokenizer)

    label_map = {"LABEL_0": "not_politics", "LABEL_1": "politics"}
    political_articles = []

    for headline in headlines:
        result = topic_classifier(headline)
        label = label_map[result[0]["label"]]
        if label == "politics":
            political_articles.append(headline)

    return political_articles


# Classify political bias
def classify_political_bias(political_articles):
    sentiment_classifier = pipeline("text-classification", model="cardiffnlp/twitter-roberta-base-sentiment")
    sentiment_label_map = {"LABEL_0": "Negative", "LABEL_1": "Neutral", "LABEL_2": "Positive"}
    classified_bias = {}

    for article in political_articles:
        result = sentiment_classifier(article)
        label = sentiment_label_map[result[0]["label"]]
        score = result[0]["score"]
        classified_bias[article] = {"bias": label, "confidence": score}

    return classified_bias
