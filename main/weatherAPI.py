import requests
from PIL import ImageTk, Image
from io import BytesIO
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable


# Function to get coordinates based on city and country
def get_coordinates(city, country):
    geolocator = Nominatim(user_agent="geoapiExercises")
    try:
        location = geolocator.geocode(city + ',' + country)
        if location:
            return location.latitude, location.longitude
        else:
            return None, None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None

# Function to get weather information and display it
def fetch_weather(city, country):
    lat, lon = get_coordinates(city, country)
    if lat is None or lon is None:
        return 'Coordinates could not be found.', None, None, None

    try:
        response = requests.get(f"https://api.weatherapi.com/v1/current.json?key=9f81700dee234f0a829113545241501&q={lat},{lon}")
        response.raise_for_status()
        data = response.json()

        condition = data['current']['condition']['text']
        icon_url = 'https:' + data['current']['condition']['icon']
        temp = data['current']['temp_c']
        name = data['location']['name']
        country = data['location']['country']

        icon_response = requests.get(icon_url)
        icon_data = icon_response.content
        icon_image = Image.open(BytesIO(icon_data))
        icon_photo = ImageTk.PhotoImage(icon_image)

        return '', temp, condition, icon_photo
    except requests.exceptions.RequestException as e:
        return 'Error fetching weather data: {e}', None, None, None