import time
import newspaper

from playwright.sync_api import sync_playwright
from sqlmodel import Session, select

from models import TopHeadline


PLAYWRIGHT_TIMEOUT_MILLISECONDS = 60000
PYSTD_TIME_SECONDS = 3


def clean_malformed_escaped_url(url: str) -> str:
    print(url)
    url = url.replace("\\\\u003d", "=")
    return url


def scrape_with_playwright(url: str):
    """Scrape content of a webpage using Playwright"""
    try:
        with sync_playwright() as p:
            with p.chromium.launch() as browser:
                context = browser.new_context()
                context.set_default_timeout(PLAYWRIGHT_TIMEOUT_MILLISECONDS)
                page = context.new_page()
                response = page.goto(url, wait_until="domcontentloaded", timeout=PLAYWRIGHT_TIMEOUT_MILLISECONDS)
                time.sleep(PYSTD_TIME_SECONDS)  # Allow the javascript to render

                # Check for paywall (common 403 or other indicators)
                if response and response.status == 403:
                    raise PermissionError("Paywall detected.")

                content = page.content()

        # Use newspaper4k to process the scraped HTML
        article = newspaper.article(url, input_html=content, language="en")
        return article
    except PermissionError as e:
        print(f"Paywall detected for URL: {url}. Error: {e}")
        return "Paywalled"
    except Exception as e:
        print(f"Error scraping URL: {url}. Error: {e}")
        return None


def get_article_text_and_insert(engine):
    """Fetch and insert article content into the database."""
    with Session(engine) as session:
        contents = session.exec(select(TopHeadline).where(TopHeadline.content.is_(None))).all()

        for content in contents:
            try:
                # Clean up URL and Scrape
                content.url = clean_malformed_escaped_url(content.url)
                article = scrape_with_playwright(content.url)

                if article and article.text:
                    content.content = article.text
                    print(f"Content for {content.title} was added.")
                else:
                    print(f"I couldn't scrape this {content.title}")
                    session.delete(content)

                session.commit()
                print(f"Content commited for URL: {content.url}")

            except Exception as e:
                if "403" in str(e):
                    content.content = "Paywalled"
                else:
                    content.content = f"Error: {e}"
