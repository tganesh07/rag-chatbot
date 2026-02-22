import streamlit as st
import os
import sys
import threading
import time

# Add the project root to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.settings import settings
# Initialize backend components
# We import them here so they initialize when the app starts
from app.core.rag import rag_pipeline
from app.watcher import file_watcher

st.set_page_config(
    page_title="Local RAG Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📄 Local RAG Chat")

# --- Sidebar ---
with st.sidebar:
    st.header("Configuration")
    st.info(f"**Provider**: {settings.LLM_PROVIDER.upper()}")
    st.info(f"**Model**: {settings.LLM_MODEL}")
    st.success(f"**Watching**: `{settings.DATA_PATH}`")
    
    # Config Validation
    valid, msg = settings.validate()
    if not valid:
        st.error(f"Config Error: {msg}")
        st.stop()

    st.divider()
    st.subheader("System Status")
    
    # Start File Watcher
    # We use session state to track if we've attempted to start it to avoid spamming start calls
    # although the watcher class handles idempotency mostly.
    if "watcher_running" not in st.session_state:
        try:
            # Check if already running (global instance might create issues with hot reload, 
            # ideally we'd use st.cache_resource for the singleton)
            if not file_watcher.observer.is_alive():
                file_watcher.index_initial_files()
                file_watcher.start()
            st.session_state.watcher_running = True
            st.toast("File Watcher Started & Files Indexed", icon="👀")
        except Exception as e:
            st.error(f"Watcher failed: {e}")

    if st.session_state.get("watcher_running"):
        st.caption("✅ File Watcher Active")
    else:
        st.caption("❌ File Watcher Stopped")

# --- Main Chat UI ---

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask a question about your documents..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            with st.spinner("Thinking..."):
                if rag_pipeline:
                    response = rag_pipeline.query(prompt)
                    full_response = response
                else:
                    full_response = "Error: RAG Pipeline is not initialized. Check logs."
            
            message_placeholder.markdown(full_response)
        except Exception as e:
            full_response = f"Error generating response: {str(e)}"
            message_placeholder.error(full_response)
            
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
