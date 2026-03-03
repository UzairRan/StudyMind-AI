"""
StudyMind AI - Main Application
Complete RAG system with local LLM support and cloud fallback
"""

# MUST BE FIRST - Page config before any other Streamlit commands
# MUST BE FIRST - Page config before any other Streamlit commands
import streamlit as st
st.set_page_config(
    page_title="StudyMind AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Rest of imports
import os
import tempfile
import time
from pathlib import Path
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# ============================================================================
# DEFINE ENVIRONMENT DETECTION FIRST (BEFORE MODULE IMPORTS)
# ============================================================================
import sys
IN_STREAMLIT_CLOUD = False

# Multiple detection methods for Streamlit Cloud
if os.path.exists("/.dockerenv"):
    IN_STREAMLIT_CLOUD = True
elif "STREAMLIT_SHARING" in os.environ:
    IN_STREAMLIT_CLOUD = True
elif "STREAMLIT_RUNTIME" in os.environ:
    IN_STREAMLIT_CLOUD = True
elif os.path.exists("/mount/src"):
    IN_STREAMLIT_CLOUD = True
elif "REPLIT" in os.environ:
    IN_STREAMLIT_CLOUD = True
elif os.getenv("STREAMLIT_SERVER_PORT"):
    IN_STREAMLIT_CLOUD = True

# ============================================================================
# NOW IMPORT MODULES (after environment detection)
# ============================================================================
from modules.document_processor import DocumentProcessor

# Conditional import for embeddings (cloud vs local)
if IN_STREAMLIT_CLOUD:
    from modules.embeddings_light import EmbeddingManagerLight as EmbeddingManager
    print("✅ Using lightweight fastembed for cloud")
else:
    from modules.embeddings_local import EmbeddingManager  # Updated name 
    print("✅ Using sentence-transformers for local")

from modules.retriever import Retriever
from modules.quiz_generator import QuizGenerator

# Import appropriate LLM based on environment
if IN_STREAMLIT_CLOUD:
    from modules.tiny_llm import TinyLLM as LLM
    DEFAULT_MODEL = "GPT-2 (124M)"  # ← Change from Phi-1.5 to GPT-2
    os.environ["USE_CLOUD_MODE"] = "true"
    print("✅ Using TinyLLM (GPT-2) for cloud") 
else:
    try:
        from modules.local_llm import LocalLLM as LLM
        DEFAULT_MODEL = "llama3.2:3b"
        print("✅ Using LocalLLM (Llama 3.2) for local")
    except ImportError:
        from modules.tiny_llm import TinyLLM as LLM
        DEFAULT_MODEL = "Phi-1.5 (1.3B)"
        print("⚠️ LocalLLM not available, falling back to TinyLLM")

# Rest of your code continues... 

# Custom CSS with improved colors and layout
st.markdown("""
<style>
    /* Main container */
    .main {
        padding: 0rem 1rem;
    }
    
    /* Header container for logo and title */
    .header-container {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        padding: 1rem 0 0.5rem 0;
        margin-bottom: 0.5rem;
        border-bottom: 1px solid #e2e8f0;
    }
    
    /* Logo styling - larger than title */
    .header-logo {
        height: 90px;
        width: auto;
        margin-right: 0.25rem;
    }
    
    /* Title styling - smaller than logo */
    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6366f1 0%, #14b8a6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        line-height: 1.2;
        letter-spacing: -0.02em;
    }
    
    /* Mode badge in sidebar */
    .mode-badge {
        background: linear-gradient(135deg, #6366f1 0%, #14b8a6 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 2rem;
        text-align: center;
        font-weight: 600;
        margin: 1rem 0;
        font-size: 0.9rem;
    }
    
    /* Cards */
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #6366f1;
        transition: transform 0.2s;
    }
    
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 20px 30px -10px rgba(99,102,241,0.2);
    }
    
    /* Stats card */
    .stats-card {
        background: linear-gradient(135deg, #6366f1 0%, #14b8a6 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.75rem;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }
    
    /* Chat messages */
    .user-message {
        background: #eef2ff;
        padding: 1rem 1.5rem;
        border-radius: 1.5rem 1.5rem 1.5rem 0.5rem;
        margin: 0.75rem 0;
        border-left: 4px solid #6366f1;
        color: #1e293b;
    }
    
    .assistant-message {
        background: #f8fafc;
        padding: 1rem 1.5rem;
        border-radius: 1.5rem 1.5rem 0.5rem 1.5rem;
        margin: 0.75rem 0;
        border-right: 4px solid #14b8a6;
        color: #1e293b;
    }
    
    /* Source citations */
    .source-box {
        background: #fff7ed;
        padding: 0.75rem;
        border-radius: 0.75rem;
        margin: 0.5rem 0;
        font-size: 0.9rem;
        border-left: 4px solid #f97316;
        color: #422006;
    }
    
    /* Buttons */
    .stButton > button {
        width: 100%;
        border-radius: 2rem;
        font-weight: 600;
        transition: all 0.3s;
        background: linear-gradient(135deg, #6366f1 0%, #14b8a6 100%);
        color: white;
        border: none;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px -5px rgba(99,102,241,0.4);
    }
    
    /* Progress bars */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #6366f1, #14b8a6);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8fafc;
    }
    
    /* File uploader */
    .stFileUploader {
        padding: 0.5rem 0;
    }
    
    /* Metrics */
    .stMetric {
        background: white;
        padding: 1rem;
        border-radius: 0.75rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    """Initialize all session state variables"""
    defaults = {
        'processed': False,
        'embedding_manager': None,
        'doc_processor': DocumentProcessor(),
        'retriever': Retriever(),
        'quiz_generator': None,
        'llm': None,
        'chapters': [],
        'chat_history': [],
        'documents_processed': 0,
        'total_chunks': 0,
        'processing_time': 0,
        'current_document_id': None
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# Initialize LLM and generators
if st.session_state.llm is None:
    try:
        st.session_state.llm = LLM()
        st.session_state.quiz_generator = QuizGenerator(st.session_state.llm)
    except Exception as e:
        st.error(f"Failed to initialize LLM: {e}")
        st.session_state.quiz_generator = QuizGenerator()

# ============================================================================
# MAIN HEADER WITH LOGO AND TITLE
# ============================================================================

# Create a single row for header
header_col1, header_col2 = st.columns([1, 5])

with header_col1:
    # Logo - now 90px, larger than title
    try:
        st.image("assets/logo.png", width=90)
    except:
        st.markdown('<div style="font-size: 4rem;">📚</div>', unsafe_allow_html=True)

with header_col2:
    # Title - immediately after logo, smaller than logo
    st.markdown('<div class="header-title">StudyMind AI</div>', unsafe_allow_html=True)

# No separator line - removed completely

# Sidebar
with st.sidebar:
    # Mode badge with model info
    if IN_STREAMLIT_CLOUD:
        st.markdown('<div class="mode-badge">☁️ Cloud Mode (Phi-1.5)</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="mode-badge">💻 Local Mode (Llama 3.2)</div>', unsafe_allow_html=True)
    
    # File upload section - no extra line
    st.markdown("### Upload Notes")
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=['pdf'],
        accept_multiple_files=True,
        help="Upload your course notes (PDF format)"
    )
    
    if uploaded_files:
        st.markdown(f"**Selected:** {len(uploaded_files)} files")
        
        # Process button
        if st.button("Process Notes", type="primary", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            start_time = time.time()
            all_documents = []
            
            # Get the processor from session state (outside thread)
            doc_processor = st.session_state.doc_processor
            
            # Process files in parallel
            def process_single_file(uploaded_file, processor):
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                docs = processor.process_pdf(
                    tmp_path, 
                    source_file=uploaded_file.name
                )
                os.unlink(tmp_path)
                return docs
            
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = {executor.submit(process_single_file, file, doc_processor): file for file in uploaded_files}
                
                for i, future in enumerate(as_completed(futures)):
                    docs = future.result()
                    all_documents.extend(docs)
                    progress_bar.progress((i + 1) / len(uploaded_files))
                    status_text.text(f"Processed {i + 1}/{len(uploaded_files)} files...")
            
            if all_documents:
                chunks = [doc.page_content for doc in all_documents]
                metadatas = [doc.metadata for doc in all_documents]
                
                status_text.text("Creating embeddings...")
                st.session_state.embedding_manager = EmbeddingManager()
                st.session_state.embedding_manager.create_embeddings(chunks, metadatas)
                
                st.session_state.processed = True
                st.session_state.documents_processed = len(uploaded_files)
                st.session_state.total_chunks = len(chunks)
                st.session_state.processing_time = time.time() - start_time
                
                chapters = set()
                for meta in metadatas:
                    chapter = meta.get('chapter', 'General')
                    chapters.add(chapter)
                st.session_state.chapters = sorted(list(chapters))
                
                status_text.text("Processing complete!")
                time.sleep(1)
                st.rerun()
    
    # Statistics section
    if st.session_state.processed:
        with st.expander("Statistics", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Documents", st.session_state.documents_processed)
            with col2:
                st.metric("Chunks", st.session_state.total_chunks)
            
            st.metric("Chapters", len(st.session_state.chapters))
            
            if st.session_state.processing_time > 0:
                st.metric("Processing Time", f"{st.session_state.processing_time:.1f}s")
        
        # Clear button
        if st.button("Clear All Data", use_container_width=True):
            st.session_state.processed = False
            st.session_state.embedding_manager = None
            st.session_state.chapters = []
            st.session_state.chat_history = []
            st.session_state.documents_processed = 0
            st.session_state.total_chunks = 0
            st.rerun()
    
    # Model info
    if hasattr(st.session_state.llm, 'model_name'):
        with st.expander("Model Info", expanded=False):
            model_display = "Cloud (Phi-1.5)" if IN_STREAMLIT_CLOUD else f"Local ({st.session_state.llm.model_name})"
            st.info(f"**Model:** {model_display}")

# Main content area
if not st.session_state.processed:
    # Welcome screen - Step cards directly below header
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>Step 1: Upload</h3>
            <p>Upload your PDF notes. Support multiple files at once.</p>
            <ul style="color: #475569;">
                <li>PDF format only</li>
                <li>Any file size</li>
                <li>Auto-detects chapters</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>Step 2: Ask</h3>
            <p>Ask questions naturally. AI finds relevant information.</p>
            <ul style="color: #475569;">
                <li>Natural language</li>
                <li>Filter by chapter</li>
                <li>See source citations</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>Step 3: Learn</h3>
            <p>Generate quizzes to test your understanding.</p>
            <ul style="color: #475569;">
                <li>Multiple choice quizzes</li>
                <li>Chapter-specific content</li>
                <li>Download options</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

else:
    # Main tabs (3 tabs)
    tab1, tab2, tab3 = st.tabs([
        "Chat with Notes", 
        "Generate Quiz", 
        "Browse Chapters"
    ])
    
    with tab1:
        st.markdown("### Ask Questions About Your Notes")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            chapter_filter = st.selectbox(
                "Filter by Chapter:",
                ["All Chapters"] + st.session_state.chapters,
                key="chat_chapter_filter"
            )
        
        with col2:
            num_results = st.slider(
                "Results:",
                min_value=3,
                max_value=10,
                value=5
            )
        
        # Chat history
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f'<div class="user-message">User: {message["content"]}</div>', 
                          unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="assistant-message">AI: {message["content"]}</div>', 
                          unsafe_allow_html=True)
                
                if "sources" in message and message["sources"]:
                    with st.expander("View Sources", expanded=False):
                        for i, source in enumerate(message["sources"], 1):
                            st.markdown(f"""
                            <div class="source-box">
                                <strong>Source {i}:</strong> {source['source']} (Page {source['page']})<br>
                                <strong>Chapter:</strong> {source['chapter']}<br>
                                <strong>Excerpt:</strong> {source['content'][:150]}...
                            </div>
                            """, unsafe_allow_html=True)
        
        # Query input
        query = st.chat_input("Ask a question about your notes...")
        
        if query:
            st.session_state.chat_history.append({
                "role": "user",
                "content": query
            })
            
            with st.spinner("Searching and generating answer..."):
                filter_value = None if chapter_filter == "All Chapters" else chapter_filter
                
                chunks, metadatas = st.session_state.retriever.search(
                    st.session_state.embedding_manager,
                    query,
                    filter_value,
                    k=num_results
                )
                
                if chunks:
                    answer = st.session_state.llm.generate_response(query, chunks)
                    
                    sources = []
                    for chunk, meta in zip(chunks, metadatas):
                        sources.append({
                            "source": meta.get('source', 'Unknown'),
                            "page": meta.get('page', 'N/A'),
                            "chapter": meta.get('chapter', 'General'),
                            "content": chunk
                        })
                    
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })
                else:
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": "No relevant information found. Try a different question or upload more documents."
                    })
            
            st.rerun()
    
    with tab2:
        st.markdown("### Generate Quiz Questions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            quiz_chapter = st.selectbox(
                "Select Chapter:",
                st.session_state.chapters,
                key="quiz_chapter_select"
            )
        
        with col2:
            num_questions = st.slider(
                "Number of Questions:",
                min_value=3,
                max_value=10,
                value=5,
                key="quiz_num"
            )
        
        if st.button("Generate Quiz", type="primary", use_container_width=True):
            with st.spinner("Creating your quiz..."):
                all_chunks = st.session_state.embedding_manager.get_all_chunks()
                chapter_chunks = [
                    chunk for chunk, meta in zip(all_chunks['texts'], all_chunks['metadatas'])
                    if meta.get('chapter', '').lower() == quiz_chapter.lower()
                ]
                
                if chapter_chunks:
                    quiz = st.session_state.quiz_generator.generate_quiz(
                        chunks=chapter_chunks,
                        num_questions=num_questions,
                        chapter=quiz_chapter,
                        use_llm=True
                    )
                    
                    st.markdown("### Your Quiz")
                    st.markdown(quiz['questions'])
                    
                    st.download_button(
                        "Download Quiz",
                        quiz['questions'],
                        file_name=f"quiz_{quiz_chapter}_{datetime.now().strftime('%Y%m%d')}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                else:
                    st.warning("No content found for this chapter.")
    
    with tab3:
        st.markdown("### Browse Chapter Contents")
        
        selected_chapter = st.selectbox(
            "Select Chapter to Explore:",
            st.session_state.chapters,
            key="browse_chapter"
        )
        
        if selected_chapter:
            all_chunks = st.session_state.embedding_manager.get_all_chunks()
            
            chapter_data = []
            for chunk, meta in zip(all_chunks['texts'], all_chunks['metadatas']):
                if meta.get('chapter', '').lower() == selected_chapter.lower():
                    chapter_data.append({
                        'content': chunk,
                        'source': meta.get('source', 'Unknown'),
                        'page': meta.get('page', 'N/A')
                    })
            
            st.markdown(f"**Found {len(chapter_data)} sections**")
            
            for i, item in enumerate(chapter_data[:15]):
                with st.expander(f"{item['source']} - Page {item['page']}"):
                    st.write(item['content']) 