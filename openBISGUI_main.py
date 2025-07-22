import streamlit as st


st.title('openBIS GUI for Neurone')
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


with st.sidebar:
    st.header('Neurone openBIS Companion App')

    
