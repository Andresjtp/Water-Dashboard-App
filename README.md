# Water Quality Dashboard

An interactive Streamlit web app for exploring water quality data collected in Biscayne Bay, Miami, FL.

**CIS 3590 - Internship-Ready Software Development** · Prof. Gregory Reis

- **Live app:** _<add your Streamlit Community Cloud URL here>_
- **Repository:** _<add your GitHub repository URL here>_

## Purpose

Water quality sensors produce hundreds of readings that are hard to make sense of in a spreadsheet. This dashboard turns that raw data into interactive charts and maps so a user can quickly answer questions like:

- How did temperature, salinity, or dissolved oxygen change during the survey?
- Where along the route were conditions different?
- Are any parameters related to each other (for example, warmer water being saltier)?
- What does the bay floor look like along the vehicle's path?

## Dataset

**File:** `biscayneBay_waterquality.csv` (942 rows)

The data was collected by an autonomous surface vehicle on **February 4, 2022** during a roughly 16-minute mission in Biscayne Bay (around 25.91° N, 80.14° W). The vehicle logged a reading about once per second, combining:

- **Navigation data:** latitude, longitude, heading, speed, battery state, and other vehicle telemetry
- **Water quality data:** temperature (°C), salinity (ppt), pH, dissolved oxygen (mg/L and % saturation), turbidity (NTU), chlorophyll (µg/L), and total water column depth (m)

> Note: some turbidity and chlorophyll readings are negative, which points to a sensor calibration offset. The Insights tab flags this.

## Features

| Section | What it shows |
|---|---|
| **Overview** | Description of the project, how to use the app, and summary metrics |
| **Data** | Raw data table (with a checkbox to show all telemetry columns) and descriptive statistics |
| **Charts** | Plotly line chart of any parameter over time (chosen from a dropdown), temperature vs. salinity scatter plot, and a 3D view of the bay floor |
| **Maps** | The vehicle's route on an interactive map, colored by a parameter of your choice |
| **Insights** | Auto-generated findings for the current selection and a correlation heatmap |

**Interactive widgets:** CSV file uploader, time window slider, water depth slider, parameter dropdowns, and a column toggle checkbox. All tabs update when the sidebar filters change.

## How to Use the App

1. Open the live app link above (or run it locally, see below).
2. Read the **Overview** tab for a summary of the data.
3. Use the **sidebar sliders** to narrow the data to a time window or depth range.
4. Go to **Charts** and pick a parameter from the dropdown to see how it changed over time. Hover over any chart for exact values, drag to zoom, and double-click to reset.
5. Go to **Maps** to see where readings were taken and color the route by any parameter.
6. Check **Insights** for key takeaways about the current selection.
7. Optionally, upload your own CSV in the sidebar. It must use the same column names as the included dataset (at minimum `Latitude`, `Longitude`, `Time hh:mm:ss`, `Temperature (c)`, `Salinity (ppt)`, and `Total Water Column (m)`).

## Running Locally

```bash
git clone <your-repo-url>
cd Water-Dashboard-App
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run water_dashboard.py
```

The app opens at http://localhost:8501.

## Tech Stack

- [Streamlit](https://streamlit.io/) for the web app and widgets
- [pandas](https://pandas.pydata.org/) for loading and filtering the data
- [Plotly Express](https://plotly.com/python/plotly-express/) for the interactive charts and map

## Project Structure

```
Water-Dashboard-App/
├── water_dashboard.py            # Streamlit app
├── biscayneBay_waterquality.csv  # Dataset
├── requirements.txt              # Python dependencies
└── README.md
```

## Agile Process

The project was built in short iterations, each delivering a working version of the app that was committed to Git:

| Sprint | User story | Result |
|---|---|---|
| 1 | As a user, I want to see the raw data so I know what was measured. | Data tab with raw table and statistics, CSV upload |
| 2 | As a user, I want to pick a parameter and see how it changes over time. | Plotly line chart with dropdown, scatter plot, 3D bay floor |
| 3 | As a user, I want to see where readings were taken. | Interactive map of the vehicle track |
| 4 | As a user, I want explanations and takeaways so I understand the data without being an expert. | Overview and Insights tabs, axis labels, sidebar filters |
| 5 | As a reviewer, I want to open the app from a link and read the code. | requirements.txt, README, GitHub repo, Streamlit Community Cloud deployment |
