from abc import ABC, abstractmethod
from newspaper import Article

url = "https://www.cnn.com/2024/11/14/politics/trump-outrage-washington-cabinet-analysis/index.html"

class NewsSource(ABC):
    @abstractmethod
    def fetch_news(self):
        """Fetch news data from source"""
        pass

class Newspaper3kNewsSource(NewsSource):
    def fetch_news(self):
        """Fecth news data via library newspaper3k"""
        article = Article(self.url)
        article.download()
        article.parse()
        return article.title


class RSSNewsSource(NewsSource):
    def fetch_news(self):
        """Implement for fetching news via RSS"""
        pass

class WebScrapingNewsSource(NewsSource):
    def fetch_news(self):
        """Implement for fetching news via web scraping"""
        pass

class APINewsSource(NewsSource):
    def fetch_news(self):
        """Implement for fetching news via API"""
        pass

np3k = NewsSource()
print(np3k.fetch_news)