"""
Insyte AI - Streamlit Dashboard
Main dashboard for productivity tracking and AI interaction.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ai.llm_manager import LLMManager
from ai.voice_manager import VoiceManager
from ai.search_manager import SearchManager
from data.data_manager import DataManager
from data.data_loader import DataLoader

# Configure Streamlit page
st.set_page_config(
    page_title="Insyte AI - Productivity Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataManager()
    st.session_state.data_manager.initialize_database()

if 'llm_manager' not in st.session_state:
    st.session_state.llm_manager = LLMManager()

if 'search_manager' not in st.session_state:
    st.session_state.search_manager = SearchManager()

if 'voice_manager' not in st.session_state:
    st.session_state.voice_manager = VoiceManager()

if 'session_id' not in st.session_state:
    st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def main():
    """Main dashboard application."""
    
    # Sidebar navigation
    st.sidebar.title("🧠 Insyte AI")
    st.sidebar.markdown("*Your Offline Productivity Assistant*")
    
    page = st.sidebar.selectbox(
        "Navigate to:",
        ["🏠 Dashboard", "💬 AI Chat", "📊 Analytics", "🔍 Search", "🎤 Voice", "⚙️ Settings"]
    )
    
    # System status
    with st.sidebar.expander("🔧 System Status"):
        show_system_status()
    
    # Main content area
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "💬 AI Chat":
        show_chat_interface()
    elif page == "📊 Analytics":
        show_analytics()
    elif page == "🔍 Search":
        show_search_interface()
    elif page == "🎤 Voice":
        show_voice_interface()
    elif page == "⚙️ Settings":
        show_settings()

def show_system_status():
    """Display system component status."""
    
    # LLM Status
    llm_info = st.session_state.llm_manager.get_model_info()
    if llm_info['status'] == 'loaded':
        st.success("✅ LLM Ready")
    else:
        st.error("❌ LLM Not Loaded")
    
    # Search Index Status
    search_info = st.session_state.search_manager.get_index_info()
    if search_info['status'] == 'loaded':
        st.success(f"✅ Search Index ({search_info['total_documents']} docs)")
    else:
        st.warning("⚠️ Search Index Not Loaded")
    
    # Voice Status
    voice_info = st.session_state.voice_manager.get_model_info()
    if voice_info['status'] == 'loaded':
        st.success("✅ Voice Recognition Ready")
    else:
        st.warning("⚠️ Voice Not Loaded")
    
    # Database Status
    db_stats = st.session_state.data_manager.get_database_stats()
    if db_stats:
        st.success(f"✅ Database ({db_stats.get('conversations_count', 0)} conversations)")
    else:
        st.error("❌ Database Error")

def show_dashboard():
    """Main dashboard overview."""
    
    st.title("🏠 Insyte AI Dashboard")
    st.markdown("Welcome to your personal productivity assistant!")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        conversations = st.session_state.data_manager.get_conversations(limit=1000)
        st.metric("Total Conversations", len(conversations))
    
    with col2:
        documents = st.session_state.data_manager.get_documents(limit=1000)
        st.metric("Documents Stored", len(documents))
    
    with col3:
        # Get recent productivity metrics
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        metrics = st.session_state.data_manager.get_productivity_metrics(start_date, end_date)
        st.metric("This Week's Metrics", len(metrics))
    
    with col4:
        search_info = st.session_state.search_manager.get_index_info()
        indexed_docs = search_info.get('total_documents', 0) if search_info['status'] == 'loaded' else 0
        st.metric("Indexed Documents", indexed_docs)
    
    # Recent activity
    st.subheader("📝 Recent Activity")
    
    tab1, tab2, tab3 = st.tabs(["Conversations", "Documents", "Metrics"])
    
    with tab1:
        recent_conversations = st.session_state.data_manager.get_conversations(limit=5)
        if recent_conversations:
            for conv in recent_conversations:
                with st.expander(f"💬 {conv['timestamp']} - {conv['user_input'][:50]}..."):
                    st.write(f"**You:** {conv['user_input']}")
                    st.write(f"**AI:** {conv['ai_response']}")
        else:
            st.info("No conversations yet. Start chatting with the AI!")
    
    with tab2:
        recent_docs = st.session_state.data_manager.get_documents(limit=5)
        if recent_docs:
            for doc in recent_docs:
                with st.expander(f"📄 {doc['title']}"):
                    st.write(f"**Type:** {doc['doc_type']}")
                    st.write(f"**Content:** {doc['content'][:200]}...")
                    if doc['tags']:
                        st.write(f"**Tags:** {', '.join(doc['tags'])}")
        else:
            st.info("No documents stored yet.")
    
    with tab3:
        if metrics:
            df = pd.DataFrame(metrics)
            if not df.empty:
                fig = px.line(df, x='date', y='metric_value', color='metric_type',
                             title="Recent Productivity Metrics")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No productivity metrics recorded yet.")

def show_chat_interface():
    """AI chat interface."""
    
    st.title("💬 AI Chat Assistant")
    
    # Check if LLM is loaded
    llm_info = st.session_state.llm_manager.get_model_info()
    if llm_info['status'] != 'loaded':
        st.warning("⚠️ LLM not loaded. Please load the model in Settings first.")
        return
    
    # Chat history
    conversations = st.session_state.data_manager.get_conversations(
        session_id=st.session_state.session_id, 
        limit=50
    )
    
    # Display chat history
    for conv in reversed(conversations):
        with st.chat_message("user"):
            st.write(conv['user_input'])
        with st.chat_message("assistant"):
            st.write(conv['ai_response'])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about productivity..."):
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.llm_manager.generate_response(prompt)
                    st.write(response)
                    
                    # Save conversation
                    st.session_state.data_manager.save_conversation(
                        st.session_state.session_id, prompt, response
                    )
                    
                except Exception as e:
                    st.error(f"Error generating response: {str(e)}")

def show_analytics():
    """Analytics and productivity metrics."""
    
    st.title("📊 Productivity Analytics")
    
    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input("End Date", datetime.now())
    
    # Get metrics
    metrics = st.session_state.data_manager.get_productivity_metrics(
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d')
    )
    
    if not metrics:
        st.info("No productivity metrics found for the selected date range.")
        
        # Add sample metrics button
        if st.button("Add Sample Metrics"):
            sample_metrics = [
                ("tasks_completed", 8, "Completed daily tasks"),
                ("focus_time", 4.5, "Hours of focused work"),
                ("meetings", 3, "Number of meetings attended"),
                ("break_time", 1.2, "Hours of break time")
            ]
            
            for metric_type, value, description in sample_metrics:
                st.session_state.data_manager.save_productivity_metric(
                    datetime.now().strftime('%Y-%m-%d'),
                    metric_type, value, description
                )
            
            st.success("Sample metrics added! Refresh to view.")
            st.experimental_rerun()
        
        return
    
    # Create DataFrame
    df = pd.DataFrame(metrics)
    
    # Metrics overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_metrics = len(metrics)
        st.metric("Total Metrics", total_metrics)
    
    with col2:
        unique_types = df['metric_type'].nunique()
        st.metric("Metric Types", unique_types)
    
    with col3:
        date_range = (pd.to_datetime(df['date']).max() - pd.to_datetime(df['date']).min()).days
        st.metric("Date Range (days)", date_range)
    
    # Visualizations
    st.subheader("📈 Metrics Over Time")
    
    # Line chart by metric type
    fig = px.line(df, x='date', y='metric_value', color='metric_type',
                  title="Productivity Metrics Trend")
    st.plotly_chart(fig, use_container_width=True)
    
    # Bar chart of average values by type
    avg_by_type = df.groupby('metric_type')['metric_value'].mean().reset_index()
    fig2 = px.bar(avg_by_type, x='metric_type', y='metric_value',
                  title="Average Metric Values by Type")
    st.plotly_chart(fig2, use_container_width=True)
    
    # Detailed metrics table
    st.subheader("📋 Detailed Metrics")
    st.dataframe(df[['date', 'metric_type', 'metric_value', 'description']], use_container_width=True)

def show_search_interface():
    """Semantic search interface."""
    
    st.title("🔍 Semantic Search")
    
    # Check if search index is loaded
    search_info = st.session_state.search_manager.get_index_info()
    if search_info['status'] != 'loaded':
        st.warning("⚠️ Search index not loaded. Please initialize in Settings first.")
        return
    
    st.info(f"Search index contains {search_info['total_documents']} documents")
    
    # Search interface
    query = st.text_input("🔍 Search your knowledge base:", placeholder="Enter your search query...")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        max_results = st.slider("Max Results", 1, 20, 5)
    with col2:
        min_score = st.slider("Minimum Similarity Score", 0.0, 1.0, 0.3, 0.1)
    
    if query:
        with st.spinner("Searching..."):
            try:
                results = st.session_state.search_manager.search(
                    query, k=max_results, threshold=min_score
                )
                
                if results:
                    st.success(f"Found {len(results)} relevant documents")
                    
                    for i, result in enumerate(results, 1):
                        with st.expander(f"Result {i} - Score: {result['score']:.3f}"):
                            st.write(result['document'])
                            
                            if result['metadata']:
                                st.json(result['metadata'])
                else:
                    st.info("No results found. Try a different query or lower the similarity threshold.")
                    
            except Exception as e:
                st.error(f"Search error: {str(e)}")

def show_voice_interface():
    """Voice transcription interface."""
    
    st.title("🎤 Voice Assistant")
    
    # Check if voice model is loaded
    voice_info = st.session_state.voice_manager.get_model_info()
    if voice_info['status'] != 'loaded':
        st.warning("⚠️ Voice model not loaded. Please load in Settings first.")
        return
    
    st.info("Voice recognition is ready!")
    
    # File upload for audio transcription
    st.subheader("📁 Upload Audio File")
    uploaded_file = st.file_uploader(
        "Choose an audio file",
        type=['wav', 'mp3', 'm4a', 'flac', 'ogg']
    )
    
    if uploaded_file is not None:
        # Save uploaded file temporarily
        temp_path = f"temp_audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        if st.button("🎤 Transcribe Audio"):
            with st.spinner("Transcribing audio..."):
                try:
                    result = st.session_state.voice_manager.transcribe_audio(temp_path)
                    
                    if result['text']:
                        st.success("Transcription completed!")
                        
                        # Display results
                        st.subheader("📝 Transcription")
                        st.write(result['text'])
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Language", result['language'])
                        with col2:
                            st.metric("Confidence", f"{result['confidence']:.2%}")
                        with col3:
                            st.metric("Duration", f"{result.get('duration', 0):.1f}s")
                        
                        # Save transcription
                        st.session_state.data_manager.save_voice_session(
                            result['text'],
                            result['confidence'],
                            result.get('duration'),
                            result['language']
                        )
                        
                        # Option to chat with AI about transcription
                        if st.button("💬 Discuss with AI"):
                            st.session_state.temp_voice_text = result['text']
                            st.experimental_rerun()
                    
                    else:
                        st.error("Transcription failed or no speech detected.")
                        
                except Exception as e:
                    st.error(f"Transcription error: {str(e)}")
                
                finally:
                    # Clean up temporary file
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
    
    # Display recent transcriptions
    st.subheader("📜 Recent Transcriptions")
    # This would require a method to get voice sessions from data_manager
    st.info("Recent transcriptions feature coming soon!")

def show_settings():
    """System settings and configuration."""
    
    st.title("⚙️ Settings")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🤖 AI Models", "🔍 Search Index", "📊 Data", "🔧 System"])
    
    with tab1:
        st.subheader("🤖 AI Model Management")
        
        # LLM Settings
        st.write("**Language Model**")
        llm_info = st.session_state.llm_manager.get_model_info()
        
        if llm_info['status'] == 'loaded':
            st.success(f"✅ Model loaded: {llm_info['model_name']}")
            st.write(f"Parameters: {llm_info.get('parameters', 'Unknown'):,}")
            st.write(f"Device: {llm_info['device']}")
            
            if st.button("🔄 Reload Model"):
                with st.spinner("Reloading model..."):
                    success = st.session_state.llm_manager.load_model()
                    if success:
                        st.success("Model reloaded successfully!")
                    else:
                        st.error("Failed to reload model.")
        else:
            if st.button("📥 Load LLM Model"):
                with st.spinner("Loading model... This may take a few minutes."):
                    success = st.session_state.llm_manager.load_model()
                    if success:
                        st.success("Model loaded successfully!")
                        st.experimental_rerun()
                    else:
                        st.error("Failed to load model. Check logs for details.")
        
        st.divider()
        
        # Voice Model Settings
        st.write("**Voice Recognition Model**")
        voice_info = st.session_state.voice_manager.get_model_info()
        
        if voice_info['status'] == 'loaded':
            st.success(f"✅ Whisper model loaded: {voice_info['model_size']}")
        else:
            model_size = st.selectbox("Whisper Model Size", 
                                    ['tiny', 'base', 'small', 'medium', 'large'])
            
            if st.button("📥 Load Voice Model"):
                with st.spinner("Loading Whisper model..."):
                    st.session_state.voice_manager.model_size = model_size
                    success = st.session_state.voice_manager.load_model()
                    if success:
                        st.success("Voice model loaded successfully!")
                        st.experimental_rerun()
                    else:
                        st.error("Failed to load voice model.")
    
    with tab2:
        st.subheader("🔍 Search Index Management")
        
        search_info = st.session_state.search_manager.get_index_info()
        
        if search_info['status'] == 'loaded':
            st.success(f"✅ Search index loaded with {search_info['total_documents']} documents")
            
            if st.button("🗑️ Clear Index"):
                if st.session_state.search_manager.clear_index():
                    st.success("Index cleared successfully!")
                    st.experimental_rerun()
        else:
            st.warning("⚠️ Search index not initialized.")
            
            if st.button("🔧 Initialize Search"):
                with st.spinner("Initializing search components..."):
                    # Load embedding model
                    embedding_success = st.session_state.search_manager.load_embedding_model()
                    
                    if embedding_success:
                        # Create index
                        index_success = st.session_state.search_manager.create_index()
                        
                        if index_success:
                            # Load sample documents
                            data_loader = DataLoader()
                            documents = data_loader.load_documents_for_indexing()
                            
                            if documents:
                                texts = [doc['content'] for doc in documents]
                                metadata = [{'title': doc['title'], 'category': doc['category']} 
                                          for doc in documents]
                                
                                add_success = st.session_state.search_manager.add_documents(texts, metadata)
                                
                                if add_success:
                                    st.session_state.search_manager.save_index()
                                    st.success("Search index initialized successfully!")
                                    st.experimental_rerun()
                                else:
                                    st.error("Failed to add documents to index.")
                            else:
                                st.warning("No documents found to index. Creating empty index.")
                                st.session_state.search_manager.save_index()
                                st.success("Empty search index created.")
                        else:
                            st.error("Failed to create search index.")
                    else:
                        st.error("Failed to load embedding model.")
    
    with tab3:
        st.subheader("📊 Data Management")
        
        # Database stats
        db_stats = st.session_state.data_manager.get_database_stats()
        if db_stats:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Conversations", db_stats.get('conversations_count', 0))
                st.metric("Documents", db_stats.get('documents_count', 0))
            with col2:
                st.metric("Productivity Metrics", db_stats.get('productivity_metrics_count', 0))
                st.metric("Voice Sessions", db_stats.get('voice_sessions_count', 0))
            
            st.metric("Database Size", f"{db_stats.get('database_size_mb', 0):.2f} MB")
        
        st.divider()
        
        # Sample data management
        st.write("**Sample Data**")
        data_loader = DataLoader()
        
        if st.button("📥 Create Sample Datasets"):
            with st.spinner("Creating sample datasets..."):
                success = data_loader.create_sample_datasets()
                if success:
                    st.success("Sample datasets created successfully!")
                else:
                    st.error("Failed to create sample datasets.")
        
        # List existing datasets
        datasets = data_loader.list_datasets()
        if datasets:
            st.write("**Available Datasets:**")
            for dataset in datasets:
                st.write(f"- {dataset['filename']}: {dataset.get('record_count', 'Unknown')} records")
    
    with tab4:
        st.subheader("🔧 System Information")
        
        # System info
        import torch
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Hardware**")
            st.write(f"CUDA Available: {torch.cuda.is_available()}")
            if torch.cuda.is_available():
                st.write(f"CUDA Devices: {torch.cuda.device_count()}")
                st.write(f"Current Device: {torch.cuda.current_device()}")
        
        with col2:
            st.write("**Software**")
            st.write(f"PyTorch Version: {torch.__version__}")
            st.write(f"Python Version: {sys.version.split()[0]}")
        
        # Logs and diagnostics
        if st.button("🔍 Run Diagnostics"):
            st.info("Diagnostics feature coming soon!")

if __name__ == "__main__":
    main()
