import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import os
import time
from utils.api_handlers import get_weather_data
from utils.visualization import create_heatmap
from utils.data_processing import identify_hotspots

# Set page configuration
st.set_page_config(
    page_title="Urban Heat Island Analyzer",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cache this function so it does NOT re-run on every rerender
@st.cache_resource(ttl=60)  # Set to 1 minute refresh
def get_app_version():
    """This function is called once at startup and helps stabilize the app"""
    return int(time.time())

# Call the cache function to stabilize the app
APP_VERSION = get_app_version()

# Define callbacks for button clicks
def fetch_weather_data():
    """Callback for fetching weather data"""
    with st.spinner(f"Fetching weather data for {st.session_state.selected_city}..."):
        weather_data = get_weather_data(st.session_state.selected_city)
        if weather_data:
            st.session_state.weather_data = weather_data
            st.session_state.data_stale = False
            st.session_state.refresh_needed = True
            st.rerun()
        else:
            st.error("Failed to fetch weather data. Please try again.")

def load_satellite_view():
    """Callback for loading satellite view"""
    st.session_state.satellite_loaded = True
    st.toast("✅ Satellite view loaded")

def load_community_reports():
    """Callback for loading community reports"""
    st.session_state.reports_loaded = True
    st.toast("✅ Community reports loaded")

def change_city(selected_city):
    """Safely handle city change without triggering auto-refreshes"""
    if selected_city != st.session_state.selected_city:
        st.session_state.selected_city = selected_city
        st.session_state.data_stale = True
        st.session_state.satellite_loaded = False
        st.session_state.reports_loaded = False

# Initialize session state variables if they don't exist
if 'weather_data' not in st.session_state:
    st.session_state.weather_data = None
if 'community_reports' not in st.session_state:
    st.session_state.community_reports = pd.DataFrame(
        columns=['latitude', 'longitude', 'temperature', 'timestamp', 'description', 'reporter']
    )
if 'selected_city' not in st.session_state:
    st.session_state.selected_city = "New York"
if 'data_stale' not in st.session_state:
    st.session_state.data_stale = False
if 'satellite_loaded' not in st.session_state:
    st.session_state.satellite_loaded = False
if 'reports_loaded' not in st.session_state:
    st.session_state.reports_loaded = False

# Sidebar
with st.sidebar:
    st.title("Urban Heat Island Analyzer")
    st.write("Analyze and visualize urban heat islands in cities worldwide.")
    
    # City selection
    city_options = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose", 
                  "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Lucknow"]
    
    # Group cities by region
    us_cities = city_options[:10]
    indian_cities = city_options[10:]
    
    # Create region selector
    region = st.radio("Select Region:", ["US Cities", "Indian Cities"], 
                    index=0 if st.session_state.selected_city in us_cities else 1,
                    horizontal=True, key=f"region_{APP_VERSION}")
    
    # Show appropriate city selector based on region choice
    if region == "US Cities":
        selected_city = st.selectbox("Select a US city:", us_cities, 
                                 index=us_cities.index(st.session_state.selected_city) if st.session_state.selected_city in us_cities else 0,
                                 key=f"us_city_{APP_VERSION}")
    else:
        selected_city = st.selectbox("Select an Indian city:", indian_cities,
                                 index=indian_cities.index(st.session_state.selected_city) if st.session_state.selected_city in indian_cities else 0,
                                 key=f"india_city_{APP_VERSION}")
    
    # Use our function to handle city change
    if selected_city != st.session_state.selected_city:
        change_city(selected_city)
    
    # Data refresh button
    if st.button("Refresh Weather Data", key=f"sidebar_refresh_{APP_VERSION}"):
        fetch_weather_data()
    
    st.divider()
    
    # Navigation
    st.subheader("Navigation")
    st.page_link("app.py", label="Home", icon="🏠")
    st.page_link("pages/community_input.py", label="Community Input", icon="📝")
    st.page_link("pages/analysis.py", label="Heat Island Analysis", icon="📊")
    st.page_link("pages/about.py", label="About", icon="ℹ️")

# Main content
st.title(f"Urban Heat Map: {st.session_state.selected_city}")

# Tabs for different views
tab1, tab2, tab3 = st.tabs(["Temperature Map", "Satellite View", "Community Reports"])

with tab1:
    # Add a fetch button for weather data
    col1, col2 = st.columns([1, 4])
    with col1:
        fetch_data = st.button("Fetch Data", type="primary", key=f"fetch_main_data_{APP_VERSION}", on_click=fetch_weather_data)
    
    if st.session_state.weather_data is None:
        st.info("Click the 'Fetch Data' button to load the weather data and map.")
    elif st.session_state.data_stale:
        st.warning(f"You changed the city to {st.session_state.selected_city}. Click 'Fetch Data' to get updated data.")
    
    if st.session_state.weather_data is not None and not st.session_state.data_stale:
        # Only create and display the map when data is fetched
        st.subheader("Current Temperature Distribution")
        
        # Create static heatmap
        if 'heatmap' not in st.session_state or st.session_state.get('refresh_needed', True):
            st.session_state.heatmap = create_heatmap(st.session_state.weather_data, st.session_state.community_reports)
            st.session_state.refresh_needed = False
        
        # Display the map
        st_folium(st.session_state.heatmap, height=600, key="static_heatmap")
        
        # Display weather information in a more prominent way
        st.subheader(f"Temperature Details for {st.session_state.selected_city}")
        col1, col2 = st.columns(2)
        with col1:
            if 'main' in st.session_state.weather_data and 'temp' in st.session_state.weather_data['main']:
                st.metric("Current Temperature", f"{st.session_state.weather_data['main']['temp']}°C")
            if 'main' in st.session_state.weather_data and 'humidity' in st.session_state.weather_data['main']:
                st.metric("Humidity", f"{st.session_state.weather_data['main']['humidity']}%")
        with col2:
            if 'main' in st.session_state.weather_data and 'feels_like' in st.session_state.weather_data['main']:
                st.metric("Feels Like", f"{st.session_state.weather_data['main']['feels_like']}°C")
            if 'wind' in st.session_state.weather_data and 'speed' in st.session_state.weather_data['wind']:
                st.metric("Wind Speed", f"{st.session_state.weather_data['wind']['speed']} m/s")

with tab2:
    st.info("Satellite imagery integration is under development.")
    
    # Placeholder for satellite imagery
    st.subheader("Satellite View")
    
    # Add a fetch button for satellite view
    col1, col2 = st.columns([1, 4])
    with col1:
        load_satellite = st.button("Load Satellite", type="primary", key=f"load_satellite_{APP_VERSION}", on_click=load_satellite_view)
    
    # Get city coordinates based on selected city
    if st.session_state.satellite_loaded:
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
        
        city_location = city_centers.get(st.session_state.selected_city, [40.7128, -74.0060])
        
        # Using a free satellite view tile provider
        m = folium.Map(
            location=city_location,
            zoom_start=12,
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attr='Esri World Imagery'
        )
        
        st_folium(m, width=1000, height=600, key=f"satellite_map_{APP_VERSION}")
    else:
        st.info("Click 'Load Satellite' button to display the satellite imagery.")
    
    st.write("Satellite imagery can help identify surface materials that contribute to heat islands, such as dark roofs, asphalt, and areas lacking vegetation.")

with tab3:
    st.subheader("Community Temperature Reports")
    
    # Add a fetch button for community reports view
    col1, col2 = st.columns([1, 4])
    with col1:
        load_reports = st.button("Load Reports", type="primary", key=f"load_reports_{APP_VERSION}", on_click=load_community_reports)
    
    if not st.session_state.reports_loaded:
        st.info("Click 'Load Reports' button to display community temperature reports and hotspots.")
    
    elif not st.session_state.community_reports.empty and st.session_state.reports_loaded:
        # Display community reports as a table
        st.dataframe(
            st.session_state.community_reports[['latitude', 'longitude', 'temperature', 'timestamp', 'description']],
            use_container_width=True,
            hide_index=True,
            key=f"reports_table_{APP_VERSION}"
        )
        
        # Identify and display hotspots
        if len(st.session_state.community_reports) >= 3:  # Need minimum points for clustering
            hotspots = identify_hotspots(st.session_state.community_reports)
            if hotspots is not None and not hotspots.empty:
                st.subheader("Identified Heat Island Hotspots")
                st.dataframe(hotspots, use_container_width=True, hide_index=True, key=f"hotspots_table_{APP_VERSION}")
                
                # Show the hotspots on a map
                m = folium.Map(location=[hotspots['latitude'].mean(), hotspots['longitude'].mean()], zoom_start=12)
                
                # Add markers for hotspots
                for idx, row in hotspots.iterrows():
                    folium.Marker(
                        location=[row['latitude'], row['longitude']],
                        popup=f"Hotspot: {row['temperature']}°C",
                        icon=folium.Icon(color='red', icon='fire', prefix='fa')
                    ).add_to(m)
                
                st_folium(m, width=1000, height=400, key=f"hotspots_map_{APP_VERSION}")
                
                # Recommendations based on hotspots
                st.subheader("Eco-Friendly Interventions")
                st.write("Based on the identified hotspots, here are some recommended interventions:")
                
                interventions = [
                    "Increase urban tree canopy in hotspot areas",
                    "Install green roofs on buildings in affected zones",
                    "Use cool pavement technologies in high-temperature streets",
                    "Create pocket parks in dense urban areas",
                    "Implement reflective roofing materials in commercial districts"
                ]
                
                for i, intervention in enumerate(interventions, 1):
                    st.write(f"{i}. {intervention}")
    else:
        st.info("No community reports available yet. Go to the 'Community Input' page to submit your observations.")

# Footer
st.divider()
st.markdown("### Help us map urban heat islands!")
st.write("By collecting temperature data from community members, we can create more accurate heat maps and better identify urban heat islands.")
st.write("Click on 'Community Input' in the sidebar to contribute your observations.")