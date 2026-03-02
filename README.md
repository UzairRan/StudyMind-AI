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

flowchart LR
    A[PDF Upload]:::a --> B[Text Extraction]:::b
    B --> C[Chunking]:::c
    C --> D[Embeddings<br>Sentence-Transformers]:::d
    D --> E[FAISS Index]:::e
    E --> F[Retriever]:::f
    F --> G[Local / Cloud Model]:::g
    G --> H[Answer to User]:::h

classDef a fill:#ffabab,stroke:#000;
classDef b fill:#ffd6a5,stroke:#000;
classDef c fill:#fdffb6,stroke:#000;
classDef d fill:#caffbf,stroke:#000;
classDef e fill:#9bf6ff,stroke:#000;
classDef f fill:#a0c4ff,stroke:#000;
classDef g fill:#bdb2ff,stroke:#000;
classDef h fill:#ffc6ff,stroke:#000; 

----------------------------------------------------
