import React, { useState, useEffect } from 'react';
import { Toaster, toast } from 'react-hot-toast';
import { motion, AnimatePresence } from 'framer-motion';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import Upload from './components/Upload';
import Chat from './components/Chat';
import Quiz from './components/Quiz';
import { healthCheck } from './services/api';
import './styles/App.css';

function App() {
    const [activeTab, setActiveTab] = useState('upload');
    const [documents, setDocuments] = useState([]);
    const [chapters, setChapters] = useState([]);
    const [selectedModel, setSelectedModel] = useState('gemini-1.5-flash');
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        // Check backend health on startup
        const checkBackend = async () => {
            try {
                await healthCheck();
                toast.success('Connected to backend');
            } catch (error) {
                toast.error('Cannot connect to backend. Please check if server is running.');
            }
        };
        checkBackend();
    }, []);

    const renderContent = () => {
        switch(activeTab) {
            case 'upload':
                return (
                    <Upload 
                        documents={documents}
                        setDocuments={setDocuments}
                        setChapters={setChapters}
                        setIsLoading={setIsLoading}
                    />
                );
            case 'chat':
                return (
                    <Chat 
                        chapters={chapters}
                        selectedModel={selectedModel}
                        isLoading={isLoading}
                        setIsLoading={setIsLoading}
                    />
                );
            case 'quiz':
                return (
                    <Quiz 
                        chapters={chapters}
                        selectedModel={selectedModel}
                        isLoading={isLoading}
                        setIsLoading={setIsLoading}
                    />
                );
            default:
                return null;
        }
    };

    return (
        <div className="app">
            <Toaster position="top-right" />
            
            <Navbar 
                activeTab={activeTab}
                setActiveTab={setActiveTab}
                toggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
            />
            
            <div className="main-container">
                <AnimatePresence>
                    {isSidebarOpen && (
                        <motion.div
                            initial={{ x: -300, opacity: 0 }}
                            animate={{ x: 0, opacity: 1 }}
                            exit={{ x: -300, opacity: 0 }}
                            transition={{ duration: 0.3 }}
                            className="sidebar-wrapper"
                        >
                            <Sidebar 
                                documents={documents}
                                chapters={chapters}
                                selectedModel={selectedModel}
                                setSelectedModel={setSelectedModel}
                                onClear={() => {
                                    setDocuments([]);
                                    setChapters([]);
                                }}
                            />
                        </motion.div>
                    )}
                </AnimatePresence>
                
                <motion.main 
                    className="content"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.5 }}
                >
                    {renderContent()}
                </motion.main>
            </div>
        </div>
    );
}

export default App; 