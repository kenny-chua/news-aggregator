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
