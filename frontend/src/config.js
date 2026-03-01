// API Configuration
const config = {
    // Development API URL
    DEV_API_URL: 'http://localhost:8000',
    
    // Production API URL (Render)
    PROD_API_URL: 'https://studymind-api.onrender.com',
    
    // Get current API URL based on environment
    get API_URL() {
        return process.env.NODE_ENV === 'production' 
            ? this.PROD_API_URL 
            : this.DEV_API_URL;
    }
};

export default config; 