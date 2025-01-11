import os

from dotenv import load_dotenv
from sqlmodel import SQLModel, Session, create_engine, select
from urllib.parse import urlencode
import requests

from models import RawHeadline, TopHeadline
from processor import clean_malformed_escaped_url, get_article_text_and_insert
from sentiment import (
    classify_political_bias_harshal_Bert,
    prefilter_political_articles,
    sentiment_analysis,
)

# Constants and global configurations
load_dotenv()
os.environ["TOKENIZERS_PARALLELISM"] = "false"
NEWSAPI_TOPHEADLINES = "https://newsapi.org/v2/top-headlines"
BLACKLISTED_URLS = ["removed.com", "washingtonpost"]
sqlite_file_name = os.getenv("DB")
sqlite_url = f"sqlite:///{sqlite_file_name}"

# Global resource: SQL database engine
engine = create_engine(sqlite_url)


# Schema creation
def create_db_and_tables(engine):
    SQLModel.metadata.create_all(engine)


def get_raw_values_from_api(country="us", language="en") -> list[RawHeadline]:
    api_key = os.getenv("NEWSAPI_API_KEY")
    top_headlines_params = {"country": country, "language": language, "apiKey": api_key}
    endpoint = f"{NEWSAPI_TOPHEADLINES}?{urlencode(top_headlines_params)}"
    response = requests.get(endpoint)
    json_data = response.json()
    articles = json_data.get("articles", [])

    raw_headlines = [
        RawHeadline(
            published_at=article.get("publishedAt"),
            source_id=article["source"].get("id"),
            source_name=article["source"].get("name"),
            author=article.get("author"),
            url=clean_malformed_escaped_url(article.get("url")),
            title=article.get("title"),
            subheading=article.get("description"),
        )
        for article in articles
        if article.get("url")
        and not any(blacklisted in article["url"] for blacklisted in BLACKLISTED_URLS)
    ]
    return raw_headlines


def create_db_with_raw_headlines(engine, raw_headlines: list[RawHeadline]) -> None:
    with Session(engine) as session:
        existing_headlines = {row for row in session.exec(select(TopHeadline.url))}
        for raw_headline in raw_headlines:
            if raw_headline.url in existing_headlines:
                continue
            db_headline = TopHeadline(**raw_headline._asdict())
            session.add(db_headline)
        session.commit()


def main():
    create_db_and_tables(engine)
    raw_headlines = get_raw_values_from_api()
    create_db_with_raw_headlines(engine, raw_headlines)
    get_article_text_and_insert(engine)
    sentiment_analysis(engine)
    prefilter_political_articles(engine)
    classify_political_bias_harshal_Bert(engine)


if __name__ == "__main__":
    main()
