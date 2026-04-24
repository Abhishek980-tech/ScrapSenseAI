"""
map_view.py
-----------
Generates an interactive global pollution map using Folium.
Renders pollution report markers from community-submitted data.
"""

import folium
import pandas as pd
from folium.plugins import MarkerCluster


def build_pollution_map(reports_df: pd.DataFrame) -> folium.Map:
    """
    Build a Folium map with markers for each valid pollution report.

    Args:
        reports_df (pd.DataFrame): DataFrame containing valid report data
                                   (must have Latitude, Longitude, Name,
                                    Location, Description columns).

    Returns:
        folium.Map: Configured Folium map object with all markers added.
    """
    # Initialize map centered at a global view
    pollution_map = folium.Map(
        location=[20, 0],
        zoom_start=2,
        tiles="CartoDB positron",  # Clean, minimal basemap
        attr="CartoDB"
    )

    if reports_df.empty:
        # Add a placeholder info box when no reports exist
        folium.Marker(
            location=[20, 0],
            popup=folium.Popup("No reports yet. Submit one in the Community Reports tab!", max_width=250),
            icon=folium.Icon(color="gray", icon="info-sign")
        ).add_to(pollution_map)
        return pollution_map

    # Use MarkerCluster for better performance with many markers
    cluster = MarkerCluster(name="Pollution Reports").add_to(pollution_map)

    for _, row in reports_df.iterrows():
        try:
            lat = float(row["Latitude"])
            lon = float(row["Longitude"])
            name = str(row.get("Name", "Anonymous"))
            location = str(row.get("Location", "Unknown Location"))
            description = str(row.get("Description", "No description provided."))
            timestamp = str(row.get("Timestamp", ""))

            # Build popup HTML content
            popup_html = f"""
            <div style="font-family: Arial, sans-serif; min-width: 200px;">
                <h4 style="color: #1a6b8a; margin-bottom: 6px;">🌊 Pollution Report</h4>
                <hr style="border-color: #1a6b8a; margin: 4px 0;">
                <p><strong>👤 Reporter:</strong> {name}</p>
                <p><strong>📍 Location:</strong> {location}</p>
                <p><strong>📝 Description:</strong><br>{description}</p>
                {"<p><strong>🕐 Reported:</strong> " + timestamp + "</p>" if timestamp else ""}
            </div>
            """

            popup = folium.Popup(popup_html, max_width=300)

            # Use a custom red pollution marker
            folium.Marker(
                location=[lat, lon],
                popup=popup,
                tooltip=f"📍 {location} — {name}",
                icon=folium.Icon(
                    color="red",
                    icon="exclamation-sign",
                    prefix="glyphicon"
                )
            ).add_to(cluster)

        except (ValueError, TypeError):
            # Skip rows with invalid coordinates
            continue

    # Add a layer control panel
    folium.LayerControl().add_to(pollution_map)

    return pollution_map
