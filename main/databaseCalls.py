from datetime import datetime
import sqlite3

#TODO remove duration here, transform event_date, start_time, end_time to better data types
#TODO add event_id

def initialize_or_add_event(event_name=None, event_description=None, event_location=None, event_duration=None, event_participants=None, event_priority=None, event_date=None, start_time=None, end_time=None):
    conn = sqlite3.connect('event_database.db')
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS events (
        event_name TEXT,
        event_description TEXT,
        event_location TEXT,    
        event_duration TEXT,
        event_participants INTEGER,
        event_priority INTEGER,
        event_date TEXT,
        start_time TEXT,
        end_time TEXT
    )""")
    
    # Handling None or empty strings for start_time and end_time
    start_time_val = start_time if start_time else None  # Insert NULL if start_time is empty
    end_time_val = end_time if end_time else None  # Insert NULL if end_time is empty
    
    if all([event_name, event_description, event_location, event_duration, event_participants, event_priority, event_date]):  # Removed start_time and end_time from this check
        cursor.execute('''
        INSERT INTO events (event_name, event_description, event_location, event_duration, event_participants, event_priority, event_date, start_time, end_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (event_name, event_description, event_location, event_duration, event_participants, event_priority, event_date, start_time_val, end_time_val))
    
    conn.commit()
    conn.close()


def fetch_event_details(event_name, event_date):
    conn = sqlite3.connect('event_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events WHERE event_name = ? AND event_date = ?", (event_name, event_date))
    event_details = cursor.fetchone()
    conn.close()
    return event_details

def update_event(original_event_name, original_event_date, event_name, event_description, event_location, event_duration, event_participants, event_priority, event_date, start_time, end_time):
    conn = sqlite3.connect('event_database.db')
    cursor = conn.cursor()
    cursor.execute("""UPDATE events SET event_name = ?, event_description = ?, event_location = ?, event_duration = ?, event_participants = ?, event_priority = ?, event_date = ?, start_time = ?, end_time = ? WHERE event_name = ? AND event_date = ?""", (event_name, event_description, event_location, event_duration, event_participants, event_priority, event_date, start_time, end_time, original_event_name, original_event_date))
    conn.commit()
    conn.close()
    print("Event updated successfully.")

def delete_event(event_name, event_date):
    conn = sqlite3.connect('event_database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM events WHERE event_name = ? AND event_date = ?", (event_name, event_date))
    conn.commit()
    conn.close()
    print(f"Deleted event '{event_name}' on {event_date}.")





# now make all the methods based on ID
def initialize_database():
    conn = sqlite3.connect('event_database.db')
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_name TEXT,
        event_description TEXT,
        event_location TEXT,
        event_participants INTEGER,
        event_priority INTEGER,
        event_date TEXT,
        start_time TEXT,
        end_time TEXT
    )""")
    conn.commit()
    conn.close()

def add_event(event_name=None, event_description=None, event_location=None, event_participants=None, event_priority=None, event_date=None, start_time=None, end_time=None):
    conn = sqlite3.connect('event_database.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO events (event_name, event_description, event_location, event_participants, event_priority, event_date, start_time, end_time)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (event_name, event_description, event_location, event_participants, event_priority, event_date, start_time, end_time))
    conn.commit()
    conn.close()

def fetch_event_details(event_id):
    conn = sqlite3.connect('event_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events WHERE event_id = ?", (event_id,))
    event_details = cursor.fetchone()
    conn.close()
    return event_details

def update_event(event_id, event_name=None, event_description=None, event_location=None, event_participants=None, event_priority=None, event_date=None, start_time=None, end_time=None):
    conn = sqlite3.connect('event_database.db')
    cursor = conn.cursor()
    cursor.execute("""UPDATE events SET event_name = ?, event_description = ?, event_location = ?, event_participants = ?, event_priority = ?, event_date = ?, start_time = ?, end_time = ? WHERE event_id = ?""", (event_name, event_description, event_location, event_participants, event_priority, event_date, start_time, end_time, event_id))
    conn.commit()
    conn.close()
    print("Event updated successfully.")

def delete_event(event_id):
    conn = sqlite3.connect('event_database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM events WHERE event_id = ?", (event_id,))
    conn.commit()
    conn.close()
    print(f"Deleted event with ID {event_id}.")


def fetch_events_by_date(date):
    """
    Fetches all events for a specific date from the database.

    :param date: The date in DD.MM.YYYY format.
    :return: A list of tuples containing event details.
    """
    conn = sqlite3.connect('event_database.db')
    cursor = conn.cursor()
    query = """
    SELECT event_id, event_name, event_description, event_location, event_participants, event_priority, event_date, start_time, end_time
    FROM events
    WHERE event_date = ?
    ORDER BY event_priority DESC, CASE WHEN start_time IS NULL THEN 1 ELSE 0 END, start_time
    """
    cursor.execute(query, (date,))
    events = cursor.fetchall()
    conn.close()
    return events

def fetch_upcoming_events():
    """
    Fetches all upcoming events from the database, assuming event_date is in DD.MM.YYYY format.
    Returns a list of tuples containing event details for events on or after today.
    """
    # Convert today's date to YYYY-MM-DD format for comparison
    today_date = datetime.now().strftime("%Y-%m-%d")

    # Initialize database connection
    conn = sqlite3.connect('event_database.db')
    cursor = conn.cursor()

    # Query to fetch upcoming events
    query = """
    SELECT event_id, event_name, event_description, event_date, start_time
    FROM events
    WHERE SUBSTR(event_date, 7, 4) || '-' || SUBSTR(event_date, 4, 2) || '-' || SUBSTR(event_date, 1, 2) >= ?
    ORDER BY SUBSTR(event_date, 7, 4) || '-' || SUBSTR(event_date, 4, 2) || '-' || SUBSTR(event_date, 1, 2) ASC, start_time ASC
    """
    cursor.execute(query, (today_date,))

    # Fetch all matching events
    upcoming_events = cursor.fetchall()

    # Close the database connection
    conn.close()

    return upcoming_events


