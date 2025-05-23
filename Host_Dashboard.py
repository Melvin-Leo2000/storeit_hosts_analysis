import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime
# from dotenv import load_dotenv
import os

# from components.customer_match import display_customer_host_map
from components.customer_checkin import display_selected_customer_map
from components.customer_checkin import customer_checkin

from components.customer_current_location import display_hosts_map

# load_dotenv()
# from location import OneMapTokenManager, get_address_from_postal


st.set_page_config(page_title="StoreIt Host & Customer Map", layout="wide")


# # Google Sheet Info

host_sheet_id = st.secrets["HOST_SHEET_ID"]
host_gid = st.secrets["HOST_GID"]
customer_gid = st.secrets["CUSTOMER_GID"]

# OneMap API
ONEMAP_EMAIL = st.secrets["ONEMAP_EMAIL"]
ONEMAP_PASSWORD = st.secrets["ONEMAP_PASSWORD"]


# # Google Sheet IDs
# host_sheet_id = os.getenv("HOST_SHEET_ID")
# host_gid = os.getenv("HOST_GID")
# customer_gid = os.getenv("CUSTOMER_GID")

# # OneMap API
# ONEMAP_EMAIL = os.getenv("ONEMAP_EMAIL")
# ONEMAP_PASSWORD = os.getenv("ONEMAP_PASSWORD")

host_url = f"https://docs.google.com/spreadsheets/d/{host_sheet_id}/export?format=csv&gid={host_gid}"
customer_url = f"https://docs.google.com/spreadsheets/d/{host_sheet_id}/export?format=csv&gid={customer_gid}"


@st.cache_data(ttl=300)
def load_host_data(url):
    df = pd.read_csv(url)
    df['Available Start Date'] = pd.to_datetime(df['Available Start Date'], errors='coerce')
    df['Available End Date'] = pd.to_datetime(df['Available End Date'], errors='coerce')
    today = pd.Timestamp.today().normalize()
    df = df[df['Available End Date'] >= today]
    return df.dropna(subset=['Latitude', 'Longitude'])

@st.cache_data(ttl=300)
def load_customer_data(url):
    df = pd.read_csv(url)
    df['Check-In Date'] = pd.to_datetime(df['Check-In Date'], errors='coerce')
    df['End Date'] = pd.to_datetime(df['End Date'], errors='coerce')
    df = df[
        (df['Stage'] >= 2) &
        (df['End Date'] > pd.Timestamp.today()) &
        (df['Has Paid'] == 1)
    ]
    return df.dropna(subset=['Latitude', 'Longitude'])


hosts = load_host_data(host_url)
customers = load_customer_data(customer_url)

### Customer Checkin Dates ###
st.subheader("📋 Customer Checkin Dates")
host_coords = hosts.drop_duplicates('Username').set_index('Username')[['Latitude','Longitude']].to_dict(orient='index')

# Get selected customer
selected_customer = customer_checkin(customers)
display_selected_customer_map(selected_customer, customers, host_coords)

### Customer Manual Matching ###
display_hosts_map(customers, hosts)






####### Ongoing Matched Customers and Hosts #########

# Load customer data
@st.cache_data(ttl=300)
def load_upaid_customer_data(url):
    df = pd.read_csv(url)
    df['Check-In Date'] = pd.to_datetime(df['Check-In Date'], errors='coerce')
    df['End Date'] = pd.to_datetime(df['End Date'], errors='coerce')

    df = df[
        (df['Stage'].isin([0, 1])) &
        (df['End Date'] > pd.Timestamp.today()) &
        (df['Matched Host'].notna()) &
        (df['Matched Host'] != "")
    ]

    return df.dropna(subset=['Latitude', 'Longitude'])





# unpaid_customers = load_upaid_customer_data(customer_url)

# st.subheader("🗺️ Map of Ongoing Matched Customers and Hosts")
# um = folium.Map(location=map_center, zoom_start=11)

# # Plot hosts (blue)
# for _, row in hosts.iterrows():
#     folium.Marker(
#         location=[row['Latitude'], row['Longitude']],
#         tooltip=row['Username'],
#         popup=f"Host Available: {row['Available Start Date'].date()} to {row['Available End Date'].date()}",
#         icon=folium.Icon(color='blue', icon='home')
#     ).add_to(um)

# for _, row in unpaid_customers.iterrows():
#     cust_loc = (row['Latitude'], row['Longitude'])
#     folium.Marker(
#         location=[row['Latitude'], row['Longitude']],
#         tooltip=row['Username'],
#         popup=f"Unpaid Customer: {row['Check-In Date'].date()} to {row['End Date'].date()}",
#         icon=folium.Icon(color='white', icon='user')
#     ).add_to(um)

#     matched = row.get('Matched Host')
#     if pd.notna(matched) and matched in host_coords:
#         host_loc = (host_coords[matched]['Latitude'], host_coords[matched]['Longitude'])
        
#         folium.PolyLine(
#             locations=[cust_loc, host_loc],
#             color='blue',         # make it stand out
#             weight=5,             # thicker line
#             opacity=1,
#             tooltip=f"Customer: {row['Username']} ↔ Host: {matched}"  
#         ).add_to(um)


# st_folium(um, width=900, height=550)





# st.subheader("📋 Customer Return Date")

# # Step 1: Start with the original selection
# raw_df = customers[['Username', 'Storage Cost', 'End Date', 'Matched Host']].copy()

# # Step 2: Sort and reset index
# raw_df = raw_df.sort_values(by='End Date')
# raw_df.index = range(1, len(raw_df) + 1)

# # Step 3: Highlight function using datetime comparison
# today = pd.Timestamp.today().strftime('%Y-%m-%d')
# today = pd.to_datetime(today)

# def highlight_rows(row):
#     checkin = pd.to_datetime(row['End Date'])
#     if pd.isna(checkin):
#         return [''] * len(row)
#     elif checkin == today:
#         return ['background-color: yellow'] * len(row)
#     elif checkin < today:
#         return ['background-color: lightgreen'] * len(row)
#     else:
#         return [''] * len(row)

# # Step 4: Format display version (string format only for table, not for logic)
# display_df = raw_df.copy()
# display_df['Storage Cost'] = display_df['Storage Cost'].round(2)
# display_df['End Date'] = display_df['End Date'].dt.strftime('%Y-%m-%d')

# # Step 5: Apply highlight logic using raw datetimes
# styled_df = display_df.style.apply(highlight_rows, axis=1)

# # Step 6: Display styled table
# st.write(styled_df)


# # --- Dropdown Filter ---
# st.subheader("🏡 Active Hosts with Upcoming Availability")

# token_manager = OneMapTokenManager(ONEMAP_EMAIL, ONEMAP_PASSWORD)
# token = token_manager.get_token()

# def enrich_host_addresses(df):
#     df = df.copy()
#     df['Full Address'] = df['Postal Code'].apply(lambda x: get_address_from_postal(str(x), token)[0]['ADDRESS'])
#     return df

# duration_option = st.selectbox(
#     "Select minimum availability duration:",
#     ("All", "At least 3 months", "At least 6 months", "At least 1 year", "1 year and beyond")
# )

# # Duration in days
# duration_map = {
#     "At least 3 months": 90,
#     "At least 6 months": 180,
#     "At least 1 year": 365,
#     "1 year and beyond": 366
# }


# # Apply filters
# if duration_option == "All":
#     filtered_hosts = hosts[hosts['Available End Date'] > today]
# else:
#     min_days = duration_map[duration_option]
#     filtered_hosts = hosts[
#         (hosts['Available End Date'] > today) &
#         ((hosts['Available End Date'] - today).dt.days >= min_days)
#     ]

# # Select and format relevant columns
# filtered_hosts = filtered_hosts[[
#     'Username', 
#     'Postal Code', 
#     'Available Start Date', 
#     'Available End Date',
#     'Transaction Count', 
#     'Revenue Projected'
# ]].copy()

# filtered_hosts = filtered_hosts.sort_values(by='Available End Date')
# filtered_hosts.index = range(1, len(filtered_hosts) + 1)
# filtered_hosts['Available Start Date'] = pd.to_datetime(filtered_hosts['Available Start Date']).dt.strftime('%Y-%m-%d')
# filtered_hosts['Available End Date'] = pd.to_datetime(filtered_hosts['Available End Date']).dt.strftime('%Y-%m-%d')
# filtered_hosts['Revenue Projected'] = filtered_hosts['Revenue Projected'].round(2)
# filtered_hosts = enrich_host_addresses(filtered_hosts)

# # Display
# st.dataframe(filtered_hosts, use_container_width=True)



# st.button("🔄 Refresh Data")