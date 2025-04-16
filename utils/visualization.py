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
    # Set default coordinates (New York) if weather data is None
    if weather_data is None or 'coord' not in weather_data:
        center_lat, center_lon = 40.7128, -74.0060
    else:
        center_lat = weather_data['coord']['lat']
        center_lon = weather_data['coord']['lon']
    
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
        HeatMap(
            heat_data,
            radius=radius,
            min_opacity=0.4,
            blur=15,
            gradient={
                0.2: 'blue',
                0.4: 'green',
                0.6: 'yellow',
                0.8: 'orange',
                1.0: 'red'
            },
            max_val=40,  # Adjust based on expected maximum temperature
        ).add_to(m)
    
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
        "San Jose": [37.3382, -121.8863]
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
