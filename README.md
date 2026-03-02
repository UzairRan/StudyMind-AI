<p align="left"> <img src="https://img.shields.io/badge/Streamlit-App-blue?style=for-the-badge" /> <img src="https://img.shields.io/badge/Python-3.10+-yellow?style=for-the-badge" /> <img src="https://img.shields.io/badge/RAG-Enabled-green?style=for-the-badge" /> <img src="https://img.shields.io/badge/FAISS-VectorDB-orange?style=for-the-badge" /> <img src="https://img.shields.io/badge/SentenceTransformers-Embeddings-red?style=for-the-badge" /> <img src="https://img.shields.io/badge/Ollama-LocalLLM-purple?style=for-the-badge" /> <img src="https://img.shields.io/badge/Transformers-TinyModels-lightgrey?style=for-the-badge" /> <img src="https://img.shields.io/badge/License-MIT-brightgreen?style=for-the-badge" /> </p>

# StudyMind AI

**Smart Notes → Search → Ask → Quiz**

---------------------------------------------------

# Overview

- StudyMind AI is a simple study assistant that lets you:

- Upload study PDFs

- Process notes into clean chunks

- Search topics fast

- Ask questions using a local or cloud model

- Generate small quizzes

- Everything works offline on your PC and online on Streamlit Cloud.

--------------------------------------------------------

# Flow Diagram: Full System


```mermaid
flowchart TB
    A[PDF Upload]:::node --> B[Text Extraction]:::node
    B --> C[Chunking]:::node
    C --> D[Embeddings<br>Sentence-Transformers]:::node
    D --> E[FAISS Index]:::node
    E --> F[Retriever]:::node
    F --> G[Local / Cloud Model]:::node
    G --> H[Answer to User]:::node

    classDef node fill:#e8f1ff,stroke:#000,stroke-width:2px,color:#000,font-size:18px,padding:18px;
```

----------------------------------------------------


# Tech Stack

**Core**

- Streamlit

- Python

- LangChain

- FAISS

- Sentence-Transformers

- PDF Processing

- pypdf

- pdfplumber

**Models**

- Local: Ollama (Llama 3.2 3B)

- Cloud: Tiny Models (Phi-1.5)

- Utilities

- numpy

- pandas

- dotenv

- plotly

-------------------------------------------------

# Key Concepts Covered

- RAG pipeline

- Local embeddings

- Vector search using FAISS

- Note chunking

- Context retrieval

- Local + Cloud LLM switching(Streamlit)

- PDF ingestion

- Simple quiz generation

- Streamlit UI workflow

---------------------------------------------------

# Local vs Cloud Usage(Streamlit)

**Local PC**

- PDF processing works

- Embeddings work

- FAISS search works

- Local LLM through Ollama works


**Streamlit Cloud**

- PDF processing works

- Embeddings work

- FAISS search works

- Local LLM not supported

- Tiny models work

-----------------------------------------------

# Flow Diagram: Local vs Cloud Path

```mermaid
flowchart TB
    A[User Question]:::node --> B[Retrieve Context]:::node
    B --> C{Running Environment?}:::node
    C -->|Local PC| D[Ollama Model]:::node
    C -->|Streamlit Cloud| E[Tiny Model]:::node
    D --> F[Final Answer]:::node
    E --> F[Final Answer]:::node

    classDef node fill:#e8f1ff,stroke:#000,stroke-width:2px,color:#000,font-size:16px,padding:12px;'''

---------------------------------------------------------

# Installation Instructions

**For Windows**

- Clone the repository

git clone https://github.com/yourusername/StudyMind-AI.git

cd StudyMind-AI

- Create virtual environment

python -m venv venv

- Activate virtual environment

venv\Scripts\activate

- Install dependencies

pip install --upgrade pip

pip install -r requirements.txt

- Install Ollama (for local LLM)

Download from: **https://ollama.com/download/windows**

Run the installer (typical Windows installation)

- Pull a model (in new PowerShell window, not in venv)

ollama pull llama3.2:3b

- Run the app

streamlit run app.py

-----------------------------

**For Mac and Linux**

- Clone the repository

git clone https://github.com/yourusername/StudyMind-AI.git

cd StudyMind-AI

- Create virtual environment

python3 -m venv venv

- Activate virtual environment

source venv/bin/activate

- Install dependencies

pip install --upgrade pip

pip install -r requirements.txt

- Install Ollama

curl -fsSL https://ollama.com/install.sh | sh

- Pull Llama model

ollama pull llama3.2:3b

- Launch application

streamlit run app.py

--------------------------------------------------------
--------------------------------------------------------



