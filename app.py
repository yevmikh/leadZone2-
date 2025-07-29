import streamlit as st
import json
from geopy.distance import geodesic
import matplotlib.pyplot as plt

st.title("XCTrack .xctsk Analyzer: Lead Zone Calculator")

uploaded = st.file_uploader("Upload .xctsk file", type="xctsk")

def parse_task(json_data):
    turnpoints = json_data["turnpoints"]
    coords = [(pt["waypoint"]["lat"], pt["waypoint"]["lon"]) for pt in turnpoints]
    names = [pt["waypoint"]["name"] for pt in turnpoints]
    return coords, names

def calc_distances(coords):
    segments = [geodesic(coords[i], coords[i+1]).km for i in range(len(coords)-1)]
    return segments, sum(segments)

if uploaded:
    try:
        data = uploaded.read().decode("utf-8")
        json_data = json.loads(data)
        coords, names = parse_task(json_data)
        segments, total_dist = calc_distances(coords)

        st.markdown(f"### Total task distance: **{total_dist:.2f} km**")

        zone_start = total_dist * 0.2
        zone_end = total_dist * 0.6
        st.markdown(f"🟧 Max lead points zone: **{zone_start:.2f} - {zone_end:.2f} km**")

        st.markdown("### Task segments:")
        for i, dist in enumerate(segments):
            st.write(f"{names[i]} → {names[i+1]}: {dist:.2f} km")

        # Побудова графіка зони
        x = [sum(segments[:i]) for i in range(len(segments)+1)]
        y = [0]*len(x)
        fig, ax = plt.subplots()
        ax.plot(x, y, "o-", label="Task Route")
        ax.axvspan(zone_start, zone_end, color="orange", alpha=0.3, label="Max lead zone")
        ax.set_xlabel("Distance (km)")
        ax.set_yticks([])
        ax.set_title("Lead Points Zone in Task")
        ax.legend()
        st.pyplot(fig)

    except Exception as e:
        st.error(f"Failed to process file: {e}")
