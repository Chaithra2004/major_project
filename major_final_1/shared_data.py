# shared_data.py

WARD_DATA = {
    "Tumakuru": {"Temp_2m": 39, "Humidity": 58, "Green_Cover_": 25, "Traffic_Index": 80, "AIQ": 65, "Precipitation_mm": 6},
    "Kunigal": {"Temp_2m": 42, "Humidity": 55, "Green_Cover_": 18, "Traffic_Index": 60, "AIQ": 65, "Precipitation_mm": 4},
    "Turuvekere": {"Temp_2m": 41, "Humidity": 53, "Green_Cover_": 20, "Traffic_Index": 45, "AIQ": 40, "Precipitation_mm": 5},
    "Tiptur": {"Temp_2m": 43, "Humidity": 50, "Green_Cover_": 15, "Traffic_Index": 85, "AIQ": 70, "Precipitation_mm": 3},
    "Chikkanayakanahalli": {"Temp_2m": 38, "Humidity": 60, "Green_Cover_": 30, "Traffic_Index": 50, "AIQ": 50, "Precipitation_mm": 7},
    "Sira": {"Temp_2m": 40, "Humidity": 57, "Green_Cover_": 22, "Traffic_Index": 65, "AIQ": 58, "Precipitation_mm": 5},
    "Pavagada": {"Temp_2m": 70, "Humidity": 52, "Green_Cover_": 30, "Traffic_Index": 40, "AIQ": 35, "Precipitation_mm": 2},
    "Madhugiri": {"Temp_2m": 41, "Humidity": 30, "Green_Cover_": 20, "Traffic_Index": 60, "AIQ": 50, "Precipitation_mm": 30},
    "Koratagere": {"Temp_2m": 60, "Humidity": 40, "Green_Cover_": 25, "Traffic_Index": 30, "AIQ": 20, "Precipitation_mm": 6}
}

def calculate_heatwave_percentage(data):
    tempWeight = 0.4
    humidityWeight = 0.1
    greenCoverWeight = -0.1  # more green cover reduces heatwave
    trafficWeight = 0.2
    aiqWeight = 0.2
    precipitationWeight = -0.1  # more rain reduces heatwave

    score = (
        data["Temp_2m"] * tempWeight +
        data["Humidity"] * humidityWeight +
        data["Green_Cover_"] * greenCoverWeight +
        data["Traffic_Index"] * trafficWeight +
        data["AIQ"] * aiqWeight +
        data["Precipitation_mm"] * precipitationWeight
    )
    percentage = min(max(round(score), 0), 100)
    return percentage
