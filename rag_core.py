from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
import os
from typing import List

class RAGCore:
    def __init__(self, persist_dir="./vector_store"):
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.persist_dir = persist_dir
        self.vectorstore = None
    
    def chunk_documents(self, docs: List[Document], chunk_size=500, chunk_overlap=50):
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        return splitter.split_documents(docs)
    
    def index_documents(self, docs: List[Document]):
        chunks = self.chunk_documents(docs)
        self.vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=self.persist_dir
        )
        self.vectorstore.persist()
        return len(chunks)
    
    def retrieve(self, query: str, k=5):
        if not self.vectorstore:
            self.vectorstore = Chroma(persist_directory=self.persist_dir, embedding_function=self.embeddings)
        docs = self.vectorstore.similarity_search(query, k=k)
        
        # Deduplicate by source + content preview
        seen = set()
        unique_docs = []
        for doc in docs:
            source = doc.metadata.get("source", "unknown")
            content_preview = doc.page_content[:100]
            key = f"{source}_{content_preview}"
            if key not in seen:
                seen.add(key)
                unique_docs.append(doc)
        
        return unique_docs[:3]  # Return top 3 unique chunks