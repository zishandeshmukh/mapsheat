import requests
import os
import pandas as pd
import json
from datetime import datetime
import streamlit as st

def get_weather_data(city_name):
    """
    Fetch current weather data for a city using OpenWeatherMap API.
    
    Args:
        city_name: Name of the city to get weather data for
    
    Returns:
        JSON response from OpenWeatherMap API
    """
    api_key = os.getenv("OPENWEATHERMAP_API_KEY", "d4ed9ca97c5caa95f56dfd6b96ccbb9a")  # Default key for development
    
    # Base URL for OpenWeatherMap API
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    
    # Parameters for the API request
    params = {
        "q": city_name,
        "appid": api_key,
        "units": "metric"  # Use metric units (Celsius)
    }
    
    try:
        # Make the API request
        response = requests.get(base_url, params=params)
        
        # Check if the request was successful
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching weather data: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Exception occurred while fetching weather data: {str(e)}")
        return None

def get_forecast_data(city_name):
    """
    Fetch 5-day forecast data for a city using OpenWeatherMap API.
    
    Args:
        city_name: Name of the city to get forecast for
    
    Returns:
        JSON response from OpenWeatherMap API
    """
    api_key = os.getenv("OPENWEATHERMAP_API_KEY", "d4ed9ca97c5caa95f56dfd6b96ccbb9a")  # Default key for development
    
    # Base URL for OpenWeatherMap forecast API
    base_url = "https://api.openweathermap.org/data/2.5/forecast"
    
    # Parameters for the API request
    params = {
        "q": city_name,
        "appid": api_key,
        "units": "metric"  # Use metric units (Celsius)
    }
    
    try:
        # Make the API request
        response = requests.get(base_url, params=params)
        
        # Check if the request was successful
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching forecast data: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Exception occurred while fetching forecast data: {str(e)}")
        return None

def get_satellite_imagery(lat, lon, zoom=13):
    """
    Get satellite imagery for a location using Mapbox Static Images API.
    
    Args:
        lat: Latitude
        lon: Longitude
        zoom: Zoom level (1-20)
    
    Returns:
        URL to the satellite image
    """
    mapbox_token = os.getenv("MAPBOX_TOKEN", "pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw")
    
    # Mapbox Static Images API URL
    base_url = "https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static"
    
    # Format the URL
    image_url = f"{base_url}/{lon},{lat},{zoom},0/600x400@2x?access_token={mapbox_token}"
    
    return image_url

def add_community_report(lat, lon, temperature, description, reporter="Anonymous"):
    """
    Add a community temperature report to the session state.
    
    Args:
        lat: Latitude of the report
        lon: Longitude of the report
        temperature: Reported temperature in Celsius
        description: Description or notes about the location
        reporter: Name or identifier of the reporter
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create a new report
        new_report = {
            'latitude': lat,
            'longitude': lon,
            'temperature': temperature,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'description': description,
            'reporter': reporter
        }
        
        # Add to the existing reports
        new_df = pd.DataFrame([new_report])
        st.session_state.community_reports = pd.concat([st.session_state.community_reports, new_df], ignore_index=True)
        
        return True
    except Exception as e:
        st.error(f"Error adding community report: {str(e)}")
        return False
