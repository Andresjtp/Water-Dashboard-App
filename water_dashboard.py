import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Water Quality Dashboard",
                   page_icon="🌊",
                   layout="wide")

st.title("Water Quality Dashboard")
st.header("CIS 3590 - Internship-Ready Software Development")
st.subheader("Prof. Gregory Reis")

st.divider()

# Columns the charts rely on; an uploaded file must contain these
REQUIRED_COLUMNS = ["Latitude",
                    "Longitude",
                    "Time hh:mm:ss",
                    "Temperature (c)",
                    "Salinity (ppt)",
                    "Total Water Column (m)"]

# Friendly names for the water quality parameters shown in the dropdown
PARAMETERS = {"Temperature (c)": "Temperature (°C)",
              "Salinity (ppt)": "Salinity (ppt)",
              "pH": "pH",
              "ODO mg/L": "Dissolved Oxygen (mg/L)",
              "ODOsat %": "Dissolved Oxygen Saturation (%)",
              "Turbid+ NTU": "Turbidity (NTU)",
              "Chl ug/L": "Chlorophyll (µg/L)",
              "Total Water Column (m)": "Water Depth (m)"}


@st.cache_data
def load_default_data():
    return pd.read_csv("biscayneBay_waterquality.csv")


# ---------------- Sidebar ----------------
st.sidebar.header("File Upload")
st.sidebar.info("Upload a CSV file "
                "with water quality data")
uploaded_file=st.sidebar.file_uploader("Upload a CSV file",
                         type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    df = load_default_data()

df.columns = df.columns.str.strip()

missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
if missing:
    st.error(f"The uploaded file is missing required columns: {', '.join(missing)}")
    st.stop()

df["Timestamp"] = pd.to_datetime(df["Time hh:mm:ss"], format="%H:%M:%S", errors="coerce")
df = df.dropna(subset=["Timestamp"])

# Only offer parameters that exist in the data
parameters = {col: label for col, label in PARAMETERS.items() if col in df.columns}

st.sidebar.header("Filters")
start_time, end_time = st.sidebar.slider("Time window",
                                         min_value=df["Timestamp"].min().to_pydatetime(),
                                         max_value=df["Timestamp"].max().to_pydatetime(),
                                         value=(df["Timestamp"].min().to_pydatetime(),
                                                df["Timestamp"].max().to_pydatetime()),
                                         format="HH:mm:ss")
min_depth, max_depth = st.sidebar.slider("Water depth (m)",
                                         min_value=float(df["Total Water Column (m)"].min()),
                                         max_value=float(df["Total Water Column (m)"].max()),
                                         value=(float(df["Total Water Column (m)"].min()),
                                                float(df["Total Water Column (m)"].max())))

filtered = df[(df["Timestamp"] >= start_time) &
              (df["Timestamp"] <= end_time) &
              (df["Total Water Column (m)"] >= min_depth) &
              (df["Total Water Column (m)"] <= max_depth)]

st.sidebar.caption(f"Showing {len(filtered)} of {len(df)} readings")

if filtered.empty:
    st.warning("No readings match the selected filters. Widen the time window or depth range.")
    st.stop()

overview, tables, plots, maps, insights = st.tabs(["Overview",
                                                   "Data",
                                                   "Charts",
                                                   "Maps",
                                                   "Insights"])

# ---------------- Overview ----------------
with overview:
    st.subheader("About this Dashboard")
    st.markdown(
        "This dashboard explores water quality readings collected by an autonomous "
        "surface vehicle in **Biscayne Bay, Miami, FL** on February 4, 2022. "
        "As the vehicle followed its route, onboard sensors logged its GPS position "
        "along with water temperature, salinity, pH, dissolved oxygen, turbidity, "
        "chlorophyll and depth about once per second."
    )
    st.markdown(
        "**How to use it:**\n"
        "- Use the **sidebar sliders** to narrow the data to a time window or depth range. "
        "Every tab updates to match.\n"
        "- **Data** shows the raw readings and summary statistics.\n"
        "- **Charts** lets you pick a parameter from the dropdown and see how it changes over time, "
        "plus how temperature relates to salinity and what the bay floor looks like in 3D.\n"
        "- **Maps** plots the vehicle's route colored by the parameter you choose.\n"
        "- **Insights** summarizes key findings for the current selection.\n"
        "- You can also **upload your own CSV** in the sidebar, as long as it uses the same column names."
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Readings", f"{len(filtered):,}")
    col2.metric("Avg Temperature", f"{filtered['Temperature (c)'].mean():.2f} °C")
    col3.metric("Avg Salinity", f"{filtered['Salinity (ppt)'].mean():.2f} ppt")
    col4.metric("Avg Depth", f"{filtered['Total Water Column (m)'].mean():.2f} m")

# ---------------- Data ----------------
with tables:
    st.subheader("Data Display")
    st.write("The table below shows every reading in the current selection. "
             "Click a column header to sort it.")
    show_all_columns = st.checkbox("Show all columns (including vehicle telemetry)", value=False)
    if show_all_columns:
        display_df = filtered.drop(columns=["Timestamp"])
    else:
        display_df = filtered[["Time hh:mm:ss", "Latitude", "Longitude"] + list(parameters)]
    st.dataframe(display_df)
    st.caption("Raw Data")
    st.dataframe(display_df.describe())
    st.caption("Descriptive Statistics")

# ---------------- Charts ----------------
with plots:
    st.subheader("Line Chart")
    st.write("Choose a water quality parameter to see how it changed over the course of the mission.")
    parameter = st.selectbox("Select a parameter",
                             options=list(parameters),
                             format_func=lambda col: parameters[col])

    fig1 = px.line(filtered,
                   x="Timestamp",
                   y=parameter,
                   title=f"{parameters[parameter]} over Time",
                   labels={"Timestamp": "Time of Day",
                           parameter: parameters[parameter]})
    fig1.update_xaxes(tickformat="%H:%M:%S")
    st.plotly_chart(fig1)

    st.subheader("Temperature vs Salinity")
    st.write("Each point is one reading, colored by water depth. "
             "This shows whether warmer water also tends to be saltier.")
    fig2 = px.scatter(filtered,
                      x="Temperature (c)",
                      y="Salinity (ppt)",
                      color="Total Water Column (m)",
                      title="Temperature vs Salinity",
                      labels={"Temperature (c)": "Temperature (°C)",
                              "Salinity (ppt)": "Salinity (ppt)",
                              "Total Water Column (m)": "Depth (m)"})
    st.plotly_chart(fig2)

    st.subheader("3D Bay Floor")
    st.write("Position and water depth combined into a 3D view of the bay floor along the route. "
             "Drag to rotate.")
    fig3 = px.scatter_3d(filtered,
                         x="Longitude",
                         y="Latitude",
                         z="Total Water Column (m)",
                         color="Temperature (c)",
                         title="3D Visualization of the Bay Floor",
                         labels={"Total Water Column (m)": "Depth (m)",
                                 "Temperature (c)": "Temperature (°C)"})
    fig3.update_scenes(zaxis_autorange="reversed")
    fig3.update_traces(marker_size=3)
    st.plotly_chart(fig3)

# ---------------- Maps ----------------
with maps:
    st.subheader("Maps")
    st.write("The vehicle's route plotted on a map. Pick a parameter to color the track by.")
    map_parameter = st.selectbox("Color the route by",
                                 options=list(parameters),
                                 format_func=lambda col: parameters[col],
                                 key="map_parameter")
    first_map = px.scatter_map(
        filtered,
        lat="Latitude",
        lon="Longitude",
        title=f"Vehicle Track Colored by {parameters[map_parameter]}",
        center={"lat":filtered["Latitude"].mean(),"lon":filtered["Longitude"].mean()},
        zoom=16,
        color=map_parameter,
        labels={map_parameter: parameters[map_parameter]},
        hover_data=["Time hh:mm:ss"],
        color_continuous_scale="viridis")
    st.plotly_chart(first_map)

# ---------------- Insights ----------------
with insights:
    st.subheader("Insights")
    st.write("Key findings for the current selection. These update as you change the sidebar filters.")

    temp = filtered["Temperature (c)"]
    sal = filtered["Salinity (ppt)"]
    depth = filtered["Total Water Column (m)"]
    temp_sal_corr = temp.corr(sal)

    st.markdown(
        f"- **Temperature** ranged from **{temp.min():.2f} °C** to **{temp.max():.2f} °C** "
        f"(average {temp.mean():.2f} °C).\n"
        f"- **Salinity** ranged from **{sal.min():.2f}** to **{sal.max():.2f} ppt** "
        f"(average {sal.mean():.2f} ppt), which is typical of a coastal marine bay.\n"
        f"- **Water depth** along the route varied from **{depth.min():.2f} m** to **{depth.max():.2f} m**.\n"
        f"- The correlation between temperature and salinity is **{temp_sal_corr:.2f}**, "
        f"a {'weak' if abs(temp_sal_corr) < 0.4 else 'moderate' if abs(temp_sal_corr) < 0.7 else 'strong'} "
        f"{'positive' if temp_sal_corr >= 0 else 'negative'} relationship."
    )
    if "ODO mg/L" in filtered.columns:
        odo = filtered["ODO mg/L"].mean()
        status = "above" if odo >= 4 else "below"
        st.markdown(f"- Average **dissolved oxygen** was **{odo:.2f} mg/L**, {status} the ~4 mg/L "
                    "level generally considered healthy for marine life.")
    if "Turbid+ NTU" in filtered.columns and (filtered["Turbid+ NTU"] < 0).any():
        st.markdown("- Some **turbidity** readings are negative, which is physically impossible. "
                    "This suggests a sensor calibration offset, so those values should be "
                    "treated with caution.")

    st.subheader("Parameter Correlations")
    st.write("How strongly each pair of parameters moves together "
             "(1 = move together, -1 = move in opposite directions, 0 = unrelated).")
    corr = filtered[list(parameters)].corr().rename(index=parameters, columns=parameters)
    fig4 = px.imshow(corr,
                     text_auto=".2f",
                     color_continuous_scale="RdBu",
                     zmin=-1,
                     zmax=1,
                     title="Correlation Between Water Quality Parameters",
                     labels={"color": "Correlation"})
    st.plotly_chart(fig4)
