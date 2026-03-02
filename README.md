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

# Flow Diagram 1  Full System

```mermaid
flowchart TB
    A[PDF Upload]:::node --> B[Text Extraction]:::node
    B --> C[Chunking]:::node
    C --> D[Embeddings<br>Sentence-Transformers]:::node
    D --> E[FAISS Index]:::node
    E --> F[Retriever]:::node
    F --> G[Local / Cloud Model]:::node
    G --> H[Answer to User]:::node

    %% Larger and cleaner style
    classDef node fill:#e8f1ff,stroke:#000,stroke-width:2px,
        color:#000,font-size:18px,padding:18px;
```



----------------------------------------------------


