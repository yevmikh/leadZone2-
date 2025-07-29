import streamlit as st
import cv2
import numpy as np
import base64
import xml.etree.ElementTree as ET
from io import BytesIO
from PIL import Image
import matplotlib.pyplot as plt

def decode_qr_opencv(image: Image.Image) -> str:
    np_image = np.array(image.convert("RGB"))
    detector = cv2.QRCodeDetector()
    data, _, _ = detector.detectAndDecode(np_image)
    return data

def parse_gpx_from_text(text: str):
    try:
        root = ET.fromstring(text)
        wpts = root.findall(".//{http://www.topografix.com/GPX/1/1}wpt")
        points = []
        for wpt in wpts:
            lat = float(wpt.attrib["lat"])
            lon = float(wpt.attrib["lon"])
            name = wpt.find("{http://www.topografix.com/GPX/1/1}name")
            points.append((lat, lon, name.text if name is not None else ""))
        return points
    except:
        return None

st.title("QR GPX Parser with OpenCV")

uploaded_file = st.file_uploader("Upload QR-code from XCTrack", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    qr_text = decode_qr_opencv(image)
    if qr_text:
        st.success("QR detected.")
        gpx_points = parse_gpx_from_text(qr_text)
        if gpx_points:
            st.success(f"Parsed {len(gpx_points)} waypoints.")
            for lat, lon, name in gpx_points:
                st.write(f"📍 {name}: {lat}, {lon}")
        else:
            st.error("QR detected but could not parse GPX waypoints.")
    else:
        st.error("No QR code detected.")
