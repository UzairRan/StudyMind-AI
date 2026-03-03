"""
Tiny LLM Module
Uses ultra-small models that run on Streamlit Cloud (under 512MB)
"""

from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
import torch
from typing import List, Optional
import streamlit as st

class TinyLLM:
    def __init__(self, model_name: str = "gpt2"):
        """
        Initialize tiny model for cloud deployment
        
        Args:
            model_name: HuggingFace model name (must be VERY small for 512MB)
        """
        self.model_name = model_name
        
        # Ultra-small models (ALL under 512MB)
        self.available_models = {
            "GPT-2 (124M)": "gpt2",                          # 500MB - RECOMMENDED
            "DistilGPT-2 (82M)": "distilgpt2",               # 350MB
            "OPT-125M": "facebook/opt-125m",                 # 250MB
            "TinyBERT (14M)": "huawei-noah/TinyBERT_4L_312D", # 50MB
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
                
                # Add padding token for GPT-2
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
                
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float32,
                    low_cpu_mem_usage=True
                )
                
                self.pipeline = pipeline(
                    "text-generation",
                    model=self.model,
                    tokenizer=self.tokenizer,
                    max_new_tokens=100,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
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
            # Build prompt - simpler for small models
            if context:
                context_text = "\n".join(context[:2])  # Limit context
                full_prompt = f"Context: {context_text}\n\nQuestion: {prompt}\n\nAnswer:"
            else:
                full_prompt = f"Question: {prompt}\n\nAnswer:"
            
            # Generate
            result = self.pipeline(
                full_prompt, 
                max_new_tokens=100, 
                num_return_sequences=1,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            # Extract just the answer part
            generated = result[0]['generated_text']
            if "Answer:" in generated:
                return generated.split("Answer:")[-1].strip()
            return generated.strip()
            
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
            context_text = "\n".join(context[:1])  # Even less context
            
            prompt = f"Based on: {context_text}\n\nCreate {num_questions} questions:"
            
            result = self.pipeline(
                prompt, 
                max_new_tokens=200, 
                num_return_sequences=1,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            return result[0]['generated_text'].replace(prompt, "").strip()
            
        except Exception as e:
            return f"Error: {str(e)}" 