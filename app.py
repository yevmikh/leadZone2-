
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO
import xml.etree.ElementTree as ET
import re
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic
import cv2

def weight_curve(x, total_dist):
    x_rel = x / total_dist
    rising = (1 - 10 ** (-9 * x_rel)) ** 5
    falling = (1 - 10 ** (-3 * (1 - x_rel))) ** 2
    return rising * falling

def decode_qr(uploaded_image):
    image = Image.open(uploaded_image).convert("RGB")
    img_np = np.array(image)
    img_cv = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    detector = cv2.QRCodeDetector()
    data, _, _ = detector.detectAndDecode(img_cv)
    return data if data else None

def parse_gpx_coords(qr_data):
    try:
        root = ET.fromstring(qr_data)
        coords = []
        for wpt in root.findall(".//wpt"):
            lat = float(wpt.attrib["lat"])
            lon = float(wpt.attrib["lon"])
            coords.append((lat, lon))
        return coords if len(coords) >= 2 else None
    except:
        return None

def compute_task_distance(coords):
    dists = [geodesic(coords[i], coords[i+1]).km for i in range(len(coords)-1)]
    return sum(dists)

st.title("XCTrack QR → Max Lead Zone with Map (OpenCV QR)")

uploaded_image = st.file_uploader("Upload QR-code from XCTrack", type=["png", "jpg", "jpeg"])
coords = []
dist = None

if uploaded_image:
    qr_data = decode_qr(uploaded_image)
    if qr_data:
        coords = parse_gpx_coords(qr_data)
        if coords:
            dist = compute_task_distance(coords)
            st.success(f"Parsed task distance: {dist:.1f} km")
            # карта
            m = folium.Map(location=coords[0], zoom_start=12)
            for i, (lat, lon) in enumerate(coords):
                folium.Marker([lat, lon], tooltip=f"WPT {i+1}").add_to(m)
            folium.PolyLine(coords, color="blue").add_to(m)
            st_folium(m, width=700, height=500)
        else:
            st.error("QR detected but could not parse GPX waypoints.")
    else:
        st.error("QR not recognized.")

if not dist:
    dist = st.number_input("Or enter task distance manually (in km)", min_value=10.0, max_value=300.0, value=100.0)

if dist:
    x = np.linspace(0, dist, 1000)
    y = weight_curve(x, dist)
    max_weight = max(y)
    threshold = max_weight * 0.98
    zone_indices = np.where(y >= threshold)[0]
    zone_start = x[zone_indices[0]]
    zone_end = x[zone_indices[-1]]

    st.markdown(f"### Best zone to lead:\n**{zone_start:.1f} km** to **{zone_end:.1f} km** ({zone_end - zone_start:.1f} km)")

    fig, ax = plt.subplots()
    ax.plot(x, y, label="Leading Weight Curve")
    ax.fill_between(x, y, where=(y >= threshold), color="orange", alpha=0.3,
                    label=f"Max Lead Zone: {zone_start:.1f}-{zone_end:.1f} km")
    ax.set_xlabel("Distance in task (km)")
    ax.set_ylabel("Relative weight")
    ax.set_title("Leading Coefficient Weight Curve")
    ax.legend()
    st.pyplot(fig)
