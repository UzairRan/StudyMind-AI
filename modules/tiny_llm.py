"""
Tiny LLM Module
Uses small models that run on Streamlit Cloud (under 512MB)
"""

from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
import torch
from typing import List, Optional
import streamlit as st

class TinyLLM:
    def __init__(self, model_name: str = "microsoft/phi-1_5"):
        """
        Initialize tiny model for cloud deployment
        
        Args:
            model_name: HuggingFace model name (must be small)
        """
        self.model_name = model_name
        
        # Available tiny models (all under 2GB, run on CPU)
        self.available_models = {
            "Phi-1.5 (1.3B)": "microsoft/phi-1_5",
            "TinyLlama (1.1B)": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
            "GPT-2 (124M)": "gpt2",
            "OPT-125M": "facebook/opt-125m",
        }
        
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        
        # Load model (cached after first load)
        self._load_model()
    
    def _load_model(self):
        """Load the model (cached)"""
        try:
            with st.spinner(f"Loading {self.model_name}... (first time only)"):
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float32,
                    low_cpu_mem_usage=True
                )
                
                self.pipeline = pipeline(
                    "text-generation",
                    model=self.model,
                    tokenizer=self.tokenizer,
                    max_new_tokens=200,
                    temperature=0.7,
                    do_sample=True
                )
        except Exception as e:
            st.error(f"Failed to load model: {e}")
    
    def generate_response(self, prompt: str, context: List[str] = None) -> str:
        """
        Generate response using tiny model
        
        Args:
            prompt: User query
            context: Retrieved context
            
        Returns:
            Generated response
        """
        if self.pipeline is None:
            return "Model not loaded. Please try again."
        
        try:
            # Build prompt
            if context:
                context_text = "\n".join(context[:3])  # Limit context for tiny models
                full_prompt = f"""Context: {context_text}

Question: {prompt}

Answer:"""
            else:
                full_prompt = prompt
            
            # Generate
            result = self.pipeline(full_prompt, max_new_tokens=150, num_return_sequences=1)
            
            return result[0]['generated_text'].replace(full_prompt, "").strip()
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def generate_quiz(self, context: List[str], num_questions: int = 3) -> str:
        """
        Generate simple quiz (limited for tiny models)
        
        Args:
            context: Context chunks
            num_questions: Number of questions
            
        Returns:
            Quiz text
        """
        if self.pipeline is None:
            return "Model not loaded"
        
        try:
            context_text = "\n".join(context[:2])
            
            prompt = f"""Based on this text, create {num_questions} questions:

{context_text}

Questions:"""
            
            result = self.pipeline(prompt, max_new_tokens=300, num_return_sequences=1)
            
            return result[0]['generated_text'].replace(prompt, "").strip()
            
        except Exception as e:
            return f"Error: {str(e)}" 