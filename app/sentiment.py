from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from sqlalchemy.sql import and_
from sqlmodel import Session, select
from models import TopHeadline
from textblob import TextBlob

SENTIMENT_SQL = select(TopHeadline).where(TopHeadline.sentiment.is_(None))
PREFILTER_SQL = select(TopHeadline).where(TopHeadline.political_classification.is_(None))
BIAS_SQL = select(TopHeadline).where(
    and_(TopHeadline.bias.is_(None), TopHeadline.political_classification.is_not(None))
)

# Helper
def classify_sentiment(polarity):
    if polarity < 0:
        return "negative"
    elif polarity == 0:
        return "neutral"
    else:
        return "positive"

# Positive Negative Sentiment Analysis
def sentiment_analysis(engine):
    with Session(engine) as session:
        rows = session.exec(SENTIMENT_SQL).all()
        for row in rows:
            polarity = TextBlob(row.content).sentiment.polarity
            row.sentiment = classify_sentiment(polarity)
        session.commit()
        print(f"This article has an overall {sentiment} sentiment")


# Pre-filter for political relevance
def prefilter_political_articles(engine):
    topic_tokenizer = AutoTokenizer.from_pretrained("dell-research-harvard/topic-politics")
    topic_model = AutoModelForSequenceClassification.from_pretrained("dell-research-harvard/topic-politics")
    topic_classifier = pipeline("text-classification", model=topic_model, tokenizer=topic_tokenizer)

    label_map = {"LABEL_0": "not_politics", "LABEL_1": "politics"}

    with Session(engine) as session:
        rows = session.exec(PREFILTER_SQL).all()
        for row in rows:
            result = topic_classifier(row.title)
            classified_label = label_map[result[0]["label"]]
            row.political_classification = classified_label
            print(f"Classified '{row.title}' as {classified_label}")
        session.commit()


# Classify political bias
def classify_political_bias(engine):
    bias_classifier = pipeline("text-classification", model="cardiffnlp/twitter-roberta-base-sentiment")
    bias_label_map = {"LABEL_0": "Negative", "LABEL_1": "Neutral", "LABEL_2": "Positive"}

    with Session(engine) as session:
        rows = session.exec(BIAS_SQL).all()
        for row in rows:
            result = bias_classifier(row.title)
            label = bias_label_map[result[0]["label"]]
            score = result[0]["score"]
            row.bias = f"{label} ({score:.2f})"
            print(f"Article '{row.title}' leans {label} with confidence score of {score:.2f}")
