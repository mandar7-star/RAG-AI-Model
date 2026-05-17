# Multimodal RAG System with Real-Time Web Search and Intelligent File Generation

## Overview

This project implements an advanced multimodal Retrieval-Augmented Generation (RAG) system capable of extracting, processing, indexing, and retrieving information from multiple data sources including PDFs, images, scanned files, CSV files, and text documents. The system supports real-time web search integration, generates intelligent responses and files, and allows users to modify or regenerate responses through follow-up prompts.

## Features

- Extract text from PDFs, images (OCR), and scanned documents
- Understand and caption images using vision-language models (BLIP)
- Process structured data (CSV) and unstructured data (text files)
- Index and store embeddings in a vector database (ChromaDB)
- Perform semantic search on uploaded documents
- Integrate real-time web search using DuckDuckGo API
- Generate responses using local LLM (Ollama)
- Save responses as downloadable files
- Modify or regenerate responses based on user prompts
- Provide traceable references from both documents and web sources

## System Requirements

- Python 3.8 or higher
- 8GB RAM minimum (16GB recommended)
- Storage: 5GB for models and dependencies
- Operating System: Windows, Linux, or macOS
- Requires Ollama for remote access
- Requires Ollama for offline access

## Installation

### Step 1: Clone or create the project folder

```bash
mkdir multimodal_rag_system
cd multimodal_rag_system