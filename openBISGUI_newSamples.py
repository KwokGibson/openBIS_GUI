import streamlit as st
import pandas as pd
from io import StringIO


st.image("flower.png", caption="Caption")


with open("flower.png", "rb") as file:
    st.download_button(
        label="Download this image",
        data=file,
        file_name="flower.png",
        mime="image/png",
    )
    
    
    option_map = {
    0: "EAF Ingot",
    1: "VIM Ingot",
    2: "Lab Ingot",
    3: "Thermomechanical Treatment",
}
selection = st.pills(
    "Tool",
    options=option_map.keys(),
    format_func=lambda option: option_map[option],
    selection_mode="single",
)
st.write(
    "You want to add a: "
    f"{None if selection is None else option_map[selection]}"
)
    
    

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    st.write(bytes_data)

    # To convert to a string based IO:
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    st.write(stringio)

    # To read file as string:
    string_data = stringio.read()
    st.write(string_data)

    # Can be used wherever a "file-like" object is accepted:
    dataframe = pd.read_csv(uploaded_file)
    st.write(dataframe)