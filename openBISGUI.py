import streamlit as st

# Define the pages
main_page = st.Page("openBISGUI_main.py", title="Main Page", icon="🏠")

sample_moving = st.Page("openBISGUI_moving.py", title="Move Samples", icon="🚚")

data_reporting = st.Page("openBISGUI_reporting.py", title="Data Reporting", icon="📘")

new_samples = st.Page("openBISGUI_newSamples.py", title="Register New Samples", icon="⚙️")

# Set up navigation
pg = st.navigation([main_page, new_samples, sample_moving, data_reporting ])

# Run the selected page
pg.run()




