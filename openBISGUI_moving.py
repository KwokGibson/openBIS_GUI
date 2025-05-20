import streamlit as st

st.markdown("# Move Samples")
st.sidebar.markdown("# Move Samples")


with st.form('Move_Sample_Form'):
    st.header('Update a sample\'s location in the 🅝eurone database')
    location_submitted = st.form_submit_button('Update Location', type='primary')

    new_sample_name = st.text_input('Sample Name', 'Name of your sample')
    storage_option = st.selectbox('Choose a storage location', list(['MRF','FTF','Oxford','Manchester']), 
                               index=None,
                               placeholder='Select storage location'
    )
    
    

