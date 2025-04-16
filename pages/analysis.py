import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
from utils.data_processing import identify_hotspots
from utils.api_handlers import get_forecast_data
from utils.visualization import create_heatmap, create_time_series_plot

st.set_page_config(
    page_title="Analysis | Urban Heat Island Analyzer",
    page_icon="🌡️",
    layout="wide"
)

# Initialize session state variables if they don't exist
if 'community_reports' not in st.session_state:
    st.session_state.community_reports = pd.DataFrame(
        columns=['latitude', 'longitude', 'temperature', 'timestamp', 'description', 'reporter']
    )
if 'selected_city' not in st.session_state:
    st.session_state.selected_city = "New York"
if 'forecast_data' not in st.session_state:
    st.session_state.forecast_data = None

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
                    horizontal=True)
    
    # Show appropriate city selector based on region choice
    if region == "US Cities":
        selected_city = st.selectbox("Select a US city:", us_cities, 
                                  index=us_cities.index(st.session_state.selected_city) if st.session_state.selected_city in us_cities else 0)
    else:
        selected_city = st.selectbox("Select an Indian city:", indian_cities,
                                  index=indian_cities.index(st.session_state.selected_city) if st.session_state.selected_city in indian_cities else 0)
    
    if selected_city != st.session_state.selected_city:
        st.session_state.selected_city = selected_city
        st.session_state.forecast_data = None
    
    # Data refresh button
    if st.button("Refresh Forecast Data"):
        with st.spinner("Fetching forecast data..."):
            st.session_state.forecast_data = get_forecast_data(selected_city)
            if st.session_state.forecast_data:
                st.success(f"Forecast data for {selected_city} updated!")
            else:
                st.error("Failed to fetch forecast data. Please try again.")
    
    # Navigation
    st.subheader("Navigation")
    st.page_link("app.py", label="Home", icon="🏠")
    st.page_link("pages/community_input.py", label="Community Input", icon="📝")
    st.page_link("pages/analysis.py", label="Heat Island Analysis", icon="📊")
    st.page_link("pages/about.py", label="About", icon="ℹ️")

# Main content
st.title("Urban Heat Island Analysis")

# Tabs for different analyses
tab1, tab2, tab3 = st.tabs(["Hotspot Identification", "Temperature Forecast", "Mitigation Strategies"])

with tab1:
    st.subheader(f"Heat Island Hotspots in {st.session_state.selected_city}")
    
    # Check if we have enough community reports for clustering
    if len(st.session_state.community_reports) < 3:
        st.info("We need more community temperature reports to identify heat island hotspots accurately. Please contribute by adding your observations on the Community Input page.")
        
        # Get city location for the map
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
        
        # Show a placeholder map
        m = folium.Map(
            location=city_location,
            zoom_start=12,
            tiles="cartodb positron"
        )
        st_folium(m, width=800, height=500)
    else:
        # Identify hotspots
        hotspots = identify_hotspots(st.session_state.community_reports)
        
        if hotspots is not None and not hotspots.empty:
            # Display hotspots table
            st.write("Identified urban heat island hotspots based on community temperature reports:")
            st.dataframe(hotspots, use_container_width=True, hide_index=True)
            
            # Show hotspots on a map
            st.write("Hotspot locations:")
            
            # Create base map centered on average hotspot location
            m = folium.Map(
                location=[hotspots['latitude'].mean(), hotspots['longitude'].mean()],
                zoom_start=12,
                tiles="cartodb positron"
            )
            
            # Add markers for each hotspot
            for idx, row in hotspots.iterrows():
                # Color based on severity
                if row['severity'] == "Extreme":
                    color = "red"
                elif row['severity'] == "High":
                    color = "orange"
                else:
                    color = "yellow"
                
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=15,
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.7,
                    popup=f"Temperature: {row['temperature']}°C<br>Severity: {row['severity']}"
                ).add_to(m)
            
            # Add all community reports as small markers
            for idx, row in st.session_state.community_reports.iterrows():
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=5,
                    color='blue',
                    fill=True,
                    fill_color='blue',
                    fill_opacity=0.5,
                    popup=f"Temperature: {row['temperature']}°C<br>Time: {row['timestamp']}"
                ).add_to(m)
            
            # Display the map
            st_folium(m, width=800, height=500)
            
            # Analysis of factors contributing to heat islands
            st.subheader("Contributing Factors Analysis")
            
            # Mocked up analysis for demonstration
            st.write("Based on the identified hotspots, here are the likely contributing factors:")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Surface materials chart
                materials_data = pd.DataFrame({
                    'Material': ['Asphalt', 'Concrete', 'Buildings', 'Vegetation', 'Water'],
                    'Percentage': [40, 30, 20, 8, 2]
                })
                
                fig = px.pie(
                    materials_data, 
                    values='Percentage', 
                    names='Material',
                    title='Surface Material Composition',
                    color_discrete_sequence=px.colors.sequential.Viridis
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Temperature variation by time
                hours = list(range(24))
                temps = [22, 21, 20, 20, 19, 19, 20, 22, 24, 26, 28, 30, 31, 32, 32, 31, 30, 29, 27, 26, 25, 24, 23, 22]
                urban_temps = [26, 25, 24, 23, 23, 22, 23, 24, 26, 28, 30, 32, 34, 35, 35, 34, 33, 32, 30, 29, 28, 28, 27, 26]
                
                time_data = pd.DataFrame({
                    'Hour': hours,
                    'Suburban Temperature': temps,
                    'Urban Temperature': urban_temps
                })
                
                fig = px.line(
                    time_data, 
                    x='Hour', 
                    y=['Suburban Temperature', 'Urban Temperature'],
                    title='Urban vs. Suburban Temperature Variation',
                    labels={'value': 'Temperature (°C)', 'variable': 'Location'},
                    color_discrete_sequence=['blue', 'red']
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No significant heat island hotspots identified in the current data. Add more temperature reports for better analysis.")

with tab2:
    st.subheader(f"Temperature Forecast for {st.session_state.selected_city}")
    
    # Fetch forecast data if not already in session state
    if st.session_state.forecast_data is None:
        with st.spinner("Fetching forecast data..."):
            st.session_state.forecast_data = get_forecast_data(st.session_state.selected_city)
    
    if st.session_state.forecast_data is not None and 'list' in st.session_state.forecast_data:
        # Process the forecast data
        forecast_list = st.session_state.forecast_data['list']
        
        # Extract timestamps and temperatures
        timestamps = []
        temperatures = []
        feels_like = []
        humidity = []
        
        for item in forecast_list:
            # Convert timestamp to datetime
            dt = datetime.fromtimestamp(item['dt'])
            timestamps.append(dt)
            
            # Extract temperature data
            temperatures.append(item['main']['temp'])
            feels_like.append(item['main']['feels_like'])
            humidity.append(item['main']['humidity'])
        
        # Create a DataFrame for the forecast
        forecast_df = pd.DataFrame({
            'timestamp': timestamps,
            'temperature': temperatures,
            'feels_like': feels_like,
            'humidity': humidity
        })
        
        # Display the forecast
        st.write("5-day temperature forecast:")
        
        # Create temperature forecast chart
        fig_temp = create_time_series_plot(
            forecast_df, 
            'timestamp', 
            'temperature', 
            'Temperature Forecast (°C)',
            'red'
        )
        st.plotly_chart(fig_temp, use_container_width=True)
        
        # Create feels like chart
        fig_feels = create_time_series_plot(
            forecast_df, 
            'timestamp', 
            'feels_like', 
            'Feels Like Temperature (°C)',
            'orange'
        )
        
        # Create humidity chart
        fig_humidity = create_time_series_plot(
            forecast_df, 
            'timestamp', 
            'humidity', 
            'Humidity (%)',
            'blue'
        )
        
        # Display charts side by side
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig_feels, use_container_width=True)
        with col2:
            st.plotly_chart(fig_humidity, use_container_width=True)
        
        # Show forecast table
        with st.expander("Show detailed forecast data"):
            # Format the timestamp for display
            forecast_df['Date'] = forecast_df['timestamp'].dt.strftime('%Y-%m-%d')
            forecast_df['Time'] = forecast_df['timestamp'].dt.strftime('%H:%M')
            
            # Display the table
            st.dataframe(
                forecast_df[['Date', 'Time', 'temperature', 'feels_like', 'humidity']].rename(
                    columns={
                        'temperature': 'Temperature (°C)',
                        'feels_like': 'Feels Like (°C)',
                        'humidity': 'Humidity (%)'
                    }
                ),
                use_container_width=True,
                hide_index=True
            )
    else:
        st.error("Failed to fetch forecast data. Please try refreshing the data.")

with tab3:
    st.subheader("Heat Island Mitigation Strategies")
    
    # Explanation of different mitigation strategies
    st.write("""
    Urban heat islands can be mitigated through various strategies. Below are some of the most effective 
    approaches that can be implemented in urban areas to reduce the heat island effect.
    """)
    
    # Mitigation categories
    mitigation_categories = [
        "Green Infrastructure", 
        "Cool Materials", 
        "Urban Design", 
        "Water Management",
        "Policy Measures"
    ]
    selected_category = st.selectbox("Select mitigation category:", mitigation_categories)
    
    # Content based on selected category
    if selected_category == "Green Infrastructure":
        st.markdown("""
        ### Green Infrastructure Solutions
        
        **1. Urban Forestry and Tree Planting**
        - Trees provide shade and reduce ambient temperatures through evapotranspiration
        - Strategic placement can reduce building energy consumption by 25-40%
        - Prioritize planting in areas with high pedestrian activity and vulnerable populations
        
        **2. Green Roofs**
        - Living vegetation installed on rooftops
        - Can reduce roof temperatures by 30-40°C compared to conventional roofs
        - Provide additional benefits: stormwater management, air quality improvement, extended roof life
        
        **3. Green Walls/Vertical Gardens**
        - Vegetation systems attached to building facades
        - Can reduce wall surface temperatures by 15-30°C
        - Particularly effective in dense urban areas with limited horizontal space
        
        **4. Urban Parks and Open Spaces**
        - Larger green spaces create "cool islands" within cities
        - A park of 1-2 hectares can be 1-2°C cooler than surrounding urban areas
        - Network of small parks and corridors can extend cooling effects throughout a city
        """)
        
        # Display an image of green infrastructure
        st.markdown("""
        <div style="text-align: center;">
            <svg width="700" height="300" xmlns="http://www.w3.org/2000/svg">
                <!-- Background sky -->
                <rect width="700" height="300" fill="#E1F5FE" />
                
                <!-- Ground -->
                <rect x="0" y="250" width="700" height="50" fill="#AED581" />
                
                <!-- Buildings -->
                <g>
                    <!-- Building 1 with green roof -->
                    <rect x="50" y="100" width="100" height="150" fill="#B0BEC5" />
                    <rect x="50" y="100" width="100" height="20" fill="#7CB342" /> <!-- Green roof -->
                    
                    <!-- Windows -->
                    <rect x="65" y="130" width="15" height="15" fill="#E3F2FD" />
                    <rect x="90" y="130" width="15" height="15" fill="#E3F2FD" />
                    <rect x="115" y="130" width="15" height="15" fill="#E3F2FD" />
                    
                    <rect x="65" y="160" width="15" height="15" fill="#E3F2FD" />
                    <rect x="90" y="160" width="15" height="15" fill="#E3F2FD" />
                    <rect x="115" y="160" width="15" height="15" fill="#E3F2FD" />
                    
                    <rect x="65" y="190" width="15" height="15" fill="#E3F2FD" />
                    <rect x="90" y="190" width="15" height="15" fill="#E3F2FD" />
                    <rect x="115" y="190" width="15" height="15" fill="#E3F2FD" />
                    
                    <rect x="65" y="220" width="15" height="15" fill="#E3F2FD" />
                    <rect x="90" y="220" width="15" height="15" fill="#E3F2FD" />
                    <rect x="115" y="220" width="15" height="15" fill="#E3F2FD" />
                </g>
                
                <!-- Building 2 with green wall -->
                <g>
                    <rect x="180" y="120" width="120" height="130" fill="#B0BEC5" />
                    <!-- Green wall -->
                    <rect x="180" y="120" width="15" height="130" fill="#7CB342" />
                    
                    <!-- Windows -->
                    <rect x="205" y="135" width="20" height="15" fill="#E3F2FD" />
                    <rect x="235" y="135" width="20" height="15" fill="#E3F2FD" />
                    <rect x="265" y="135" width="20" height="15" fill="#E3F2FD" />
                    
                    <rect x="205" y="160" width="20" height="15" fill="#E3F2FD" />
                    <rect x="235" y="160" width="20" height="15" fill="#E3F2FD" />
                    <rect x="265" y="160" width="20" height="15" fill="#E3F2FD" />
                    
                    <rect x="205" y="185" width="20" height="15" fill="#E3F2FD" />
                    <rect x="235" y="185" width="20" height="15" fill="#E3F2FD" />
                    <rect x="265" y="185" width="20" height="15" fill="#E3F2FD" />
                    
                    <rect x="205" y="210" width="20" height="15" fill="#E3F2FD" />
                    <rect x="235" y="210" width="20" height="15" fill="#E3F2FD" />
                    <rect x="265" y="210" width="20" height="15" fill="#E3F2FD" />
                </g>
                
                <!-- Trees -->
                <g>
                    <!-- Tree 1 -->
                    <circle cx="350" cy="180" r="40" fill="#66BB6A" />
                    <rect x="345" y="220" width="10" height="30" fill="#795548" />
                    
                    <!-- Tree 2 -->
                    <circle cx="420" cy="200" r="30" fill="#66BB6A" />
                    <rect x="415" y="230" width="10" height="20" fill="#795548" />
                    
                    <!-- Tree 3 -->
                    <circle cx="480" cy="190" r="35" fill="#66BB6A" />
                    <rect x="475" y="225" width="10" height="25" fill="#795548" />
                    
                    <!-- Tree 4 -->
                    <circle cx="550" cy="170" r="45" fill="#66BB6A" />
                    <rect x="545" y="215" width="10" height="35" fill="#795548" />
                    
                    <!-- Tree 5 -->
                    <circle cx="630" cy="185" r="35" fill="#66BB6A" />
                    <rect x="625" y="220" width="10" height="30" fill="#795548" />
                </g>
                
                <!-- Park area -->
                <g>
                    <ellipse cx="500" cy="245" rx="180" ry="15" fill="#81C784" />
                </g>
                
                <!-- Cool effects visualized -->
                <g opacity="0.5">
                    <path d="M350,140 Q380,110 410,140 Q440,170 470,140 Q500,110 530,140" stroke="#29B6F6" stroke-width="5" fill="none" />
                    <path d="M345,160 Q375,130 405,160 Q435,190 465,160 Q495,130 525,160" stroke="#29B6F6" stroke-width="4" fill="none" />
                    <path d="M340,180 Q370,150 400,180 Q430,210 460,180 Q490,150 520,180" stroke="#29B6F6" stroke-width="3" fill="none" />
                </g>
                
                <!-- Labels -->
                <g font-family="Arial" font-size="10" fill="#000000">
                    <text x="60" y="95" text-anchor="middle">Green Roof</text>
                    <text x="180" y="110" text-anchor="start">Green Wall</text>
                    <text x="450" y="260" text-anchor="middle">Urban Park Area</text>
                    <text x="450" y="120" text-anchor="middle" font-size="12" font-weight="bold">Green Infrastructure for Urban Cooling</text>
                </g>
            </svg>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("Green infrastructure not only reduces urban heat islands but also provides numerous co-benefits including improved air quality, enhanced biodiversity, and better stormwater management.")
        
    elif selected_category == "Cool Materials":
        st.markdown("""
        ### Cool Materials Solutions
        
        **1. Cool Roofs**
        - High solar reflectance and thermal emittance materials
        - Can reduce roof surface temperatures by 28-33°C during summer
        - Options include cool coatings, single-ply membranes, and reflective roof tiles
        
        **2. Cool Pavements**
        - Reflective or permeable pavements that stay cooler than conventional materials
        - Can reduce surface temperatures by 11-22°C
        - Includes reflective coatings, permeable concrete, and light-colored aggregates
        
        **3. Reflective Walls**
        - Light-colored or specially coated building facades
        - Can reduce wall surface temperatures by 8-15°C
        - Most effective on east and west-facing walls that receive intense sun exposure
        
        **4. Permeable Surfaces**
        - Allow water infiltration and storage
        - Increased evaporation creates cooling effect
        - Examples include permeable pavers, porous asphalt, and pervious concrete
        """)
        
        # Display a comparison chart
        cool_materials_data = pd.DataFrame({
            'Material Type': ['Conventional Dark Roof', 'Cool Roof', 'Conventional Asphalt', 'Cool Pavement', 'Green Roof'],
            'Peak Surface Temperature (°C)': [80, 45, 65, 40, 35],
            'Solar Reflectance (%)': [5, 70, 10, 50, 20]
        })
        
        fig = px.bar(
            cool_materials_data, 
            x='Material Type', 
            y=['Peak Surface Temperature (°C)', 'Solar Reflectance (%)'],
            barmode='group',
            title='Comparison of Conventional vs. Cool Materials',
            labels={'value': 'Value', 'variable': 'Metric'},
            color_discrete_sequence=['#FF5252', '#42A5F5']
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.write("Implementing cool materials is often the most cost-effective approach for existing buildings and infrastructure, with significant energy savings potential.")
        
    elif selected_category == "Urban Design":
        st.markdown("""
        ### Urban Design Solutions
        
        **1. Street Canyon Design**
        - Optimize the height-to-width ratio of street canyons
        - Orientation of streets to maximize ventilation
        - Can reduce air temperature by 1-2°C through improved airflow
        
        **2. Strategic Shading**
        - Architectural features like awnings, canopies, and pergolas
        - Reduce direct solar radiation on buildings and pedestrian areas
        - Can reduce surface temperatures by 10-15°C in shaded areas
        
        **3. Urban Water Features**
        - Fountains, ponds, and water installations
        - Cooling through evaporation and increased humidity
        - Can reduce surrounding air temperatures by 2-4°C
        
        **4. Wind Corridor Planning**
        - Design cities to channel prevailing winds
        - Improved ventilation disperses heat and pollutants
        - Building height variations and open spaces create pressure differences that enhance airflow
        """)
        
        # Display urban design factors
        st.write("Impact of different urban design factors on local temperature reduction:")
        
        design_factors = pd.DataFrame({
            'Factor': ['Building Orientation', 'Street Width', 'Urban Parks', 'Water Features', 'Wind Corridors', 'Building Materials'],
            'Temperature Reduction (°C)': [1.2, 0.8, 2.5, 1.7, 1.0, 3.2]
        })
        
        fig = px.bar(
            design_factors, 
            x='Factor', 
            y='Temperature Reduction (°C)',
            title='Impact of Urban Design Factors on Temperature Reduction',
            color='Temperature Reduction (°C)',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.write("Effective urban design requires integrated planning across multiple scales, from individual buildings to district and city levels.")
        
    elif selected_category == "Water Management":
        st.markdown("""
        ### Water Management Solutions
        
        **1. Retention Ponds and Wetlands**
        - Collect and store stormwater
        - Provide evaporative cooling and habitat
        - Can reduce surrounding temperatures by 2-3°C
        
        **2. Rain Gardens and Bioswales**
        - Landscaped depressions that collect and filter runoff
        - Combine vegetation cooling with water management
        - Help recharge groundwater and support vegetation during dry periods
        
        **3. Permeable Pavements**
        - Allow water infiltration for natural cooling
        - Reduce runoff and help maintain soil moisture
        - Can be 10-15°C cooler than conventional pavements
        
        **4. Water Recycling Systems**
        - Gray water reuse for irrigation and cooling
        - Passive cooling through strategic water features
        - Reduces water consumption while maximizing cooling benefits
        """)
        
        # Water management benefits chart
        water_benefits = pd.DataFrame({
            'Benefit': ['Temperature Reduction', 'Stormwater Management', 'Water Conservation', 'Flood Prevention', 'Groundwater Recharge'],
            'Retention Ponds': [3, 5, 2, 4, 3],
            'Rain Gardens': [2, 3, 1, 2, 4],
            'Permeable Pavements': [2, 4, 1, 3, 5]
        })
        
        fig = px.imshow(
            water_benefits.set_index('Benefit'),
            text_auto=True,
            labels=dict(x="Solution Type", y="Benefit", color="Rating (1-5)"),
            x=water_benefits.columns[1:],
            y=water_benefits['Benefit'],
            color_continuous_scale='Blues',
            title="Benefits of Water Management Solutions (Rating: 1-5)"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.write("Water management solutions provide dual benefits of cooling and stormwater management, making them particularly valuable in climate adaptation strategies.")
        
    elif selected_category == "Policy Measures":
        st.markdown("""
        ### Policy and Planning Measures
        
        **1. Urban Heat Island Mitigation Plans**
        - Comprehensive strategies at city level
        - Set targets for temperature reduction and green cover
        - Coordinate actions across multiple departments and stakeholders
        
        **2. Building Codes and Standards**
        - Requirements for cool roofs on new construction
        - Minimum solar reflectance standards
        - Green space requirements for new developments
        
        **3. Incentive Programs**
        - Tax rebates for cool roof installations
        - Stormwater fee reductions for permeable surfaces
        - Grants for community green space projects
        
        **4. Urban Forestry Ordinances**
        - Tree protection and replacement requirements
        - Canopy coverage goals
        - Street tree planting programs
        
        **5. Heat Vulnerability Mapping**
        - Identify areas with highest temperatures and vulnerable populations
        - Prioritize interventions in highest-need areas
        - Monitor effectiveness of interventions over time
        """)
        
        # Policy implementation timeline
        st.write("Example Implementation Timeline for Urban Heat Island Policy Measures:")
        
        policy_timeline = pd.DataFrame({
            'Policy Measure': ['Develop Heat Vulnerability Map', 'Update Building Codes', 'Create Cool Roof Incentive Program', 
                            'Implement Tree Planting Initiative', 'Revise Zoning for Green Infrastructure'],
            'Implementation Year': [1, 2, 2, 3, 4],
            'Cost Level': ['Low', 'Medium', 'Medium', 'High', 'Medium'],
            'Impact Level': ['Medium', 'High', 'Medium', 'High', 'High']
        })
        
        fig = px.timeline(
            policy_timeline, 
            x_start='Implementation Year', 
            x_end='Implementation Year', 
            y='Policy Measure',
            color='Impact Level',
            title="Urban Heat Island Policy Implementation Timeline",
            labels={"Implementation Year": "Year"}
        )
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig, use_container_width=True)
        
        st.write("Effective policies combine regulatory requirements with incentives and education to accelerate adoption of heat island mitigation strategies.")
    
    # Cost-benefit analysis section
    st.subheader("Cost-Benefit Analysis of Mitigation Strategies")
    
    cost_benefit_data = pd.DataFrame({
        'Strategy': ['Tree Planting', 'Green Roofs', 'Cool Roofs', 'Cool Pavements', 'Water Features'],
        'Implementation Cost': [3, 5, 2, 4, 4],  # 1-5 scale
        'Maintenance Cost': [2, 3, 1, 2, 4],  # 1-5 scale
        'Temperature Reduction': [4, 4, 3, 3, 3],  # 1-5 scale
        'Additional Benefits': [5, 4, 2, 3, 4]  # 1-5 scale
    })
    
    fig = px.scatter(
        cost_benefit_data,
        x='Implementation Cost',
        y='Temperature Reduction',
        size='Additional Benefits',
        color='Maintenance Cost',
        hover_name='Strategy',
        labels={
            'Implementation Cost': 'Implementation Cost (1-5)',
            'Temperature Reduction': 'Temperature Reduction (1-5)',
            'Maintenance Cost': 'Maintenance Cost (1-5)',
            'Additional Benefits': 'Additional Benefits (1-5)'
        },
        title='Cost-Benefit Analysis of Heat Island Mitigation Strategies',
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.write("""
    The chart above shows the relationship between implementation costs and cooling benefits of different strategies, 
    with the size of each bubble representing additional co-benefits (such as stormwater management, air quality improvement, 
    and habitat creation) and the color representing ongoing maintenance costs.
    """)
    
    # Recommendation section
    st.subheader("Recommended Approach")
    st.write("""
    For most effective urban heat island mitigation, we recommend a combined approach that:
    
    1. Starts with low-cost, high-impact measures like cool roofs and strategic tree planting
    2. Incorporates policy changes to ensure long-term implementation
    3. Targets interventions in areas with highest temperatures and vulnerable populations
    4. Monitors outcomes and adjusts strategies based on measured temperature reductions
    5. Engages communities in implementation and maintenance of green infrastructure
    
    Each city needs a customized approach based on its specific climate, urban form, and resources.
    """)

# Footer
st.divider()
st.write("© 2023 Urban Heat Island Analyzer - Using data science and community engagement to create cooler, more livable cities")
