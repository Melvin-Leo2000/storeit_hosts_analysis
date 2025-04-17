import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime

st.set_page_config(page_title="StoreIt Host & Customer Map", layout="wide")
st.title("📦 StoreIt Host & Customer Dashboard")

# Google Sheet Info
host_sheet_id = "1j6_OeNNilcKX81RNCGBoI2zewVU9D45ftPxSO0_-qRo"
host_gid = "422088740"  # "Host Database"
customer_gid = "0"       # assuming this is the "Customers" tab

host_url = f"https://docs.google.com/spreadsheets/d/{host_sheet_id}/export?format=csv&gid={host_gid}"
customer_url = f"https://docs.google.com/spreadsheets/d/{host_sheet_id}/export?format=csv&gid={customer_gid}"

# Load host data
@st.cache_data(ttl=300)
def load_host_data(url):
    df = pd.read_csv(url)
    df['Available Start Date'] = pd.to_datetime(df['Available Start Date'], errors='coerce')
    df['Available End Date'] = pd.to_datetime(df['Available End Date'], errors='coerce')
    today = pd.Timestamp.today().normalize()
    df = df[df['Available End Date'] >= today]
    return df.dropna(subset=['Latitude', 'Longitude'])

# Load customer data
@st.cache_data(ttl=300)
def load_customer_data(url):
    df = pd.read_csv(url)
    df['Check-In Date'] = pd.to_datetime(df['Check-In Date'], errors='coerce')
    df['End Date'] = pd.to_datetime(df['End Date'], errors='coerce')
    df = df[(df['Stage'] >= 2) & (df['End Date'] > pd.Timestamp.today())]
    return df.dropna(subset=['Latitude', 'Longitude'])

hosts = load_host_data(host_url)
customers = load_customer_data(customer_url)


hosts_unique = hosts.drop_duplicates(subset=['Username'])

host_coords = (
    hosts_unique
    .set_index('Username')[['Latitude','Longitude']]
    .to_dict(orient='index')
)

# --- Map Visualization ---
st.subheader("🗺️ Map of Hosts and Customers")

map_center = [1.3521, 103.8198]
m = folium.Map(location=map_center, zoom_start=11)

# Plot hosts (blue)
for _, row in hosts.iterrows():
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        tooltip=row['Username'],
        popup=f"Host Available: {row['Available Start Date'].date()} to {row['Available End Date'].date()}",
        icon=folium.Icon(color='blue', icon='home')
    ).add_to(m)

# Plot customers (green w/ user icon)
for _, row in customers.iterrows():
    cust_loc = (row['Latitude'], row['Longitude'])
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        tooltip=row['Username'],
        popup=f"Customer: {row['Check-In Date'].date()} to {row['End Date'].date()}",
        icon=folium.Icon(color='red', icon='user')
    ).add_to(m)

    matched = row.get('Matched Host')
    if pd.notna(matched) and matched in host_coords:
        host_loc = (host_coords[matched]['Latitude'], host_coords[matched]['Longitude'])
        
        folium.PolyLine(
            locations=[cust_loc, host_loc],
            color='red',         # make it stand out
            weight=5,             # thicker line
            opacity=0.8,
            tooltip=f"Customer: {row['Username']} ↔ Host: {matched}"  
        ).add_to(m)


st_folium(m, width=900, height=550)


st.button("🔄 Refresh Data")