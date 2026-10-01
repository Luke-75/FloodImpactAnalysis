import streamlit as st

from src.flimpanal_geo import analyze_location
from src.flimpanal_map import create_map
import streamlit.components.v1 as components
import requests


def run_ui():
    st.title("Flood Impact Analysis")

    location = st.text_input(
        "Location",
        value="Prague"
    )

    radius_km = st.number_input(
        "Analysis radius (km)",
        min_value=0.5,
        max_value=10.0,
        value=2.0,
        step=0.5
    )


    if st.button("Analyze"):

        try:
            with st.spinner("Analyzing flood impact..."):
                (
                    lat,
                    lon,
                    analysis_area,
                    flood_zones,
                    buildings,
                    affected_buildings,
                ) = analyze_location(
                    location,
                    radius_km
                )
        except ValueError as e:
            st.error(str(e))
            return

        except requests.RequestException:
            st.error("Could not retrieve external data. Please try again later.")
            return

        #st.success("Analysis complete")
        if flood_zones.empty:
            st.info(
                "No Q100 flood zone was found within the analysis area."
            )
        else:
            if flood_zones.empty:
                st.info(
                "Analysis complete. No Q100 flood zone was found "
                "within the analysis area."
                )
            else:
                st.success("Analysis complete")

        #st.write(f"Total buildings: {len(buildings)}")
        #st.write(f"Affected buildings: {len(affected_buildings)}")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Total buildings",
            f"{len(buildings):,}"
        )

        col2.metric(
            "Affected buildings",
            f"{len(affected_buildings):,}"
        )

        flood_area_km2 = flood_zones.geometry.area.sum() / 1_000_000

        col3.metric(
            "Q100 flood area",
            f"{flood_area_km2:.2f} km²"
        )

        flood_map = create_map(lat, lon, analysis_area, flood_zones, affected_buildings)

        html = flood_map.get_root().render()

        #st.write(f"Map HTML size: {len(html):,} characters")

        components.html(
            #flood_map.get_root().render(),
            html,
            height=650,
            scrolling=False,
        )


#if __name__ == "__main__":
#    run_ui()
