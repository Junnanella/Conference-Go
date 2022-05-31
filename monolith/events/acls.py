from .key import PEXELS_API_KEY, OPEN_WEATHER_API_KEY
import requests
import json


def get_photo(city, state):
    # Create a dictionary for the headers to use in the request
    headers = {
        "Authorization": PEXELS_API_KEY,
    }
    params = {
        "per_page": 1,
        "query": city + " " + state,
    }
    # Create the URL for the request with the city and state
    url = "https://api.pexels.com/v1/search"
    # Make the request
    res = requests.get(url, params=params, headers=headers)
    # Parse the JSON response
    content = json.loads(res.content)
    # Return a dictionary that contains a `picture_url` key and
    #   one of the URLs for one of the pictures in the response
    try:
        return {"picture_url": content["photos"][0]["src"]["original"]}
    except:
        return {"picture_url": None}


def get_weather_data(city, state):
    print(f"I am querying city: {city}, state: {state}")

    params = {
        "q": city + "," + state,
        "appid": OPEN_WEATHER_API_KEY,
    }
    # Create the URL for the geocoding API with the city and state
    url = "http://api.openweathermap.org/geo/1.0/direct"
    # Make the request
    res = requests.get(url, params=params)
    # Parse the JSON response
    content = json.loads(res.content)

    print(content)

    # Get the latitude and longitude from the response
    lat = content[0]["lat"]
    lon = content[0]["lon"]
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPEN_WEATHER_API_KEY,
    }

    # Create the URL for the current weather API with the latitude
    url = "https://api.openweathermap.org/data/2.5/weather"
    #   and longitude
    # Make the request
    res = requests.get(url, params=params)
    # Parse the JSON response
    content = json.loads(res.content)
    # Get the main temperature and the weather's description and put
    #   them in a dictionary
    # Return the dictionary
    try:
        return {"weather": content["weather"]}
    except:
        return {"weather": None}
