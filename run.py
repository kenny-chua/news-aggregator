from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask

from app.app import create_db_and_tables, engine
from app.app import scrape_and_process as run_scraper
from app.log import LoggerSingleton
from app.routes import routes
from app.utils import format_date

logger = LoggerSingleton.get_logger(__name__)


def create_app():
    app = Flask(__name__, template_folder="app/templates", static_folder="app/static")

    # Ensure the database and tables are created when the Flask app starts
    @app.before_first_request
    def initialize_database():
        create_db_and_tables(engine)

    app.register_blueprint(routes)

    # Register the Jinja2 filter
    app.jinja_env.filters["format_date"] = format_date

    return app


# Function to schedule the scraper
def schedule_scraper():
    """Run the scraping task."""
    try:
        logger.info("Running the scraper task...")
        run_scraper()  # Call the `main()` function from app.py
        logger.info("Scraper task completed succesfully.")
    except Exception as e:
        logger.error(f"Error running the scraper: {e}", exc_info=True)


# Initialize and start the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(
    schedule_scraper, "interval", days=1
)  # Schedule the scraper to run once a day
scheduler.start()


if __name__ == "__main__":
    logger.info("Starting the Flask app with scheduler...")
    app = create_app()
    app.run(host="0.0.0.0", port=5001, debug=True)
