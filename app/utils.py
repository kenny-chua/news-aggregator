from datetime import datetime


def format_date(value):
    """Format a datetime string into a human-readable date."""
    try:
        date_obj = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
        return date_obj.strftime("%B %d, %Y")
    except ValueError:
        return value  # Return the original value if parsing fails
