import streamlit as st
from datetime import datetime, timedelta
from praytimes import PrayTimes
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import random

# Mock function to get lat/lon from waypoint names
def mock_geocode_waypoint(wpt):
    # Just generate a fake lat/lon for demo purposes
    random.seed(wpt)
    lat = random.uniform(10, 50)
    lon = random.uniform(-30, 60)
    return lat, lon

# Interpolate timestamps along the route
def interpolate_times(start_time, num_points, interval_minutes=20):
    return [start_time + timedelta(minutes=i * interval_minutes) for i in range(num_points)]

# Get prayer times using PrayTimes lib
def get_prayer_times(lat, lon, dt):
    pt = PrayTimes('MWL')
    pt.adjust({'fajr': 18, 'isha': 17})
    times = pt.getTimes(
        dt.replace(tzinfo=None), (lat, lon), 0)
    return times

# Streamlit UI
st.title("🛫 Route-based Islamic Prayer Time Calculator")
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

        # Mock geocode
        geo_points = [mock_geocode_waypoint(wpt) for wpt in waypoints]

        # Interpolate times
        base_dt = datetime.combine(departure_date, departure_time)
        times = interpolate_times(base_dt, len(geo_points))

        # Calculate prayer times
        prayer_results = []
        for idx, (lat, lon) in enumerate(geo_points):
            prayers = get_prayer_times(lat, lon, times[idx])
            prayer_results.append((waypoints[idx], lat, lon, times[idx], prayers))

        # Map
        m = folium.Map(location=geo_points[0], zoom_start=4)
        marker_cluster = MarkerCluster().add_to(m)

        for wp, lat, lon, dt, pr in prayer_results:
            popup_text = f"<b>{wp}</b><br>{dt.strftime('%Y-%m-%d %H:%M')} UTC<br>" + "<br>".join(
                [f"{k.title()}: {v}" for k, v in pr.items()]
            )
            folium.Marker(location=(lat, lon), popup=popup_text).add_to(marker_cluster)

        st.markdown("### 🌍 Route Map with Prayer Times")
        st_data = st_folium(m, width=800, height=500)

        # Table
        st.markdown("### 🕌 Prayer Time Table")
        st.write([
            {
                "Waypoint": wp,
                "Time (UTC)": dt.strftime("%H:%M"),
                **pr
            } for wp, _, _, dt, pr in prayer_results
        ])
