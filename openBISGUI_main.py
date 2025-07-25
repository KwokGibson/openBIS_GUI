import warnings
import argparse
import streamlit as st
from streamlit import config as st_config
import os
import time
import pybis
from pybis import Openbis
import pandas as pd
from configparser import ConfigParser
from io import StringIO
#from pybis import check_role, get_full_identifier
#https://git.rwth-aachen.de/Kerzel/openbistools/-/blob/main/register_linkdata/pybis_tools.py



#Login
openbis_url = "https://neurone-openbis.apps.l:8443"

def init_session_state(temp_dir: str):
    # Initialize Streamlit Session State

    SESSION_DEFAULTS = {
        "oBis": None,
        "ds_type_set": set(),
        "openbis_username": "",
        "openbis_password": "",
        "openbis_token": "",
        "openbis_upload_allowed": False,
        "s3_upload_allowed": False,
        "experiments": {},
        "experiment_name_list": [],
        "obis_dmscode": "",
        "logged_in": False,
        "setup_done": False,
        "disable_upload": True,
        "include_samples": False,
        "s3_clients": dict(),  # Read Clients
        "s3_client": None,  # Write Client
        "s3_bucket_names": dict(),
        "s3_bucket_name": "",
        "s3_upload_ok": False,
        "s3_download_ok": False,
        "temp_dir": "./tmp",
        "options": None,
    }
    for k, v in SESSION_DEFAULTS.items():
        if k not in st.session_state:
            setattr(st.session_state, k, v)
    st.session_state.temp_dir = temp_dir
    st.session_state.max_size = st_config.get_option("server.maxUploadSize")  # Mb




def openbis_login(openbis_url):
    """
    Performs startup tasks (login to OpenBIS and identification of roles and permissions).
    """

    username = None
    try:
        st.session_state.oBis = Openbis(openbis_url, verify_certificates=False)
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

def find_relevant_locations(username, include_samples=False):
    """Fetches all ELN entries the user can link to."""

    # Add spaces corresponding to research projects (+ user's personal space)

    space_list = [
        username.upper(),
        "DOCUMENTATION",
        "DOCUMENTATION_NOTEBOOK",
        "MATERIALS",
        "METHODS",
        "PUBLICATIONS",
        "STORAGE",
    ]




def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--temp_dir",
        type=str,
        required=False,
        default="./tmp",
        help="Path to where the data will be staged (anbd later deleted)",
    )
    parser.add_argument(
        "--openbis_url", type=str, required=False, help="openBIS endpoint"
    )
    parser.add_argument(
        "--coscine_url", type=str, required=False, help="Default Coscine endpoint"
    )
    args = parser.parse_args()
    init_session_state(temp_dir=args.temp_dir)

    # Clean up temporary directory

    if os.path.isdir(st.session_state.temp_dir):
        for file in os.scandir(st.session_state.temp_dir):
            if file.is_file():
                os.unlink(file.path)
    else:
        os.makedirs(st.session_state.temp_dir)
    # Display Welcome section

    st.title("NEURONE openBIS Companion App")
    #st.image("media/NEURONE-dark-logo.png")
    st.markdown(
        """
        In NEURONE, we organise all the metadata about our samples in openBIS.
        
        This web-app allows a cleaner interaction for common tasks than the openBIS web interface.
        
        Login to openBIS below. Refreshing occassionally breaks the connection, please come back here if so.
        
        """
    )

    st.subheader("Log into openBIS")

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
                placeholder="username",

            )
        with col3:
            password = st.text_input(
                "Enter your openBIS password",
                type="password",
                placeholder="password",

            )

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
                find_relevant_locations(username, include_samples=False)
            if st.session_state.logged_in and not st.session_state.s3_upload_allowed:
                st.session_state.setup_done = True
            placeholder1.empty()
    placeholder2 = st.empty()

    # Prompt user to upload credentials needed for upload to Coscine

    warning_msg = None

    if st.session_state.s3_upload_allowed and not st.session_state.setup_done:
        with placeholder2.form("Form_S3_credentials"):
            st.write("Enter S3 storage credentials (to upload to Coscine)")
            st.write(
                "If you are not uploading files, you can click on *Configure S3* without uploading a config file."
            )
            s3_credentials = st.file_uploader(
                "Choose a file",
                accept_multiple_files=False,
                type=["cfg"],
                help=open("s3_credentials_demo.cfg", "r")
                .read()
                .replace("#", "\#")
                .replace("\n", "  \n"),
            )
            config_btn = st.form_submit_button("Configure S3", type="primary")
            if config_btn:
                placeholder1.empty()
                placeholder2.empty()
                if not st.session_state.s3_client:
                    if s3_credentials:
                        client, bucket, dmscode = get_s3client(
                            s3_credentials, from_path=False
                        )
                    else:
                        dmscode = next(iter(st.session_state.s3_clients))
                        client = st.session_state.s3_clients[dmscode]
                        bucket = st.session_state.s3_bucket_names[dmscode]
                    access_key = client._request_signer._credentials.access_key
                    if not access_key.startswith("write_"):
                        warning_msg = f"You might not be able to upload to Coscine using access key {access_key}"
                    st.session_state.s3_client = client
                    st.session_state.s3_bucket_name = bucket
                    st.session_state.obis_dmscode = dmscode
                response = check_s3()
                st.session_state.setup_done = True
    if st.session_state.setup_done:
        placeholder1.empty()
        placeholder2.empty()
        if st.session_state.s3_upload_ok:
            bucket = st.session_state.s3_bucket_name
            dms_code = st.session_state.obis_dmscode
            st.success(
                f"S3 storage **{dms_code}** found, bucket name: **{bucket}**",
                icon="✅",
            )
            if warning_msg is not None:
                st.warning(warning_msg)
        st.write("Logged into openBIS: ", st.session_state.logged_in)
        #st.write("openBIS Upload OK: ", st.session_state.openbis_upload_allowed)
        #st.write("Coscine Upload OK: ", st.session_state.s3_upload_ok)
        #st.write("Coscine Download OK: ", st.session_state.s3_download_ok)
        st.write("You can now either Register New Samples, Move a Sample and Update its Location, or Produce a Report")


if __name__ == "__main__":
    main()



    
