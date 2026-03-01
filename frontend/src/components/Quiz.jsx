import React, { useState } from 'react';
import { FaBrain, FaDownload, FaRedo } from 'react-icons/fa';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import { generateQuiz } from '../services/api';
import { toast } from 'react-hot-toast';

const Quiz = ({ chapters, selectedModel, isLoading, setIsLoading }) => {
    const [selectedChapter, setSelectedChapter] = useState('');
    const [numQuestions, setNumQuestions] = useState(5);
    const [quiz, setQuiz] = useState(null);

    const handleGenerateQuiz = async () => {
        if (!selectedChapter) {
            toast.error('Please select a chapter');
            return;
        }

        setIsLoading(true);
        try {
            const response = await generateQuiz(selectedChapter, numQuestions);
            setQuiz(response);
            toast.success('Quiz generated successfully!');
        } catch (error) {
            toast.error('Failed to generate quiz. Please try again.');
            console.error('Quiz generation error:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleDownloadQuiz = () => {
        if (!quiz) return;
        
        const element = document.createElement('a');
        const file = new Blob([quiz.questions], {type: 'text/plain'});
        element.href = URL.createObjectURL(file);
        element.download = `quiz-${selectedChapter}-${Date.now()}.txt`;
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    };

    return (
        <div className="quiz-container">
            <div className="quiz-header">
                <h2>Generate Revision Quiz</h2>
                <p>Create practice questions from your notes to test your understanding.</p>
            </div>

            <div className="quiz-controls">
                <div className="control-group">
                    <label>Select Chapter:</label>
                    <select 
                        value={selectedChapter} 
                        onChange={(e) => setSelectedChapter(e.target.value)}
                        disabled={isLoading}
                    >
                        <option value="">Choose a chapter</option>
                        {chapters.map((chapter, index) => (
                            <option key={index} value={chapter}>{chapter}</option>
                        ))}
                    </select>
                </div>

                <div className="control-group">
                    <label>Number of Questions:</label>
                    <input 
                        type="number" 
                        min="1" 
                        max="10" 
                        value={numQuestions}
                        onChange={(e) => setNumQuestions(parseInt(e.target.value))}
                        disabled={isLoading}
                    />
                </div>

                <motion.button
                    className="generate-btn"
                    onClick={handleGenerateQuiz}
                    disabled={isLoading || !selectedChapter}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                >
                    <FaBrain /> Generate Quiz
                </motion.button>
            </div>

            <AnimatePresence>
                {quiz && (
                    <motion.div 
                        className="quiz-result"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 20 }}
                    >
                        <div className="quiz-actions">
                            <button onClick={handleDownloadQuiz}>
                                <FaDownload /> Download
                            </button>
                            <button onClick={() => setQuiz(null)}>
                                <FaRedo /> New Quiz
                            </button>
                        </div>
                        
                        <div className="quiz-content">
                            <ReactMarkdown>{quiz.questions}</ReactMarkdown>
                        </div>
                        
                        <div className="quiz-footer">
                            <span>Generated with {quiz.model}</span>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {isLoading && (
                <div className="quiz-loading">
                    <div className="spinner"></div>
                    <p>Generating your quiz...</p>
                </div>
            )}
        </div>
    );
};

export default Quiz; 