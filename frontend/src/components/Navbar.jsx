import React from 'react';
import { FaBars, FaUpload, FaComment, FaQuestionCircle } from 'react-icons/fa';
import { motion } from 'framer-motion';

const Navbar = ({ activeTab, setActiveTab, toggleSidebar }) => {
    const tabs = [
        { id: 'upload', label: 'Upload Notes', icon: <FaUpload /> },
        { id: 'chat', label: 'Ask Questions', icon: <FaComment /> },
        { id: 'quiz', label: 'Generate Quiz', icon: <FaQuestionCircle /> },
    ];

    return (
        <nav className="navbar">
            <div className="navbar-left">
                <button className="menu-btn" onClick={toggleSidebar}>
                    <FaBars />
                </button>
                <h1 className="logo">
                    <span className="logo-study">Study</span>
                    <span className="logo-mind">Mind</span>
                    <span className="logo-ai">AI</span>
                </h1>
            </div>

            <div className="navbar-tabs">
                {tabs.map(tab => (
                    <motion.button
                        key={tab.id}
                        className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
                        onClick={() => setActiveTab(tab.id)}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                    >
                        <span className="tab-icon">{tab.icon}</span>
                        <span className="tab-label">{tab.label}</span>
                    </motion.button>
                ))}
            </div>

            <div className="navbar-right">
                <a 
                    href="https://github.com/yourusername/StudyMind-AI" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="github-link"
                >
                    GitHub
                </a>
            </div>
        </nav>
    );
};

export default Navbar; 