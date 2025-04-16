import folium
from folium.plugins import HeatMap
import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st
from utils.data_processing import generate_coordinates_around_city

def create_heatmap(weather_data, community_reports, radius=25):
    """
    Create a folium map with a heat map overlay based on weather and community data.
    
    Args:
        weather_data: Weather data from OpenWeatherMap API
        community_reports: DataFrame of community temperature reports
        radius: Radius of heat map points
    
    Returns:
        Folium Map object with heat map
    """
    # Set default coordinates and handle weather data
    if weather_data is None or 'coord' not in weather_data:
        center_lat, center_lon = 40.7128, -74.0060
    else:
        center_lat = weather_data['coord']['lat']
        center_lon = weather_data['coord']['lon']
        
    # Add temperature info to map title
    if weather_data and 'main' in weather_data:
        current_temp = weather_data['main']['temp']
        st.write(f"🌡️ Current Temperature: {current_temp}°C")
    
    # Create a base map centered on the city
    m = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles="cartodb positron")
    
    # Generate heat data
    heat_data = []
    
    # Add community reports to heat data if available
    if not community_reports.empty:
        for _, row in community_reports.iterrows():
            # Each point contains [lat, lon, intensity]
            heat_data.append([row['latitude'], row['longitude'], row['temperature']])
    
    # If no or few community reports, generate some points around the city for visualization
    if len(heat_data) < 10:
        city_name = weather_data.get('name', 'New York') if weather_data else 'New York'
        simulated_coords = generate_coordinates_around_city(city_name, num_points=20)
        
        base_temp = weather_data['main']['temp'] if weather_data and 'main' in weather_data else 25
        
        for coord in simulated_coords:
            # Add some random variation to temperature (-2 to +3 degrees)
            temp_variation = np.random.uniform(-2, 3)
            simulated_temp = base_temp + temp_variation
            
            heat_data.append([coord[0], coord[1], simulated_temp])
    
    # Add heat map layer if we have data
    if heat_data:
        # Add temperature markers
        for point in heat_data:
            temp = point[2]  # Temperature value
            # Choose color based on temperature
            if temp >= 35:
                color = 'red'
            elif temp >= 30:
                color = 'orange'
            elif temp >= 25:
                color = 'yellow'
            else:
                color = 'blue'
            
            folium.CircleMarker(
                location=[point[0], point[1]],
                radius=8,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.7,
                popup=f'Temperature: {temp:.1f}°C'
            ).add_to(m)
        
        # Add wind direction arrow if wind data is available
        if 'wind' in weather_data:
            wind_speed = weather_data['wind'].get('speed', 0)
            wind_deg = weather_data['wind'].get('deg', 0)
            
            center_lat = weather_data['coord']['lat']
            center_lon = weather_data['coord']['lon']
            
            folium.plugins.SemiCircle(
                location=[center_lat, center_lon],
                radius=1000,
                direction=wind_deg,
                arc=30,
                popup=f'Wind: {wind_speed} m/s',
                color='blue',
                fill=True,
                weight=2
            ).add_to(m)
            
            # Add wind speed legend
            legend_html = f'''
                <div style="position: fixed; bottom: 150px; right: 50px; 
                    background-color: white; padding: 10px; border: 1px solid grey;">
                    <p><b>Wind Speed: {wind_speed} m/s</b></p>
                    <p>Direction: {wind_deg}°</p>
                </div>
            '''
            m.get_root().html.add_child(folium.Element(legend_html))
    
    # Add temperature legend
    legend_html = '''
        <div style="position: fixed; bottom: 50px; right: 50px; 
            background-color: white; padding: 10px; border: 1px solid grey;">
            <p><b>Temperature</b></p>
            <p><span style="color: red;">●</span> ≥ 35°C</p>
            <p><span style="color: orange;">●</span> 30-35°C</p>
            <p><span style="color: yellow;">●</span> 25-30°C</p>
            <p><span style="color: blue;">●</span> < 25°C</p>
        </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Add markers for community reports
    if not community_reports.empty:
        for _, row in community_reports.iterrows():
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=f"Temperature: {row['temperature']}°C<br>Time: {row['timestamp']}<br>Notes: {row['description']}",
                icon=folium.Icon(color='green', icon='info-sign')
            ).add_to(m)
    
    # Add legend
    legend_html = '''
        <div style="position: fixed; 
            bottom: 50px; right: 50px; width: 150px; height: 130px; 
            border:2px solid grey; z-index:9999; font-size:12px;
            background-color:white; padding: 10px;
            ">
            <p><b>Temperature (°C)</b></p>
            <div style="display: flex; align-items: center;">
                <div style="width: 20px; height: 20px; background-color: blue;"></div>
                <span style="margin-left: 5px;">< 20</span>
            </div>
            <div style="display: flex; align-items: center;">
                <div style="width: 20px; height: 20px; background-color: green;"></div>
                <span style="margin-left: 5px;">20-25</span>
            </div>
            <div style="display: flex; align-items: center;">
                <div style="width: 20px; height: 20px; background-color: yellow;"></div>
                <span style="margin-left: 5px;">25-30</span>
            </div>
            <div style="display: flex; align-items: center;">
                <div style="width: 20px; height: 20px; background-color: orange;"></div>
                <span style="margin-left: 5px;">30-35</span>
            </div>
            <div style="display: flex; align-items: center;">
                <div style="width: 20px; height: 20px; background-color: red;"></div>
                <span style="margin-left: 5px;">> 35</span>
            </div>
        </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    return m

def create_color_coded_map(data_points, city_name="New York"):
    """
    Create a color-coded map based on temperature values.
    
    Args:
        data_points: DataFrame with latitude, longitude, and temperature columns
        city_name: Name of the city for centering the map
    
    Returns:
        Folium Map object with color-coded markers
    """
    # City center coordinates (approximate)
    city_centers = {
        "New York": [40.7128, -74.0060],
        "Los Angeles": [34.0522, -118.2437],
        "Chicago": [41.8781, -87.6298],
        "Houston": [29.7604, -95.3698],
        "Phoenix": [33.4484, -112.0740],
        "Philadelphia": [39.9526, -75.1652],
        "San Antonio": [29.4241, -98.4936],
        "San Diego": [32.7157, -117.1611],
        "Dallas": [32.7767, -96.7970],
        "San Jose": [37.3382, -121.8863],
        # Indian cities
        "Mumbai": [19.0760, 72.8777],
        "Delhi": [28.6139, 77.2090],
        "Bangalore": [12.9716, 77.5946],
        "Hyderabad": [17.3850, 78.4867],
        "Chennai": [13.0827, 80.2707],
        "Kolkata": [22.5726, 88.3639],
        "Pune": [18.5204, 73.8567],
        "Ahmedabad": [23.0225, 72.5714],
        "Jaipur": [26.9124, 75.7873],
        "Lucknow": [26.8467, 80.9462]
    }
    
    center = city_centers.get(city_name, [40.7128, -74.0060])  # Default to NYC if not found
    
    # Create map
    m = folium.Map(location=center, zoom_start=12, tiles="cartodb positron")
    
    # Define a function to determine color based on temperature
    def get_color(temp):
        if temp < 20:
            return 'blue'
        elif temp < 25:
            return 'green'
        elif temp < 30:
            return 'yellow'
        elif temp < 35:
            return 'orange'
        else:
            return 'red'
    
    # Add color-coded markers for each data point
    if not data_points.empty:
        for _, row in data_points.iterrows():
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=8,
                popup=f"Temperature: {row['temperature']}°C",
                color=get_color(row['temperature']),
                fill=True,
                fill_color=get_color(row['temperature']),
                fill_opacity=0.7
            ).add_to(m)
    
    return m

def create_time_series_plot(data, x_col, y_col, title, color='blue'):
    """
    Create a simple time series line plot using Plotly.
    
    Args:
        data: DataFrame containing the data
        x_col: Column name for x-axis
        y_col: Column name for y-axis
        title: Plot title
        color: Line color
    
    Returns:
        Plotly figure object
    """
    import plotly.express as px
    
    fig = px.line(data, x=x_col, y=y_col, title=title)
    fig.update_traces(line_color=color)
    fig.update_layout(
        xaxis_title=x_col,
        yaxis_title=y_col,
        template="plotly_white"
    )
    
    return fig
