import streamlit as st
from datetime import datetime, timedelta
from suntime import Sun
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import random

# Safe wrapper for sunrise/sunset
def safe_sun_time(func, date):
    try:
        return func(date).time()
    except:
        return datetime.min.time()

# Calculate prayer times using solar angles
def get_prayer_times(lat, lon, date):
    sun = Sun(lat, lon)
    sunrise = safe_sun_time(sun.get_sunrise_time, date)
    sunset = safe_sun_time(sun.get_sunset_time, date)
    fajr = (datetime.combine(date, sunrise) - timedelta(minutes=90)).time()
    isha = (datetime.combine(date, sunset) + timedelta(minutes=90)).time()
    dhuhr = (datetime.combine(date, sunrise) + (datetime.combine(date, sunset) - datetime.combine(date, sunrise)) / 2).time()
    asr = (datetime.combine(date, dhuhr) + timedelta(minutes=90)).time()
    return {
        "Fajr": fajr.strftime("%H:%M"),
        "Sunrise": sunrise.strftime("%H:%M"),
        "Dhuhr": dhuhr.strftime("%H:%M"),
        "Asr": asr.strftime("%H:%M"),
        "Maghrib": sunset.strftime("%H:%M"),
        "Isha": isha.strftime("%H:%M")
    }

# Fake coordinates per waypoint
def mock_geocode_waypoint(wpt):
    random.seed(wpt)
    lat = random.uniform(10, 50)
    lon = random.uniform(-30, 60)
    return lat, lon

def interpolate_times(start_time, n, interval=20):
    return [start_time + timedelta(minutes=i * interval) for i in range(n)]

# --- Streamlit App ---
st.set_page_config(page_title="Lido Flight Prayer Times", layout="wide")
st.title("🛫 Flight Route Islamic Prayer Times")

route_input = st.text_area("Paste Lido route string:", height=100)

