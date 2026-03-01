"""
Quiz Generator Module
Creates quizzes from document chunks
"""

from typing import List, Dict, Any

class QuizGenerator:
    def __init__(self, llm):
        self.llm = llm
    
    def generate_quiz(self, context: List[str], num_questions: int = 5, chapter: str = "") -> Dict:
        """
        Generate quiz from context
        """
        try:
            # Generate questions using LLM
            questions = self.llm.generate_quiz_questions(
                context=context,
                num_questions=num_questions,
                chapter=chapter
            )
            
            # Parse and structure the quiz
            parsed_quiz = self._parse_quiz(questions)
            
            return {
                "success": True,
                "questions": questions,
                "parsed": parsed_quiz,
                "model": "gemini-1.5-flash",
                "chapter": chapter
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "questions": "",
                "model": "gemini-1.5-flash"
            }
    
    def _parse_quiz(self, quiz_text: str) -> List[Dict]:
        """
        Parse quiz text into structured format
        """
        questions = []
        current_question = {}
        
        lines = quiz_text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('Q') and ':' in line:
                # New question
                if current_question:
                    questions.append(current_question)
                
                # Extract question number and text
                parts = line.split(':', 1)
                q_num = parts[0].strip()
                q_text = parts[1].strip() if len(parts) > 1 else ""
                
                current_question = {
                    'number': q_num,
                    'question': q_text,
                    'options': [],
                    'correct_answer': '',
                    'explanation': ''
                }
            
            elif line.startswith(('A)', 'B)', 'C)', 'D)')):
                # Option
                if current_question:
                    current_question['options'].append(line)
            
            elif line.startswith('Correct Answer:'):
                # Correct answer
                if current_question:
                    current_question['correct_answer'] = line.replace('Correct Answer:', '').strip()
            
            elif line.startswith('Explanation:'):
                # Explanation
                if current_question:
                    current_question['explanation'] = line.replace('Explanation:', '').strip()
        
        # Add last question
        if current_question:
            questions.append(current_question)
        
        return questions 