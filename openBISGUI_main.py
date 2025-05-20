import streamlit as st


st.title('openBIS GUI for Neurone')

with st.sidebar:
    st.header('Neurone openBIS Companion App')

openBISlogin = st.form('openBISlogin')

openBISuser = openBISlogin.text_input('openBIS Username')
openBISpass = openBISlogin.text_input('openBIS password', type="password")
submit = openBISlogin.form_submit_button(f'Submit Login Information')

if submit:
    openBISlogin.subheader(openBISuser)
else:
    openBISlogin.subheader('&nbsp;')
    
