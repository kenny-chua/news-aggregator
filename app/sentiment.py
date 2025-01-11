from log import setup_logger
from sqlmodel import Session, select
from textblob import TextBlob
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
import torch

from models import TopHeadline

logger = setup_logger(__name__)

SENTIMENT_SQL = select(TopHeadline).where(TopHeadline.sentiment.is_(None))
PREFILTER_SQL = select(TopHeadline).where(TopHeadline.political_class.is_(None))
BIAS_SQL = select(TopHeadline).where(TopHeadline.bias.is_(None))


# Helper
def classify_sentiment(polarity) -> str:
    if polarity < 0:
        return "negative"
    elif polarity == 0:
        return "neutral"
    else:
        return "positive"


# Positive Negative Sentiment Analysis
def sentiment_analysis(engine) -> None:
    logger.info("Starting sentiment analysis...")
    with Session(engine) as session:
        rows = session.exec(SENTIMENT_SQL).all()
        for row in rows:
            polarity = TextBlob(row.content).sentiment.polarity
            row.sentiment = classify_sentiment(polarity)
            logger.info(
                f"Article '{row.title}' has an overall {row.sentiment} sentiment"
            )
        session.commit()
    logger.info("Sentiment analysis completed.")


# Pre-filter for political relevance
def prefilter_political_articles(engine) -> None:
    logger.info("Starting prefiltering of political articles...")
    topic_tokenizer = AutoTokenizer.from_pretrained(
        "dell-research-harvard/topic-politics"
    )
    topic_model = AutoModelForSequenceClassification.from_pretrained(
        "dell-research-harvard/topic-politics"
    )
    topic_classifier = pipeline(
        "text-classification", model=topic_model, tokenizer=topic_tokenizer
    )

    label_map = {"LABEL_0": "not_politics", "LABEL_1": "politics"}

    with Session(engine) as session:
        rows = session.exec(PREFILTER_SQL).all()
        for row in rows:
            result = topic_classifier(row.title)
            classified_label = label_map[result[0]["label"]]
            row.political_class = classified_label
            logger.info(f"Classified '{row.title}' as {classified_label}")
        session.commit()
    logger.info("Prefiltering of political articles completed.")


# Classify political bias via harshal-11/Bert-political-classification which looks at the whole text in content.
def classify_political_bias_harshal_Bert(engine) -> None:
    logger.info("Starting classification of political bias using Harshal BERT...")
    # Load the model and tokenizer
    model_name = "harshal-11/Bert-political-classification"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    labels = ["liberal", "moderate", "conservative"]

    with Session(engine) as session:
        rows = session.exec(BIAS_SQL).all()
        for row in rows:
            inputs = tokenizer(
                row.content, return_tensors="pt", truncation=True, max_length=512
            )
            with torch.no_grad():
                outputs = model(**inputs)
                probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
                predicted_label = labels[torch.argmax(probs).item()]
                confidence = probs.max().item()
            row.bias = f"{predicted_label} ({confidence:.2f})"
            logger.info(
                f"Article '{row.title}' leans {predicted_label} with confidence score of {confidence:.2f}"
            )
        session.commit()
        logger.info("Political bias classification completed.")
