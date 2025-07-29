
import streamlit as st
import cv2
import numpy as np
from PIL import Image
import xml.etree.ElementTree as ET
from io import BytesIO

st.title("QR GPX Parser with OpenCV")

uploaded_file = st.file_uploader("Upload QR-code from XCTrack", type=["png", "jpg", "jpeg"])
if uploaded_file:
    image = Image.open(uploaded_file)
    img_array = np.array(image)

    detector = cv2.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(img_array)

    if data:
        st.success("QR detected.")
        if "<gpx" in data:
            try:
                root = ET.fromstring(data)
                waypoints = root.findall(".//{http://www.topografix.com/GPX/1/1}rtept")
                st.success(f"Parsed {len(waypoints)} waypoints from GPX.")
                for i, wpt in enumerate(waypoints):
                    lat = wpt.attrib["lat"]
                    lon = wpt.attrib["lon"]
                    name = wpt.find("{http://www.topografix.com/GPX/1/1}name").text if wpt.find("{http://www.topografix.com/GPX/1/1}name") is not None else "N/A"
                    st.markdown(f"**{i+1}. {name}** — {lat}, {lon}")
            except Exception as e:
                st.error(f"Failed to parse GPX: {e}")
        else:
            st.error("QR detected but does not contain GPX data.")
    else:
        st.error("No QR code detected.")
    
