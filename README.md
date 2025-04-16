
# Urban Heat Island Analyzer

A Streamlit web application for analyzing and visualizing urban heat islands in cities worldwide.

## Prerequisites

- Python 3.11+
- pip (Python package installer)

## Local Setup in VS Code

1. **Open Project**
   - Open VS Code
   - Open the project folder
   - Ensure Python extension is installed in VS Code

2. **Install Dependencies**
   ```bash
   pip install streamlit folium numpy pandas plotly requests scikit-learn streamlit-folium trafilatura
   ```

3. **Configure Environment**
   - Open `.streamlit/config.toml` to adjust port/host settings if needed
   - Default port is 5000

4. **Run Application**
   ```bash
   streamlit run app.py
   ```
   The app will start on `http://localhost:5000`

5. **Accessing the App**
   - Open your browser to `http://localhost:5000`
   - Or use the URL shown in the terminal

## Project Structure
```
├── app.py                 # Main application file
├── pages/                 # Additional pages
├── utils/                 # Utility functions
└── .streamlit/           # Streamlit configuration
```

## Features
- Real-time temperature mapping
- Community temperature reporting
- Heat island analysis
- Mitigation strategy recommendations

## Troubleshooting

If you encounter port conflicts:
1. Change the port in `.streamlit/config.toml`
2. Restart the application


