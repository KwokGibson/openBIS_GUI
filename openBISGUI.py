import streamlit as st


# Define the pages
main_page = st.Page("openBISGUI_main.py", title="Main Page", icon="🏠")

sample_moving = st.Page("openBISGUI_moving.py", title="Move Samples", icon="🚚")

data_reporting = st.Page("openBISGUI_reporting.py", title="Data Reporting", icon="📘")

new_samples = st.Page("openBISGUI_newSamples.py", title="Register New Samples", icon="⚙️")

quick_add = st.Page("openBISGUI_quickAdd.py", title="Quick-Add A Sample", icon="💪")

# Set up navigation
pg = st.navigation([main_page, quick_add, new_samples, sample_moving, data_reporting ])


st.sidebar.image("media/NEURONE-dark-logo.png")
#st.sidebar.write("Logged into openBIS: ", st.session_state.logged_in)






# Run the selected page
pg.run()




