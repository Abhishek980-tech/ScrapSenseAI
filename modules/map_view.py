import folium
import pandas as pd
from folium.plugins import MarkerCluster


def build_pollution_map(reports_df: pd.DataFrame) -> folium.Map:
    """
    Build a Folium map with markers for each valid pollution report.

    Args:
        reports_df (pd.DataFrame): DataFrame containing valid report data
                                   (must have latitude, longitude, name,
                                    location_name, description columns).

    Returns:
        folium.Map: Configured Folium map object with all markers added.
    """
    pollution_map = folium.Map(
        location=[20, 0],
        zoom_start=2,
        tiles="CartoDB positron",
        attr="CartoDB"
    )

    if reports_df.empty:
        folium.Marker(
            location=[20, 0],
            popup=folium.Popup("No reports yet. Submit one in the Community Reports tab!", max_width=250),
            icon=folium.Icon(color="gray", icon="info-sign")
        ).add_to(pollution_map)
        return pollution_map

    cluster = MarkerCluster(name="Pollution Reports").add_to(pollution_map)

    for _, row in reports_df.iterrows():
        try:
            lat = float(row["latitude"])
            lon = float(row["longitude"])
            name = str(row.get("name", "Anonymous"))
            location_name = str(row.get("location_name", row.get("location", "Unknown Location")))
            description = str(row.get("description", "No description provided."))
            timestamp = row.get("timestamp", "")
            source = str(row.get("source", "manual")).capitalize()
            user_email = str(row.get("user_email", ""))

            popup_html = f"""
            <div style="font-family: Arial, sans-serif; min-width: 220px; max-height: 300px; overflow-y: auto;">
                <h4 style="color: #1a6b8a; margin-bottom: 6px;">🌊 Pollution Report</h4>
                <hr style="border-color: #1a6b8a; margin: 4px 0;">
                <p><strong>👤 Reporter:</strong> {name}</p>
                <p><strong>📍 Location:</strong> {location_name}</p>
                <p><strong>📝 Description:</strong><br>{description}</p>
                {f"<p><strong>🕐 Reported:</strong> {timestamp}</p>" if timestamp else ""}
                {f"<p><strong>📌 Source:</strong> {source}</p>" if source else ""}
                {f"<p><strong>✉️ User:</strong> {user_email}</p>" if user_email else ""}
            </div>
            """

            popup = folium.Popup(popup_html, max_width=320)

            # Different icons based on source: detection vs manual community reports
            source_lower = str(row.get("source", "manual")).lower()
            
            if source_lower == "detection":
                # Blue marker with camera icon for detection reports
                icon = folium.Icon(color="blue", icon="camera", prefix="fa")
                tooltip = f"🔍 Detection: {location_name}"
            else:
                # Red marker with exclamation sign for community reports
                icon = folium.Icon(color="red", icon="exclamation-sign", prefix="glyphicon")
                tooltip = f"📍 {location_name} — {name}"
            
            folium.Marker(
                location=[lat, lon],
                popup=popup,
                tooltip=tooltip,
                icon=icon
            ).add_to(cluster)

        except (ValueError, TypeError):
            continue

    folium.LayerControl().add_to(pollution_map)
    return pollution_map
