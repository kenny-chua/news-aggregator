from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask

from app.app import create_db_and_tables, engine
from app.app import scrape_and_process as run_scraper
from app.log import LoggerSingleton
from app.routes import routes
from app.utils import format_date

logger = LoggerSingleton.get_logger(__name__)


def initialize_database():
    create_db_and_tables(engine)


def create_app():
    app = Flask(__name__, template_folder="app/templates", static_folder="app/static")

    # Ensure the database and tables are created when the Flask app starts
    initialize_database()

    app.register_blueprint(routes)

    # Register the Jinja2 filter
    app.jinja_env.filters["format_date"] = format_date

    return app


def start_scheduler(scheduler):
    """Set up and start the scheduler."""

    # Run the scraper immediately after the Flask app starts
    def run_initial_scraper():
        try:
            logger.info("Running initial scraper task...")
            run_scraper()
            logger.info("Initial scraper task completed.")
        except Exception as e:
            logger.error(f"Error running the initial scraper: {e}", exc_info=True)

    # Add the initial scraper job to run immediately
    scheduler.add_job(run_initial_scraper, "date", id="initial_scraper")

    # Add the daily scraper job
    scheduler.add_job(run_scraper, "interval", hours=24, id="daily_scraper")

    scheduler.start()
    logger.info("Scheduler started with initial and daily scraper jobs.")


if __name__ == "__main__":
    logger.info("Starting the Flask app with scheduler...")
    app = create_app()

    # Set up the scheduler
    scheduler = BackgroundScheduler()
    start_scheduler(scheduler)

    # Run the Flask app
    app.run(host="0.0.0.0", port=5001, debug=True)
