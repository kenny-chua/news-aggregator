from abc import ABC, abstractmethod

class NewsSource(ABC):
    @abstractmethod
    def fetch_news(self):
        """Fetch news data from source"""
        pass

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
