import streamlit as st
from datetime import datetime, timedelta
from suntime import Sun
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import random
import fitz  # PyMuPDF for PDF reading

st.set_page_config(page_title="Lido Flight Prayer Times", layout="wide")
st.title("🛫 Lido Flight Plan Prayer Time Calculator")

# --- INPUTS ---

upload = st.file_uploader("📎 Upload Lido PDF flight plan (optional)", type=["pdf"])
route_text = st.text_area("✏️ Or paste Lido route string", height=100)
departure_date = st.date_input("📆 Departure Date")
departure_time = st.time_input("🕓 Departure Time (UTC)")
altitude = st.number_input("🛫 Cruise Flight Level (e.g. FL360)", min_value=100, max_value=500, value_
