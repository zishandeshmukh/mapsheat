
# Urban Heat Island Analyzer

A Streamlit web application for analyzing and visualizing urban heat islands in cities worldwide.

## Recommended Usage

This project is optimized for Replit and we recommend using it there for the best experience:
1. Visit the project on Replit
2. Click the "Run" button
3. Access the app through the webview panel

## Local Setup (Alternative)

If you still want to run locally, follow these steps:

1. **Clone the Repository**
```bash
git clone <your-repository-url>
cd urban-heat-island-analyzer
```

2. **Install Dependencies**
```bash
pip install streamlit folium numpy pandas plotly requests scikit-learn streamlit-folium trafilatura
```

3. **Run the Application**
```bash
streamlit run app.py
```

The app will start on `http://localhost:5000`

## Project Structure
```
├── app.py                 # Main application file
├── pages/                 # Additional pages
│   ├── community_input.py # Community data input page
│   ├── analysis.py       # Analysis and visualization page
│   └── about.py          # About page
├── utils/                 # Utility functions
│   ├── api_handlers.py   # API interaction functions
│   ├── data_processing.py# Data processing utilities
│   └── visualization.py  # Visualization functions
```

## Features

- Real-time temperature mapping
- Community temperature reporting
- Heat island analysis
- Mitigation strategy recommendations

## Note

This application is designed and optimized for Replit. Some features might require additional configuration when running locally.
