from flask import Blueprint, render_template, request
from sqlmodel import Session, select, create_engine
from .models import TopHeadline
from app.config import sqlite_url

# Define the database location
engine = create_engine(sqlite_url)

# Blueprint for Flask routes
routes = Blueprint("routes", __name__)


@routes.route("/")
def index():
    """Homepage displaying all headlines."""
    with Session(engine) as session:
        headlines = session.exec(
            select(TopHeadline)
            .order_by(TopHeadline.published_at.desc())  # Order by the most recent first
            .limit(5)  # Limit the number of results to 5
        ).all()
    return render_template("index.html", headlines=headlines)


@routes.route("/detail/<int:headline_id>")
def detail(headline_id):
    """Detailed view of a single headline."""
    with Session(engine) as session:
        headline = session.get(TopHeadline, headline_id)
    return render_template("detail.html", headline=headline)


@routes.route("/load-more", methods=["GET"])
def load_more():
    """Dynamically load more headlines."""
    offset = int(request.args.get("offset", 0))  # Get offset from query params
    limit = 5  # Load 5 headlines at a time

    with Session(engine) as session:
        headlines = session.exec(select(TopHeadline).offset(offset).limit(limit)).all()

    print(f"Offset: {offset}, Limit: {limit}, Fetched: {len(headlines)} headlines")

    return render_template("partials/headlines.html", headlines=headlines)
