import streamlit as st
import json
import cv2
import numpy as np
from PIL import Image
from geopy.distance import geodesic
import matplotlib.pyplot as plt

def decode_qr_from_image(uploaded_image):
    image = Image.open(uploaded_image).convert("RGB")
    img_np = np.array(image)
    detector = cv2.QRCodeDetector()
    data, _, _ = detector.detectAndDecode(img_np)
    return data

def parse_task_from_xctsk(json_data):
    turnpoints = json_data["turnpoints"]
    coords = [(pt["waypoint"]["lat"], pt["waypoint"]["lon"]) for pt in turnpoints]
    names = [pt["waypoint"]["name"] for pt in turnpoints]
    return coords, names

def calc_distances(coords):
    segments = [geodesic(coords[i], coords[i+1]).km for i in range(len(coords)-1)]
    return segments, sum(segments)

st.title("XCTrack QR Analyzer with Lead Points Zone")

uploaded_qr = st.file_uploader("Upload QR-code image (from XCTrack)", type=["png", "jpg", "jpeg"])

if uploaded_qr:
    qr_data = decode_qr_from_image(uploaded_qr)
    if not qr_data:
        st.error("❌ QR-код не розпізнано.")
    else:
        try:
            task_json = json.loads(qr_data)
            coords, names = parse_task_from_xctsk(task_json)
            segments, total_dist = calc_distances(coords)

            zone_start = total_dist * 0.2
            zone_end = total_dist * 0.6

            st.markdown(f"### Загальна довжина таску: **{total_dist:.2f} км**")
            st.markdown(f"🟧 Зона макс. лідерських балів: **{zone_start:.2f} — {zone_end:.2f} км**")

            st.markdown("### Сегменти маршруту:")
            for i, dist in enumerate(segments):
                st.write(f"{names[i]} → {names[i+1]}: {dist:.2f} км")

            x = [sum(segments[:i]) for i in range(len(segments)+1)]
            y = [0]*len(x)
            fig, ax = plt.subplots()
            ax.plot(x, y, "o-", label="Маршрут")
            ax.axvspan(zone_start, zone_end, color="orange", alpha=0.3, label="Зона лідерства")
            ax.set_xlabel("Відстань (км)")
            ax.set_yticks([])
            ax.legend()
            st.pyplot(fig)
        except Exception as e:
            st.error(f"Помилка обробки таску: {e}")
