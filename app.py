import streamlit as st
import os
import requests
import json
from document_loader import DocumentLoader
from rag_core import RAGCore
from multimodal_processor import MultimodalProcessor
from web_search import WebSearcher
from file_generator import FileGenerator
from langchain_core.documents import Document

st.set_page_config(page_title="Multimodal RAG System", layout="wide")
st.title("📚 Advanced Multimodal RAG with Web Search & File Generation")

@st.cache_resource
def init_rag():
    return RAGCore()

rag = init_rag()
multimodal = MultimodalProcessor()
web_search = WebSearcher()
file_gen = FileGenerator()

uploaded_files = st.file_uploader("Upload PDFs, Images, CSVs", type=["pdf", "png", "jpg", "jpeg", "csv", "txt"], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        file_path = f"./uploaded_files/{uploaded_file.name}"
        os.makedirs("./uploaded_files", exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Uploaded: {uploaded_file.name}")
        
        if uploaded_file.name.endswith(".pdf"):
            docs = DocumentLoader.load_pdf(file_path)
            rag.index_documents(docs)
        elif uploaded_file.name.endswith((".png", ".jpg", ".jpeg")):
            text = multimodal.extract_text_from_image(file_path)
            caption = multimodal.caption_image(file_path)
            rag.index_documents([Document(page_content=f"Image text: {text}\nCaption: {caption}", metadata={"source": file_path})])
        elif uploaded_file.name.endswith(".csv"):
            docs = DocumentLoader.load_csv(file_path)
            rag.index_documents(docs)
        elif uploaded_file.name.endswith(".txt"):
            docs = DocumentLoader.load_text(file_path)
            rag.index_documents(docs)

query = st.text_input("Ask a question (supports document context + live web search)")
use_web = st.checkbox("Include real-time web search", value=True)

def call_ollama(prompt, model="llama3.2"):
    try:
        response = requests.post('http://localhost:11434/api/generate', 
            json={'model': model, 'prompt': prompt, 'stream': False}, 
            timeout=120)  # Increased timeout
        if response.status_code == 200:
            return response.json()['response']
        else:
            return f"Ollama error: {response.status_code} - {response.text}"
    except requests.exceptions.ConnectionError:
        return "❌ Cannot connect to Ollama. Make sure 'ollama serve' is running."
    except Exception as e:
        return f"❌ Error: {str(e)}"

if st.button("Generate Response") and query:
    with st.spinner("Retrieving from documents..."):
        docs = rag.retrieve(query)
        context = "\n".join([d.page_content for d in docs])
    
    web_results = []
    if use_web:
        with st.spinner("Searching web..."):
            web_results = web_search.search(query)
            context += "\n\n[Web Results]\n" + "\n".join([f"{r['title']}: {r['snippet']}" for r in web_results])
    
    with st.spinner("Generating response with Ollama..."):
        prompt = f"""You are a helpful assistant. Answer the question based ONLY on the provided context.

Context:
{context}

Question: {query}

Answer concisely and accurately:"""
        
        answer = call_ollama(prompt)
    
    # Fix: Deduplicate references and clean web URLs
    doc_refs = []
    for d in docs:
        source = d.metadata.get("source", "document")
        if source not in doc_refs:
            doc_refs.append(source)
    
    web_refs = []
    for w in web_results:
        link = w.get('link', '')
        if link and link not in web_refs and not link.startswith('//duckduckgo'):
            web_refs.append(link)
    
    references = doc_refs + web_refs
    
    output_file = file_gen.generate_response_file(query, answer, references)
    
    st.subheader("Answer")
    st.write(answer)
    st.subheader("References")
    for ref in references[:5]:
        st.write(f"- {ref}")
    st.success(f"Response file saved: {output_file}")
    
    modification = st.text_input("Modify or regenerate response (enter prompt)")
    if st.button("Apply Modification"):
        new_file = file_gen.modify_response(output_file, modification)
        st.info(f"Modified file: {new_file}")