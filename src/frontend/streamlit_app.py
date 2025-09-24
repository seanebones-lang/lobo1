"""
Modern Streamlit frontend for the RAG system.
"""

import streamlit as st
import requests
import json
import time
from typing import Dict, Any, List, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# Configure page
st.set_page_config(
    page_title="🤖 Advanced RAG System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .source-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 20%;
    }
    
    .assistant-message {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        margin-right: 20%;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

class RAGClient:
    """Client for interacting with the RAG API."""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
    
    def query(self, question: str, **kwargs) -> Dict[str, Any]:
        """Send a query to the RAG system."""
        try:
            response = requests.post(
                f"{self.base_url}/query",
                json={"question": question, **kwargs},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to API: {e}")
            return None
    
    def get_health(self) -> Dict[str, Any]:
        """Get system health status."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        try:
            response = requests.get(f"{self.base_url}/stats", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None
    
    def get_models(self) -> Dict[str, Any]:
        """Get available models."""
        try:
            response = requests.get(f"{self.base_url}/models", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None

# Initialize client
@st.cache_resource
def get_rag_client():
    return RAGClient()

def main():
    """Main application."""
    client = get_rag_client()
    
    # Header
    st.markdown('<h1 class="main-header">🤖 Advanced RAG System</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Configuration
        st.subheader("API Settings")
        api_url = st.text_input("API URL", value=API_BASE_URL, help="Base URL for the RAG API")
        
        # Query Configuration
        st.subheader("Query Settings")
        prompt_type = st.selectbox(
            "Prompt Type",
            ["qa", "summarization", "analysis", "conversation", "code_explanation", "creative_writing"],
            help="Type of prompt to use for generation"
        )
        
        system_role = st.selectbox(
            "System Role",
            ["assistant", "expert", "analyst", "creative", "teacher"],
            help="Role for the AI assistant"
        )
        
        top_k = st.slider("Documents to Retrieve", 1, 20, 5, help="Number of documents to retrieve")
        rerank_top_k = st.slider("Documents after Reranking", 1, 10, 3, help="Number of documents to use after reranking")
        
        temperature = st.slider("Temperature", 0.0, 2.0, 0.1, 0.1, help="Creativity level (0=deterministic, 2=very creative)")
        max_tokens = st.slider("Max Tokens", 100, 4000, 1000, help="Maximum tokens to generate")
        
        include_sources = st.checkbox("Include Sources", value=True, help="Show source documents")
        
        # System Status
        st.subheader("System Status")
        health = client.get_health()
        if health:
            status_color = "🟢" if health["status"] == "healthy" else "🔴"
            st.write(f"{status_color} Status: {health['status']}")
            st.write(f"📊 Version: {health['version']}")
        else:
            st.error("❌ Cannot connect to API")
    
    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat", "📊 Analytics", "📁 Documents", "🔧 Settings"])
    
    with tab1:
        chat_interface(client, prompt_type, system_role, top_k, rerank_top_k, temperature, max_tokens, include_sources)
    
    with tab2:
        analytics_interface(client)
    
    with tab3:
        documents_interface(client)
    
    with tab4:
        settings_interface(client)

def chat_interface(client, prompt_type, system_role, top_k, rerank_top_k, temperature, max_tokens, include_sources):
    """Chat interface."""
    st.header("💬 Chat with RAG System")
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    
    # Chat input
    with st.form("chat_form"):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_input = st.text_input(
                "Ask a question:",
                placeholder="Type your question here...",
                key="user_input"
            )
        
        with col2:
            submit_button = st.form_submit_button("Send", use_container_width=True)
    
    # Process query
    if submit_button and user_input:
        with st.spinner("🤔 Thinking..."):
            # Add user message to history
            st.session_state.messages.append({
                "role": "user",
                "content": user_input,
                "timestamp": datetime.now()
            })
            
            # Query the RAG system
            response = client.query(
                question=user_input,
                prompt_type=prompt_type,
                system_role=system_role,
                top_k=top_k,
                rerank_top_k=rerank_top_k,
                temperature=temperature,
                max_tokens=max_tokens,
                include_sources=include_sources
            )
            
            if response:
                # Add assistant response to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response["answer"],
                    "sources": response.get("sources", []),
                    "confidence": response.get("confidence", 0.0),
                    "processing_time": response.get("total_time", 0.0),
                    "timestamp": datetime.now()
                })
                
                # Update conversation history for context
                st.session_state.conversation_history.append({
                    "human": user_input,
                    "assistant": response["answer"]
                })
    
    # Display chat history
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="chat-message user-message">{message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message assistant-message">{message["content"]}</div>', unsafe_allow_html=True)
            
            # Show metadata
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Confidence", f"{message.get('confidence', 0):.2f}")
            with col2:
                st.metric("Processing Time", f"{message.get('processing_time', 0):.2f}s")
            with col3:
                st.metric("Sources", len(message.get('sources', [])))
            
            # Show sources if available
            if message.get("sources") and include_sources:
                with st.expander("📚 Sources"):
                    for i, source in enumerate(message["sources"], 1):
                        st.markdown(f"""
                        <div class="source-card">
                            <strong>Source {i}</strong><br>
                            <small>Score: {source.get('score', 0):.3f}</small><br>
                            {source.get('text', '')[:200]}...
                        </div>
                        """, unsafe_allow_html=True)
    
    # Clear chat button
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.conversation_history = []
        st.rerun()

def analytics_interface(client):
    """Analytics and monitoring interface."""
    st.header("📊 System Analytics")
    
    # Get system stats
    stats = client.get_stats()
    if not stats:
        st.error("Cannot retrieve system statistics")
        return
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Uptime", f"{stats.get('uptime', 0):.1f}s")
    
    with col2:
        llm_models = len(stats.get('llm_stats', {}).get('available_models', []))
        st.metric("Available Models", llm_models)
    
    with col3:
        cache_size = stats.get('embedding_stats', {}).get('cache_size', 0)
        st.metric("Embedding Cache", cache_size)
    
    with col4:
        total_docs = stats.get('retriever_stats', {}).get('total_documents', 0)
        st.metric("Total Documents", total_docs)
    
    # Detailed statistics
    st.subheader("Detailed Statistics")
    
    # LLM Statistics
    if 'llm_stats' in stats:
        st.subheader("LLM Statistics")
        llm_data = stats['llm_stats']
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Available Models:**")
            for model in llm_data.get('available_models', []):
                st.write(f"- {model}")
        
        with col2:
            st.write("**Model Information:**")
            st.json(llm_data)
    
    # Embedding Statistics
    if 'embedding_stats' in stats:
        st.subheader("Embedding Statistics")
        embedding_data = stats['embedding_stats']
        
        # Create a simple chart
        fig = go.Figure(data=go.Bar(
            x=['Cache Size', 'Max Cache Size'],
            y=[embedding_data.get('cache_size', 0), embedding_data.get('max_cache_size', 1000)],
            marker_color=['#667eea', '#764ba2']
        ))
        fig.update_layout(title="Embedding Cache Usage", height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Retriever Statistics
    if 'retriever_stats' in stats:
        st.subheader("Retriever Statistics")
        retriever_data = stats['retriever_stats']
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Documents", retriever_data.get('total_documents', 0))
        with col2:
            st.metric("Vector Weight", f"{retriever_data.get('alpha', 0):.2f}")
        with col3:
            st.metric("BM25 Weight", f"{retriever_data.get('bm25_weight', 0):.2f}")

def documents_interface(client):
    """Document management interface."""
    st.header("📁 Document Management")
    
    # Upload section
    st.subheader("Upload Documents")
    
    uploaded_files = st.file_uploader(
        "Choose files to upload",
        accept_multiple_files=True,
        type=['pdf', 'txt', 'docx'],
        help="Upload PDF, TXT, or DOCX files to add to the knowledge base"
    )
    
    if uploaded_files:
        st.write(f"Selected {len(uploaded_files)} files")
        
        # Processing options
        col1, col2, col3 = st.columns(3)
        with col1:
            chunk_method = st.selectbox("Chunking Method", ["recursive", "semantic"])
        with col2:
            chunk_size = st.number_input("Chunk Size", 100, 2000, 1000)
        with col3:
            chunk_overlap = st.number_input("Chunk Overlap", 0, 500, 200)
        
        if st.button("📤 Process and Upload Documents"):
            with st.spinner("Processing documents..."):
                # Save uploaded files temporarily
                file_paths = []
                for uploaded_file in uploaded_files:
                    file_path = f"temp_{uploaded_file.name}"
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    file_paths.append(file_path)
                
                # Upload to API
                try:
                    response = requests.post(
                        f"{client.base_url}/documents/upload",
                        json={
                            "file_paths": file_paths,
                            "chunk_method": chunk_method,
                            "chunk_size": chunk_size,
                            "chunk_overlap": chunk_overlap
                        },
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result["success"]:
                            st.success(f"✅ Successfully processed {result['documents_processed']} documents into {result['chunks_created']} chunks")
                        else:
                            st.error(f"❌ Upload failed: {result.get('error', 'Unknown error')}")
                    else:
                        st.error(f"❌ Upload failed with status {response.status_code}")
                
                except Exception as e:
                    st.error(f"❌ Error uploading documents: {e}")
                
                finally:
                    # Clean up temporary files
                    for file_path in file_paths:
                        if os.path.exists(file_path):
                            os.remove(file_path)
    
    # Document statistics
    st.subheader("Document Statistics")
    stats = client.get_stats()
    if stats and 'retriever_stats' in stats:
        retriever_data = stats['retriever_stats']
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Documents", retriever_data.get('total_documents', 0))
        with col2:
            st.metric("Vector Store Type", retriever_data.get('vector_store_type', 'Unknown'))

def settings_interface(client):
    """Settings and configuration interface."""
    st.header("🔧 System Settings")
    
    # API Configuration
    st.subheader("API Configuration")
    
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("API Base URL", value=API_BASE_URL, disabled=True)
    with col2:
        if st.button("🔄 Refresh Connection"):
            st.rerun()
    
    # Model Information
    st.subheader("Available Models")
    models = client.get_models()
    if models:
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**LLM Models:**")
            for model in models.get('llm_models', []):
                st.write(f"- {model}")
        
        with col2:
            st.write("**Embedding Model:**")
            st.write(f"- {models.get('embedding_model', 'Unknown')}")
        
        st.write("**Prompt Types:**")
        for prompt_type in models.get('prompt_types', []):
            st.write(f"- {prompt_type}")
    else:
        st.error("Cannot retrieve model information")
    
    # System Health
    st.subheader("System Health")
    health = client.get_health()
    if health:
        st.write(f"**Status:** {health['status']}")
        st.write(f"**Version:** {health['version']}")
        st.write(f"**Timestamp:** {health['timestamp']}")
        
        if 'components' in health:
            st.write("**Component Status:**")
            for component, status in health['components'].items():
                status_icon = "🟢" if status == "healthy" else "🔴"
                st.write(f"{status_icon} {component}: {status}")
    else:
        st.error("Cannot retrieve system health")

if __name__ == "__main__":
    main()

