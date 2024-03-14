# updatet version of testView2
# The new feature is a complete new version of the day view with an integrated database from the event view. The day view is now able to show all events of a specific day and delete them.
#TODO: Konzept überlegen: Wie man Events vom gleichen Tag in einer Übersicht hat, um die konkreten Uhrzeiten der Events zu sehen und vergleichen
#TODO: Event Erstellung: Jedes Feld sollte richtigen Datentypen haben und auch die richtige Eingabevariaten (aka Uhrzeit als HH:MM und immer mit Timtpicker oder Mini Kalendar der angezeigt wird zum Datum auswählen)
#TODO: Bestehende Events sollten bearbeitbar sein
import sqlite3
import tkinter as tk
from tkinter import ttk
import calendar
import json
import boto3
from requests.exceptions import HTTPError
from datetime import datetime

# import from other files
import databaseCalls as db
import weatherAPI 

#TODO what does this button do?


global add_event_button

# Function to add event from the GUI
def add_event(event_name, event_description, event_location, event_participants, 
              event_priority, event_date, start_time, end_time):
    
    day, month, year = event_date.split('.')
    
    # Insert into the database
    db.add_event(
    event_name, event_description, event_location, event_participants, 
    event_priority, event_date, start_time, end_time
    )
    
    print("Event added successfully.")
    
    # Automatically switch to the day view of the added event
    # Ensure that yearGlobal and monthGlobal are updated if the event is in a different month/year
    global yearGlobal, monthGlobal
    yearGlobal, monthGlobal = int(year), int(month)

    # Call show_day_view with the correct day parameter
    show_day_view(int(day))
    populate_upcoming_events()


def show_event_view():
    global currentView
    currentView = "event"

    global add_event_button, event_name_entry, event_description_entry, event_location_entry
    global event_participants_entry, event_priority_entry, event_date_entry, start_time_entry, end_time_entry

    view_header_label.config(text="Event View")
    # clear the middle page
    for widget in middle_box.winfo_children():
        widget.destroy()

    # create the different entry fields of an event
    labels = ["Event Name", "Event Description", "Event Location",  "Event Participants", "Event Priority", "Event Date (DD.MM.YYYY)", "Start Time (HH:MM)", "End Time (HH:MM)"]
    entries = []
    for row, label_text in enumerate(labels):
        label = tk.Label(middle_box, text=label_text)
        label.grid(row=row, column=0, padx=5, pady=5, sticky="e")
        entry = tk.Entry(middle_box)
        entry.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
        entries.append(entry)

    event_name_entry, event_description_entry, event_location_entry, event_participants_entry, event_priority_entry, event_date_entry, start_time_entry, end_time_entry = entries

    # add button
    add_event_button = tk.Button(middle_box, text='Add Event', command=lambda: add_event(
        event_name_entry.get(), 
        event_description_entry.get(), 
        event_location_entry.get(), 
        event_participants_entry.get(), 
        event_priority_entry.get(), 
        event_date_entry.get(),
        start_time_entry.get(),
        end_time_entry.get()
    ))
    add_event_button.grid(row=9, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

    
def populate_event_view_for_editing(event_id):
    # Fetch event details from the database
    event_details = db.fetch_event_details(event_id)
    if not event_details:
        print("Event details not found.")
        return

    # Switch to event view if not already there
    switch_to_event_view()

    # Populate form fields with event details
    event_name_entry.delete(0, tk.END)
    event_name_entry.insert(0, event_details[1])

    event_description_entry.delete(0, tk.END)
    event_description_entry.insert(0, event_details[2])

    event_location_entry.delete(0, tk.END)
    event_location_entry.insert(0, event_details[3])

    event_participants_entry.delete(0, tk.END)
    event_participants_entry.insert(0, event_details[4])

    event_priority_entry.delete(0, tk.END)
    event_priority_entry.insert(0, event_details[5])

    event_date_entry.delete(0, tk.END)
    event_date_entry.insert(0, event_details[6])

    start_time_entry.delete(0, tk.END)
    start_time_entry.insert(0, event_details[7] if event_details[7] else "")

    end_time_entry.delete(0, tk.END)
    end_time_entry.insert(0, event_details[8] if event_details[8] else "")

    # Update the command of the add event button to handle the event update
    global add_event_button
    add_event_button.config(text='Update Event', command=lambda: update_event_and_refresh_view(
        original_event_id = event_id,
        event_name=event_name_entry.get(),
        event_description=event_description_entry.get(),
        event_location=event_location_entry.get(),
        event_participants=int(event_participants_entry.get()),
        event_priority=int(event_priority_entry.get()),
        event_date=event_date_entry.get(),
        start_time=start_time_entry.get(),
        end_time=end_time_entry.get()
    ))

def update_event_and_refresh_view(original_event_id, event_name, event_description, event_location, 
                                  event_participants, event_priority, event_date, start_time, end_time):
    # Update the event in the database
    db.update_event(original_event_id, event_name, event_description, event_location, event_participants, 
                    event_priority, event_date, start_time, end_time)
    
    # Ensure global variables are correctly set for the date
    global yearGlobal, monthGlobal
    day, month, year = map(int, event_date.split('.'))
    yearGlobal, monthGlobal = year, month

    # Refresh the views
    show_day_view(day)  # Show the updated day view
    populate_upcoming_events()  # Refresh the upcoming events list


# Global variables
monthGlobal = 2
yearGlobal = 2024
currentView = "month"

def next_month():
    global monthGlobal, yearGlobal
    if monthGlobal == 12:
        monthGlobal = 1
        yearGlobal += 1
    else:
        monthGlobal += 1
    populate_month(monthGlobal, yearGlobal)


def previous_month():
    global monthGlobal, yearGlobal
    if monthGlobal == 1:
        monthGlobal = 12
        yearGlobal -= 1
    else:
        monthGlobal -= 1
    populate_month(monthGlobal, yearGlobal)

def resize(event):
    # Resize logic here
    pass

def number_to_month(number):
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    if number >= 1 and number <= 12:
        return months[number - 1]
    else:
        return None

def populate_month(month, year):
    # Update the global variables
    global monthGlobal, yearGlobal, currentView
    monthGlobal = month
    yearGlobal = year

    # Set the current view to month
    currentView = "month"
    month_name = number_to_month(month)
    view_header_label.config(text=str(month_name) + ", " + str(yearGlobal))


    # Clear content frame
    for widget in middle_box.winfo_children():
        widget.destroy()

    # Draw month view
    cal = calendar.monthcalendar(year, month)

    # Get the current day
    current_day = calendar.datetime.date.today().day
    current_month = calendar.datetime.date.today().month
    current_year = calendar.datetime.date.today().year

    # Create a 8x8 grid view
    for row in range(8):
        middle_box.grid_rowconfigure(row, weight=1)  # Set row weight to 1
        for col in range(7):
            middle_box.grid_columnconfigure(col, weight=1)  # Set column weight to 1
            if row == 0 and col == 0:
                day_label = tk.Label(middle_box, text=str("<"))
                day_label.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")  # Use sticky="nsew" to fill the entire cell
                day_label.bind("<Button-1>", lambda event: previous_month())  # Bind the click event to the show_day_view function with the respective day as a parameter
            elif row == 0 and col == 1:
                day_label = tk.Label(middle_box, text=str(">"))
                day_label.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")  # Use sticky="nsew" to fill the entire cell
                day_label.bind("<Button-1>", lambda event: next_month())  # Bind the click event to the show_day_view function with the respective day as a parameter   
            # insert the first row with the days
            elif row == 0:
                pass
            elif row == 1:
                days = ["M", "T", "W", "T", "F", "S", "S"]
                day_label = tk.Label(middle_box, text=str(days[col]))
                day_label.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")  # Use sticky="nsew" to fill the entire cell

            else:
                # Create a label widget for each day in the calendar
                try:
                    day = cal[row-2][col]
                    if day != 0:
                        day_label = tk.Label(middle_box, text=str(day))
                        day_label.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")  # Use sticky="nsew" to fill the entire cell
                        day_label.bind("<Button-1>", lambda event, day=day: show_day_view(day))  # Bind the click event to the show_day_view function with the respective day as a parameter

                        # Color the current day
                        if day == current_day and monthGlobal == current_month and yearGlobal == current_year:
                            day_label.config(bg="lightblue")  # Set the background color to red for the current day
                except IndexError:
                    print("IndexError: cal[{}][{}]".format(row, col))




def fetch_weather(city, country):
    text, temp, condition, icon_photo = weatherAPI.fetch_weather(city, country)

    if len(text) < 1:
        weather_label.config(text=f"Weather in {city}, {country}: {temp}°C, {condition}", image=icon_photo, compound='top')
        weather_label.image = icon_photo
    else:
        weather_label.config(text = text)


def delete_event_and_refresh_upcoming(event_id):
    # Delete the event
    db.delete_event(event_id)
    
    # Refresh the upcoming events list
    populate_upcoming_events()


def show_day_view(day):
    global currentView, monthGlobal, yearGlobal
    currentView = "day"
    # Adjust the date format to match the database format (DD.MM.YYYY)
    selected_date = f"{day:02d}.{monthGlobal:02d}.{yearGlobal}"
    view_header_label.config(text=f"{day}. {number_to_month(monthGlobal)}, {yearGlobal}")
    
    # Clear previously displayed widgets
    for widget in middle_box.winfo_children():
        widget.destroy()

    # Add "Add Event" button to day view
    add_event_button = tk.Button(middle_box, text="Add Event", command=show_event_view)
    add_event_button.pack(pady=10)

    # Connect to the database and fetch events for the selected date
    events = db.fetch_events_by_date(selected_date)

    # Display events, handling None start and end times
    if events:
        for event in events:
            start_time_display = "Start Time: Not specified" if event[7] is None else f"Start Time: {event[7]}"
            end_time_display = "End Time: Not specified" if event[8] is None else f"End Time: {event[8]}"
            
            event_info = f"Name: {event[1]}\nDescription: {event[2]}\nLocation: {event[3]}\nParticipants: {event[4]}\nPriority: {event[5]}\nDate: {event[6]}\n{start_time_display}\n{end_time_display}"
            event_frame = tk.Frame(middle_box)
            event_frame.pack(fill='x', padx=5, pady=5, anchor="w")
            tk.Label(event_frame, text=event_info, justify="left").pack(side="left")
            
            edit_btn = tk.Button(event_frame, text="Edit", command=lambda e=event: populate_event_view_for_editing(e[0]))
            edit_btn.pack(side="right", padx=5)
            
            delete_btn = tk.Button(event_frame, text="Delete", command=lambda e=event: delete_event_and_refresh_view(e[0], day))
            delete_btn.pack(side="right", padx=5)
            
            ttk.Separator(middle_box).pack(fill='x', padx=5, pady=5)
    else:
        no_events_label = tk.Label(middle_box, text="No events for this day.")
        no_events_label.pack(padx=10, pady=5)
    

def delete_event_and_refresh_view(event_id, day):
    db.delete_event(event_id)
    show_day_view(day)
    populate_upcoming_events()


def populate_upcoming_events():
    # First, clear any existing content in the right box
    for widget in right_box.winfo_children():
        widget.destroy()

    upcoming_events = db.fetch_upcoming_events()

    # Loop through the upcoming events and create a frame for each event
    for event in upcoming_events:
        event_frame = tk.Frame(right_box)
        event_frame.pack(fill='x', padx=5, pady=5, anchor="w")

        # Display the event details
        start_time_display = event[4] if event[4] else "Time Not Specified"
        event_info = f"Name: {event[1]}, Date: {event[3]}, Start: {start_time_display}\nDesc: {event[2]}"
        tk.Label(event_frame, text=event_info, justify="left").pack(side="left")

        # Add "Edit" and "Delete" buttons for each event
        edit_btn = tk.Button(event_frame, text="Edit", command=lambda e=event: populate_event_view_for_editing(e[0]))
        edit_btn.pack(side="right", padx=5)

        delete_btn = tk.Button(event_frame, text="Delete", command=lambda e=event: delete_event_and_refresh_upcoming(e[0]))
        delete_btn.pack(side="right", padx=5)




# Function to switch to the month view
def switch_to_month_view():
    if currentView != "month":
        populate_month(monthGlobal, yearGlobal)

def switch_to_day_view():
    if currentView != "day":
        show_day_view(1)

def switch_to_event_view():
    if currentView != "event":
        show_event_view()

# Create the main window
root = tk.Tk()

# Create the main header
header_frame = tk.Frame(root, bd=2, relief=tk.SOLID, bg="lightblue")
header_frame.pack(fill=tk.X)

header_text = "Calendar Application"
header_label = tk.Label(header_frame, text=header_text, font=("Arial", 16, "bold"))
header_label.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X)

# Add view switch buttons to the main header
month_button = tk.Button(header_frame, text="Month View", command=switch_to_month_view)
month_button.pack(side=tk.LEFT, padx=10, pady=10)

day_button = tk.Button(header_frame, text="Day View", command=switch_to_day_view)
day_button.pack(side=tk.LEFT, padx=10, pady=10)

event_button = tk.Button(header_frame, text="Event View", command=switch_to_event_view)
event_button.pack(side=tk.LEFT, padx=10, pady=10)

# Add additional header for view indication
view_header_text = "Current View: " + currentView.capitalize()
view_header_label = tk.Label(root, text=view_header_text, font=("Arial", 12), bd=2, relief=tk.SOLID, bg="lightgreen")
view_header_label.pack(fill=tk.X)

# Create left, middle, and right boxes
left_box = tk.Frame(root, bd=2, relief=tk.SOLID, bg="blue")
left_box.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
left_box.configure(highlightbackground="darkblue", highlightcolor="blue", highlightthickness=2)

middle_box = tk.Frame(root, bd=2, relief=tk.SOLID, bg="Grey")
middle_box.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
middle_box.configure(highlightbackground="Black", highlightcolor="Black", highlightthickness=2)


right_box = tk.Frame(root, bd=2, relief=tk.SOLID, bg="lightgreen")
right_box.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
right_box.configure(highlightbackground="lightgreen", highlightcolor="red", highlightthickness=2)

# GUI code (root, header_frame, header_label, view_header_label, left_box, middle_box, right_box)

# Weather input fields and button
weather_frame = tk.Frame(left_box)
weather_frame.pack(pady=10)

city_label = tk.Label(weather_frame, text="City:")
city_label.grid(row=0, column=0)
city_entry = tk.Entry(weather_frame)
city_entry.grid(row=0, column=1)

country_label = tk.Label(weather_frame, text="Country:")
country_label.grid(row=1, column=0)
country_entry = tk.Entry(weather_frame)
country_entry.grid(row=1, column=1)

fetch_weather_button = tk.Button(weather_frame, text="Fetch Weather", command=weatherAPI.fetch_weather(city_entry.get(), country_entry.get()))
fetch_weather_button.grid(row=2, column=0, columnspan=2)

weather_label = tk.Label(left_box, text="Weather Information")
weather_label.pack()

# Example usage
# To initialize the database or table without adding an event, simply call the function without arguments.
db.initialize_database()

# Bind resize event
root.bind("<Configure>", resize)

# Call populate_month initially
populate_month(monthGlobal, yearGlobal)

# Call the function to initially populate the right box
populate_upcoming_events()

# Start the main event loop
root.mainloop()



populate_month(monthGlobal, yearGlobal)
root.mainloop()