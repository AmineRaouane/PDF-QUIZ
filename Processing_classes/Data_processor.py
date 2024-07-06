import os
import uuid
import tempfile
from langchain_community.document_loaders import PyPDFLoader
import streamlit as st


def Document_Processor(uploaded_files):
    Pages = []
    my_bar = st.progress(0, text="Processing files...")
    for index,file in enumerate(uploaded_files):
        id = uuid.uuid4().hex
        name, extension = os.path.splitext(file.name)
        temp_file_name = f"{name}_{id}{extension}"
        temp_file_path = os.path.join(tempfile.gettempdir(), temp_file_name)
        with open(temp_file_path,'wb') as f:
            f.write(file.getvalue())
        loader = PyPDFLoader(file_path=temp_file_path)
        pages = loader.load_and_split()
        Pages.extend(pages)
        os.remove(temp_file_path)
        my_bar.progress((index+1)/len(uploaded_files))
    return Pages




