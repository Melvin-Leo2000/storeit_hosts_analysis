import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

def display_hosts_map(customers_df, hosts_df):
    # Host markers
    host_map = folium.Map(location=[1.3521, 103.8198], zoom_start=12)  # Singapore center default

    for _, row in hosts_df.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"Host: {row['Username']}",
            icon=folium.Icon(color='blue', icon='home')
        ).add_to(host_map)

    # Customer selection
    customer_options = customers_df['Username'].unique()
    selected_customer = st.selectbox("🎯 Select a customer to plot on map", customer_options)

    # Plot selected customer
    if selected_customer:
        customer_row = customers_df[customers_df['Username'] == selected_customer].iloc[0]
        customer_location = [customer_row['Latitude'], customer_row['Longitude']]

        folium.Marker(
            location=customer_location,
            popup=f"Customer: {selected_customer}",
            icon=folium.Icon(color='red', icon='user')
        ).add_to(host_map)

        folium.Circle(
            location=customer_location,
            radius=5000,  # meters
            color='red',
            fill=True,
            fill_opacity=0.1,
            popup="~5km radius"
        ).add_to(host_map)


        host_map.location = customer_location
        host_map.zoom_start = 14

    st_folium(host_map, use_container_width=True)
