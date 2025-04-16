import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
from datetime import datetime
import json
from utils.api_handlers import add_community_report
from utils.visualization import create_color_coded_map

st.set_page_config(
    page_title="Community Input | Urban Heat Island Analyzer",
    page_icon="🌡️",
    layout="wide"
)

# Initialize session state for community reports if not already initialized
if 'community_reports' not in st.session_state:
    st.session_state.community_reports = pd.DataFrame(
        columns=['latitude', 'longitude', 'temperature', 'timestamp', 'description', 'reporter']
    )

# Initialize map state
if 'selected_location' not in st.session_state:
    st.session_state.selected_location = None

# Sidebar
with st.sidebar:
    st.title("Urban Heat Island Analyzer")
    st.write("Analyze and visualize urban heat islands in cities worldwide.")
    
    # Navigation
    st.subheader("Navigation")
    st.page_link("app.py", label="Home", icon="🏠")
    st.page_link("pages/community_input.py", label="Community Input", icon="📝")
    st.page_link("pages/analysis.py", label="Heat Island Analysis", icon="📊")
    st.page_link("pages/about.py", label="About", icon="ℹ️")

# Main content
st.title("Community Temperature Reporting")
st.write("Help us map urban heat islands by submitting your local temperature observations.")

# Tabs for input and viewing
tab1, tab2 = st.tabs(["Submit Report", "View Your Reports"])

with tab1:
    st.subheader("Submit a Temperature Report")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("Select your location on the map by clicking where you want to report the temperature.")
        
        # Create a map for location selection
        m = folium.Map(location=[40.7128, -74.0060], zoom_start=12)
        
        # Add a callback for clicking on the map
        m.add_child(folium.LatLngPopup())
        
        # Display the map
        map_data = folium_static(m, width=600, height=400, returned_objects=True)
        
        # Check if a location was selected
        if map_data and "last_clicked" in map_data and map_data["last_clicked"]:
            st.session_state.selected_location = map_data["last_clicked"]
            st.success(f"Location selected: {st.session_state.selected_location}")
        
        st.write("Or enter coordinates manually:")
        col1a, col1b = st.columns(2)
        with col1a:
            latitude = st.number_input("Latitude", min_value=-90.0, max_value=90.0, 
                                       value=st.session_state.selected_location[0] if st.session_state.selected_location else 40.7128,
                                       format="%.6f")
        with col1b:
            longitude = st.number_input("Longitude", min_value=-180.0, max_value=180.0, 
                                        value=st.session_state.selected_location[1] if st.session_state.selected_location else -74.0060,
                                        format="%.6f")
    
    with col2:
        st.write("Enter temperature details:")
        
        temperature = st.number_input("Temperature (°C)", min_value=-50.0, max_value=60.0, value=25.0, step=0.1)
        
        time_options = ["Now", "Custom"]
        time_choice = st.radio("Time of measurement:", time_options)
        
        if time_choice == "Custom":
            report_date = st.date_input("Date", value=datetime.now().date())
            report_time = st.time_input("Time", value=datetime.now().time())
            timestamp = datetime.combine(report_date, report_time).strftime("%Y-%m-%d %H:%M:%S")
        else:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        description = st.text_area("Location description (optional)", 
                                  placeholder="E.g., Downtown park, Concrete parking lot, Residential area with trees, etc.")
        
        reporter = st.text_input("Your name (optional)", value="Anonymous")
    
    if st.button("Submit Temperature Report", type="primary"):
        # Validate input
        if temperature < -50 or temperature > 60:
            st.error("Please enter a valid temperature between -50°C and 60°C.")
        else:
            # Add the report
            success = add_community_report(
                lat=latitude,
                lon=longitude,
                temperature=temperature,
                description=description,
                reporter=reporter
            )
            
            if success:
                st.success("Thank you for your temperature report! It has been added to our database.")
                st.balloons()
            else:
                st.error("There was an error submitting your report. Please try again.")

with tab2:
    st.subheader("Your Submitted Reports")
    
    if st.session_state.community_reports.empty:
        st.info("You haven't submitted any temperature reports yet. Use the 'Submit Report' tab to add data.")
    else:
        # Display reports in a table
        st.dataframe(
            st.session_state.community_reports[['latitude', 'longitude', 'temperature', 'timestamp', 'description']],
            use_container_width=True,
            hide_index=True
        )
        
        # Show reports on a map
        st.subheader("Map of Your Reports")
        
        # Create a color-coded map of reports
        report_map = create_color_coded_map(st.session_state.community_reports)
        
        # Display the map
        folium_static(report_map, width=800, height=500)
        
        # Option to download data
        st.download_button(
            "Download Your Reports (JSON)",
            data=st.session_state.community_reports.to_json(orient="records"),
            file_name="temperature_reports.json",
            mime="application/json"
        )

# Information about the importance of community data
st.divider()
st.subheader("Why Your Reports Matter")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### The Power of Citizen Science
    
    Your temperature reports help us:
    
    - **Create accurate heat maps** that identify urban heat islands
    - **Track temperature changes** over time and in different weather conditions
    - **Validate satellite data** with ground-level measurements
    - **Target interventions** in the areas most affected by extreme heat
    - **Engage communities** in climate resilience efforts
    """)

with col2:
    st.markdown("""
    ### Tips for Accurate Reporting
    
    For the most useful data, please:
    
    - Measure temperature in an open space, away from direct sources of heat or cooling
    - Take measurements at approximately 1.5 meters (5 feet) above the ground
    - Use a reliable thermometer or weather app that shows your exact location's temperature
    - Include details about the surrounding environment (pavement, grass, trees, buildings)
    - Report at different times of day when possible (morning, afternoon, evening)
    """)

# Footer
st.divider()
st.write("© 2023 Urban Heat Island Analyzer - Thank you for contributing to our community science project!")
