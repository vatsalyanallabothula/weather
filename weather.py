import streamlit as st
from streamlit_js_eval import get_geolocation
import requests

# -------------------------------
# 🌍 APP CONFIGURATION
# -------------------------------
st.set_page_config(page_title="☁️ WeatherSense", page_icon="🌎", layout="wide")

WEATHER_API_KEY = "65b9ebfde30d0bbd0e38a973a638f850"

st.title("🌦️ WeatherSense — Real Feel Weather Assistant")
st.markdown("Get **real-time weather** and **natural comfort insights** 🌤️")
st.divider()

# -------------------------------
# 📍 AUTO LOCATION DETECTION
# -------------------------------
if "location_data" not in st.session_state:
    st.session_state.location_data = None

if st.session_state.location_data is None:
    with st.spinner("📡 Detecting your location... please allow browser permission"):
        loc = get_geolocation()
        if loc:
            st.session_state.location_data = loc
            st.rerun()
        else:
            st.stop()

# Extract coordinates
loc = st.session_state.location_data
lat = loc.get("coords", {}).get("latitude")
lon = loc.get("coords", {}).get("longitude")

if not lat or not lon:
    st.stop()

st.success(f"✅ Location detected — Latitude: `{lat:.4f}`, Longitude: `{lon:.4f}`")

# -------------------------------
# 🌦️ FETCH WEATHER DATA
# -------------------------------
weather_url = (
    f"https://api.openweathermap.org/data/2.5/weather"
    f"?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
)

try:
    res = requests.get(weather_url, timeout=10)
    res.raise_for_status()
    data_we = res.json()
except requests.exceptions.RequestException as e:
    st.error(f"⚠️ Unable to fetch weather data: {e}")
    st.stop()

# Extract data
city = data_we.get("name", "Unknown Area")  # only city name
weather_info = data_we.get("weather", [{}])[0]
weather_desc = weather_info.get("description", "N/A").title()
icon = weather_info.get("icon", "01d")

main = data_we.get("main", {})
temp = main.get("temp", "N/A")
humidity = main.get("humidity", "N/A")
wind_speed = data_we.get("wind", {}).get("speed", "N/A")
icon_url = f"http://openweathermap.org/img/wn/{icon}@2x.png"

# -------------------------------
# 🗺️ DISPLAY WEATHER & MAP
# -------------------------------
col_map, col_weather = st.columns([1.2, 1.3])

with col_map:
    st.subheader("🗺️ Your Location")
    st.map([{"lat": lat, "lon": lon}])

with col_weather:
    st.subheader(f"🌆 Weather — {city}")  # 👈 only city name, no country
    c1, c2 = st.columns([1, 2])
    with c1:
        st.image(icon_url, width=90)
    with c2:
        st.markdown(f"**🌤 Condition:** {weather_desc}")
        st.metric("🌡 Temperature", f"{temp}°C")
        st.metric("💧 Humidity", f"{humidity}%")
        st.metric("🌬 Wind Speed", f"{wind_speed} m/s")

st.divider()

# -------------------------------
# 🌈 NATURAL COMFORT ANALYSIS
# -------------------------------
st.subheader("🌈 Natural Comfort Summary")

if isinstance(temp, (int, float)):
    if temp < 0:
        st.info("🥶 Extremely cold! Frostbite risk — stay indoors and wear thermal layers.")
    elif 0 <= temp < 10:
        st.warning("🧣 Very cold — dress warmly with a coat or jacket.")
    elif 10 <= temp < 18:
        st.info("🌬️ Cool and pleasant, might need a light jacket in evenings.")
    elif 18 <= temp < 26:
        st.success("😊 Ideal weather — comfortable and fresh air!")
    elif 26 <= temp < 32:
        if humidity > 70:
            st.warning("💦 Warm and humid — feels sticky, stay hydrated.")
        else:
            st.info("🌤 Slightly warm — wear breathable cotton clothes.")
    elif 32 <= temp < 38:
        st.warning("🥵 Hot — avoid heavy outdoor work, drink plenty of water.")
    else:
        st.error("🔥 Extreme heat! Stay cool and avoid direct sunlight.")
else:
    st.warning("⚠️ Unable to determine temperature.")

st.caption("Data powered by OpenWeatherMap 🌎")
