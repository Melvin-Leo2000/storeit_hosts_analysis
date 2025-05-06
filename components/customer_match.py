import pandas as pd
import folium
from streamlit_folium import st_folium
import streamlit as st


def display_customer_host_map(hosts, customers):

    # Load data
    hosts_unique = hosts.drop_duplicates(subset=['Username'])

    # Create a lookup of host coordinates
    host_coords = (
        hosts_unique
        .set_index('Username')[['Latitude', 'Longitude']]
        .to_dict(orient='index')
    )

    # Select customer
    customer_usernames = customers['Username'].unique()
    selected_customer = st.selectbox("Select a customer to view match", customer_usernames)

    selected_row = customers[customers['Username'] == selected_customer].iloc[0]

    # Display map
    st.subheader(f"🗺️ Map View for {selected_customer}")

    map_center = [selected_row['Latitude'], selected_row['Longitude']]
    m = folium.Map(location=map_center, zoom_start=13)

    # Customer marker
    folium.Marker(
        location=[selected_row['Latitude'], selected_row['Longitude']],
        tooltip=selected_row['Username'],
        popup=f"Customer: {selected_row['Check-In Date'].date()} to {selected_row['End Date'].date()}",
        icon=folium.Icon(color='red', icon='user')
    ).add_to(m)

    # Host marker and connection
    matched = selected_row.get('Matched Host')
    if pd.notna(matched) and matched in host_coords:
        host_loc = (host_coords[matched]['Latitude'], host_coords[matched]['Longitude'])
        folium.Marker(
            location=host_loc,
            tooltip=matched,
            popup=f"Host Matched: {matched}",
            icon=folium.Icon(color='blue', icon='home')
        ).add_to(m)

        folium.PolyLine(
            locations=[[selected_row['Latitude'], selected_row['Longitude']], host_loc],
            color='green',
            weight=5,
            opacity=0.8,
            tooltip=f"{selected_customer} ↔ {matched}"
        ).add_to(m)

    st_folium(m, width=900, height=550)
