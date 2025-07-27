import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
from openai import OpenAI


# --- Configuration ---
# Replace with your actual OpenWeatherMap API key
# NEVER hardcode API keys directly in public repositories or client-side code.
# For a real deployment, use environment variables (e.g., st.secrets)
# For local development, you can place it here for quick testing.
# Access the API key using st.secrets
# Streamlit will automatically load this from .streamlit/secrets.toml
# or from the Streamlit Community Cloud secrets interface when deployed.

try:
    OPENWEATHER_API_KEY = st.secrets["OPENWEATHER_API_KEY"]
except KeyError:
    st.error("OpenWeatherMap API key not found. "
             "Please set it in .streamlit/secrets.toml or Streamlit Cloud secrets.")
    st.stop() # Stop the app if the key is not found

BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"



def get_weather_data(city):
    """
    Fetches weather data for a given city using the OpenWeatherMap API.
    """
    # Construct the complete URL
    complete_url = f"{BASE_URL}q={city}&appid={OPENWEATHER_API_KEY}&units=metric"

    try:
        response = requests.get(complete_url)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json() # Parse the JSON response

        # Check if the API call was successful
        if data.get("cod") == 200: # 'cod' is the status code from OpenWeatherMap
            main_data = data["main"]
            weather_description = data["weather"][0]["description"].capitalize()
            wind_data = data["wind"]
            
            # Extract relevant data
            temperature = f"{main_data['temp']}°C"
            feels_like = f"{main_data['feels_like']}°C"
            humidity = f"{main_data['humidity']}%"
            wind_speed = f"{wind_data['speed']} m/s" 
            location_name = data["name"] 

            return {
                "location": location_name,
                "temperature": temperature,
                "feels_like": feels_like,
                "description": weather_description,
                "humidity": humidity,
                "wind": wind_speed
            }
        else:
            # Handle API-specific errors (e.g., city not found)
            error_message = data.get("message", "Unknown error from API")
            st.error(f"Error from OpenWeatherMap API: {error_message}. Please check the city name.")
            return None

    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to OpenWeatherMap API: {e}. Please check your internet connection or API endpoint.")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None

# --- Streamlit App ---
st.set_page_config(page_title="Live Weather App (OpenWeatherMap API)", layout="centered")

st.title("☀️ Live Weather Data App")
st.markdown("Get current weather information for any city using the OpenWeatherMap API.")

city_input = st.text_input("Enter city name:", "") 

if st.button("Get Weather"):
    if city_input:
        with st.spinner("Fetching weather data..."):
            weather_data = get_weather_data(city_input)
            
            if weather_data:
                st.subheader(f"Weather in {weather_data['location']}")
                st.metric("Temperature", weather_data['temperature'], help=f"Feels like: {weather_data['feels_like']}")
                st.write(f"**Description:** {weather_data['description']}")
                st.write(f"**Humidity:** {weather_data['humidity']}")
                st.write(f"**Wind Speed:** {weather_data['wind']}")
                
                st.info(f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S IST')}")
            else:
                # Error message already displayed by get_weather_data function
                pass
    else:
        st.warning("Please enter a city name.")

st.markdown("---")
st.markdown("Powered by [OpenWeatherMap API](https://openweathermap.org/api)")