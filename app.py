import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
import os
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

# Initialize session state variables if they don't exist
if 'weather_data' not in st.session_state:
    st.session_state.weather_data = None
if 'community_reports' not in st.session_state:
    st.session_state.community_reports = pd.DataFrame(
        columns=['latitude', 'longitude', 'temperature', 'timestamp', 'description', 'reporter']
    )
if 'selected_city' not in st.session_state:
    st.session_state.selected_city = "New York"

# Sidebar
with st.sidebar:
    st.title("Urban Heat Island Analyzer")
    st.write("Analyze and visualize urban heat islands in cities worldwide.")
    
    # City selection
    city_options = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"]
    selected_city = st.selectbox("Select a city:", city_options, index=city_options.index(st.session_state.selected_city))
    
    if selected_city != st.session_state.selected_city:
        st.session_state.selected_city = selected_city
        st.session_state.weather_data = None
    
    # Data refresh button
    if st.button("Refresh Weather Data"):
        with st.spinner("Fetching latest weather data..."):
            st.session_state.weather_data = get_weather_data(selected_city)
            st.success(f"Weather data for {selected_city} updated!")
    
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
    # Fetch weather data if not already in session state
    if st.session_state.weather_data is None:
        with st.spinner("Fetching weather data..."):
            st.session_state.weather_data = get_weather_data(st.session_state.selected_city)
    
    if st.session_state.weather_data is not None:
        # Create the base map centered on the city
        m = create_heatmap(st.session_state.weather_data, st.session_state.community_reports)
        
        # Display the map
        st.subheader("Current Temperature Distribution")
        folium_static(m, width=1000, height=600)
        
        # Display weather information
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
    else:
        st.error("Failed to fetch weather data. Please try again.")

with tab2:
    st.info("Satellite imagery integration is under development.")
    
    # Placeholder for satellite imagery
    st.subheader("Satellite View")
    
    # Using Mapbox for basic satellite view
    m = folium.Map(
        location=[40.7128, -74.0060] if st.session_state.selected_city == "New York" else [34.0522, -118.2437],
        zoom_start=12,
        tiles="https://api.mapbox.com/styles/v1/mapbox/satellite-v9/tiles/{z}/{x}/{y}?access_token=" + 
              os.getenv("MAPBOX_TOKEN", "pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw"),
        attr='Mapbox'
    )
    
    folium_static(m, width=1000, height=600)
    
    st.write("Satellite imagery can help identify surface materials that contribute to heat islands, such as dark roofs, asphalt, and areas lacking vegetation.")

with tab3:
    st.subheader("Community Temperature Reports")
    
    if not st.session_state.community_reports.empty:
        # Display community reports as a table
        st.dataframe(
            st.session_state.community_reports[['latitude', 'longitude', 'temperature', 'timestamp', 'description']],
            use_container_width=True,
            hide_index=True
        )
        
        # Identify and display hotspots
        if len(st.session_state.community_reports) >= 3:  # Need minimum points for clustering
            hotspots = identify_hotspots(st.session_state.community_reports)
            if hotspots is not None and not hotspots.empty:
                st.subheader("Identified Heat Island Hotspots")
                st.dataframe(hotspots, use_container_width=True, hide_index=True)
                
                # Show the hotspots on a map
                m = folium.Map(location=[hotspots['latitude'].mean(), hotspots['longitude'].mean()], zoom_start=12)
                
                # Add markers for hotspots
                for idx, row in hotspots.iterrows():
                    folium.Marker(
                        location=[row['latitude'], row['longitude']],
                        popup=f"Hotspot: {row['temperature']}°C",
                        icon=folium.Icon(color='red', icon='fire', prefix='fa')
                    ).add_to(m)
                
                folium_static(m, width=1000, height=400)
                
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
