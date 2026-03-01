"""
Gemini LLM Module
Handles all interactions with Google's Gemini API
"""

import os
import google.generativeai as genai
from typing import List, Dict, Any, Optional

class GeminiLLM:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini with API key
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key not found")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Available models
        self.models = {
            "gemini-1.5-flash": {
                "name": "Gemini 1.5 Flash",
                "description": "Fast, efficient for most tasks",
                "context": 1000000
            },
            "gemini-1.5-pro": {
                "name": "Gemini 1.5 Pro",
                "description": "Powerful, best for complex reasoning",
                "context": 1000000
            },
            "gemini-1.0-pro": {
                "name": "Gemini 1.0 Pro",
                "description": "Legacy model, stable",
                "context": 30000
            }
        }
        
        # Generation config
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
    
    def get_available_models(self) -> Dict:
        """
        Return available models
        """
        return self.models
    
    def generate_response(self, prompt: str, context: List[str] = None, model_name: str = "gemini-1.5-flash") -> str:
        """
        Generate response using Gemini
        """
        try:
            # Get model
            model = genai.GenerativeModel(model_name)
            
            # Build prompt with context
            if context:
                context_text = "\n\n".join(context)
                full_prompt = f"""You are StudyMind AI, an educational assistant helping students understand their course materials.

CONTEXT FROM DOCUMENTS:
{context_text}

USER QUESTION: {prompt}

INSTRUCTIONS:
1. Answer based ONLY on the context provided above
2. If the answer isn't in the context, say "I cannot find this information in your notes"
3. Be concise and educational
4. Use bullet points for lists when appropriate
5. Include page numbers if mentioned in context

ANSWER:"""
            else:
                full_prompt = prompt
            
            # Generate response
            response = model.generate_content(
                full_prompt,
                generation_config=self.generation_config
            )
            
            return response.text
            
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def generate_quiz_questions(self, context: List[str], num_questions: int = 5, chapter: str = "") -> str:
        """
        Generate quiz questions from context
        """
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            context_text = "\n\n".join(context[:10])  # Limit context for quiz
            
            prompt = f"""You are StudyMind AI, creating a quiz for students based on their course materials.

CHAPTER: {chapter}

CONTENT:
{context_text}

Create {num_questions} multiple-choice questions for revision.

FORMAT EACH QUESTION EXACTLY AS:

Q1: [Question text]
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]
Correct Answer: [Letter]
Explanation: [Brief explanation of why this is correct]

---
Q2: [Question text]
... and so on.

Make questions:
- Test understanding, not just memorization
- Clear and unambiguous
- Based strictly on the provided content
- Include one correct answer and three plausible distractors

Generate the quiz now:"""
            
            response = model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Error generating quiz: {str(e)}" 