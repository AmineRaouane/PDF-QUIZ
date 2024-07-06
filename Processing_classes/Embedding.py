from langchain_google_vertexai import VertexAIEmbeddings
import os
import streamlit as st
from langchain_huggingface.embeddings import HuggingFaceEmbeddings

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "GOOGLE_APPLICATION_CREDENTIALS.json"

class EmbeddingClient :
    def __init__(self):
        self.client = HuggingFaceEmbeddings()

    def embed_query(self,query):
        return self.client.embed_query(query)

    def embed_document(self, documents):
        embeddings = []
        my_bar = st.progress(0, text="Embedding files...")
        for index,doc in enumerate(documents):
            embedding = self.client.embed_documents([doc])[0] # type: ignore
            embeddings.append(embedding)
            my_bar.progress((index+1)/len(documents))
        return embeddings

