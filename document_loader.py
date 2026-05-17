import os
from typing import List, Dict
from langchain_community.document_loaders import PyPDFLoader, TextLoader, CSVLoader
from langchain_core.documents import Document
import pandas as pd
from PIL import Image

class DocumentLoader:
    @staticmethod
    def load_pdf(file_path: str) -> List[Document]:
        loader = PyPDFLoader(file_path)
        return loader.load()
    
    @staticmethod
    def load_text(file_path: str) -> List[Document]:
        loader = TextLoader(file_path)
        return loader.load()
    
    @staticmethod
    def load_csv(file_path: str) -> List[Document]:
        loader = CSVLoader(file_path)
        return loader.load()
    
    @staticmethod
    def load_image_metadata(file_path: str) -> Dict:
        img = Image.open(file_path)
        return {"source": file_path, "format": img.format, "size": img.size}