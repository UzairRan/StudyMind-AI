"""
Document Processing Module
Handles PDF loading, text extraction, and chunking
"""

import os
from typing import List, Dict, Any
from pypdf import PdfReader
import pdfplumber
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

class DocumentProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def extract_text_from_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract text and metadata from PDF file
        """
        pages = []
        
        # Try with pypdf first
        try:
            reader = PdfReader(file_path)
            for page_num, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                if text.strip():
                    pages.append({
                        'page': page_num,
                        'text': text,
                        'source': os.path.basename(file_path)
                    })
        except:
            # Fallback to pdfplumber for complex PDFs
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text and text.strip():
                        pages.append({
                            'page': page_num,
                            'text': text,
                            'source': os.path.basename(file_path)
                        })
        
        return pages
    
    def detect_chapters(self, text: str) -> str:
        """
        Simple chapter detection based on common patterns
        """
        lines = text.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            # Look for chapter patterns
            if line.lower().startswith('chapter') or line.lower().startswith('lecture'):
                return line
        return "General"
    
    def process_pdf(self, file_path: str, source_file: str) -> List[Document]:
        """
        Process PDF and return chunks as LangChain Documents
        """
        pages = self.extract_text_from_pdf(file_path)
        documents = []
        
        for page in pages:
            # Try to detect chapter from page content
            chapter = self.detect_chapters(page['text'])
            
            # Create metadata
            metadata = {
                'source': source_file,
                'page': page['page'],
                'chapter': chapter,
                'file_path': file_path
            }
            
            # Split text into chunks
            chunks = self.text_splitter.split_text(page['text'])
            
            # Create documents for each chunk
            for i, chunk in enumerate(chunks):
                chunk_metadata = metadata.copy()
                chunk_metadata['chunk_id'] = i
                chunk_metadata['chunk_start'] = i * (self.chunk_size - self.chunk_overlap)
                
                doc = Document(
                    page_content=chunk,
                    metadata=chunk_metadata
                )
                documents.append(doc)
        
        return documents 