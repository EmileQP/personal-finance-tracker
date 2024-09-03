
from flask import redirect, session
from functools import wraps
from datetime import datetime
import pytz

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function



def format_timestamp(timestamp):
    # Define the Spain timezone
    spain_tz = pytz.timezone('Europe/Madrid')
    
    # Convert timestamp to datetime if it is a string
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp)  # Adjust if your string format is different
        except ValueError:
            return "Invalid date"  # Handle the error as appropriate

    # Localize the timestamp to Spain timezone
    if timestamp.tzinfo is None:
        timestamp = spain_tz.localize(timestamp)
    else:
        timestamp = timestamp.astimezone(spain_tz)

    now = datetime.now(spain_tz)
    
    # Check if the timestamp is from today
    is_today = timestamp.date() == now.date()
    
    # Format the timestamp
    if is_today:
        # Show only the time in 12-hour format with AM/PM
        return timestamp.strftime('%I:%M %p')  # 12-hour format without seconds
    else:
        # Show the date in "Month Day, Year" format
        return timestamp.strftime('%B %d, %Y %I:%M %p')  # Full month name, day, and year