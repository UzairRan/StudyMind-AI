import React, { useState } from 'react';
import { FaSend, FaFile, FaBook } from 'react-icons/fa';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import { queryDocuments } from '../services/api';
import { toast } from 'react-hot-toast';

const Chat = ({ chapters, selectedModel, isLoading, setIsLoading }) => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [selectedChapter, setSelectedChapter] = useState('All Chapters');

    const handleSend = async () => {
        if (!input.trim()) return;

        // Add user message
        const userMessage = {
            role: 'user',
            content: input,
            timestamp: new Date().toISOString()
        };
        setMessages(prev => [...prev, userMessage]);
        setInput('');

        setIsLoading(true);
        try {
            const response = await queryDocuments(
                input, 
                selectedChapter === 'All Chapters' ? null : selectedChapter,
                selectedModel
            );
            
            // Add AI response
            const aiMessage = {
                role: 'assistant',
                content: response.answer,
                sources: response.sources,
                model: response.model_used,
                timestamp: new Date().toISOString()
            };
            setMessages(prev => [...prev, aiMessage]);
        } catch (error) {
            toast.error('Failed to get response. Please try again.');
            console.error('Query error:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className="chat-container">
            <div className="chat-header">
                <h2>Ask Questions About Your Notes</h2>
                <div className="chapter-filter">
                    <FaBook className="filter-icon" />
                    <select 
                        value={selectedChapter} 
                        onChange={(e) => setSelectedChapter(e.target.value)}
                    >
                        <option value="All Chapters">All Chapters</option>
                        {chapters.map((chapter, index) => (
                            <option key={index} value={chapter}>{chapter}</option>
                        ))}
                    </select>
                </div>
            </div>

            <div className="messages-container">
                <AnimatePresence>
                    {messages.map((message, index) => (
                        <motion.div
                            key={index}
                            className={`message ${message.role}`}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            transition={{ delay: index * 0.1 }}
                        >
                            <div className="message-content">
                                <ReactMarkdown>{message.content}</ReactMarkdown>
                            </div>
                            
                            {message.sources && message.sources.length > 0 && (
                                <div className="message-sources">
                                    <p className="sources-title">Sources:</p>
                                    {message.sources.map((source, idx) => (
                                        <div key={idx} className="source-item">
                                            <FaFile />
                                            <span>
                                                {source.source} - Page {source.page}
                                                {source.chapter && ` (${source.chapter})`}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            )}
                            
                            <div className="message-meta">
                                <span className="message-time">
                                    {new Date(message.timestamp).toLocaleTimeString()}
                                </span>
                                {message.model && (
                                    <span className="message-model">{message.model}</span>
                                )}
                            </div>
                        </motion.div>
                    ))}
                </AnimatePresence>

                {isLoading && (
                    <motion.div 
                        className="message assistant loading"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                    >
                        <div className="typing-indicator">
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>
                    </motion.div>
                )}
            </div>

            <div className="chat-input-container">
                <textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask a question about your notes..."
                    disabled={isLoading}
                    rows={3}
                />
                <motion.button
                    onClick={handleSend}
                    disabled={isLoading || !input.trim()}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                >
                    <FaSend />
                </motion.button>
            </div>
        </div>
    );
};

export default Chat; 