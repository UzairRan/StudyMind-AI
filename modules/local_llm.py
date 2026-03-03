"""
Local LLM Module
Handles Ollama integration for local model inference
"""

import subprocess
import json
import requests
from typing import List, Optional
import streamlit as st

class LocalLLM:
    def __init__(self, model_name: str = "llama3.2:3b"):
        """
        Initialize local LLM via Ollama
        
        Args:
            model_name: Ollama model name (e.g., 'llama3.2:3b', 'phi3:mini')
        """
        self.model_name = model_name
        self.base_url = "http://localhost:11434"
        
        # Check if Ollama is running
        self.ollama_available = self._check_ollama()
        
        if self.ollama_available:
            # Ensure model is pulled
            self._ensure_model()
    
    def _check_ollama(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except:
            return False
    
    def _ensure_model(self):
        """Ensure the model is available locally"""
        try:
            # List available models
            response = requests.get(f"{self.base_url}/api/tags")
            models = response.json().get('models', [])
            
            model_exists = any(m['name'] == self.model_name for m in models)
            
            if not model_exists:
                st.warning(f"Model {self.model_name} not found. Please pull it first:")
                st.code(f"ollama pull {self.model_name}")
        except:
            pass
    
    def generate_response(self, prompt: str, context: List[str] = None) -> str:
        """
        Generate response using local model
        
        Args:
            prompt: User query
            context: Retrieved context chunks
            
        Returns:
            Generated response
        """
        if not self.ollama_available:
            return "⚠️ Ollama is not running. Please start Ollama and try again."
        
        try:
            # Build prompt with context
            if context:
                context_text = "\n\n".join(context[:5])
                full_prompt = f"""You are a helpful study assistant. Answer the question based ONLY on the provided context.

CONTEXT:
{context_text}

QUESTION: {prompt}

ANSWER:"""
            else:
                full_prompt = prompt
            
            # Call Ollama API
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 500
                    }
                }
            )
            
            if response.status_code == 200:
                return response.json()['response']
            else:
                return f"Error: {response.status_code}"
                
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def generate_quiz(self, context: List[str], num_questions: int = 5) -> str:
        """
        Generate quiz from context
        
        Args:
            context: Context chunks
            num_questions: Number of questions
            
        Returns:
            Quiz text
        """
        if not self.ollama_available:
            return "⚠️ Ollama is not running. Please start Ollama and try again."
        
        try:
            context_text = "\n\n".join(context[:10])
            
            prompt = f"""Create {num_questions} multiple choice questions from this content:

CONTENT:
{context_text}

Format each question exactly as:
Q1: [Question]
A) [Option]
B) [Option]
C) [Option]
D) [Option]
Correct Answer: [Letter]
Explanation: [Brief explanation]

---"""
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.8,
                        "num_predict": 1500
                    }
                }
            )
            
            if response.status_code == 200:
                return response.json()['response']
            else:
                return f"Error generating quiz"
                
        except Exception as e:
            return f"Error: {str(e)}" 