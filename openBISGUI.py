import streamlit as st

#Login
OPENBIS_URL = "https://neurone-openbis.apps.l:8443"

def openbis_login(openbis_url):
    """
    Performs startup tasks (login to OpenBIS and identification of roles and permissions).
    """

    username = None
    try:
        st.session_state.oBis = Openbis(openbis_url, verify_certificates=True)
        if len(st.session_state.openbis_token):
            st.session_state.oBis.set_token(
                st.session_state.openbis_token,
                save_token=True,
            )
        else:
            st.session_state.oBis.login(
                username=st.session_state.openbis_username.strip(),
                password=st.session_state.openbis_password.strip(),
            )
        username = st.session_state.oBis._get_username()

        # Check if user is allowed to upload to openBIS directly
        # .i.e. all users who have an OBSERVER role in the space IMM
        st.session_state.openbis_upload_allowed = check_role(
            oBis=st.session_state.oBis,
            username=username,
        )

        st.session_state.logged_in = True
        st.session_state.openbis_username = username
        st.session_state.openbis_password = ""
        st.session_state.openbis_token = st.session_state.oBis.token

    except Exception as e:
        st.error(f"Cannot connect to openBIS {openbis_url}: {e}", icon="🔥")
        st.snow()
        st.stop()

def check_openbis_login_success():
    """Validates whether login to openBIS was successful or not."""
    try:
        username = st.session_state.oBis._get_username()
        return username
    except Exception as e:
        st.error(f"Login to openBIS failed: {e}")
        return None










# Define the pages
main_page = st.Page("openBISGUI_main.py", title="Main Page", icon="🏠")

sample_moving = st.Page("openBISGUI_moving.py", title="Move Samples", icon="🚚")

data_reporting = st.Page("openBISGUI_reporting.py", title="Data Reporting", icon="📘")

new_samples = st.Page("openBISGUI_newSamples.py", title="Register New Samples", icon="⚙️")

# Set up navigation
pg = st.navigation([main_page, new_samples, sample_moving, data_reporting ])


st.sidebar.image("media/NEURONE-dark-logo.png")
#st.sidebar.write("Logged into openBIS: ", st.session_state.logged_in)






# Run the selected page
pg.run()




