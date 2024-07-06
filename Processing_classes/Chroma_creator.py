import streamlit as st
import os

from langchain_core.documents import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Chroma #type:ignore


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "GOOGLE_APPLICATION_CREDENTIALS.json"

class Chroma_collection_creator:
    def __init__(self,client):
        self.embedding_client = client  # Initialize your embedding client
        self.db = None

    def create_chroma_collection(self, Pages):
        if not Pages:
            st.warning("No documents to process.")
            return

        texts = [page.page_content for page in Pages]

        text_splitter = CharacterTextSplitter()
        split_texts = []
        for text in texts:
            split_texts.extend(text_splitter.split_text(text))

        # Embedding the split texts
        embeddings = self.embedding_client.embed_document(split_texts)
        
        documents = [Document(page_content=text, embedding=embedding) for text, embedding in zip(split_texts, embeddings)]
        
        self.db = Chroma.from_documents(documents, self.embedding_client.client ,persist_directory="./chroma_db")

    def query_chroma_collection(self, query,n):
        results = None
        if self.db:
            results = self.db.similarity_search_with_relevance_scores(query, k=n)

        return results #type:ignore