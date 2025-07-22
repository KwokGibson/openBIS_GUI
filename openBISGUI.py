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

    st.subheader("Log into openBIS and configure access to Coscine")

    placeholder1 = st.empty()

    # Prompt user to login to opemBIS

    with placeholder1.form("form-openbis-login"):
        st.write(
            "You can use the session token from the openBIS ELN-LIMS GUI to login to the companion app or your username and password."
        )
        col1, col2, col3 = st.columns([0.5, 0.25, 0.25])
        with col1:
            token = st.text_input(
                "Enter your openBIS session token",
                placeholder="Go to /Utilities /User Profile",
            )
        with col2:
            username = st.text_input(
                "Enter your openBIS username",
            )
        with col3:
            password = st.text_input(
                "Enter your openBIS password",
                type="password",
            )
        include_samples = st.toggle(
            "Are you uploading data to samples?",
            help="Only relevant for users uploading simulation data. Experimental data should be uploaded to experiments.",
        )
        if not st.session_state.setup_done:
            st.session_state.include_samples = include_samples
        if include_samples:
            spinner_message = "Trying to locate your samples and experiments"
        else:
            spinner_message = "Trying to locate your experiments"
        login_btn = st.form_submit_button(
            "openBIS Login",
            type="primary",
        )
        if login_btn and (len(token) > 0 or len(username) * len(password)):
            st.session_state.openbis_token = token
            st.session_state.openbis_username = username
            st.session_state.openbis_password = password
            if not st.session_state.logged_in:
                openbis_login(openbis_url)
            username = check_openbis_login_success()
            if username is not None:
                user = st.session_state.oBis.get_user(username)
                first_name = user.firstName
                last_name = user.lastName
                full_name = f"{first_name} {last_name}"
                if full_name is None:
                    full_name = username
                st.success(
                    f"Hello {full_name}, login to openBIS was successful",
                    icon="✅",
                )
            with st.spinner(spinner_message):
                find_relevant_locations(username, include_samples)
            with st.spinner("Configuring download from Coscine"):
                configure_download_from_coscine()
            if st.session_state.logged_in and not st.session_state.s3_upload_allowed:
                st.session_state.setup_done = True
            placeholder1.empty()
    placeholder2 = st.empty()








# Define the pages
main_page = st.Page("openBISGUI_main.py", title="Main Page", icon="🏠")

sample_moving = st.Page("openBISGUI_moving.py", title="Move Samples", icon="🚚")

data_reporting = st.Page("openBISGUI_reporting.py", title="Data Reporting", icon="📘")

new_samples = st.Page("openBISGUI_newSamples.py", title="Register New Samples", icon="⚙️")

# Set up navigation
pg = st.navigation([main_page, new_samples, sample_moving, data_reporting ])


st.sidebar.image("media/NEURONE-dark-logo.png")
st.sidebar.write("Logged into openBIS: ", st.session_state.logged_in)






# Run the selected page
pg.run()




