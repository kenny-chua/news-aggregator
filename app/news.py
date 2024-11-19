import os
from typing import NamedTuple, List, Optional
from urllib.parse import urlencode
import requests
from sqlmodel import SQLModel, Field, create_engine, Session

# Define a named tuple for processing the data
class RawHeadline(NamedTuple):
    source_id: Optional[str]
    source_name: Optional[str]
    author: Optional[str]
    title: str
    description: Optional[str]
    url: str
    url_to_image: Optional[str]
    published_at: str
    content: Optional[str]

# Define the SQLModel class for top headlines
class TopHeadline(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    source_id: Optional[str] = Field(default=None)
    source_name: Optional[str] = Field(default=None)
    author: Optional[str] = Field(default=None)
    title: str
    description: Optional[str] = Field(default=None)
    url: str
    url_to_image: Optional[str] = Field(default=None)
    published_at: str
    content: Optional[str] = Field(default=None)

TOPHEADLINES_URL = "https://newsapi.org/v2/top-headlines"

def get_top_headlines(country='us', language='en') -> List[RawHeadline]:
    api_key = os.getenv("NEWSAPI_API_KEY")
    
    top_headlines_params = {
        "country": country,
        "language": language,
        "apiKey": api_key
    }

    endpoint = f"{TOPHEADLINES_URL}?{urlencode(top_headlines_params)}"
    response = requests.get(endpoint)
    json_data = response.json()

    articles = json_data.get('articles', [])
    
    raw_headlines = [
        RawHeadline(
            source_id=article['source'].get('id'),
            source_name=article['source'].get('name'),
            author=article.get('author'),
            title=article.get('title'),
            description=article.get('description'),
            url=article.get('url'),
            url_to_image=article.get('urlToImage'),
            published_at=article.get('publishedAt'),
            content=article.get('content')
        )
        for article in articles
    ]
    
    return raw_headlines

def create_db_tables(engine):
    SQLModel.metadata.create_all(engine)

def insert_headlines_into_db(engine, raw_headlines: List[RawHeadline]):
    with Session(engine) as session:
        # Convert named tuples to SQLModel objects and add to the session
        for raw_headline in raw_headlines:
            db_headline = TopHeadline(**raw_headline._asdict())
            session.add(db_headline)
        session.commit()

def create_db():
    sqlite_url = "sqlite:///newslist.db"
    engine = create_engine(sqlite_url)
    create_db_tables(engine)
    
    # Get raw headlines as named tuples
    raw_headlines = get_top_headlines()
    insert_headlines_into_db(engine, raw_headlines)

if __name__ == "__main__":
    create_db()
