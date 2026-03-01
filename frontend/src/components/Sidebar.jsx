import React, { useState, useEffect } from 'react';
import { FaFile, FaFolder, FaTrash, FaCog, FaDownload } from 'react-icons/fa';
import { motion } from 'framer-motion';
import { getModels, clearAllData } from '../services/api';
import { toast } from 'react-hot-toast';

const Sidebar = ({ documents, chapters, selectedModel, setSelectedModel, onClear }) => {
    const [models, setModels] = useState({});
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        loadModels();
    }, []);

    const loadModels = async () => {
        try {
            const data = await getModels();
            setModels(data);
        } catch (error) {
            console.error('Failed to load models:', error);
        }
    };

    const handleClearAll = async () => {
        if (window.confirm('Are you sure? This will delete all uploaded documents.')) {
            setIsLoading(true);
            try {
                await clearAllData();
                onClear();
                toast.success('All data cleared');
            } catch (error) {
                toast.error('Failed to clear data');
            } finally {
                setIsLoading(false);
            }
        }
    };

    return (
        <div className="sidebar">
            <div className="sidebar-section">
                <h3>
                    <FaCog /> Settings
                </h3>
                <div className="model-selector">
                    <label>AI Model:</label>
                    <select 
                        value={selectedModel} 
                        onChange={(e) => setSelectedModel(e.target.value)}
                    >
                        {Object.entries(models).map(([key, model]) => (
                            <option key={key} value={key}>
                                {model.name}
                            </option>
                        ))}
                    </select>
                    {selectedModel && models[selectedModel] && (
                        <p className="model-description">
                            {models[selectedModel].description}
                        </p>
                    )}
                </div>
            </div>

            <div className="sidebar-section">
                <h3>
                    <FaFolder /> Documents ({documents.length})
                </h3>
                <div className="document-list">
                    {documents.map((doc, index) => (
                        <motion.div 
                            key={index}
                            className="document-item"
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: index * 0.1 }}
                        >
                            <FaFile className="doc-icon" />
                            <span className="doc-name">{doc.name}</span>
                            <span className="doc-size">{doc.size}</span>
                        </motion.div>
                    ))}
                    {documents.length === 0 && (
                        <p className="no-docs">No documents uploaded</p>
                    )}
                </div>
            </div>

            <div className="sidebar-section">
                <h3>
                    <FaFolder /> Chapters ({chapters.length})
                </h3>
                <div className="chapter-list">
                    {chapters.map((chapter, index) => (
                        <div key={index} className="chapter-item">
                            📚 {chapter}
                        </div>
                    ))}
                    {chapters.length === 0 && (
                        <p className="no-docs">No chapters detected</p>
                    )}
                </div>
            </div>

            <div className="sidebar-footer">
                <motion.button 
                    className="clear-btn"
                    onClick={handleClearAll}
                    disabled={isLoading || documents.length === 0}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                >
                    <FaTrash /> Clear All Data
                </motion.button>
            </div>
        </div>
    );
};

export default Sidebar; 