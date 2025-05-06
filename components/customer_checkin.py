import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium

def customer_checkin(customers):

    raw_df = customers[['Username', 'Storage Cost', 'Check-In Date', 'End Date', 'Matched Host', 'Stage']].copy()
    raw_df = raw_df.sort_values(by='Check-In Date')
    raw_df.insert(0, "No.", range(1, len(raw_df) + 1))

    # Map stage to status
    stage_map = {0: "Awaiting Host Acceptance", 1: "Awaiting Customer Transaction", 2: "Transaction Succeeded", 3: "In Storage Process", 4: "Completed Deal"}
    raw_df["Status"] = raw_df["Stage"].map(stage_map).fillna("Unknown")
    raw_df.drop(columns=["Stage"], inplace=True)

    # Host filter
    host_list = sorted(raw_df['Matched Host'].dropna().unique())
    selected_host = st.selectbox("🔎 Filter by Matched Host", options=["All"] + host_list)

    if selected_host != "All":
        filtered_df = raw_df[raw_df['Matched Host'] == selected_host].copy()
    else:
        filtered_df = raw_df.copy()

    # Format dates
    filtered_df['Storage Cost'] = filtered_df['Storage Cost'].round(2)
    filtered_df['Check-In Date'] = pd.to_datetime(filtered_df['Check-In Date']).dt.strftime('%Y-%m-%d')
    filtered_df['End Date'] = pd.to_datetime(filtered_df['End Date']).dt.strftime('%Y-%m-%d')

    # Add selection column
    filtered_df.insert(0, "Select", False)

    # Set up session key
    session_key = f"select_all_for_{selected_host}"
    if session_key not in st.session_state:
        st.session_state[session_key] = False

    # Button to select all
    if selected_host != "All":
        if st.button(f"✅ Select All Customers for Host: {selected_host}"):
            st.session_state[session_key] = True

    # If the flag is True, mark all as selected
    if st.session_state[session_key]:
        filtered_df["Select"] = True

    # Display interactive editor
    selected_df = st.data_editor(
        filtered_df,
        key="select_customer_row",
        column_config={"Select": st.column_config.CheckboxColumn(required=True)},
        use_container_width=True,
        hide_index=True,
        num_rows="fixed"
    )

    # Return selected customers
    selected_usernames = selected_df[selected_df["Select"] == True]["Username"].tolist()
    return selected_usernames






def display_selected_customer_map(selected_usernames, customers, host_coords):
    if not selected_usernames:
        return

    m = folium.Map(location=[1.3521, 103.8198], zoom_start=12)

    for username in selected_usernames:
        customer = customers[customers['Username'] == username].iloc[0]
        customer_loc = [customer['Latitude'], customer['Longitude']]

        # Add customer marker
        folium.Marker(
            location=customer_loc,
            tooltip=username,
            popup=f"{customer['Check-In Date'].date()} to {customer['End Date'].date()}",
            icon=folium.Icon(color='red', icon='user')
        ).add_to(m)

        # Add host marker and polyline if matched
        matched = customer['Matched Host']
        if pd.notna(matched) and matched in host_coords:
            host_loc = [host_coords[matched]['Latitude'], host_coords[matched]['Longitude']]

            folium.Marker(
                location=host_loc,
                tooltip=matched,
                popup=f"Host: {matched}",
                icon=folium.Icon(color='blue', icon='home')
            ).add_to(m)

            folium.PolyLine(
                locations=[customer_loc, host_loc],
                color='green',
                weight=5,
                opacity=0.8,
                tooltip=f"{username} ↔ {matched}"
            ).add_to(m)

    st_folium(m, width=900, height=550)

