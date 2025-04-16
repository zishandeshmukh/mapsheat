import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from datetime import datetime, timedelta
import random  # for simulating coordinates around a city center, not for mock data

def identify_hotspots(community_reports_df, eps=0.01, min_samples=3, temp_threshold=30):
    """
    Identify heat island hotspots from community temperature reports using DBSCAN clustering.
    
    Args:
        community_reports_df: DataFrame containing community temperature reports
        eps: The maximum distance between two samples for one to be considered in the neighborhood of the other
        min_samples: The number of samples in a neighborhood for a point to be considered a core point
        temp_threshold: Minimum temperature to consider as a potential hotspot
    
    Returns:
        DataFrame containing identified hotspots
    """
    if community_reports_df.empty:
        return None
    
    # Filter for high temperatures only
    high_temp_reports = community_reports_df[community_reports_df['temperature'] >= temp_threshold]
    
    if len(high_temp_reports) < min_samples:
        return pd.DataFrame(columns=['latitude', 'longitude', 'temperature', 'severity'])
    
    # Extract coordinates for clustering
    coords = high_temp_reports[['latitude', 'longitude']].values
    
    # Apply DBSCAN clustering
    clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(coords)
    
    # Add cluster labels to the dataframe
    high_temp_reports = high_temp_reports.copy()
    high_temp_reports['cluster'] = clustering.labels_
    
    # Filter out noise points (cluster = -1)
    clustered_reports = high_temp_reports[high_temp_reports['cluster'] != -1]
    
    if clustered_reports.empty:
        return pd.DataFrame(columns=['latitude', 'longitude', 'temperature', 'severity'])
    
    # Group by cluster and find the hotspot centers
    hotspots = clustered_reports.groupby('cluster').agg({
        'latitude': 'mean',
        'longitude': 'mean',
        'temperature': 'mean'
    }).reset_index()
    
    # Add severity based on temperature
    def calculate_severity(temp):
        if temp >= 35:
            return "Extreme"
        elif temp >= 32:
            return "High"
        else:
            return "Moderate"
    
    hotspots['severity'] = hotspots['temperature'].apply(calculate_severity)
    hotspots['temperature'] = hotspots['temperature'].round(1)
    
    return hotspots[['latitude', 'longitude', 'temperature', 'severity']]

def generate_coordinates_around_city(city_name, num_points=20, radius=0.05):
    """
    Generate a set of coordinates around a city center for testing/simulation purposes.
    
    Args:
        city_name: Name of the city
        num_points: Number of coordinate pairs to generate
        radius: Maximum distance from city center in degrees
    
    Returns:
        List of [latitude, longitude] pairs
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
    
    if city_name not in city_centers:
        # Default to New York if city not found
        city_name = "New York"
    
    city_center = city_centers[city_name]
    
    # Generate random points around the city center
    coordinates = []
    for _ in range(num_points):
        # Random distance and angle from center
        random_distance = radius * np.sqrt(random.random())
        random_angle = 2 * np.pi * random.random()
        
        # Convert polar coordinates to Cartesian
        x_offset = random_distance * np.cos(random_angle)
        y_offset = random_distance * np.sin(random_angle)
        
        # Add offset to city center coordinates
        lat = city_center[0] + y_offset
        lon = city_center[1] + x_offset
        
        coordinates.append([lat, lon])
    
    return coordinates
