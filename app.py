import streamlit as st
from datetime import datetime, timedelta
from suntime import Sun
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import random
import math

# Function to calculate prayer times (simplified)
def get_prayer_times(lat, lon, date):
    sun = Sun(lat, lon)
    try:
        sunrise = sun.get_sunrise_time(date).time()
        sunset = sun.get_sunset_time(date).time()
    except:
        sunrise = sunset = datetime.min.time()

    # Fajr and Isha using 18° angle approximation
    fajr = (datetime.combine(date, sunrise) - timedelta(minutes=90)).time()
    isha = (datetime.combine(date, sunset) + timedelta(minutes=90)).time()

    # Dhuhr = solar noon
    dhuhr = (datetime.combine(date, sunrise) + (datetime.combine(date, sunset) - datetime.combine(date, sunrise)) / 2).time()

    # Asr (simplified, shadow 1x)
    asr = (datetime.combine(date, dhuhr) + timedelta(minutes=90)).time()

    return {
        "Fajr": fajr.strftime("%H:%M"),
        "Sunrise": sunrise.strftime("%H:%M"),
        "Dhuhr": dhuhr.strftime("%H:%M"),
        "Asr": asr.strftime("%H:%M"),
        "Maghrib": sunset.strftime("%H:%M"),
        "Isha": isha.strftime("%H:%M"),
    }

# Mock geocode
def mock_geocode_waypoint(wpt):
    random.seed(wpt)
    lat = random.uniform(10, 50)
    lon = random.uniform(-30, 60)
    return lat, lon

# Interpolate time
def interpolate_times(start_time, num_points, interval_minutes=20):
    return [start_time + timedelta(minutes=i * interval_minutes) for i in range(num_points)]

# Streamlit App
st.title("🛫 Flight Route Islamic Prayer Times")
route_input = st.text_area("Paste Lido route string:", height=150)

departure_date = st.date_input("Departure date")
departure_time = st.time_input("Departure time (UTC)")

if st.button("Calculate Prayer Times"):
    if not route_input.strip():
        st.warning("Please paste a valid route string.")
    else:
        route_list = route_input.strip().split()
        waypoints = [wpt for wpt in route_list if wpt not in ["DCT"] and len(wpt) <= 6]
        st.success(f"Detected {len(waypoints)} waypoints")

        geo_points = [mock_geocode_waypoint(wpt) for wpt in waypoints]
        base_dt = datetime.combine(departure_date, departure_time)
        times = interpolate_times(base_dt, len(geo_points))

        prayer_results = []
        for idx, (lat, lon) in enumerate(geo_points):
            dt = times[idx]
            prayers = get_prayer_times(lat, lon, dt.date())
            prayer_results.append((waypoints[idx], lat, lon, dt, prayers))

        m = folium.Map(location=geo_points[0], zoom_start=4)
        marker_cluster = MarkerCluster().add_to(m)

        for wp, lat, lon, dt, pr in prayer_results:
            popup_text = f"<b>{wp}</b><br>{dt.strftime('%Y-%m-%d %H:%M')} UTC<br>" + "<br>".join(
                [f"{k}: {v}" for k, v in pr.items()]
            )
            folium.Marker(location=(lat, lon), popup=popup_text).add_to(marker_cluster)

        st.markdown("### 🌍 Route Map")
        st_data = st_folium(m, width=800, height=500)

        st.markdown("### 🕌 Prayer Time Table")
        st.write([
            {
                "Waypoint": wp,
                "Time (UTC)": dt.strftime("%H:%M"),
                **pr
            } for wp, _, _, dt, pr in prayer_results
        ])
