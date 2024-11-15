from urllib.parse import urlencode
import requests
from collections import namedtuple
import os

# Get the API key from the environment variables for secure storage
NEWSAPI_API_KEY = os.getenv("NEWSAPI_API_KEY")

# Base URLs for the API endpoints
SOURCES_BASE_URL = "https://newsapi.org/v2/top-headlines/sources"
HEADLINES_BASE_URL = "https://newsapi.org/v2/top-headlines"

# Dictionary holding query parameters for the request
query_params = {
    "country": "us",        # Filter for news sources and headlines from the US
    "language": "en",       # Filter for English language news
    "apiKey": NEWSAPI_API_KEY  # API key for authentication
}

# Construct the full URL for fetching the list of news sources in the US
us_sources_endpoint = f"{SOURCES_BASE_URL}?{urlencode(query_params)}"

# Construct the full URL for fetching the top headlines in the US
us_top_headlines_endpoint = f"{HEADLINES_BASE_URL}?{urlencode(query_params)}"

# Print the constructed URLs for verification
print("US Sources Endpoint URL:")
print(us_sources_endpoint)

print("\nUS Top Headlines Endpoint URL:")
print(us_top_headlines_endpoint)

# Fetch the data for news sources
response_news_sources = requests.get(us_sources_endpoint)
json_data_news_sources = response_news_sources.json()  # Parse JSON response to Python dictionary

# Extract the 'sources' list from the JSON data (list of dictionaries)
news_sources_list = json_data_news_sources['sources']

# Get the field names from the first entry to create a named tuple structure for sources
news_source_field_names = news_sources_list[0].keys()
NewsSource = namedtuple('NewsSource', news_source_field_names)

# Convert each source dictionary into a 'NewsSource' named tuple
news_sources_named_tuples = [NewsSource(**source) for source in news_sources_list]

# Print a sample of the named tuples for verification
print("\nSample News Sources Named Tuples:")
for source in news_sources_named_tuples[:5]:  # Print the first 5 named tuples
    print(source)

# Fetch the data for top headlines
response_top_headlines = requests.get(us_top_headlines_endpoint)
json_data_top_headlines = response_top_headlines.json()  # Parse JSON response to Python dictionary

# Extract the 'articles' list from the JSON data (list of dictionaries representing top headlines)
top_headlines_list = json_data_top_headlines['articles']

# Get the field names from the first entry to create a named tuple structure for headlines
top_headline_field_names = top_headlines_list[0].keys()
TopHeadline = namedtuple('TopHeadline', top_headline_field_names)

# Convert each article dictionary into a 'TopHeadline' named tuple
top_headlines_named_tuples = [TopHeadline(**article) for article in top_headlines_list]

# Print a sample of the named tuples for verification
print("\nSample Top Headlines Named Tuples:")
for headline in top_headlines_named_tuples[:5]:  # Print the first 5 named tuples
    print(headline)
