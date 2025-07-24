import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime
import os
import qrcode
from PIL import Image
import base64

 
st.title("Quick-Add A Sample To openBIS")

st.write(
    """
1. Enter your name and a short sample description
2. Add to openBIS, this will be inserted into the "NEURONE_PLACEHOLDER_SAMPLES" collection
3. (Optionally), show the associated QR code to the new sample ID
4. Print the QR code and attach it to the sample.
5. ⚠️ Then go back into openBIS on your PC and update the sample metadata properly! ⚠️

    """

)
st.markdown('##')
#st.subheader('Quick-Add, Or Select a sample type')
with st.form("EnterSamples", clear_on_submit=True):

    quickAddSampleName = st.text_input('quickAddSampleName', value="", max_chars=128, key='quickAddSampleName', type="default", help=None, autocomplete=None, on_change=None, args=None, kwargs=None, placeholder='Name Your Sample', disabled=False, label_visibility="hidden", icon=None)
    quickAddName = st.text_input('quickAddName', value="", max_chars=128, key='quickAddName', type="default", help=None, autocomplete=None, on_change=None, args=None, kwargs=None, placeholder='Enter Your Name', disabled=False, label_visibility="hidden", icon=None)
    quickAddNotes = st.text_input('quickAddNotes', value="", max_chars=512, key='quickAddNotes', type="default", help=None, autocomplete=None, on_change=None, args=None, kwargs=None, placeholder='Input A Brief Sample Description', disabled=False, label_visibility="hidden", icon=None)

    #Ideally would be able to add a picture of the thing, but I can't work out how to put images into the notes section via pybis.
    #enable = st.checkbox("Enable camera")
    #quickAddPicture = st.camera_input("Take a picture", disabled=not enable)
    #if quickAddPicture:
    #    st.image(quickAddPicture)


    #Streamlit needs two white spaces before the newline character in order to recognise it
    confirm_btn = st.form_submit_button(
        "🆙 Quick-Add Sample to OpenBIS" + "  \n" + "(NERUONE_PLACEHOLDER_SAMPLES)",
        type="primary", #label='quickAddButton', label_visibility=hidden,
    )
    
    #progress_text = "Creating samples. Please wait."
    progress_bar = st.progress(0)
    
    #This is the actual bit that makes openBIS samples
    new_permids = []
    
    if confirm_btn:
        name = quickAddSampleName
        owner = quickAddName
        notes = quickAddNotes
        
        new_sample = st.session_state.oBis.new_object(
            type="BIT_OF_METAL",
            collection="/MATERIALS/NEURONE/NEURONE_PLACEHOLDERS",
            props = {"$name": name, "owner": owner, "notes": notes}
                

        )
        new_sample.save()
        permid = new_sample.permId
        print(new_sample.permId)
        st.session_state.permid = permid
        ##
        
        

        progress_bar.empty()
        st.success(
            f"Samples added succesfully. \n",
            icon="✅",
        )
        print(permid)
        

# Function to generate QR code image
def generate_qr_image(data):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_Q,
        box_size=10,
        border=1,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    return img

# Function to convert image to base64 and return download link and img tag
def get_base64_image(img: Image.Image):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    img_bytes = buf.read()
    b64_img = base64.b64encode(img_bytes).decode()
    return b64_img

# --- Main App ---

if "permid" in st.session_state:
    qr_data = st.session_state.permid
else:
    st.warning("No openBIS permID created")

# Check if permID exists
permid_exists = "permid" in st.session_state
qr_data = st.session_state.permid if permid_exists else None

# Generate QR image + base64 only if permid exists
if permid_exists:
    qr_img = generate_qr_image(qr_data)
    b64_img = get_base64_image(qr_img)

# SHOW QR BUTTON
with st.container(border=True):
    showQR_btn = st.button(
        "Show QR Code",
        type="primary",
        icon="💻",
        disabled=not permid_exists  # ✅ Disable if no permid
    )

    if showQR_btn and permid_exists:
        st.image(qr_img, caption=qr_data)
        st.markdown(
            f'<a href="data:image/png;base64,{b64_img}" download="qr_code.png">📥 Download QR Code</a>',
            unsafe_allow_html=True,
        )

# PRINT QR BUTTON
with st.container(border=True):
    printQR_btn = st.button(
        "Print QR Code",
        type="primary",
        icon="🖨️",
        disabled=not permid_exists  # ✅ Disable if no permid
    )

    if printQR_btn and permid_exists:
        st.markdown(
            f"""
            <script>
                var win = window.open();
                win.document.write('<title>QR Code</title>');
                win.document.write('<img src="data:image/png;base64,{b64_img}" style="width:300px;margin:50px auto;display:block;" />');
                win.document.close();
            </script>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <p>⚠️ If the print window didn’t open automatically, 
            <a href="data:image/png;base64,{b64_img}" target="_blank">click here to open QR Code in new tab</a>.</p>
            """,
            unsafe_allow_html=True
        )

        st.info("Use Cmd/Ctrl + P to print the QR code.")

        del st.session_state.permid




###########################################
