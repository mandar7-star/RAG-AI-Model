import streamlit as st
import os
import requests
import re
from document_loader import DocumentLoader
from rag_core import RAGCore
from multimodal_processor import MultimodalProcessor
from web_search import WebSearcher
from file_generator import FileGenerator
from langchain_core.documents import Document

st.set_page_config(page_title="Multimodal RAG System", layout="wide")
st.title("Multimodal RAG System with Web Search and File Generation")

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

query = st.text_input("Ask a question about your documents")
use_web = st.checkbox("Include real-time web search", value=True)

def call_ollama(prompt, model="llama3.2:1b"):
    try:
        response = requests.post('http://localhost:11434/api/generate', 
            json={'model': model, 'prompt': prompt, 'stream': False}, timeout=120)
        if response.status_code == 200:
            return response.json()['response']
        else:
            return f"Ollama error: {response.status_code} - {response.text}"
    except requests.exceptions.ConnectionError:
        return "Cannot connect to Ollama. Please run 'ollama serve' in a separate terminal."
    except Exception as e:
        return f"Ollama error: {str(e)}"

if st.button("Generate Response") and query:
    with st.spinner("Searching documents..."):
        docs = rag.retrieve(query)
        context = "\n".join([d.page_content for d in docs])
    
    web_results = []
    if use_web:
        with st.spinner("Searching web..."):
            web_results = web_search.search(query)
            
            # Display web results in sidebar for debugging
            with st.sidebar.expander("Web Search Results", expanded=True):
                st.write(f"Found {len(web_results)} results")
                for idx, wr in enumerate(web_results):
                    st.write(f"**{idx+1}. {wr.get('title', 'No title')}**")
                    st.write(f"Link: {wr.get('link', 'No link')}")
                    st.write(f"Snippet: {wr.get('snippet', 'No snippet')[:150]}...")
                    st.write("---")
            
            if web_results:
                context += "\n\n=== Web Search Results ===\n"
                for r in web_results:
                    context += f"\nTitle: {r.get('title', '')}\n"
                    context += f"Content: {r.get('snippet', '')}\n"
                    context += f"Source: {r.get('link', '')}\n"
    
    with st.spinner("Generating response with Ollama (llama3.2:1b)..."):
        prompt = f"""Answer the question based on the context below. Include citations by mentioning the source names.

Context:
{context}

Question: {query}

Answer:"""
        
        answer = call_ollama(prompt)
    
    # Build document references
    doc_refs = []
    for d in docs:
        source = d.metadata.get("source", "document")
        if source not in doc_refs:
            doc_refs.append(f"Document: {source}")
    
    # Build web references
    web_refs = []
    for w in web_results:
        title = w.get('title', 'Web Source')
        link = w.get('link', '')
        if link and link != '':
            web_refs.append(f"Web: {title} - {link}")
        elif title:
            web_refs.append(f"Web: {title}")
    
    references = doc_refs + web_refs
    output_file = file_gen.generate_response_file(query, answer, references)
    
    st.subheader("Answer")
    st.write(answer)
    
    st.subheader("References")
    if references:
        for ref in references[:10]:
            st.write(f"- {ref}")
    else:
        st.write("No references available")
    
    st.success(f"Response saved: {output_file}")
    
    modification = st.text_input("Modify response (enter prompt)")
    if st.button("Apply Modification"):
        new_file = file_gen.modify_response(output_file, modification)
        st.info(f"Modified file: {new_file}")