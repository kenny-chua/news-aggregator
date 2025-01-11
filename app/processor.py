import time
from log import setup_logger
import newspaper

from playwright.sync_api import sync_playwright
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from models import TopHeadline

logger = setup_logger(__name__)


PLAYWRIGHT_TIMEOUT_MILLISECONDS = 60000
PYSTD_TIME_SECONDS = 3


def clean_malformed_escaped_url(url: str) -> str:
    logger.debug(f"Cleaning URL: {url}")
    url = url.replace("\\\\u003d", "=")
    return url


def scrape_with_playwright(url: str):
    """Scrape content of a webpage using Playwright"""
    try:
        logger.info(f"Scraping URL: {url}")
        with sync_playwright() as p:
            with p.chromium.launch() as browser:
                context = browser.new_context()
                context.set_default_timeout(PLAYWRIGHT_TIMEOUT_MILLISECONDS)
                page = context.new_page()
                response = page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=PLAYWRIGHT_TIMEOUT_MILLISECONDS,
                )
                time.sleep(PYSTD_TIME_SECONDS)  # Allow the javascript to render

                # Check for paywall (common 403 or other indicators)
                if response and response.status == 403:
                    logger.warning(f"Paywall detected for URL: {url}")
                    return None

                content = page.content()

        # Use newspaper4k to process the scraped HTML
        article = newspaper.article(url, input_html=content, language="en")
        return article
    except Exception as e:
        logger.error(f"Error scraping URL: {url}. Error: {e}")
        return None


def get_article_text_and_insert(engine):
    """Fetch and insert article content into the database."""
    with Session(engine) as session:
        contents = session.exec(
            select(TopHeadline).where(TopHeadline.content.is_(None))
        ).all()
        for content in contents:
            try:
                logger.info(f"Processing article for URL: {content.url}")
                article = scrape_with_playwright(content.url)
                if article is None:
                    logger.debug(f"Article could not be created for URL: {content.url}")
                    session.delete(content)
                elif not article.text:
                    logger.debug(f"Article text is empty for URL: {content.url}")
                    session.delete(content)
                else:
                    content.content = article.text
                    logger.info(f"Content successfully scraped for: {content.title}")

                session.commit()
                logger.info(f"Content committed for URL: {content.url}")
            except IntegrityError:
                session.rollback()
                logger.warning(f"IntegrityError for URL: {content.url}")
                continue
