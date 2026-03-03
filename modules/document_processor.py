"""
Document Processing Module
Handles PDF loading, text extraction, and intelligent chunking
"""

import os
from typing import List, Dict, Any
from pypdf import PdfReader
import pdfplumber
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

class DocumentProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the document processor with chunking parameters
        
        Args:
            chunk_size: Size of each text chunk
            chunk_overlap: Overlap between chunks for context preservation
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Smart text splitter that respects paragraphs and sentences
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ".", " ", ""]  # Priority order for splitting
        )
    
    def extract_text_from_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract text and metadata from PDF file with fallback methods
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            List of dictionaries with page text and metadata
        """
        pages = []
        
        # Try pypdf first (faster)
        try:
            reader = PdfReader(file_path)
            for page_num, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                if text and text.strip():
                    pages.append({
                        'page': page_num,
                        'text': text.strip(),
                        'source': os.path.basename(file_path)
                    })
        except Exception as e:
            print(f"pypdf failed, trying pdfplumber: {e}")
            
            # Fallback to pdfplumber (better for complex PDFs)
            try:
                with pdfplumber.open(file_path) as pdf:
                    for page_num, page in enumerate(pdf.pages, 1):
                        text = page.extract_text()
                        if text and text.strip():
                            pages.append({
                                'page': page_num,
                                'text': text.strip(),
                                'source': os.path.basename(file_path)
                            })
            except Exception as e2:
                print(f"Both PDF extractors failed: {e2}")
                return []
        
        return pages
    
    def detect_chapter(self, text: str) -> str:
        """
        Smart chapter detection from text content
        
        Args:
            text: Page text to analyze
            
        Returns:
            Detected chapter name or 'General'
        """
        # Common chapter indicators
        chapter_keywords = ['chapter', 'lecture', 'module', 'unit', 'section', 'part']
        
        # Check first few lines for chapter headings
        lines = text.split('\n')[:10]
        for line in lines:
            line_lower = line.strip().lower()
            
            # Check for chapter patterns
            for keyword in chapter_keywords:
                if keyword in line_lower:
                    # Extract the full chapter title
                    words = line.strip().split()
                    if len(words) > 5:
                        return ' '.join(words[:5])  # Limit to first 5 words
                    return line.strip()[:50]  # Limit length
        
        return "General"
    
    def process_pdf(self, file_path: str, source_file: str = None) -> List[Document]:
        """
        Complete PDF processing pipeline
        
        Args:
            file_path: Path to PDF file
            source_file: Original filename
            
        Returns:
            List of LangChain Document objects
        """
        pages = self.extract_text_from_pdf(file_path)
        documents = []
        
        for page in pages:
            # Detect chapter from page content
            chapter = self.detect_chapter(page['text'])
            
            # Create metadata
            metadata = {
                'source': source_file or page['source'],
                'page': page['page'],
                'chapter': chapter,
                'file_path': file_path
            }
            
            # Split page into chunks
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