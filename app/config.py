import os
from dotenv import load_dotenv

load_dotenv()
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Database configuration
sqlite_file_name = os.getenv(
    "DB", "newslist.db"
)  # Default to 'newslist.db' if DB is not set
sqlite_url = f"sqlite:///{sqlite_file_name}"

# News API configuration
NEWSAPI_TOPHEADLINES = "https://newsapi.org/v2/top-headlines"
BLACKLISTED_URLS = ["removed.com", "washingtonpost"]
