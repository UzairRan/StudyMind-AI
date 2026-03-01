"""
Main FastAPI Application for StudyMind AI
Handles all API endpoints for PDF upload, Q&A, and quiz generation
"""

import os
import shutil
import uuid
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import modules
from modules.document_processor import DocumentProcessor
from modules.embeddings import EmbeddingManager
from modules.retriever import Retriever
from modules.gemini_llm import GeminiLLM
from modules.quiz_generator import QuizGenerator
from modules.utils import cleanup_temp_files

# Initialize FastAPI app
app = FastAPI(
    title="StudyMind AI API",
    description="Backend API for RAG-based PDF Q&A system",
    version="1.0.0"
)

# Configure CORS
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
doc_processor = DocumentProcessor(
    chunk_size=int(os.getenv("CHUNK_SIZE", 1000)),
    chunk_overlap=int(os.getenv("CHUNK_OVERLAP", 200))
)

embedding_manager = EmbeddingManager()
retriever = Retriever(top_k=int(os.getenv("TOP_K_RESULTS", 5)))
gemini_llm = GeminiLLM(api_key=os.getenv("GEMINI_API_KEY"))
quiz_generator = QuizGenerator(gemini_llm)

# Temporary storage
UPLOAD_DIR = "temp_uploads"
VECTOR_STORE_DIR = "vector_store"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)

# Pydantic models for request/response
class QueryRequest(BaseModel):
    query: str
    chapter_filter: Optional[str] = None
    model_name: Optional[str] = "gemini-1.5-flash"

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]
    model_used: str

class QuizRequest(BaseModel):
    chapter: str
    num_questions: int = 5

class QuizResponse(BaseModel):
    questions: str
    model_used: str

class UploadResponse(BaseModel):
    message: str
    document_id: str
    num_chunks: int
    chapters: List[str]

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Welcome to StudyMind AI API", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/models")
async def get_models():
    """Get available Gemini models"""
    return gemini_llm.get_available_models()

@app.post("/upload", response_model=UploadResponse)
async def upload_pdfs(background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
    """
    Upload and process PDF files
    """
    try:
        document_id = str(uuid.uuid4())
        saved_files = []
        
        # Save uploaded files
        for file in files:
            if not file.filename.endswith('.pdf'):
                raise HTTPException(status_code=400, detail=f"File {file.filename} is not a PDF")
            
            file_path = os.path.join(UPLOAD_DIR, f"{document_id}_{file.filename}")
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            saved_files.append(file_path)
        
        # Process documents
        documents = []
        for file_path in saved_files:
            docs = doc_processor.process_pdf(file_path, source_file=os.path.basename(file_path))
            documents.extend(docs)
        
        if not documents:
            raise HTTPException(status_code=400, detail="No text could be extracted from PDFs")
        
        # Create embeddings and vector store
        chunks = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        
        embedding_manager.create_embeddings(chunks, metadatas)
        
        # Save vector store
        vector_store_path = os.path.join(VECTOR_STORE_DIR, f"index_{document_id}")
        embedding_manager.save_index(vector_store_path)
        
        # Cleanup temp files in background
        background_tasks.add_task(cleanup_temp_files, saved_files)
        
        # Extract unique chapters
        chapters = list(set([meta.get('chapter', 'Unknown') for meta in metadatas]))
        
        return UploadResponse(
            message=f"Successfully processed {len(files)} PDFs",
            document_id=document_id,
            num_chunks=len(chunks),
            chapters=chapters
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Query the documents with RAG
    """
    try:
        # Load the latest vector store
        index_files = os.listdir(VECTOR_STORE_DIR)
        if not index_files:
            raise HTTPException(status_code=400, detail="No documents uploaded yet")
        
        latest_index = os.path.join(VECTOR_STORE_DIR, sorted(index_files)[-1])
        embedding_manager.load_index(latest_index)
        
        # Search for relevant chunks
        chunks, metadatas = retriever.search(
            embedding_manager=embedding_manager,
            query=request.query,
            chapter_filter=request.chapter_filter
        )
        
        if not chunks:
            return QueryResponse(
                answer="No relevant information found in the documents.",
                sources=[],
                model_used=request.model_name
            )
        
        # Generate answer using Gemini
        answer = gemini_llm.generate_response(
            prompt=request.query,
            context=chunks,
            model_name=request.model_name
        )
        
        # Prepare sources
        sources = [
            {
                "content": chunk[:200] + "...",
                "source": meta.get('source', 'Unknown'),
                "page": meta.get('page', 'Unknown'),
                "chapter": meta.get('chapter', 'Unknown')
            }
            for chunk, meta in zip(chunks, metadatas)
        ]
        
        return QueryResponse(
            answer=answer,
            sources=sources,
            model_used=request.model_name
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-quiz", response_model=QuizResponse)
async def generate_quiz(request: QuizRequest):
    """
    Generate quiz questions from a specific chapter
    """
    try:
        # Load the latest vector store
        index_files = os.listdir(VECTOR_STORE_DIR)
        if not index_files:
            raise HTTPException(status_code=400, detail="No documents uploaded yet")
        
        latest_index = os.path.join(VECTOR_STORE_DIR, sorted(index_files)[-1])
        embedding_manager.load_index(latest_index)
        
        # Get all chunks for the chapter
        all_chunks = embedding_manager.get_all_chunks()
        chapter_chunks = [
            chunk for chunk, meta in zip(all_chunks['texts'], all_chunks['metadatas'])
            if meta.get('chapter', '').lower() == request.chapter.lower()
        ]
        
        if not chapter_chunks:
            raise HTTPException(status_code=404, detail=f"No content found for chapter: {request.chapter}")
        
        # Generate quiz
        quiz = quiz_generator.generate_quiz(
            context=chapter_chunks,
            num_questions=request.num_questions,
            chapter=request.chapter
        )
        
        return QuizResponse(
            questions=quiz['questions'],
            model_used=quiz['model']
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chapters")
async def get_chapters():
    """
    Get all available chapters from uploaded documents
    """
    try:
        index_files = os.listdir(VECTOR_STORE_DIR)
        if not index_files:
            return {"chapters": []}
        
        latest_index = os.path.join(VECTOR_STORE_DIR, sorted(index_files)[-1])
        embedding_manager.load_index(latest_index)
        
        all_chunks = embedding_manager.get_all_chunks()
        chapters = list(set([meta.get('chapter', 'Unknown') for meta in all_chunks['metadatas']]))
        
        return {"chapters": chapters}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/clear")
async def clear_all_data():
    """
    Clear all uploaded data and vector stores
    """
    try:
        # Clear upload directory
        for file in os.listdir(UPLOAD_DIR):
            file_path = os.path.join(UPLOAD_DIR, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        
        # Clear vector store
        for file in os.listdir(VECTOR_STORE_DIR):
            file_path = os.path.join(VECTOR_STORE_DIR, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        
        return {"message": "All data cleared successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(os.getenv("BACKEND_PORT", 8000)),
        reload=True
    ) 