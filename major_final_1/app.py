import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from shared_data import WARD_DATA, calculate_heatwave_percentage

# Streamlit UI
st.set_page_config(page_title="Heat Sentinel Dashboard", layout="centered")
st.title("Heat Sentinel Dashboard")

# Taluk selection
wards = list(WARD_DATA.keys())
ward = st.selectbox("Select Taluk:", ["--Select--"] + wards)

# Heatwave Percentage Box
if ward != "--Select--":
    data = WARD_DATA[ward]
    heatwave_percent = calculate_heatwave_percentage(data)
    st.markdown(f"""
        <div style='width:200px; padding:10px; margin-bottom:20px; border:2px solid #e74c3c; border-radius:8px; font-weight:bold; text-align:center; background-color:rgba(231,76,60,0.1); color:#e74c3c;'>
            Heatwave: {heatwave_percent}%
        </div>
    """, unsafe_allow_html=True)

    # Bar Chart
    labels = ["Temp_2m", "Humidity", "Green Cover %", "Traffic Index", "AIQ", "Precipitation mm"]
    values = [
        data["Temp_2m"],
        data["Humidity"],
        data["Green_Cover_"],
        data["Traffic_Index"],
        data["AIQ"],
        data["Precipitation_mm"]
    ]
    colors = [
        'rgba(231, 76, 60, 0.7)',
        'rgba(52, 152, 219, 0.7)',
        'rgba(46, 204, 113, 0.7)',
        'rgba(241, 196, 15, 0.7)',
        'rgba(155, 89, 182, 0.7)',
        'rgba(26, 188, 156, 0.7)'
    ]
    fig = go.Figure(data=[go.Bar(x=labels, y=values, marker_color=colors)])
    fig.update_layout(
        title='Heat Wave Factors for Selected Taluk',
        yaxis=dict(title='Value', range=[0, max(values)+10]),
        xaxis=dict(title='Factor'),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.markdown(f"""
        <div style='width:200px; padding:10px; margin-bottom:20px; border:2px solid #e74c3c; border-radius:8px; font-weight:bold; text-align:center; background-color:rgba(231,76,60,0.1); color:#e74c3c;'>
            Heatwave: --%
        </div>
    """, unsafe_allow_html=True)
    st.info("Please select a Taluk to view the data.")
