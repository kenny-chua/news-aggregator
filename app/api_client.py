# Constructing the API Endpoints for the number of New Sources in the US in English and the Top Headlines in the US in English

from urllib.parse import urlencode
import os

# Get the API key from the environment variables for secure storage
NEWSAPI_API_KEY = os.getenv("NEWSAPI_API_KEY")

# Base URLs for the API endpoints
SOURCES_BASE_URL = "https://newsapi.org/v2/top-headlines/sources"
HEADLINES_BASE_URL = "https://newsapi.org/v2/top-headlines"

# Dictionary holding query parameters for the request
query_params = {
    "country": "us",        # Filter for articles from the US
    "language": "en",       # Filter for English language articles
    "apiKey": NEWSAPI_API_KEY  # API key for authentication
}

# Construct the full URL for fetching the number of sources in the US
us_sources_endpoint = f"{SOURCES_BASE_URL}?{urlencode(query_params)}"

# Construct the full URL for fetching the top headlines in the US
us_top_headlines = f"{HEADLINES_BASE_URL}?{urlencode(query_params)}"

# Print the constructed URLs for verification
print("US Sources Endpoint URL:")
print(us_sources_endpoint)

print("\nUS Top Headlines Endpoint URL:")
print(us_top_headlines)
