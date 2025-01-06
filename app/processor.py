from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from models import TopHeadline
from playwright.sync_api import sync_playwright
import time
import newspaper

PLAYWRIGHT_TIMEOUT_MILLISECONDS = 60000
PYSTD_TIME_SECONDS = 3


def clean_malformed_escaped_url(url: str) -> str:
    print(url)
    url = url.replace("\\\\u003d", "=")
    return url


def scrape_with_playwright(url: str):
    with sync_playwright() as p:
        with p.chromium.launch() as browser:
            context = browser.new_context()
            context.set_default_timeout(PLAYWRIGHT_TIMEOUT_MILLISECONDS)
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=PLAYWRIGHT_TIMEOUT_MILLISECONDS)
            time.sleep(PYSTD_TIME_SECONDS)  # Allow the javascript to render
            content = page.content()

    article = newspaper.article(url, input_html=content, language="en")
    return article


def get_article_text_and_insert(engine):
    with Session(engine) as session:
        contents = session.exec(select(TopHeadline).where(TopHeadline.content.is_(None))).all()

        for content in contents:
            try:
                # Clean up URL and Scrape
                content.url = clean_malformed_escaped_url(content.url)
                article = scrape_with_playwright(content.url)

                # Update or delete row based on scrape result
                if article.text:
                    content.content = article.text
                    session.add(content)
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

            except IntegrityError as ie:
                session.rollback()
                print(f"Skipping {content.title}. Already exists. Error: {ie}")
