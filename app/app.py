import os
from typing import List
from urllib.parse import urlencode
import requests
from sqlmodel import SQLModel, create_engine, Session
from models import RawHeadline, TopHeadline
from processor import get_article_text_and_insert
from dotenv import load_dotenv
from sentiment import sentiment_analysis

load_dotenv()

NEWSAPI_TOPHEADLINES = "https://newsapi.org/v2/top-headlines"

def get_top_headlines(country="us", language="en") -> List[RawHeadline]:
    api_key = os.getenv("NEWSAPI_API_KEY")
    top_headlines_params = {"country": country, "language": language, "apiKey": api_key}
    endpoint = f"{NEWSAPI_TOPHEADLINES}?{urlencode(top_headlines_params)}"
    response = requests.get(endpoint)
    json_data = response.json()
    articles = json_data.get("articles", [])

    raw_headlines = [
        RawHeadline(
            source_id=article["source"].get("id"),
            source_name=article["source"].get("name"),
            author=article.get("author"),
            title=article.get("title"),
            description=article.get("description"),
            url=article.get("url"),
            url_to_image=article.get("urlToImage"),
            published_at=article.get("publishedAt"),
        )
        for article in articles  if article.get("url")
        if article.get("url") and "removed.com" not in article.get("url") and "washingtonpost" not in article.get("url")
    ]
    return raw_headlines


sqlite_file_name = "newslist.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url)


def create_db_and_tables(engine):
    SQLModel.metadata.create_all(engine)


def create_db_with_raw_headlines(engine, raw_headlines: List[RawHeadline]):
    with Session(engine) as session:
        # Convert named tuples to SQLModel objects and add to the session
        for raw_headline in raw_headlines:
            db_headline = TopHeadline(**raw_headline._asdict())
            session.add(db_headline)
        session.commit()


def main():
    create_db_and_tables(engine)
    raw_headlines = get_top_headlines()
    create_db_with_raw_headlines(engine, raw_headlines)
    get_article_text_and_insert(engine)
    sentiment_analysis(engine)


if __name__ == "__main__":
    main()
