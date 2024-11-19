import os
from collections import namedtuple
from urllib.parse import urlencode

import requests


# Define a named tuple for top headlines
TopHeadline = namedtuple('TopHeadline', ['source_id', 'source_name', 'author', 'title', 'description', 'url', 'url_to_image', 'published_at', 'content'])

TOPHEADLINES_URL = "https://newsapi.org/v2/top-headlines"

def get_top_headlines(country='us', language='en'):
    """
    Fetches the top headlines for a given country and language using the NewsAPI.
    
    Parameters:
        country (str): The country code to filter headlines (default is 'us').
        language (str): The language code to filter headlines (default is 'en').
    
    Returns:
        list: A list of TopHeadline named tuples.
    """
    # Retrieve the API key from the environment variable inside the function
    api_key = os.getenv("NEWSAPI_API_KEY")
    
    # Dictionary holding query parameters for the request
    top_headlines_params = {
        "country": country,
        "language": language,
        "apiKey": api_key
    }
    
    # Build the full endpoint URL with query parameters
    endpoint = f"{TOPHEADLINES_URL}?{urlencode(top_headlines_params)}"
    
    # Fetch the data for top headlines
    response = requests.get(endpoint)
    json_data = response.json()  # Parse JSON response to Python dictionary

    # Extract the 'articles' list from the JSON data
    articles = json_data.get('articles')
    
    # Convert each article dictionary into a 'TopHeadline' named tuple
    top_headlines = [
        TopHeadline(
            source_id=article['source']['id'],
            source_name=article['source']['name'],
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
    
    return top_headlines


