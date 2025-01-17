import os
from urllib.parse import urlencode

import requests
from sqlmodel import Session, SQLModel, create_engine, select

from app.config import BLACKLISTED_URLS, NEWSAPI_TOPHEADLINES, sqlite_url
from app.log import LoggerSingleton
from app.models import RawHeadline, TopHeadline
from app.processor import clean_malformed_escaped_url, get_article_text_and_insert
from app.sentiment import (
    classify_political_bias_harshal_Bert,
    prefilter_political_articles,
    sentiment_analysis,
)

logger = LoggerSingleton.get_logger(__name__)


# Global resource: SQL database engine
engine = create_engine(sqlite_url)


# Schema creation
def create_db_and_tables(engine) -> None:
    logger.info("Creating database and tables...")
    SQLModel.metadata.create_all(engine)
    logger.info("Database and tables created.")


def get_raw_values_from_api(country="us", language="en") -> list[RawHeadline]:
    api_key = os.getenv("NEWSAPI_API_KEY")
    top_headlines_params = {"country": country, "language": language, "apiKey": api_key}
    endpoint = f"{NEWSAPI_TOPHEADLINES}?{urlencode(top_headlines_params)}"
    logger.info("Fetching top headlines from API...")
    response = requests.get(endpoint)

    if response.status_code != 200:
        logger.error(
            f"Failed to fetch data from API. Status code: {response.status_code}"
        )
        response.raise_for_status()

    logger.info("Data fetched successfully from API.")

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
    logger.info("Inserting raw headlines into the database...")
    with Session(engine) as session:
        existing_headlines = {row for row in session.exec(select(TopHeadline.url))}
        for raw_headline in raw_headlines:
            if raw_headline.url in existing_headlines:
                logger.debug(f"Skipping duplicate headline: {raw_headline.url}")
                continue
            db_headline = TopHeadline(**raw_headline._asdict())
            session.add(db_headline)
        session.commit()
    logger.info("Raw headlines inserted successfully.")


def main() -> None:
    logger.info("Starting application")
    create_db_and_tables(engine)
    raw_headlines = get_raw_values_from_api()
    create_db_with_raw_headlines(engine, raw_headlines)
    get_article_text_and_insert(engine)
    sentiment_analysis(engine)
    prefilter_political_articles(engine)
    classify_political_bias_harshal_Bert(engine)
    logger.info("Application finished")


if __name__ == "__main__":
    main()
