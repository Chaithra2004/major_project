import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

# --- Tumakuru Taluk Coordinates (approximate centroids for visualization) ---
taluk_coords = {
    "Tumakuru": (13.3411, 77.1010),
    "Tiptur": (13.2569, 76.4777),
    "Madhugiri": (13.6601, 77.2123),
    "Sira": (13.7416, 76.9042),
    "Pavagada": (14.1001, 77.2806),
    "Gubbi": (13.3128, 76.9416),
    "Koratagere": (13.5222, 77.2376),
    "Chikkanayakanahalli": (13.4167, 76.6167),
    "Turuvekere": (13.1632, 76.6667),
    "Kunigal": (13.0232, 77.0256)
}

# --- Example: Use most recent forecast/heatwave data ---
from shared_data import WARD_DATA, calculate_heatwave_percentage


def show_tumakuru_map():
    """Embed the Leaflet Tumakuru heatwave map directly inside Streamlit."""
    st.title("Tumakuru District Heatwave Map")
    st.markdown(
        "Interactive Tumakuru map with markers showing **temperature** and **predicted heatwave %** for each taluk."
    )

    # Build a small JSON-like dict for passing to JS (kept here for clarity, although the
    # current Leaflet code uses the same constants directly in JS).
    map_data = []
    for taluk, (lat, lon) in taluk_coords.items():
        ward_data = WARD_DATA.get(taluk)
        if not ward_data:
            continue
        map_data.append(
            {
                "Taluk": taluk,
                "Latitude": lat,
                "Longitude": lon,
                "Temp_2m": ward_data["Temp_2m"],
                "Humidity": ward_data["Humidity"],
                "Green_Cover_": ward_data["Green_Cover_"],
                "Traffic_Index": ward_data["Traffic_Index"],
                "AIQ": ward_data["AIQ"],
                "Precipitation_mm": ward_data["Precipitation_mm"],
            }
        )

    # Data is still constructed in Python in case you want to reuse it later,
    # but we no longer render the debug table in the UI.
    df_map = pd.DataFrame(map_data)

    # Exact Leaflet HTML/JS embedded into Streamlit
    leaflet_html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <link
    rel="stylesheet"
    href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
    integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
    crossorigin=""
  />
  <style>
    html, body {
      margin: 0;
      padding: 0;
      height: 100%;
      width: 100%;
    }
    #map {
      height: 600px;
      width: 100%;
    }
    .popup-title {
      font-weight: 600;
      margin-bottom: 4px;
    }
    .popup-line {
      margin: 0;
      font-size: 13px;
    }
  </style>
</head>
<body>
  <div id="map"></div>

  <script
    src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
    integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="
    crossorigin=""
  ></script>

  <script>
    const TALUK_COORDS = {
      "Tumakuru": [13.3411, 77.1010],
      "Tiptur": [13.2569, 76.4777],
      "Madhugiri": [13.6601, 77.2123],
      "Sira": [13.7416, 76.9042],
      "Pavagada": [14.1001, 77.2806],
      "Gubbi": [13.3128, 76.9416],
      "Koratagere": [13.5222, 77.2376],
      "Chikkanayakanahalli": [13.4167, 76.6167],
      "Turuvekere": [13.1632, 76.6667],
      "Kunigal": [13.0232, 77.0256]
    };

    const WARD_DATA = {
      "Tumakuru": { Temp_2m: 39, Humidity: 58, Green_Cover_: 25, Traffic_Index: 80, AIQ: 65, Precipitation_mm: 6 },
      "Kunigal": { Temp_2m: 42, Humidity: 55, Green_Cover_: 18, Traffic_Index: 60, AIQ: 65, Precipitation_mm: 4 },
      "Turuvekere": { Temp_2m: 41, Humidity: 53, Green_Cover_: 20, Traffic_Index: 45, AIQ: 40, Precipitation_mm: 5 },
      "Tiptur": { Temp_2m: 43, Humidity: 50, Green_Cover_: 15, Traffic_Index: 85, AIQ: 70, Precipitation_mm: 3 },
      "Chikkanayakanahalli": { Temp_2m: 38, Humidity: 60, Green_Cover_: 30, Traffic_Index: 50, AIQ: 50, Precipitation_mm: 7 },
      "Sira": { Temp_2m: 40, Humidity: 57, Green_Cover_: 22, Traffic_Index: 65, AIQ: 58, Precipitation_mm: 5 },
      "Pavagada": { Temp_2m: 70, Humidity: 52, Green_Cover_: 30, Traffic_Index: 40, AIQ: 35, Precipitation_mm: 2 },
      "Madhugiri": { Temp_2m: 41, Humidity: 30, Green_Cover_: 20, Traffic_Index: 60, AIQ: 50, Precipitation_mm: 30 },
      "Koratagere": { Temp_2m: 60, Humidity: 40, Green_Cover_: 25, Traffic_Index: 30, AIQ: 20, Precipitation_mm: 6 }
    };

    function calculateHeatwavePercentage(d) {
      const tempWeight = 0.4;
      const humidityWeight = 0.1;
      const greenCoverWeight = -0.1;
      const trafficWeight = 0.2;
      const aiqWeight = 0.2;
      const precipitationWeight = -0.1;

      let score =
        d.Temp_2m * tempWeight +
        d.Humidity * humidityWeight +
        d.Green_Cover_ * greenCoverWeight +
        d.Traffic_Index * trafficWeight +
        d.AIQ * aiqWeight +
        d.Precipitation_mm * precipitationWeight;

      return Math.min(Math.max(Math.round(score), 0), 100);
    }

    const map = L.map("map").setView([13.4, 77.0], 8.5);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 18,
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    Object.keys(TALUK_COORDS).forEach((taluk) => {
      const coord = TALUK_COORDS[taluk];
      const data = WARD_DATA[taluk];
      if (!coord || !data) return;

      const heatwave = calculateHeatwavePercentage(data);
      const temp = data.Temp_2m;
      const radius = 10 + heatwave * 0.3;

      const circle = L.circleMarker(coord, {
        radius,
        color: "#c0392b",
        weight: 1,
        fillColor: "#e74c3c",
        fillOpacity: 0.6
      }).addTo(map);

      const popupHtml = `
        <div>
          <div class="popup-title">${taluk}</div>
          <p class="popup-line">Temperature: <b>${temp}&deg;C</b></p>
          <p class="popup-line">Predicted Heatwave: <b>${heatwave}%</b></p>
        </div>
      `;

      circle.bindPopup(popupHtml);
    });
  </script>
</body>
</html>
    """

    components.html(leaflet_html, height=650, scrolling=False)
