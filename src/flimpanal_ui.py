import streamlit as st

from src.flimpanal_geo import analyze_location
from src.flimpanal_map import create_map
import streamlit.components.v1 as components
import requests
from src.flimpanal_ai import parse_analysis_request
from pydantic import ValidationError
from openai import OpenAIError


def run_ui():
    st.title("Flood Impact Analysis")

    analysis_method = st.radio(
        "Analysis method",
        ["Parameters", "Natural language"],
    )

    if analysis_method == "Parameters":
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

    else:
        query = st.text_area(
            "Describe the analysis",
            placeholder=("Show me buildings exposed to flooding within 3 km of Brno.")
        )


    if st.button("Analyze"):

        try:
            if analysis_method == "Natural language":
                # empty request
                if not query.strip(): 
                    st.error("Please describe the analysis you want to perform.")
                    return

                request = parse_analysis_request(query)
            
                location = request.location
                radius_km = request.radius_km
            
                st.info(
                    f"Interpreted request: {location}, "
                    f"radius {radius_km:g} km"
                )

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

        except ValidationError:
            st.error(
                "The analysis radius must be greater than 0 "
                "and no more than 10 km."
            )
            return

        except OpenAIError:
            st.error(
                "Could not interpret the natural-language request. "
                "Please try again later or use the Parameters option."
            )
            return

        except ValueError as e:
            st.error(str(e))
            return

        except requests.RequestException:
            st.error("Could not retrieve external data. Please try again later.")
            return

        if flood_zones.empty:
            st.info(
                "Analysis complete. No Q100 flood zone was found within the analysis area."
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
