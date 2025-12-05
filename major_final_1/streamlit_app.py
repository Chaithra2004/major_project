import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import joblib
from datetime import datetime, timedelta
import plotly.express as px

# Set page config
st.set_page_config(
    page_title="Tumkur Heatwave Intelligence Hub",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Global UI styling – modern, card‑based layout
st.markdown(
    """
    <style>
    /* Page background */
    .stApp {
        background: radial-gradient(circle at top left, #fef3c7 0, #f9fafb 45%, #e0f2fe 100%);
        font-family: "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Center main column a bit and add breathing room */
    .main {
        max-width: 1200px;
        margin: 0 auto;
        padding-top: 1rem;
        padding-bottom: 2rem;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 40%, #020617 100%);
        color: #e5e7eb !important;
    }
    section[data-testid="stSidebar"] * {
        color: #e5e7eb !important;
    }

    /* Buttons */
    .stButton>button {
        border-radius: 999px;
        background: linear-gradient(90deg, #ef4444, #f97316);
        color: #ffffff;
        font-weight: 600;
        border: none;
        padding: 0.4rem 1.2rem;
        box-shadow: 0 8px 20px rgba(239, 68, 68, 0.35);
    }
    .stButton>button:hover {
        filter: brightness(1.05);
        box-shadow: 0 10px 24px rgba(248, 113, 113, 0.55);
    }

    /* Selects */
    .stSelectbox div[data-baseweb="select"] {
        border-radius: 999px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
        background-color: #ffffff;
    }

    /* Headings */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #0f172a;
        font-weight: 700;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: #ffffff;
        border-radius: 16px;
        padding: 0.9rem 1rem;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
    }

    /* Reusable card container */
    .themed-card {
        background: #ffffff;
        border-radius: 18px;
        padding: 1.25rem 1.5rem;
        box-shadow: 0 16px 40px rgba(15, 23, 42, 0.08);
        border: 1px solid rgba(148, 163, 184, 0.25);
    }
    .themed-card-header {
        font-size: 0.9rem;
        letter-spacing: .08em;
        text-transform: uppercase;
        color: #64748b;
        margin-bottom: 0.2rem;
    }
    .themed-card-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #0f172a;
    }

    /* Heatwave badge */
    .heat-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 0.35rem 0.9rem;
        border-radius: 999px;
        border: 1px solid rgba(248, 113, 113, 0.5);
        background: linear-gradient(120deg, rgba(248, 113, 113, 0.1), rgba(251, 191, 36, 0.12));
        color: #b91c1c;
        font-weight: 600;
        gap: 0.35rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Configuration
TALUKS = [
    "Tumakuru", "Tiptur", "Madhugiri", "Sira", "Pavagada",
    "Gubbi", "Koratagere", "Chikkanayakanahalli", "Turuvekere", "Kunigal"
]

START_DATE = '2025-10-01'
END_DATE_3MONTH = '2025-12-31'
END_DATE_1YEAR = '2026-09-26'

# Function to generate synthetic weather data
def generate_weather_data(start_date, end_date, taluk):
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    df = pd.DataFrame(index=dates)
    
    # Base temperature with seasonal variation for Karnataka
    day_of_year = df.index.dayofyear
    
    # Different temperature patterns based on taluk elevation and location
    if taluk in ["Pavagada", "Madhugiri"]:  # Hotter regions
        base_temp = 28 + 8 * np.sin(2 * np.pi * (day_of_year - 90) / 365)
        temp_variation = 3.5
    elif taluk in ["Tumakuru", "Gubbi", "Koratagere"]:  # Central regions
        base_temp = 27 + 7 * np.sin(2 * np.pi * (day_of_year - 100) / 365)
        temp_variation = 3.0
    else:  # Other taluks
        base_temp = 26 + 6 * np.sin(2 * np.pi * (day_of_year - 110) / 365)
        temp_variation = 2.8
    
    # Add random variation
    df['Temp_2m'] = base_temp + np.random.normal(0, temp_variation, len(dates))
    df['Temp_max'] = df['Temp_2m'] + np.random.uniform(2, 5, len(dates))
    df['Temp_min'] = df['Temp_2m'] - np.random.uniform(2, 5, len(dates))
    
    # Other features with regional variations
    df['Humidity'] = np.random.normal(65, 10, len(dates)).clip(30, 95)
    df['Heat_Index'] = df['Temp_2m'] + (df['Humidity'] / 100 * 5)
    df['Green_Cover_%'] = np.random.uniform(30, 70, len(dates))
    df['Traffic_Index'] = np.random.uniform(40, 80, len(dates))
    df['AIQ'] = np.random.uniform(50, 300, len(dates))
    df['Precipitation_mm'] = np.random.gamma(1, 2, len(dates))
    
    # Add date components
    df['day_of_year'] = df.index.dayofyear / 365.0
    df['month'] = (df.index.month - 1) / 11.0
    df['year'] = (df.index.year - 2024) / 2.0
    df['day_of_week'] = df.index.dayofweek / 6.0
    
    return df

def prepare_features(df):
    """Prepare features for prediction"""
    features = [
        'Temp_2m', 'Temp_max', 'Temp_min', 'Humidity', 'Heat_Index',
        'Green_Cover_%', 'Traffic_Index', 'AIQ', 'Precipitation_mm',
        'day_of_year', 'month', 'year', 'day_of_week'
    ]
    return df[features]


def classify_risk_level(heatwave_percent: int):
    """Map heatwave percentage to a qualitative risk band with color and advice."""
    if heatwave_percent < 25:
        return "Low", "#22c55e", "Conditions are generally safe. Maintain regular hydration and shade."
    elif heatwave_percent < 50:
        return "Moderate", "#eab308", "Avoid peak afternoon exposure and check on vulnerable groups."
    elif heatwave_percent < 75:
        return "High", "#f97316", "Limit outdoor work, provide cooling spaces and water points."
    else:
        return "Severe", "#dc2626", "Issue heat alerts, shift working hours and activate emergency protocols."

def create_3month_plot(df, taluk):
    """Create 3-month forecast plot"""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add temperature trace
    fig.add_trace(
        go.Scatter(
            x=df.index, 
            y=df['Temp_2m'],
            mode='lines',
            name='Temperature (°C)',
            line=dict(color='#2c3e50', width=2),
            hovertemplate='%{x|%b %d}<br>%{y:.1f}°C<extra></extra>'
        ),
        secondary_y=False,
    )
    
    # Add min-max range using a different approach
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['Temp_max'],
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip',
        ),
        secondary_y=False,
    )
    
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['Temp_min'],
            fill='tonexty',
            mode='lines',
            line=dict(width=0),
            fillcolor='rgba(52, 152, 219, 0.2)',
            name='Temperature Range',
            hoverinfo='skip',
        ),
        secondary_y=False,
    )
    
    # Add heatwave indicators
    heatwaves = df[df['Predicted_Heatwave'] == 1]
    if not heatwaves.empty:
        for date in heatwaves.index.unique():
            fig.add_vrect(
                x0=date, 
                x1=date + timedelta(days=1),
                fillcolor='rgba(231, 76, 60, 0.3)',
                layer="below",
                line_width=0,
            )
    
    # Update layout
    fig.update_layout(
        title=f"3-Month Heatwave Forecast for {taluk} (Oct-Dec 2025)",
        xaxis_title="Date",
        yaxis_title="Temperature (°C)",
        template="plotly_white",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=50, r=50, t=80, b=50),
        height=400,
    )
    
    # Add heatwave legend item
    fig.add_annotation(
        x=0.02,
        y=1.1,
        xref="paper",
        yref="paper",
        text="🌡️ Predicted Heatwave",
        showarrow=False,
        font=dict(color="#e74c3c", size=12)
    )
    
    return fig

def create_yearly_plot(df, taluk):
    """Create 1-year forecast plot"""
    # Resample to monthly data
    monthly_avg = df['Temp_2m'].resample('M').mean()
    monthly_min = df['Temp_min'].resample('M').min()
    monthly_max = df['Temp_max'].resample('M').max()
    
    # Count heatwave days per month
    heatwave_months = df[df['Predicted_Heatwave'] == 1].resample('M').size()
    heatwave_months = heatwave_months.reindex(monthly_avg.index, fill_value=0)
    
    # Create figure
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add temperature trace
    fig.add_trace(
        go.Scatter(
            x=monthly_avg.index,
            y=monthly_avg,
            mode='lines+markers',
            name='Avg Temperature',
            line=dict(color='#2c3e50', width=2),
            marker=dict(size=8, color='#2c3e50'),
            hovertemplate='%{x|%b %Y}<br>%{y:.1f}°C<extra></extra>'
        ),
        secondary_y=False,
    )
    
    # Add min-max range using a different approach
    fig.add_trace(
        go.Scatter(
            x=monthly_avg.index,
            y=monthly_max,
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip',
        ),
        secondary_y=False,
    )
    
    fig.add_trace(
        go.Scatter(
            x=monthly_avg.index,
            y=monthly_min,
            fill='tonexty',
            mode='lines',
            line=dict(width=0),
            fillcolor='rgba(52, 152, 219, 0.2)',
            name='Temperature Range',
            hoverinfo='skip',
        ),
        secondary_y=False,
    )
    
    # Add heatwave days as bars
    fig.add_trace(
        go.Bar(
            x=heatwave_months.index,
            y=heatwave_months.values,
            name='Heatwave Days',
            marker_color='#e74c3c',
            opacity=0.7,
            hovertemplate='%{x|%b %Y}<br>%{y} heatwave days<extra></extra>',
            width=20*24*60*60*1000,  # 20 days in milliseconds
        ),
        secondary_y=True,
    )
    
    # Update layout
    fig.update_layout(
        title=f"1-Year Heatwave Forecast for {taluk} (Oct 2025 - Sep 2026)",
        xaxis_title="Date",
        yaxis_title="Temperature (°C)",
        yaxis2_title="Heatwave Days",
        template="plotly_white",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=50, r=50, t=80, b=50),
        height=500,
    )
    
    # Update y-axes
    fig.update_yaxes(title_text="Temperature (°C)", secondary_y=False)
    fig.update_yaxes(title_text="Heatwave Days", secondary_y=True, range=[0, heatwave_months.max() * 1.2])
    
    return fig

def main():
    # Sidebar
    st.sidebar.title("🌡️ Tumkur Heatwave Forecast")
    st.sidebar.markdown("---")
    
    # Taluk selection
    selected_taluk = st.sidebar.selectbox(
        "Select Taluk",
        TALUKS,
        index=0
    )
    
    # Add a button to generate forecast
    if st.sidebar.button("Generate Forecast"):
        with st.spinner(f'Generating forecast for {selected_taluk}...'):
            # Generate data
            df_3month = generate_weather_data(START_DATE, END_DATE_3MONTH, selected_taluk)
            df_1year = generate_weather_data(START_DATE, END_DATE_1YEAR, selected_taluk)
            
            # Prepare features
            X_3month = prepare_features(df_3month)
            X_1year = prepare_features(df_1year)
            
            try:
                # Load model and predict
                model = joblib.load(r'C:\\Users\\Bhanu prakash Reddy\\Downloads\\forecasting_model.joblib')
                df_3month['Predicted_Heatwave'] = model.predict(X_3month)
                df_1year['Predicted_Heatwave'] = model.predict(X_1year)
                
                # Display 3-month forecast
                st.markdown("## 🌡️ 3-Month Heatwave Forecast")
                st.markdown(f"### {selected_taluk} Taluk (Oct-Dec 2025)")
                fig_3m = create_3month_plot(df_3month, selected_taluk)
                st.plotly_chart(fig_3m, use_container_width=True)
                
                # Display 1-year forecast
                st.markdown("---")
                st.markdown("## 📅 1-Year Heatwave Forecast")
                st.markdown(f"### {selected_taluk} Taluk (Oct 2025 - Sep 2026)")
                fig_1y = create_yearly_plot(df_1year, selected_taluk)
                st.plotly_chart(fig_1y, use_container_width=True)
                
                # Display some statistics
                st.markdown("---")
                st.markdown("## 📊 Forecast Summary")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Predicted Heatwave Days (3 Months)", 
                             f"{df_3month['Predicted_Heatwave'].sum()} days")
                with col2:
                    st.metric("Total Predicted Heatwave Days (1 Year)", 
                             f"{df_1year['Predicted_Heatwave'].sum()} days")
                with col3:
                    max_temp_month = df_1year['Temp_2m'].resample('M').mean().idxmax().strftime('%B %Y')
                    st.metric("Hottest Month", max_temp_month)
                
            except Exception as e:
                st.error(f"Error generating forecast: {str(e)}")
    else:
        # Show welcome message
        st.title("🌡️ Tumkur District Heatwave Forecast")
        st.markdown("---")
        st.markdown("""
        ### Welcome to the Tumkur District Heatwave Forecasting System
        
        This application provides heatwave forecasts for taluks in the Tumkur district of Karnataka.
        
        **How to use:**
        1. Select a taluk from the dropdown in the sidebar
        2. Click the 'Generate Forecast' button
        3. View the interactive forecast visualizations
        
        The forecast includes:
        - 3-month detailed temperature and heatwave forecast
        - 1-year overview with monthly temperature trends
        - Heatwave day counts and statistics
        """)
        
        # Removed external Tumkur district map image (was broken / cluttering the UI)

# --- Heat Sentinel Dashboard Integration ---
from shared_data import WARD_DATA, calculate_heatwave_percentage

def show_heat_sentinel_dashboard():
    st.title("Heat Sentinel Dashboard")
    st.write(
        "Explore present‑day heat stress drivers across Tumkur taluks. Select a location to see its risk profile."
    )

    wards = list(WARD_DATA.keys())
    ward = st.selectbox("Select Taluk", ["--Select--"] + wards)

    if ward == "--Select--":
        st.markdown(
            "<p style='color:#6b7280;margin-top:0.5rem;'>Choose a taluk from the dropdown to view its heat drivers.</p>",
            unsafe_allow_html=True,
        )
        return

    data = WARD_DATA[ward]
    heatwave_percent = calculate_heatwave_percentage(data)
    risk_label, risk_color, risk_advice = classify_risk_level(heatwave_percent)

    # Top summary row
    col_a, col_b, col_c = st.columns([1.3, 1, 1])
    with col_a:
        st.markdown(
            f"""
            <div class="themed-card">
              <div class="themed-card-header">Current risk</div>
              <div class="themed-card-title">{ward}</div>
              <div style="margin-top:0.75rem;">
                <span class="heat-badge" style="border-color:{risk_color};color:{risk_color}">
                  🌡️ {risk_label} risk&nbsp;&nbsp;•&nbsp;&nbsp;{heatwave_percent}%
                </span>
              </div>
              <p style="margin-top:0.75rem;font-size:0.85rem;color:#6b7280;">
                {risk_advice}
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_b:
        st.metric("Temperature (°C)", data["Temp_2m"])
        st.metric("Humidity (%)", data["Humidity"])
    with col_c:
        st.metric("Green cover (%)", data["Green_Cover_"])
        st.metric("Traffic index", data["Traffic_Index"])

    # Factors bar chart inside a card
    labels = ["Temp_2m", "Humidity", "Green Cover %", "Traffic Index", "AIQ", "Precipitation mm"]
    values = [
        data["Temp_2m"],
        data["Humidity"],
        data["Green_Cover_"],
        data["Traffic_Index"],
        data["AIQ"],
        data["Precipitation_mm"],
    ]
    colors = [
        "rgba(248, 113, 113, 0.9)",
        "rgba(59, 130, 246, 0.9)",
        "rgba(34, 197, 94, 0.9)",
        "rgba(234, 179, 8, 0.9)",
        "rgba(168, 85, 247, 0.9)",
        "rgba(45, 212, 191, 0.9)",
    ]
    fig = go.Figure(data=[go.Bar(x=labels, y=values, marker_color=colors)])
    fig.update_layout(
        title="Heatwave Driver Profile",
        yaxis=dict(title="Value", range=[0, max(values) + 10]),
        xaxis=dict(title="Factor"),
        showlegend=False,
        margin=dict(l=20, r=20, t=50, b=40),
    )

    st.markdown('<div class="themed-card" style="margin-top:1.5rem;">', unsafe_allow_html=True)
    st.markdown("<div class='themed-card-header'>Drivers</div>", unsafe_allow_html=True)
    st.markdown("<div class='themed-card-title'>Factors influencing heat stress</div>", unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(
        "<p style='font-size:0.85rem;color:#6b7280;margin-top:-0.5rem;'>"
        "High temperature, low green cover, heavy traffic and poor air quality all push risk upwards."
        "</p>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Compact overview of all taluks with their risk bands
    st.markdown("#### District‑wide risk snapshot")
    overview_rows = []
    for name, vals in WARD_DATA.items():
        pct = calculate_heatwave_percentage(vals)
        level, _, _ = classify_risk_level(pct)
        overview_rows.append({"Taluk": name, "Heatwave %": pct, "Risk level": level})
    overview_df = pd.DataFrame(overview_rows).sort_values("Heatwave %", ascending=False)
    st.dataframe(overview_df, use_container_width=True)

    # --- What‑if analysis: simulate mitigation scenarios ---
    st.markdown("#### What‑if: simulate mitigation for this taluk")
    st.write(
        "Adjust the sliders to explore how improvements in green cover, traffic and air quality could "
        "change the heatwave risk for this taluk."
    )

    base_vals = data
    c1, c2, c3 = st.columns(3)
    with c1:
        green_delta = st.slider(
            "Increase green cover (percentage points)",
            min_value=0,
            max_value=30,
            value=0,
            step=2,
        )
    with c2:
        traffic_delta = st.slider(
            "Reduce traffic index",
            min_value=0,
            max_value=40,
            value=0,
            step=5,
        )
    with c3:
        aiq_delta = st.slider(
            "Improve air quality index (lower is better)",
            min_value=0,
            max_value=60,
            value=0,
            step=5,
        )

    simulated = {
        "Temp_2m": base_vals["Temp_2m"],
        "Humidity": base_vals["Humidity"],
        "Green_Cover_": max(base_vals["Green_Cover_"] + green_delta, 0),
        "Traffic_Index": max(base_vals["Traffic_Index"] - traffic_delta, 0),
        "AIQ": max(base_vals["AIQ"] - aiq_delta, 0),
        "Precipitation_mm": base_vals["Precipitation_mm"],
    }
    sim_pct = calculate_heatwave_percentage(simulated)
    sim_level, sim_color, sim_advice = classify_risk_level(sim_pct)

    col_before, col_after = st.columns(2)
    with col_before:
        st.metric("Current heatwave risk", f"{heatwave_percent}%", help=risk_advice)
    with col_after:
        st.metric("Simulated risk", f"{sim_pct}%", help=sim_advice)

    st.markdown(
        f"<p style='font-size:0.85rem;color:#6b7280;'>Scenario risk band: "
        f"<span style='font-weight:600;color:{sim_color};'>{sim_level}</span>.</p>",
        unsafe_allow_html=True,
    )


def show_taluk_comparison():
    """Compare multiple taluks side‑by‑side on current drivers and risk."""
    st.title("Taluk Comparison")
    st.write(
        "Select two or three taluks to compare their present‑day heatwave risk and key drivers side‑by‑side."
    )

    selected = st.multiselect("Choose taluks to compare", TALUKS, default=["Tumakuru", "Pavagada"])
    if len(selected) < 2:
        st.info("Please select at least two taluks to enable comparison.")
        return
    if len(selected) > 3:
        st.warning("Comparison is limited to three taluks at a time. Please deselect one or more.")
        return

    # Build comparison data
    records = []
    for taluk in selected:
        vals = WARD_DATA.get(taluk)
        if not vals:
            continue
        pct = calculate_heatwave_percentage(vals)
        level, _, _ = classify_risk_level(pct)
        records.append(
            {
                "Taluk": taluk,
                "Heatwave_pct": pct,
                "Risk_level": level,
                "Temp_2m": vals["Temp_2m"],
                "Humidity": vals["Humidity"],
                "Green_Cover_pct": vals["Green_Cover_"],
                "Traffic_Index": vals["Traffic_Index"],
                "AIQ": vals["AIQ"],
                "Precipitation_mm": vals["Precipitation_mm"],
            }
        )

    if not records:
        st.warning("No data available for the selected taluks.")
        return

    comp_df = pd.DataFrame(records)

    # Top risk cards
    cols = st.columns(len(comp_df))
    for col, row in zip(cols, comp_df.itertuples(index=False)):
        _, color, _ = classify_risk_level(row.Heatwave_pct)
        with col:
            st.markdown(
                f"""
                <div class="themed-card">
                  <div class="themed-card-header">Taluk</div>
                  <div class="themed-card-title">{row.Taluk}</div>
                  <div style="margin-top:0.75rem;">
                    <span class="heat-badge" style="border-color:{color};color:{color}">
                      {row.Risk_level} • {row.Heatwave_pct}%
                    </span>
                  </div>
                  <p style="margin-top:0.75rem;font-size:0.85rem;color:#6b7280;">
                    Temp: {row.Temp_2m}°C • Humidity: {row.Humidity}% • Green cover: {row.Green_Cover_pct}%.
                  </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Driver comparison chart
    factor_labels = ["Temp_2m", "Humidity", "Green_Cover_pct", "Traffic_Index", "AIQ", "Precipitation_mm"]
    fig = go.Figure()
    for row in comp_df.itertuples(index=False):
        vals = [getattr(row, f) for f in factor_labels]
        fig.add_trace(go.Bar(name=row.Taluk, x=factor_labels, y=vals))

    fig.update_layout(
        barmode="group",
        title="Heatwave driver comparison",
        yaxis_title="Value",
        margin=dict(l=20, r=20, t=60, b=40),
    )

    st.markdown('<div class="themed-card" style="margin-top:1.5rem;">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Raw comparison table
    st.markdown("#### Detailed comparison table")
    st.dataframe(comp_df.set_index("Taluk"), use_container_width=True)

# --- Navigation Integration ---
def main():
    st.sidebar.title("🌡️ Tumkur Heatwave Forecast")
    st.sidebar.markdown("---")
    page = st.sidebar.radio(
        "Navigate",
        ["Forecast System", "Heat Sentinel Dashboard", "Taluk Comparison", "Tumakuru Map Visualization"],
    )

    if page == "Forecast System":
        # Existing forecast logic
        # Taluk selection
        selected_taluk = st.sidebar.selectbox(
            "Select Taluk",
            TALUKS,
            index=0
        )
        # Add a button to generate forecast
        if st.sidebar.button("Generate Forecast"):
            with st.spinner(f'Generating forecast for {selected_taluk}...'):
                df_3month = generate_weather_data(START_DATE, END_DATE_3MONTH, selected_taluk)
                df_1year = generate_weather_data(START_DATE, END_DATE_1YEAR, selected_taluk)
                X_3month = prepare_features(df_3month)
                X_1year = prepare_features(df_1year)
                try:
                    model = joblib.load(r'C:\\Users\\Bhanu prakash Reddy\\Downloads\\forecasting_model.joblib')
                    df_3month['Predicted_Heatwave'] = model.predict(X_3month)
                    df_1year['Predicted_Heatwave'] = model.predict(X_1year)
                    st.markdown("## 🌡️ 3-Month Heatwave Forecast")
                    st.markdown(f"### {selected_taluk} Taluk (Oct-Dec 2025)")
                    fig_3m = create_3month_plot(df_3month, selected_taluk)
                    st.plotly_chart(fig_3m, use_container_width=True)
                    st.markdown("---")
                    st.markdown("## 📅 1-Year Heatwave Forecast")
                    st.markdown(f"### {selected_taluk} Taluk (Oct 2025 - Sep 2026)")
                    fig_1y = create_yearly_plot(df_1year, selected_taluk)
                    st.plotly_chart(fig_1y, use_container_width=True)
                    st.markdown("---")
                    st.markdown("## 📊 Forecast Summary")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Predicted Heatwave Days (3 Months)", f"{df_3month['Predicted_Heatwave'].sum()} days")
                    with col2:
                        st.metric("Total Predicted Heatwave Days (1 Year)", f"{df_1year['Predicted_Heatwave'].sum()} days")
                    with col3:
                        max_temp_month = df_1year['Temp_2m'].resample('M').mean().idxmax().strftime('%B %Y')
                        st.metric("Hottest Month", max_temp_month)
                except Exception as e:
                    st.error(f"Error generating forecast: {str(e)}")
        else:
            # Hero welcome section
            st.markdown(
                """
                <div class="themed-card" style="margin-bottom:1.5rem;">
                  <div class="themed-card-header">Overview</div>
                  <div class="themed-card-title">🌡️ Tumkur District Heatwave Intelligence</div>
                  <p style="margin-top:0.75rem;font-size:0.9rem;color:#4b5563;">
                    Forecast and monitor heat stress for every taluk in Tumkur. Use the sidebar to pick a location
                    and generate short‑term and seasonal projections, then switch tabs to inspect current drivers
                    and the district map.
                  </p>
                  <ul style="font-size:0.85rem;color:#6b7280;margin-top:0.5rem;padding-left:1.2rem;">
                    <li><b>Forecast System</b> – 3‑month and 1‑year projections with key metrics.</li>
                    <li><b>Heat Sentinel Dashboard</b> – present‑day risk and driver breakdown.</li>
                    <li><b>Tumakuru Map Visualization</b> – interactive map with taluk‑level hotspots.</li>
                  </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )
    elif page == "Heat Sentinel Dashboard":
        show_heat_sentinel_dashboard()
    elif page == "Taluk Comparison":
        show_taluk_comparison()
    elif page == "Tumakuru Map Visualization":
        from tumakuru_map import show_tumakuru_map
        show_tumakuru_map()

if __name__ == "__main__":
    main()
