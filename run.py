from flask import Flask
from app.routes import routes
from app.utils import format_date


def create_app():
    app = Flask(__name__, template_folder="app/templates", static_folder="app/static")
    app.register_blueprint(routes)

    # Register the Jinja2 filter
    app.jinja_env.filters["format_date"] = format_date

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
