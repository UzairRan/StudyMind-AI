"""
Quiz Generator Module
Creates quizzes from document chunks (can work without LLM)
"""

import random
from typing import List, Dict
import streamlit as st

class QuizGenerator:
    def __init__(self, llm=None):
        """
        Initialize quiz generator
        
        Args:
            llm: Optional LLM for advanced quiz generation
        """
        self.llm = llm
    
    def generate_simple_quiz(self, chunks: List[str], num_questions: int = 5) -> str:
        """
        Generate simple quiz without LLM (rule-based)
        
        Args:
            chunks: Text chunks
            num_questions: Number of questions
            
        Returns:
            Quiz text
        """
        if not chunks:
            return "No content available for quiz generation."
        
        quiz = []
        
        for i in range(min(num_questions, len(chunks))):
            chunk = chunks[i]
            sentences = chunk.split('.')
            
            if len(sentences) < 3:
                continue
            
            # Take first sentence as question basis
            question_base = sentences[0].strip()
            
            # Take next sentence as answer
            if len(sentences) > 1:
                answer = sentences[1].strip()
            else:
                answer = question_base
            
            # Create a simple fill-in-the-blank question
            words = question_base.split()
            if len(words) > 5:
                # Hide a key word
                key_word_index = random.randint(2, min(5, len(words)-1))
                key_word = words[key_word_index]
                words[key_word_index] = "_____"
                question = ' '.join(words)
                
                quiz.append(f"""
Q{i+1}: {question}

Answer: {key_word}

Context: {answer[:100]}...
---
""")
        
        return '\n'.join(quiz) if quiz else "Could not generate quiz from content."
    
    def generate_quiz(self, chunks: List[str], num_questions: int = 5, 
                     chapter: str = "", use_llm: bool = True) -> Dict:
        """
        Generate quiz (uses LLM if available, otherwise rule-based)
        
        Args:
            chunks: Text chunks
            num_questions: Number of questions
            chapter: Chapter name
            use_llm: Whether to use LLM if available
            
        Returns:
            Dictionary with quiz data
        """
        # Try LLM first if available and requested
        if use_llm and self.llm and hasattr(self.llm, 'generate_quiz'):
            try:
                quiz_text = self.llm.generate_quiz(chunks, num_questions)
                return {
                    "success": True,
                    "questions": quiz_text,
                    "method": "llm",
                    "chapter": chapter
                }
            except Exception as e:
                st.warning(f"LLM quiz failed, falling back to simple quiz: {e}")
        
        # Fallback to simple quiz
        quiz_text = self.generate_simple_quiz(chunks, num_questions)
        
        return {
            "success": True,
            "questions": quiz_text,
            "method": "simple",
            "chapter": chapter
        } 