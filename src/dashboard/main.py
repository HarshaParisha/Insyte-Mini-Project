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

# Initialize session state with persistence
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    st.session_state.current_page = "🏠 Dashboard"

# Initialize managers (these persist across reruns)
if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataManager()
    st.session_state.data_manager.initialize_database()

if 'llm_manager' not in st.session_state:
    st.session_state.llm_manager = LLMManager()

if 'search_manager' not in st.session_state:
    st.session_state.search_manager = SearchManager()
    # Try to load existing index if available
    if st.session_state.search_manager.load_embedding_model():
        st.session_state.search_manager.load_index()

if 'voice_manager' not in st.session_state:
    st.session_state.voice_manager = VoiceManager()

def main():
    """Main dashboard application."""
    
    # Sidebar navigation with clean button-based menu
    with st.sidebar:
        st.title("🧠 Insyte AI")
        st.markdown("*Your Offline Productivity Assistant*")
        st.markdown("---")
        
        # Navigation menu with radio buttons for clean look
        st.markdown("### 📋 Navigation")
        
        menu_options = [
            "🏠 Dashboard",
            "💬 AI Chat",
            "📊 Analytics",
            "🔍 Search",
            "🎤 Voice",
            "⚙️ Settings"
        ]
        
        page = st.radio(
            "Navigate to:",
            menu_options,
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # System status section
        st.markdown("### 🔧 System Status")
        show_system_status()
        
        st.markdown("---")
        
        # Footer
        st.markdown("##### 💡 Quick Tips")
        st.caption("• Load AI models in Settings")
        st.caption("• Start chatting in AI Chat")
        st.caption("• Track metrics in Analytics")
    
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
    """Display system component status in a compact, clean format."""
    
    # LLM Status
    llm_info = st.session_state.llm_manager.get_model_info()
    if llm_info['status'] == 'loaded':
        st.markdown("🟢 **LLM** Ready")
    else:
        st.markdown("🔴 **LLM** Not Loaded")
    
    # Search Index Status
    search_info = st.session_state.search_manager.get_index_info()
    if search_info['status'] == 'loaded':
        st.markdown(f"🟢 **Search** {search_info['total_documents']} docs")
    else:
        st.markdown("🟡 **Search** Not Loaded")
    
    # Voice Status
    voice_info = st.session_state.voice_manager.get_model_info()
    if voice_info['status'] == 'loaded':
        st.markdown("🟢 **Voice** Ready")
    else:
        st.markdown("🟡 **Voice** Not Loaded")
    
    # Database Status
    db_stats = st.session_state.data_manager.get_database_stats()
    if db_stats:
        st.markdown(f"🟢 **Database** {db_stats.get('conversations_count', 0)} chats")
    else:
        st.markdown("🔴 **Database** Error")

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
    """AI chat interface with productivity assistant."""
    
    st.title("💬 AI Chat Assistant")
    st.markdown("*Your personal productivity mentor and guide*")
    
    # Check if LLM is loaded
    llm_info = st.session_state.llm_manager.get_model_info()
    if llm_info['status'] != 'loaded':
        st.warning("⚠️ LLM not loaded. Please load the model in Settings first.")
        st.info("👉 Go to **Settings → AI Models** to load the language model.")
        return
    
    st.markdown("---")
    
    # Helpful suggestions
    with st.expander("💡 Suggested Questions", expanded=False):
        st.markdown("""
        **Try asking:**
        - How can I improve my focus during work?
        - What's the best way to organize my daily tasks?
        - Tips for managing work-life balance
        - How to overcome procrastination?
        - Best practices for time management
        - Ways to increase productivity without burnout
        """)
    
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
    if prompt := st.chat_input("Ask me anything about productivity, time management, or work habits..."):
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking as your productivity mentor..."):
                try:
                    response = st.session_state.llm_manager.generate_response(prompt)
                    
                    # If response is poor quality, provide fallback helpful response
                    if len(response) < 50 or not any(keyword in response.lower() for keyword in ['productivity', 'time', 'work', 'task', 'focus', 'improve', 'better', 'help', 'try', 'can']):
                        # Provide structured fallback responses based on keywords
                        response = get_fallback_productivity_response(prompt)
                    
                    st.write(response)
                    
                    # Save conversation
                    st.session_state.data_manager.save_conversation(
                        st.session_state.session_id, prompt, response
                    )
                    
                except Exception as e:
                    st.error(f"❌ Error generating response: {str(e)}")
                    st.info("💡 Try rephrasing your question or check Settings to ensure the model is loaded correctly.")

def get_fallback_productivity_response(question: str) -> str:
    """Provide high-quality, concise fallback responses for productivity questions."""
    question_lower = question.lower()
    
    # Productivity tips
    if any(word in question_lower for word in ['productivity', 'productive', 'tips']):
        return """**Here are proven productivity strategies:**

• **Time Blocking**: Schedule specific time slots for different tasks to maintain focus
• **Pomodoro Technique**: Work in 25-minute intervals with 5-minute breaks
• **Prioritize Daily**: Identify your top 3 tasks each morning
• **Eliminate Distractions**: Turn off notifications and create a dedicated workspace

Start with one technique and build from there!"""
    
    # Focus
    elif any(word in question_lower for word in ['focus', 'concentrate', 'distract']):
        return """**To improve focus at work:**

• **Single-tasking**: Focus on one task at a time—multitasking reduces productivity by 40%
• **Environment**: Create a distraction-free workspace with good lighting and minimal clutter
• **Deep Work Blocks**: Schedule 90-minute focused sessions with all notifications off
• **Strategic Breaks**: Take 5-10 minute breaks every hour to maintain mental clarity

Try implementing one method today and notice the difference!"""
    
    # Time management
    elif any(word in question_lower for word in ['time', 'manage', 'organize', 'schedule']):
        return """**Effective time management practices:**

• **Plan Ahead**: Spend 10 minutes each evening planning tomorrow's priorities
• **2-Minute Rule**: If it takes less than 2 minutes, do it immediately
• **Batch Similar Tasks**: Group emails, calls, and meetings together
• **Set Boundaries**: Learn to say "no" to non-essential commitments

Focus on managing your energy, not just your time."""
    
    # Work-life balance
    elif any(word in question_lower for word in ['balance', 'life', 'stress', 'burnout']):
        return """**Maintaining work-life balance:**

• **Set Clear Boundaries**: Define work hours and stick to them
• **Transition Ritual**: Create a routine that signals the end of work (e.g., short walk)
• **Prioritize Self-Care**: Regular exercise and 7-9 hours of sleep are essential
• **Schedule Downtime**: Block time for hobbies and family like you would for meetings

Remember: Rest is productive, not lazy."""
    
    # Procrastination
    elif any(word in question_lower for word in ['procrastination', 'procrastinate', 'delay', 'start']):
        return """**Overcome procrastination with these methods:**

• **Break It Down**: Split large tasks into 5-minute actions
• **2-Minute Start**: Commit to just 2 minutes—starting is the hardest part
• **Remove Friction**: Prep your workspace and materials in advance
• **Find Your Why**: Connect the task to a meaningful goal

Action creates motivation, not the other way around!"""
    
    # Goals or planning
    elif any(word in question_lower for word in ['goal', 'plan', 'achieve', 'success']):
        return """**Setting and achieving goals:**

• **SMART Goals**: Make them Specific, Measurable, Achievable, Relevant, and Time-bound
• **Break Down**: Divide big goals into weekly and daily actions
• **Track Progress**: Review your progress weekly and adjust as needed
• **Celebrate Wins**: Acknowledge small victories to maintain momentum

Consistency beats intensity—small daily actions compound over time."""
    
    # Default response
    else:
        return """**Key productivity principles:**

• **Clarity**: Know exactly what you need to accomplish and why
• **Focus**: Work on one important task at a time with full attention
• **Consistency**: Small daily actions lead to significant results
• **Rest**: Quality breaks improve performance and creativity

What specific area would you like to improve? Ask about focus, time management, or work-life balance!"""

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
            st.rerun()
        
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
    """Semantic search interface for finding similar documents using AI."""
    
    st.title("🔍 Semantic Search")
    
    # Explanation of what search does
    with st.expander("ℹ️ What is Semantic Search?", expanded=False):
        st.markdown("""
        **Semantic Search** uses AI to understand the *meaning* of your queries, not just keywords.
        
        **How it works:**
        - 🧠 Your documents are converted to AI embeddings (numerical representations)
        - 🔍 When you search, your query is also converted to an embedding
        - 📊 The system finds documents with similar meanings, even if they use different words
        
        **Example Use Cases:**
        - Find all notes about "productivity" (even if they mention "efficiency", "time management", etc.)
        - Search for "how to focus" and get documents about concentration, meditation, and work habits
        - Discover related ideas you forgot about by searching with natural language
        
        **Perfect for:**
        - Personal knowledge bases
        - Meeting notes and ideas
        - Research documents
        - Task descriptions and project notes
        """)
    
    # Check if search index is loaded
    search_info = st.session_state.search_manager.get_index_info()
    if search_info['status'] != 'loaded':
        st.warning("⚠️ Search index not loaded yet.")
        st.info("👉 Go to **Settings → Search Index Management** to initialize the search system and add documents.")
        
        # Quick stats
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📄 Documents in Database", len(st.session_state.data_manager.get_documents(limit=1000)))
        with col2:
            st.metric("🔍 Indexed Documents", 0)
        return
    
    # Show index stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📄 Indexed Documents", search_info['total_documents'])
    with col2:
        st.metric("🧠 Embedding Model", search_info['embedding_model'].split('/')[-1])
    with col3:
        st.metric("📊 Vector Dimension", search_info['dimension'])
    
    st.markdown("---")
    
    # Search interface
    query = st.text_input(
        "🔍 Search your knowledge base:", 
        placeholder="e.g., 'improve focus and productivity' or 'time management tips'",
        help="Enter a natural language query - the AI will find semantically similar documents"
    )
    
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
    """Professional voice transcription interface with Whisper AI."""
    
    st.title("🎤 Voice Assistant")
    st.markdown("*Powered by OpenAI Whisper - State-of-the-art Speech Recognition*")
    
    # Professional info section
    with st.expander("ℹ️ About Whisper Voice Recognition", expanded=False):
        st.markdown("""
        ### 🎯 Why Whisper is Industry-Leading
        
        **OpenAI Whisper** is a state-of-the-art automatic speech recognition (ASR) system trained on 680,000 hours of multilingual data.
        
        **Key Advantages:**
        - 🌍 **Multi-language Support**: Recognizes 99+ languages with high accuracy
        - 🎯 **High Accuracy**: 95%+ word accuracy on clear audio
        - 🔒 **100% Offline**: All processing happens locally - your audio never leaves your computer
        - 🚫 **Privacy First**: No cloud services, no data collection
        - 💪 **Robust**: Handles background noise, accents, and various audio qualities
        - ⚡ **Fast**: Real-time or faster transcription depending on model size
        - 📝 **Punctuation**: Automatically adds punctuation and capitalization
        - 🎵 **Noise Handling**: Works well even with background music or noise
        
        **Model Accuracy Comparison:**
        - **Tiny**: Fast, 70-80% accuracy, good for simple tasks
        - **Base**: Balanced, 80-85% accuracy, recommended for most uses
        - **Small**: Better, 85-90% accuracy, good quality/speed trade-off
        - **Medium**: High accuracy, 90-95%, slower but very reliable
        - **Large**: Best accuracy, 95%+ accuracy, slowest but professional-grade
        
        **Professional Use Cases:**
        - Meeting transcriptions
        - Interview recordings
        - Lecture notes
        - Voice memos
        - Podcast transcription
        - Accessibility tools
        """)
    
    # Check if voice model is loaded
    voice_info = st.session_state.voice_manager.get_model_info()
    if voice_info['status'] != 'loaded':
        st.warning("⚠️ Voice model not loaded yet.")
        st.info("👉 Go to **Settings → AI Models** to load a Whisper model first.")
        
        # Show available models
        with st.expander("📊 Model Comparison"):
            model_comparison = pd.DataFrame({
                'Model': ['tiny', 'base', 'small', 'medium', 'large'],
                'Size': ['39 MB', '74 MB', '244 MB', '769 MB', '1.5 GB'],
                'Speed': ['⚡⚡⚡⚡⚡', '⚡⚡⚡⚡', '⚡⚡⚡', '⚡⚡', '⚡'],
                'Accuracy': ['70-80%', '80-85%', '85-90%', '90-95%', '95%+'],
                'Use Case': ['Quick tests', 'General use', 'Quality balance', 'Professional', 'Best quality']
            })
            st.dataframe(model_comparison, hide_index=True, use_container_width=True)
        
        return
    
    # Model info display
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🤖 Model", voice_info['model_size'].capitalize())
    with col2:
        st.metric("🌍 Languages", f"{len(voice_info.get('languages', []))}+")
    with col3:
        st.metric("✅ Status", "Ready")
    
    st.markdown("---")
    
    # File upload for audio transcription
    st.subheader("📁 Upload Audio File")
    st.caption("Supported formats: WAV, MP3, M4A, FLAC, OGG")
    
    uploaded_file = st.file_uploader(
        "Choose an audio file",
        type=['wav', 'mp3', 'm4a', 'flac', 'ogg'],
        help="Upload any audio file for transcription. Max size: 200MB"
    )
    
    if uploaded_file is not None:
        # Show file info
        file_size_mb = uploaded_file.size / (1024 * 1024)
        st.info(f"📄 **File**: {uploaded_file.name} ({file_size_mb:.2f} MB)")
        
        # Save uploaded file temporarily with proper extension
        import tempfile
        file_extension = uploaded_file.name.split('.')[-1]
        temp_path = os.path.join(tempfile.gettempdir(), f"insyte_audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_extension}")
        
        try:
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            if st.button("🎤 Transcribe Audio", type="primary", use_container_width=True):
                with st.spinner("🔄 Transcribing audio... This may take a moment depending on audio length and model size."):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    try:
                        status_text.text("Loading audio file...")
                        progress_bar.progress(20)
                        
                        status_text.text("Processing with Whisper AI...")
                        progress_bar.progress(40)
                        
                        # Transcribe
                        result = st.session_state.voice_manager.transcribe_audio(temp_path)
                        progress_bar.progress(80)
                        
                        status_text.text("Finalizing transcription...")
                        progress_bar.progress(100)
                        
                        # Clear progress indicators
                        progress_bar.empty()
                        status_text.empty()
                        
                        if result.get('text') and result['text'].strip():
                            st.success("✅ Transcription completed successfully!")
                            
                            # Display results in a professional format
                            st.markdown("---")
                            st.subheader("📝 Transcription")
                            
                            # Show transcription in a nice text box
                            st.markdown(f"""
                            <div style="background-color: #1e1e1e; padding: 20px; border-radius: 10px; border-left: 4px solid #4CAF50;">
                                <p style="color: #ffffff; font-size: 16px; line-height: 1.6; margin: 0;">
                                    {result['text']}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.markdown("---")
                            
                            # Metrics
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("🌍 Language", result.get('language', 'en').upper())
                            with col2:
                                confidence_pct = result.get('confidence', 0) * 100
                                st.metric("📊 Confidence", f"{confidence_pct:.1f}%")
                            with col3:
                                duration = result.get('duration', 0)
                                st.metric("⏱️ Duration", f"{duration:.1f}s")
                            with col4:
                                word_count = len(result['text'].split())
                                st.metric("📝 Words", word_count)
                            
                            # Action buttons
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                if st.button("💾 Save to Database", use_container_width=True):
                                    # Save transcription
                                    st.session_state.data_manager.save_voice_session(
                                        result['text'],
                                        result.get('confidence', 0),
                                        result.get('duration', 0),
                                        result.get('language', 'en')
                                    )
                                    st.success("✅ Saved to database!")
                            
                            with col2:
                                # Copy to clipboard button (visual only, actual copy needs JS)
                                st.download_button(
                                    "📋 Download as Text",
                                    result['text'],
                                    file_name=f"transcription_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                    use_container_width=True
                                )
                            
                            with col3:
                                if st.button("💬 Discuss with AI", use_container_width=True):
                                    st.session_state.temp_voice_text = result['text']
                                    st.info("💡 Go to AI Chat to discuss this transcription!")
                        
                        else:
                            st.error("❌ Transcription failed or no speech detected.")
                            st.warning("**Possible reasons:**")
                            st.markdown("""
                            - Audio file may be corrupted
                            - No speech detected in the audio
                            - Audio quality is too low
                            - Unsupported audio format or codec
                            
                            **💡 Tips for better results:**
                            - Ensure clear audio with minimal background noise
                            - Use WAV or MP3 format for best compatibility
                            - Check that the audio contains speech
                            - Try converting the audio to a different format
                            """)
                            
                    except Exception as e:
                        progress_bar.empty()
                        status_text.empty()
                        st.error(f"❌ Transcription error: {str(e)}")
                        
                        # Detailed error info
                        with st.expander("🔍 Error Details"):
                            st.code(str(e))
                            st.markdown("""
                            **Common solutions:**
                            1. Ensure the audio file is not corrupted
                            2. Try converting to WAV format
                            3. Check if the file contains actual speech
                            4. Verify the model is properly loaded
                            5. Try a different audio file to test
                            """)
                
        except Exception as e:
            st.error(f"❌ Error handling file: {str(e)}")
        
        finally:
            # Clean up temporary file
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except:
                pass
    
    # Display recent transcriptions
    st.markdown("---")
    st.subheader("📜 Recent Transcriptions")
    
    # Get recent voice sessions from database
    try:
        # This would require adding a method to data_manager
        st.info("💡 Recent transcriptions will appear here after you transcribe audio files.")
        st.caption("Transcriptions are automatically saved to your local database")
    except Exception as e:
        st.warning(f"Could not load recent transcriptions: {str(e)}")

def show_settings():
    """System settings and configuration."""
    
    st.title("⚙️ Settings")
    
    # Info about persistence
    st.info("💡 **Models stay loaded** during your session. They won't reload unless you restart the app or explicitly reload them.")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🤖 AI Models", "🔍 Search Index", "📊 Data", "🔧 System"])
    
    with tab1:
        st.subheader("🤖 AI Model Management")
        
        st.markdown("**📝 Note:** Once loaded, models remain in memory until you restart the application.")
        st.markdown("---")
        
        # LLM Settings
        st.write("**Language Model**")
        llm_info = st.session_state.llm_manager.get_model_info()
        
        if llm_info['status'] == 'loaded':
            st.success(f"✅ Model loaded: {llm_info['model_name']}")
            params = llm_info.get('parameters', 'Unknown')
            st.write(f"Parameters: {params:,}" if isinstance(params, int) else f"Parameters: {params}")
            st.write(f"Device: {llm_info['device']}")
            st.caption("✅ This model will stay loaded while the app is running")
            
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
                        st.rerun()
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
                        st.rerun()
                    else:
                        st.error("Failed to load voice model.")
    
    with tab2:
        st.subheader("🔍 Search Index Management")
        
        st.markdown("""
        **What does Search Index do?**
        - Converts your documents into AI embeddings for semantic search
        - Lets you find documents by meaning, not just keywords
        - Example: Search "time management" finds documents about "productivity", "schedules", "efficiency"
        """)
        st.markdown("---")
        
        search_info = st.session_state.search_manager.get_index_info()
        
        if search_info['status'] == 'loaded':
            st.success(f"✅ Search index loaded with {search_info['total_documents']} documents")
            
            if st.button("🗑️ Clear Index"):
                if st.session_state.search_manager.clear_index():
                    st.success("Index cleared successfully!")
                    st.rerun()
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
                                    st.rerun()
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
        st.subheader("🔧 System Information & Diagnostics")
        
        # System info
        import torch
        import platform
        import psutil
        from pathlib import Path
        
        # Hardware Overview
        st.markdown("### 💻 Hardware Information")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🖥️ CPU Cores", psutil.cpu_count(logical=False))
            st.metric("🧵 Threads", psutil.cpu_count(logical=True))
        
        with col2:
            mem = psutil.virtual_memory()
            st.metric("💾 Total RAM", f"{mem.total / (1024**3):.1f} GB")
            st.metric("📊 RAM Usage", f"{mem.percent}%")
        
        with col3:
            cuda_available = torch.cuda.is_available()
            st.metric("🎮 CUDA", "Available" if cuda_available else "Not Available")
            if cuda_available:
                st.metric("GPU Count", torch.cuda.device_count())
        
        st.markdown("---")
        
        # Software Information
        st.markdown("### 📦 Software Versions")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Core Dependencies**")
            st.code(f"""
Python: {sys.version.split()[0]}
PyTorch: {torch.__version__}
Streamlit: {st.__version__}
Platform: {platform.system()} {platform.release()}
            """.strip())
        
        with col2:
            st.write("**System Details**")
            st.code(f"""
Architecture: {platform.machine()}
Processor: {platform.processor()[:40]}...
Python Implementation: {platform.python_implementation()}
            """.strip())
        
        st.markdown("---")
        
        # Diagnostics Section
        st.markdown("### 🔍 System Diagnostics")
        
        if st.button("🚀 Run Full Diagnostics", type="primary", use_container_width=True):
            run_diagnostics()

def run_diagnostics():
    """Run comprehensive system diagnostics."""
    import torch
    import platform
    import psutil
    from pathlib import Path
    import time
    
    with st.spinner("Running diagnostics..."):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Initialize results
        results = {
            "errors": [],
            "warnings": [],
            "info": [],
            "success": []
        }
        
        # 1. Check Python Version
        status_text.text("Checking Python version...")
        progress_bar.progress(10)
        time.sleep(0.3)
        
        python_version = tuple(map(int, platform.python_version_tuple()[:2]))
        if python_version >= (3, 8):
            results["success"].append(f"✅ Python {platform.python_version()} is compatible")
        else:
            results["errors"].append(f"❌ Python {platform.python_version()} is too old (requires 3.8+)")
        
        # 2. Check Memory
        status_text.text("Checking system memory...")
        progress_bar.progress(20)
        time.sleep(0.3)
        
        mem = psutil.virtual_memory()
        if mem.available > 2 * (1024**3):  # 2GB
            results["success"].append(f"✅ Sufficient RAM available: {mem.available / (1024**3):.1f} GB free")
        elif mem.available > 1 * (1024**3):  # 1GB
            results["warnings"].append(f"⚠️ Low RAM available: {mem.available / (1024**3):.1f} GB free")
        else:
            results["errors"].append(f"❌ Critical: Very low RAM: {mem.available / (1024**3):.1f} GB free")
        
        # 3. Check Disk Space
        status_text.text("Checking disk space...")
        progress_bar.progress(30)
        time.sleep(0.3)
        
        try:
            disk = psutil.disk_usage('.')
            if disk.free > 5 * (1024**3):  # 5GB
                results["success"].append(f"✅ Sufficient disk space: {disk.free / (1024**3):.1f} GB free")
            elif disk.free > 1 * (1024**3):  # 1GB
                results["warnings"].append(f"⚠️ Low disk space: {disk.free / (1024**3):.1f} GB free")
            else:
                results["errors"].append(f"❌ Critical: Very low disk space: {disk.free / (1024**3):.1f} GB free")
        except Exception as e:
            results["warnings"].append(f"⚠️ Could not check disk space: {str(e)}")
        
        # 4. Check PyTorch
        status_text.text("Checking PyTorch installation...")
        progress_bar.progress(40)
        time.sleep(0.3)
        
        try:
            if torch.cuda.is_available():
                results["success"].append(f"✅ PyTorch with CUDA support detected")
                results["info"].append(f"ℹ️ GPU: {torch.cuda.get_device_name(0)}")
            else:
                results["info"].append(f"ℹ️ PyTorch CPU-only mode (CUDA not available)")
        except Exception as e:
            results["warnings"].append(f"⚠️ PyTorch check failed: {str(e)}")
        
        # 5. Check Database
        status_text.text("Checking database...")
        progress_bar.progress(50)
        time.sleep(0.3)
        
        try:
            db_stats = st.session_state.data_manager.get_database_stats()
            if db_stats:
                results["success"].append("✅ Database is accessible and functional")
                results["info"].append(f"ℹ️ Database size: {db_stats.get('database_size_mb', 0):.2f} MB")
            else:
                results["errors"].append("❌ Database is not responding")
        except Exception as e:
            results["errors"].append(f"❌ Database error: {str(e)}")
        
        # 6. Check LLM Manager
        status_text.text("Checking AI models...")
        progress_bar.progress(60)
        time.sleep(0.3)
        
        try:
            llm_info = st.session_state.llm_manager.get_model_info()
            if llm_info['status'] == 'loaded':
                results["success"].append(f"✅ LLM model loaded: {llm_info['model_name']}")
            else:
                results["info"].append("ℹ️ LLM model not loaded (load in Settings)")
        except Exception as e:
            results["warnings"].append(f"⚠️ LLM check failed: {str(e)}")
        
        # 7. Check Search Manager
        status_text.text("Checking search index...")
        progress_bar.progress(70)
        time.sleep(0.3)
        
        try:
            search_info = st.session_state.search_manager.get_index_info()
            if search_info['status'] == 'loaded':
                results["success"].append(f"✅ Search index loaded: {search_info['total_documents']} documents")
            else:
                results["info"].append("ℹ️ Search index not initialized (initialize in Settings)")
        except Exception as e:
            results["warnings"].append(f"⚠️ Search check failed: {str(e)}")
        
        # 8. Check Voice Manager
        status_text.text("Checking voice recognition...")
        progress_bar.progress(80)
        time.sleep(0.3)
        
        try:
            voice_info = st.session_state.voice_manager.get_model_info()
            if voice_info['status'] == 'loaded':
                results["success"].append(f"✅ Voice model loaded: {voice_info['model_size']}")
            else:
                results["info"].append("ℹ️ Voice model not loaded (load in Settings)")
        except Exception as e:
            results["warnings"].append(f"⚠️ Voice check failed: {str(e)}")
        
        # 9. Check Data Files
        status_text.text("Checking data files...")
        progress_bar.progress(90)
        time.sleep(0.3)
        
        data_dir = Path("data/datasets")
        if data_dir.exists():
            json_files = list(data_dir.glob("*.json"))
            if json_files:
                results["success"].append(f"✅ Found {len(json_files)} dataset files")
            else:
                results["warnings"].append("⚠️ No dataset files found (create in Settings)")
        else:
            results["warnings"].append("⚠️ Data directory not found")
        
        # 10. Final Checks
        status_text.text("Finalizing diagnostics...")
        progress_bar.progress(100)
        time.sleep(0.3)
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        # Display Results
        st.markdown("---")
        st.markdown("## 📊 Diagnostic Results")
        
        # Summary
        total_checks = len(results["errors"]) + len(results["warnings"]) + len(results["success"]) + len(results["info"])
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("✅ Passed", len(results["success"]))
        with col2:
            st.metric("❌ Errors", len(results["errors"]))
        with col3:
            st.metric("⚠️ Warnings", len(results["warnings"]))
        with col4:
            st.metric("ℹ️ Info", len(results["info"]))
        
        # Detailed Results
        if results["errors"]:
            st.error("**Critical Issues:**")
            for error in results["errors"]:
                st.markdown(f"- {error}")
        
        if results["warnings"]:
            st.warning("**Warnings:**")
            for warning in results["warnings"]:
                st.markdown(f"- {warning}")
        
        if results["success"]:
            st.success("**Successful Checks:**")
            for success in results["success"]:
                st.markdown(f"- {success}")
        
        if results["info"]:
            with st.expander("ℹ️ Additional Information", expanded=False):
                for info in results["info"]:
                    st.markdown(f"- {info}")
        
        # Recommendations
        st.markdown("---")
        st.markdown("### � Recommendations")
        
        if not results["errors"] and not results["warnings"]:
            st.success("🎉 **System Status: Excellent!** All checks passed. Your system is running optimally.")
        elif results["errors"]:
            st.error("⚠️ **Action Required:** Please address the critical issues above.")
        else:
            st.info("✅ **System Status: Good** with minor warnings. Consider the suggestions above.")
        
        # Performance Tips
        with st.expander("🚀 Performance Tips", expanded=False):
            st.markdown("""
            **To improve performance:**
            - Close unnecessary applications to free up RAM
            - Use GPU acceleration if available (CUDA)
            - Load models once and keep them in memory
            - Regularly clean up old database records
            - Keep only necessary datasets
            - Use smaller model variants for faster inference
            - Enable caching for frequently accessed data
            """)

if __name__ == "__main__":
    main()
