import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { FaCloudUploadAlt, FaFilePdf, FaCheckCircle } from 'react-icons/fa';
import { motion, AnimatePresence } from 'framer-motion';
import { uploadPDFs } from '../services/api';
import { toast } from 'react-hot-toast';

const Upload = ({ documents, setDocuments, setChapters, setIsLoading }) => {
    const onDrop = useCallback(async (acceptedFiles) => {
        if (acceptedFiles.length === 0) return;

        setIsLoading(true);
        const loadingToast = toast.loading('Uploading and processing PDFs...');

        try {
            const result = await uploadPDFs(acceptedFiles);
            
            // Add to documents list
            const newDocs = acceptedFiles.map(file => ({
                name: file.name,
                size: formatFileSize(file.size),
                status: 'processed'
            }));
            
            setDocuments(prev => [...prev, ...newDocs]);
            setChapters(result.chapters);
            
            toast.success(`Successfully processed ${acceptedFiles.length} PDFs`, {
                id: loadingToast
            });
        } catch (error) {
            toast.error('Failed to upload PDFs. Please try again.', {
                id: loadingToast
            });
            console.error('Upload error:', error);
        } finally {
            setIsLoading(false);
        }
    }, [setDocuments, setChapters, setIsLoading]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'application/pdf': ['.pdf']
        },
        maxSize: 200 * 1024 * 1024, // 200MB
    });

    const formatFileSize = (bytes) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    return (
        <div className="upload-container">
            <motion.div 
                className="upload-header"
                initial={{ y: -20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
            >
                <h2>Upload Your Study Notes</h2>
                <p>Upload PDFs of your course materials. Our AI will process them for instant Q&A.</p>
            </motion.div>

            <motion.div
                className={`dropzone ${isDragActive ? 'active' : ''}`}
                {...getRootProps()}
                initial={{ scale: 0.95, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.2 }}
                whileHover={{ scale: 1.02 }}
            >
                <input {...getInputProps()} />
                <FaCloudUploadAlt className="upload-icon" />
                {isDragActive ? (
                    <p>Drop your PDFs here...</p>
                ) : (
                    <>
                        <p>Drag & drop PDFs here, or click to select</p>
                        <span className="file-limit">Maximum file size: 200MB</span>
                    </>
                )}
            </motion.div>

            <AnimatePresence>
                {documents.length > 0 && (
                    <motion.div 
                        className="uploaded-files"
                        initial={{ y: 20, opacity: 0 }}
                        animate={{ y: 0, opacity: 1 }}
                        exit={{ y: 20, opacity: 0 }}
                    >
                        <h3>Uploaded Files</h3>
                        <div className="file-list">
                            {documents.map((doc, index) => (
                                <motion.div 
                                    key={index}
                                    className="file-item"
                                    initial={{ x: -20, opacity: 0 }}
                                    animate={{ x: 0, opacity: 1 }}
                                    transition={{ delay: index * 0.1 }}
                                >
                                    <FaFilePdf className="file-icon" />
                                    <span className="file-name">{doc.name}</span>
                                    <span className="file-size">{doc.size}</span>
                                    <FaCheckCircle className="file-status" />
                                </motion.div>
                            ))}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default Upload; 