import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime
import os
import qrcode
from PIL import Image
import base64

 
st.title("To Add New Things To openBIS")

st.write(
    """
1. Select the type of new sample you want to add to openBIS.

2. Download the relevant Excel template. See the [Upload Documentation](https://neurone-openbis.apps.l:8443/openbis/webapp/eln-lims/?menuUniqueId=%7B%22type%22:%22EXPERIMENT%22,%22id%22:%2220250721110241000-1680%22%7D&viewName=showViewSamplePageFromPermId&viewData=%2220250721133838589-1685%22) for additional tips.
    
3. Upload your filled-in Excel template

    """

)
st.markdown('##')
st.subheader('1. Select a sample type')
option_map = {
#0: "Bit of Metal (Placeholder)",
0: "1️⃣ EAF Ingot",
1: "2️⃣ VIM Ingot",
2: "3️⃣ Lab Ingot",
3: "4️⃣ Thermomechanical Treatment",
4: "5️⃣ Tensile Sample",
5: "6️⃣ Creep Sample",
6: "7️⃣ SEM / Nanoindentation Sample (Matchstick)",
}

# Map each option to its specific template file
template_file_map = {
#    0: "placeholderTemplate.xlsx",
    0: "EAF_Ingot_Template.xlsx",
    1: "VIM_Ingot_Template.xlsx",
    2: "Lab_Ingot_Template.xlsx",
    3: "Thermomechanical_Treatment_Template.xlsx",
    4: "Tensile_Sample_Template.xlsx",
    5: "Creep_Sample_Template.xlsx",
    6: "SEM_Nanoindentation_Sample_Template.xlsx",
}

# Map to the type in openBIS
openbis_type_map = {
    0: "EAF_INGOT",
    1: "VIM_INGOT",
    2: "LAB_INGOT",
    3: "TMT_TARGET",
    4: "Tensile",
    5: "Creep",
    6: "Matchstick",
}

# Map to the collection in openBIS
openbis_collection_map = {
    0: "/MATERIALS/NEURONE/NEURONE_EAF_INGOTS",
    1: "/MATERIALS/NEURONE/NEURONE_VIM_INGOTS",
    2: "/MATERIALS/NEURONE/NEURONE_LAB_INGOTS",
    3: "/MATERIALS/NEURONE/NEURONE_TMT",
    4: "/MATERIALS/NEURONE/NEURONE_TENSILE",
    5: "/MATERIALS/NEURONE/NEURONE_CREEP",
    6: "/MATERIALS/NEURONE/NEURONE_MATCHSTICKS",
}

# Map to the needed properties in openBIS
openbis_metadata_map = {
    0: "{\"Name\": Name}",
    1: "VIM Ingot",
    2: "Lab Ingot",
    3: "TMT Target",
    4: "Tensile",
    5: "Creep",
    6: "Matchstick",
}




selection = st.pills(
    "",
    options=option_map.keys(),
    format_func=lambda option: option_map[option],
    selection_mode="single",
    default=None
)

    
st.subheader('2. Download the metadata template')
try:
    selected_label = option_map[selection]
    file_name = template_file_map.get(selection)

    # Split filename into name and extension
    base, ext = os.path.splitext(file_name)

    # Remove "_template" from the end of the base name
    if base.endswith("_Template"):
        stripped_file_name = base[:-len("_Template")] + ext
    else:
        stripped_file_name = file_name  # unchanged if no match
    # This is so you can have the template and the filled-in sheet open at the same time

    file_path = f"templates/{file_name}"

except:
    st.warning('No sample type selected')


try:
    with open(file_path, "rb") as f:
        st.download_button(
            f'Download the "{selected_label}" Template',
            f,
            file_name=stripped_file_name
        )
except FileNotFoundError:
    st.warning(f'Template file for "{selected_label}" not found: {file_path}')
    
st.write('Here is a preview of the template:')
try:
    dataset = pd.read_excel(file_path)
    # Define a function to highlight specific columns
    def highlight_columns(x):
        df = pd.DataFrame('', index=x.index, columns=x.columns)
        highlight_cols = x.columns[:]
        for col in highlight_cols:
            df[col] = 'background-color: lightyellow'
        return df

    # Display the styled DataFrame
    st.dataframe(dataset.style.apply(highlight_columns, axis=None))
except FileNotFoundError:
    st.warning(f'Template file for "{selected_label}" not found: {file_path}')
    
    
    
st.subheader('3. Upload your filled-in Excel template')
spreadsheet = st.file_uploader("Choose a file",     accept_multiple_files=False,)

if spreadsheet:

    df_samples = pd.read_excel(spreadsheet, skiprows=3)
    st.session_state.table_loaded = True
    st.session_state.samples_df = df_samples
    st.dataframe(df_samples)



st.subheader('4. Upload samples to openBIS')
with st.form("EnterSamplesExcel"):

    confirm_btn = st.form_submit_button(
        "Create Samples in OpenBIS",
        type="primary",
    )
    
    progress_text = "Creating samples. Please wait 30s per sample."
    progress_bar = st.progress(0, text=progress_text)
    
    #This is the actual bit that makes openBIS samples
    new_permids = []
    
    if confirm_btn:
        for i, row in df_samples.iterrows():
            progress_bar.progress((i + 1) / len(df_samples), text=progress_text)
            row = row.dropna()
            
            # Convert all values to strings, with special handling for 'Manufacture Date'
            props = {}
            for k, v in row.to_dict().items():
                if pd.isna(v):
                    continue
                if k.lower() == "manufacture date":
                    try:
                        # Parse and format date
                        parsed_date = pd.to_datetime(v, errors="raise")
                        props[k] = parsed_date.strftime("%Y-%m-%d")  # Format as ISO yyyy-MM-dd
                    except Exception as e:
                        print(f"⚠️ Could not parse date '{v}' in row {i}: {e}")
                        continue  # or raise, depending on how strict you want to be
                else:
                    props[k] = str(v)
            
            
            
            
                #print(props)
                parents = props.pop("Parents", [])
                children = props.pop("Children", [])
                name = props.pop("$name", [])
                props.update({"$name":name})
                print('here')
                print(name)

                #owner = props.pop("Which NEURONE member made / did this?")
                #notes = props.pop("Notes")

                if "" in parents:
                    parents.remove("")
                if "" in children:
                    children.remove("")
                #if "" in name:
                #    name.remove("")
                new_sample = st.session_state.oBis.new_object(
                    type=openbis_type_map[selection],
                    #name = name,
                    parents=parents,
                    children=children,
                    collection=openbis_collection_map[selection],
                    props = props,
                    
                    #new_sample.p['$name'] = name,
            )
            print(props)
            new_sample.save()
            permid = new_sample.permId

            new_permids.append(permid)
        ##
        
        

        progress_bar.empty()
        st.success(
            f"Samples added succesfully. \n",
            icon="✅",
        )

