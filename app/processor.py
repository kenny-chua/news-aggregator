from sqlmodel import Session, select
from models import TopHeadline
from playwright.sync_api import sync_playwright
import time
import newspaper

def clean_malformed_escaped_url(url: str) -> str:
    print(url)
    url = url.replace("\\\\u003d", "=")
    return url

def scrape_with_playwright(url):
    # Using Playwright to render JavaScript
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        context.set_default_timeout(60000)
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(3) # Allow the javascript to render
        content = page.content()
        browser.close()
    article = newspaper.article(url, input_html=content, language='en')
    return article

def get_article_text_and_insert(engine):

    sql_stmt = select(TopHeadline).where(TopHeadline.content.is_(None))

    with Session(engine) as session:
        contents = session.exec(sql_stmt).all()
    
        for content in contents:
            try:
                content.url = clean_malformed_escaped_url(content.url)
                article = scrape_with_playwright(content.url)
                content.content = article.text
            except Exception as e:
                if "403" in str(e):
                    content.content = "Paywalled"
            finally:
                session.add(content)
                try:
                    session.commit()
                    print(f"Content committed for URL: {content.url}")
                except Exception as commit_error:
                    print(f"Error during commit for {content.url}: {commit_error}")
                    session.rollback()



