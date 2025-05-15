import streamlit as st

st.title('My first app')

with st.sidebar:
    st.header('Fill the sidebar')

    st.write('... with some text....')


with st.form('my_form'):
    user_input = st.text_input('write something')
    submitted = st.form_submit_button('Submit', type='primary')
    if submitted:
        st.write('Your input was: ', user_input)