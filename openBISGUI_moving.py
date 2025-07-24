import streamlit as st
import cv2
import numpy as np
from PIL import Image
import json

st.title("Update Sample Location")

st.write(
    """
1. Scan QR code
2. Select new sample location
3. Click 'update'
    """

)


st.subheader("📷 Scan openBIS QR Code")

# Try to get openBIS object
obis = st.session_state.get("oBis", None)

# Take a photo using the webcam
img_data = st.camera_input("Scan a QR code (should contain openBIS permID)")

if img_data is not None:
    # Load image and ensure RGB
    pil_image = Image.open(img_data).convert("RGB")

    # Proper OpenCV-safe conversion
    np_image = np.asarray(pil_image, dtype=np.uint8)
    np_image = np.ascontiguousarray(np_image)

    # Detect and decode
    detector = cv2.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(np_image)

    if data:
        st.success(f"✅ QR Code Detected: `{data}`")
        st.session_state.data = data
        # Fetch from openBIS
        try:
            obis = st.session_state.oBis
            sample = obis.get_sample(data, props="*")

            if sample:
                st.markdown("### 🧬 Sample Metadata")
                st.write("🆔 PermID:", sample.permId)
                st.write("📁 Collection:", sample.collection)
                st.write("🔤 Type:", sample.type)
                st.write("👩‍🔬 Owner:", sample.props("owner"))
                st.write("📍 Current Location:", sample.props("sample_location"))
                st.write("📎 All Metadata:", sample.props.all())
            else:
                st.error("❌ Sample not found.")

        except Exception as e:
            st.error(f"❌ Error accessing openBIS: {e}")
    else:
        st.warning("⚠️ QR code not detected.")
        
        
with st.form('Move_Sample_Form'):
    st.header('Update a sample\'s storage location')

    # Fetch vocabulary terms
    #THIS DOESN'T WORK SO I'LL BE A HEATHEN AND HARD-CODE THEM
    #location_vocab = obis.get_terms('LOCATION')
    #st.write(location_vocab)
    #validStorageLocations = location_vocab.code  # List of term objects
    #st.write(validStorageLocations)
    #location_codes = [term.code for term in validStorageLocations]
    
    # Map to the needed properties in openBIS
    openbis_location_map = {
    'FTF': "FTF Yorkshire",
    'MAN': "Manchester University",
    'MRF': "MRF, Culham",
    'OXF': "Oxford University",
    'SWANSEA': "Swansea University",
    }

    # Check if QRdata exists
    permid_exists = "data" in st.session_state
    qr_data = st.session_state.data if permid_exists else None
    if permid_exists:
        updateSampleID = st.text_input('quickAddSampleName', value=qr_data, max_chars=128, key='quickAddSampleName', type="default", help=None, autocomplete=None, on_change=None, args=None, kwargs=None, placeholder=qr_data, disabled=False, label_visibility="visible", icon=None)
    else:
        updateSampleID = st.text_input('quickAddSampleName', value="", max_chars=128, key='quickAddSampleName', type="default", help=None, autocomplete=None, on_change=None, args=None, kwargs=None, placeholder='Enter Sample ID', disabled=False, label_visibility="visible", icon=None)

    storage_option = st.selectbox(
    'Choose a new storage location',
    ["FTF Yorkshire","Manchester University","MRF, Culham","Oxford University","Swansea University"],
    index=None,
    placeholder='Select new storage location'
    )
    
    location_submitted = st.form_submit_button('Update Location', type='primary')
    
    if location_submitted and updateSampleID and storage_option:
        # Find the code (shorthand) from the selected full name
        selected_code = None
        for code, full_name in openbis_location_map.items():
            if full_name == storage_option:
                selected_code = code
                break

        if selected_code:
            try:
                sample_to_update = obis.get_sample(qr_data, props="*")
                if sample_to_update:
                    # Update the property
                    sample_to_update.props["sample_location"] = selected_code
                    sample_to_update.save()
                    st.success(f"📦 Sample `{updateSampleID}` location updated to **{storage_option}**.")
                    
                    # Clear the stored data
                    st.session_state.pop("data", None)
                    st.session_state.pop("quickAddSampleName", None)

                else:
                    st.error("❌ Sample not found during update.")
            except Exception as e:
                st.error(f"❌ Failed to update sample location: {e}")
        else:
            st.error("❌ Invalid location selected.")

