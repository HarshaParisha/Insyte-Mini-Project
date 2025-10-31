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
from utils.document_processor import DocumentProcessor
from utils.qa_generator import QAGenerator

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

if 'qa_generator' not in st.session_state:
    st.session_state.qa_generator = QAGenerator()

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
        # Get recent productivity metrics - use today's date dynamically
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
            # Convert to DataFrame and ensure proper date handling
            df = pd.DataFrame(metrics)
            if not df.empty:
                # Convert date strings to datetime for proper plotting
                df['date'] = pd.to_datetime(df['date'])
                
                # Create the metrics graph
                fig = px.line(
                    df, 
                    x='date', 
                    y='metric_value', 
                    color='metric_type',
                    title=f"Productivity Metrics ({start_date} to {end_date})",
                    labels={'date': 'Date', 'metric_value': 'Value', 'metric_type': 'Metric Type'}
                )
                
                # Update layout for better visualization
                fig.update_xaxes(
                    tickformat="%b %d\n%Y",
                    tickangle=-45,
                    dtick="D1"  # Show every day
                )
                
                fig.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Metric Value",
                    hovermode='x unified',
                    showlegend=True
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Add helpful information about metrics
                st.markdown("---")
                st.markdown("### 📊 Understanding Your Metrics")
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.markdown("""
                    **📈 Why Track Metrics?**
                    - **Identify Patterns**: See your most productive times
                    - **Track Progress**: Monitor improvement over time
                    - **Stay Accountable**: Visual reminders of your goals
                    - **Data-Driven**: Make informed productivity decisions
                    """)
                
                with col_b:
                    st.markdown("""
                    **💡 How to Use Metrics:**
                    - **Daily Review**: Check trends at day's end
                    - **Weekly Analysis**: Compare performance across days
                    - **Goal Setting**: Use data to set realistic targets
                    - **Habit Building**: Track consistency and streaks
                    """)
                
                st.info("💡 **Note**: Metrics are automatically tracked daily. The graph updates with each new entry to show your latest productivity trends.")
                
                # Add note about reset time
                st.markdown("""
                <div style="background: #2a2a2a; padding: 15px; border-radius: 8px; margin-top: 10px; border-left: 4px solid #667eea;">
                    <p style="margin: 0; color: #aaa; font-size: 0.95em;">
                        ⏰ <strong>Daily Reset:</strong> Metrics are calculated and reset at <strong>12:00 PM (noon)</strong> each day. 
                        Current data reflects metrics from the last reset period.
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No productivity metrics recorded yet. Start tracking your productivity in the Analytics tab!")

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
    """Professional project-based document search with clean UI."""
    
    st.title("🔍 AI Document Search")
    st.caption("Upload documents (PDF/DOCX/TXT) • Organize in projects • Search with AI")
    
    # Initialize components
    if 'doc_processor' not in st.session_state:
        st.session_state.doc_processor = DocumentProcessor()
    
    st.session_state.data_manager.create_project_tables()
    
    # Get all projects
    projects = st.session_state.data_manager.get_all_projects()
    
    st.markdown("---")
    
    # PROFESSIONAL LAYOUT: Project Management Bar
    if projects:
        # Existing projects - show selection bar
        col1, col2 = st.columns([3, 1])
        
        with col1:
            project_options = {f"📁 {proj['name']} ({proj['doc_count']} docs)": proj['id'] 
                             for proj in projects}
            
            # Add "Create New" option at the end
            project_options["➕ Create New Project"] = "CREATE_NEW"
            
            selected_display = st.selectbox(
                "Select Project",
                options=list(project_options.keys()),
                key="project_selector",
                label_visibility="collapsed"
            )
            
            selected_id = project_options[selected_display]
            
            if selected_id == "CREATE_NEW":
                st.session_state.show_create_form = True
                st.session_state.selected_project = None
            else:
                st.session_state.show_create_form = False
                st.session_state.selected_project = selected_id
        
        with col2:
            if st.session_state.get('selected_project'):
                if st.button("🗑️ Delete Project", use_container_width=True):
                    if st.session_state.data_manager.delete_project(st.session_state.selected_project):
                        st.success("✅ Deleted!")
                        st.session_state.selected_project = None
                        st.session_state.pop('show_create_form', None)
                        st.rerun()
    else:
        # No projects - show create form
        st.session_state.show_create_form = True
    
    st.markdown("---")
    
    # CREATE PROJECT FORM (when triggered)
    if st.session_state.get('show_create_form', False):
        st.markdown("### ➕ Create New Project")
        
        with st.form("create_project_form", clear_on_submit=True):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                project_name = st.text_input(
                    "Project Name *",
                    placeholder="e.g., Research Papers, Marketing Docs",
                    help="Give your project a descriptive name"
                )
            
            with col2:
                project_desc = st.text_input(
                    "Description (Optional)",
                    placeholder="Brief description",
                    help="Optional short description"
                )
            
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                submitted = st.form_submit_button("✅ Create", type="primary", use_container_width=True)
            with col2:
                cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
            
            if submitted and project_name.strip():
                project_id = st.session_state.data_manager.create_project(
                    project_name.strip(), 
                    project_desc.strip()
                )
                if project_id:
                    st.session_state.selected_project = project_id
                    st.session_state.show_create_form = False
                    st.success(f"✅ Project '{project_name}' created!")
                    st.rerun()
                else:
                    st.error("❌ Project name already exists!")
            
            elif submitted and not project_name.strip():
                st.warning("⚠️ Please enter a project name")
            
            elif cancel:
                st.session_state.show_create_form = False
                if projects:
                    st.session_state.selected_project = projects[0]['id']
                st.rerun()
        
        st.markdown("---")
        
        # Show help for first-time users
        if not projects:
            st.info("👆 **First time?** Create your first project to organize and search your documents with AI!")
        
        return
    
    # NO PROJECTS - MINIMAL WELCOME
    if not projects:
        st.info("👆 Create your first project to get started with AI-powered document search!")
        return
    
    # PROJECT SELECTED - SHOW INTERFACE
    selected_proj_id = st.session_state.get('selected_project')
    
    if not selected_proj_id:
        st.info("👆 Select a project from the dropdown above")
        return
    
    project = st.session_state.data_manager.get_project_by_id(selected_proj_id)
    
    if not project:
        st.error("❌ Project not found!")
        st.session_state.selected_project = None
        st.rerun()
        return
    
    # Project Header (Minimal)
    st.markdown(f"### 📁 {project['name']}")
    if project['description']:
        st.caption(project['description'])
    
    st.markdown("---")
    
    # CLEAN TAB INTERFACE
    tab1, tab2, tab3 = st.tabs(["🔍 Search", "📤 Upload", "📚 Documents"])
    
    # ========== TAB 1: SEARCH ==========
    with tab1:
        documents = st.session_state.data_manager.get_project_documents(selected_proj_id)
        
        if not documents:
            st.info("📄 No documents yet. Upload files in the **📤 Upload** tab!")
        else:
            # Build index using NLP semantic search
            with st.spinner("🔄 Indexing documents with NLP..."):
                success = st.session_state.search_manager.build_project_index(documents)
            
            if not success:
                st.error("❌ Index failed")
                return
            
            st.success(f"✅ {len(documents)} documents indexed with semantic embeddings")
            
            # Get suggested questions from database
            qa_pairs = st.session_state.data_manager.get_project_qa_pairs(selected_proj_id, limit=10)
            
            # SUGGESTED QUESTIONS SECTION
            if qa_pairs:
                with st.expander("💡 **Suggested Questions** - Auto-generated from your documents", expanded=True):
                    st.caption(f"{len(qa_pairs)} questions ready • Click to see answers")
                    
                    # Display in columns for better layout
                    for i, qa in enumerate(qa_pairs[:6]):  # Show top 6
                        col1, col2 = st.columns([4, 1])
                        
                        with col1:
                            # Question as a button
                            if st.button(
                                f"❓ {qa['question']}", 
                                key=f"qa_btn_{qa['id']}",
                                use_container_width=True
                            ):
                                # Store selected Q&A in session state
                                st.session_state.selected_qa = qa
                        
                        with col2:
                            st.caption(f"📄 {qa['filename'][:15]}...")
                    
                    if len(qa_pairs) > 6:
                        st.info(f"💡 Plus {len(qa_pairs) - 6} more questions available")
            
            # Show selected Q&A answer
            if 'selected_qa' in st.session_state and st.session_state.selected_qa:
                qa = st.session_state.selected_qa
                
                st.markdown("### 📌 Answer")
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            padding: 3px; border-radius: 12px; margin: 15px 0;">
                    <div style="background: #1a1a1a; padding: 20px; border-radius: 10px;">
                        <h4 style="color: white; margin-bottom: 10px;">
                            ❓ {qa['question']}
                        </h4>
                        <div style="color: #888; font-size: 0.9em; margin-bottom: 15px;">
                            📄 Source: {qa['filename']}
                        </div>
                        <div style="color: #fff; line-height: 1.7; font-size: 1.05em;">
                            {qa['answer']}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("❌ Clear Answer", key="clear_qa"):
                    st.session_state.selected_qa = None
                    st.rerun()
                
                st.markdown("---")
            
            # Regular Search UI
            st.markdown("### 🔍 Or Search Your Documents")
            
            query = st.text_input(
                "Ask a question",
                placeholder="e.g., 'What is Insyte AI?', 'Explain the architecture', 'Key features'",
                help="Natural language search powered by NLP semantic understanding"
            )
            
            # Simple settings
            col1, col2 = st.columns([2, 1])
            with col1:
                st.caption("💡 Powered by Sentence-Transformers NLP • No LLM required")
            with col2:
                min_similarity = st.slider("Min Match %", 10, 80, 25, 5, help="Relevance threshold")
            
            if query:
                # Semantic Search using NLP embeddings
                with st.spinner("🔍 Searching with NLP..."):
                    results = st.session_state.search_manager.search_project(
                        query, k=10, threshold=min_similarity/100
                    )
                
                if results and len(results) >= 3:
                    # Show TOP 3 ANSWERS professionally
                    st.markdown("### 📝 Top 3 Answers from Your Documents")
                    st.caption(f"Found {len(results)} relevant sections • Showing best 3 matches")
                    st.markdown("---")
                    
                    # Display 3 distinct answer cards
                    for i, result in enumerate(results[:3], 1):
                        similarity = result['similarity_percentage']
                        filename = result['metadata']['filename']
                        content = result['document']
                        
                        # Color gradient based on rank
                        if i == 1:
                            gradient = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
                            border_color = "#667eea"
                            rank_emoji = "🥇"
                            rank_text = "Best Match"
                        elif i == 2:
                            gradient = "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)"
                            border_color = "#f093fb"
                            rank_emoji = "🥈"
                            rank_text = "Second Match"
                        else:
                            gradient = "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"
                            border_color = "#4facfe"
                            rank_emoji = "🥉"
                            rank_text = "Third Match"
                        
                        # Answer Card
                        st.markdown(f"""
                        <div style="background: {gradient}; padding: 3px; border-radius: 12px; margin: 20px 0;">
                            <div style="background: #1a1a1a; padding: 20px; border-radius: 10px;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                                    <h4 style="color: white; margin: 0;">
                                        {rank_emoji} Answer {i} • {rank_text}
                                    </h4>
                                    <span style="background: {gradient}; color: white; 
                                                padding: 5px 15px; border-radius: 20px; font-weight: 600;">
                                        {similarity}% Match
                                    </span>
                                </div>
                                <div style="color: #888; font-size: 0.9em; margin-bottom: 10px;">
                                    � Source: {filename}
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Show answer content in clean format
                        with st.container():
                            # Smart excerpt length based on content
                            if len(content) > 500:
                                excerpt = content[:500].strip()
                                remaining = len(content) - 500
                                st.markdown(f"**Answer:**")
                                st.write(excerpt + "...")
                                
                                with st.expander(f"📖 Read full answer ({remaining} more characters)"):
                                    st.text(content)
                            else:
                                st.markdown(f"**Answer:**")
                                st.write(content)
                        
                        if i < 3:
                            st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Show additional results if any
                    if len(results) > 3:
                        st.markdown("---")
                        with st.expander(f"📚 View {len(results) - 3} More Relevant Sections"):
                            for i, result in enumerate(results[3:], 4):
                                similarity = result['similarity_percentage']
                                filename = result['metadata']['filename']
                                
                                st.markdown(f"**#{i}** • {filename} • {similarity}% match")
                                with st.expander("Read excerpt"):
                                    st.text(result['document'][:400] + "..." if len(result['document']) > 400 else result['document'])
                
                elif results and len(results) < 3:
                    # Less than 3 results - Still show professionally with gradient cards
                    st.markdown("### 📝 Search Results")
                    st.caption(f"Found {len(results)} relevant section(s) • Lower the threshold to find more")
                    st.markdown("---")
                    
                    for i, result in enumerate(results, 1):
                        similarity = result['similarity_percentage']
                        filename = result['metadata']['filename']
                        content = result['document']
                        
                        # Assign gradient colors based on position
                        if i == 1:
                            gradient = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
                            border_color = "#667eea"
                            rank_emoji = "🥇"
                        elif i == 2:
                            gradient = "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)"
                            border_color = "#f093fb"
                            rank_emoji = "🥈"
                        else:
                            gradient = "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"
                            border_color = "#4facfe"
                            rank_emoji = "🥉"
                        
                        # Professional Answer Card (same style as top 3)
                        st.markdown(f"""
                        <div style="background: {gradient}; padding: 3px; border-radius: 12px; margin: 20px 0;">
                            <div style="background: #1a1a1a; padding: 20px; border-radius: 10px;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                                    <h4 style="color: white; margin: 0;">
                                        {rank_emoji} Answer {i}
                                    </h4>
                                    <span style="background: {gradient}; color: white; 
                                                padding: 5px 15px; border-radius: 20px; font-weight: 600;">
                                        {similarity}% Match
                                    </span>
                                </div>
                                <div style="color: #888; font-size: 0.9em; margin-bottom: 10px;">
                                    📄 Source: {filename}
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Show content
                        with st.container():
                            if len(content) > 500:
                                excerpt = content[:500].strip()
                                remaining = len(content) - 500
                                st.markdown("**Answer:**")
                                st.write(excerpt + "...")
                                
                                with st.expander(f"📖 Read full answer ({remaining} more characters)"):
                                    st.text(content)
                            else:
                                st.markdown("**Answer:**")
                                st.write(content)
                        
                        if i < len(results):
                            st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Helpful message
                    st.markdown("---")
                    st.info("💡 **Tip:** Lower the **Min Match %** slider to 20% or 15% to find more relevant sections from your documents!")
                
                else:
                    # No results found
                    st.markdown("### ❌ No Relevant Results Found")
                    
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%); 
                                padding: 3px; border-radius: 12px; margin: 20px 0;">
                        <div style="background: #1a1a1a; padding: 25px; border-radius: 10px;">
                            <h4 style="color: white; margin-bottom: 15px;">
                                🔍 No matching content found in your documents
                            </h4>
                            <div style="color: #ccc; line-height: 1.8;">
                                <p><strong>Try these solutions:</strong></p>
                                <ul style="margin-left: 20px;">
                                    <li>🎯 <strong>Lower the threshold:</strong> Set Min Match % to 15-20%</li>
                                    <li>✏️ <strong>Rephrase your question:</strong> Use different keywords</li>
                                    <li>📄 <strong>Check your documents:</strong> Ensure they contain relevant information</li>
                                    <li>📤 <strong>Upload more files:</strong> Add documents related to your topic</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show document count for context
                    st.info(f"💡 Currently searching across **{len(documents)} document(s)** in this project")
    
    # ========== TAB 2: UPLOAD ==========
    with tab2:
        st.markdown("### 📤 Upload Documents")
        st.caption("Supported: PDF, DOCX, TXT")
        
        uploaded_files = st.file_uploader(
            "Choose files",
            type=['pdf', 'docx', 'doc', 'txt'],
            accept_multiple_files=True,
            help="Upload multiple documents"
        )
        
        if uploaded_files:
            st.info(f"📁 {len(uploaded_files)} file(s) selected")
            
            if st.button("📥 Upload All", type="primary", use_container_width=True):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                success_count = 0
                fail_count = 0
                
                for idx, uploaded_file in enumerate(uploaded_files):
                    status_text.text(f"Processing {uploaded_file.name}...")
                    
                    try:
                        file_content = uploaded_file.read()
                        text_content, metadata = st.session_state.doc_processor.process_file(
                            file_content, uploaded_file.name
                        )
                        
                        if text_content:
                            # Save document
                            doc_id = st.session_state.data_manager.save_project_document(
                                project_id=selected_proj_id,
                                filename=f"doc_{project['id']}_{uploaded_file.name}",
                                original_filename=uploaded_file.name,
                                file_type=metadata['file_type'],
                                content=text_content,
                                file_size=metadata['file_size'],
                                page_count=metadata.get('page_count', 0),
                                metadata=metadata
                            )
                            
                            if doc_id:
                                # Generate Q&A pairs in background
                                status_text.text(f"Generating Q&A for {uploaded_file.name}...")
                                qa_pairs = st.session_state.qa_generator.generate_qa_pairs(
                                    text_content, 
                                    uploaded_file.name,
                                    max_pairs=10
                                )
                                
                                # Save Q&A pairs to database
                                if qa_pairs:
                                    st.session_state.data_manager.save_document_qa_pairs(doc_id, qa_pairs)
                                
                                success_count += 1
                            else:
                                fail_count += 1
                        else:
                            fail_count += 1
                    
                    except Exception as e:
                        fail_count += 1
                        st.error(f"❌ {uploaded_file.name}: {str(e)}")
                    
                    progress_bar.progress((idx + 1) / len(uploaded_files))
                
                status_text.empty()
                progress_bar.empty()
                
                if success_count > 0:
                    st.success(f"✅ Uploaded {success_count} document(s) with auto-generated Q&A!")
                    st.balloons()
                    st.rerun()
                if fail_count > 0:
                    st.warning(f"⚠️ {fail_count} file(s) failed")
    
    # ========== TAB 3: DOCUMENTS ==========
    with tab3:
        documents = st.session_state.data_manager.get_project_documents(selected_proj_id)
        
        if not documents:
            st.info("📄 No documents yet. Upload files in the **📤 Upload** tab!")
        else:
            st.markdown(f"### 📚 {len(documents)} Document(s)")
            
            for doc in documents:
                with st.expander(f"📄 {doc['original_filename']}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Size", f"{doc['file_size'] / 1024:.1f} KB")
                    with col2:
                        if doc['page_count'] > 0:
                            st.metric("Pages", doc['page_count'])
                    with col3:
                        date = doc['upload_date'].split()[0] if doc['upload_date'] else "N/A"
                        st.metric("Date", date)
                    
                    st.markdown("**Preview:**")
                    preview = doc['content'][:300]
                    st.text(preview + "..." if len(doc['content']) > 300 else preview)
                    
                    if st.button(f"🗑️ Delete", key=f"del_doc_{doc['id']}", use_container_width=True):
                        if st.session_state.data_manager.delete_project_document(doc['id']):
                            st.success("✅ Deleted!")
                            st.rerun()


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
                        
                        # Transcribe with better error handling
                        result = st.session_state.voice_manager.transcribe_audio(temp_path)
                        
                        # Check if there's an error in the result
                        if 'error' in result and result['error']:
                            raise Exception(result['error'])
                        
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
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🤖 AI Models", "🔍 Search Index", "📊 Data", "🔧 System", "🎨 Theme"])
    
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
    
    with tab5:
        st.subheader("🎨 Theme Settings")
        
        st.markdown("""
        **Customize the appearance of Insyte AI**
        
        Choose between Light and Dark themes to match your preference.
        """)
        
        st.markdown("---")
        
        # Current theme detection (based on config file)
        from pathlib import Path
        
        config_path = Path(".streamlit/config.toml")
        
        # Read current theme
        current_theme = "Dark"  # Default
        if config_path.exists():
            with open(config_path, 'r') as f:
                content = f.read()
                if 'backgroundColor = "#FFFFFF"' in content or 'backgroundColor = "#ffffff"' in content:
                    current_theme = "Light"
                elif 'backgroundColor = "#0E1117"' in content:
                    current_theme = "Dark"
        
        st.info(f"🎨 **Current Theme**: {current_theme}")
        
        st.markdown("---")
        
        # Theme selector
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ☀️ Light Theme")
            st.markdown("""
            - Clean white background
            - High contrast for readability
            - Better for bright environments
            - Reduces eye strain in daylight
            """)
            
            if st.button("🌟 Apply Light Theme", use_container_width=True, type="primary" if current_theme == "Light" else "secondary"):
                apply_theme("light")
        
        with col2:
            st.markdown("### 🌙 Dark Theme")
            st.markdown("""
            - Dark background for comfort
            - Reduced eye strain at night
            - Modern professional look
            - Better battery life (OLED screens)
            """)
            
            if st.button("✨ Apply Dark Theme", use_container_width=True, type="primary" if current_theme == "Dark" else "secondary"):
                apply_theme("dark")
        
        st.markdown("---")
        
        # Theme preview info
        with st.expander("ℹ️ About Themes", expanded=False):
            st.markdown("""
            **How Theme Switching Works:**
            
            When you select a theme, the app updates the `.streamlit/config.toml` file with the new color scheme.
            You'll need to **refresh the page** (F5) to see the changes take effect.
            
            **Theme Details:**
            
            **Light Theme:**
            - Background: White (#FFFFFF)
            - Secondary Background: Light Gray (#F0F2F6)
            - Text: Dark Gray (#262730)
            - Primary Color: Red (#FF4B4B)
            
            **Dark Theme (Current in your screenshot):**
            - Background: Dark Navy (#0E1117)
            - Secondary Background: Dark Gray (#262730)
            - Text: Off-White (#FAFAFA)
            - Primary Color: Red (#FF4B4B)
            
            **Note:** After changing themes, please **refresh your browser** (press F5) to apply the new theme.
            """)

def apply_theme(theme_name: str):
    """Apply the selected theme by updating the config.toml file."""
    from pathlib import Path
    
    config_dir = Path(".streamlit")
    config_path = config_dir / "config.toml"
    
    # Ensure directory exists
    config_dir.mkdir(exist_ok=True)
    
    if theme_name == "light":
        # Light theme configuration
        config_content = """# Streamlit Theme Configuration for Insyte AI
# Light Theme - Clean and Professional

[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
fileWatcherType = "auto"
"""
    else:  # dark theme
        # Dark theme configuration (as shown in your screenshot)
        config_content = """# Streamlit Theme Configuration for Insyte AI
# Dark Theme - Modern and Eye-Friendly

[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"
font = "sans serif"

[server]
fileWatcherType = "auto"
"""
    
    # Write the configuration
    try:
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        st.success(f"✅ {theme_name.capitalize()} theme applied successfully!")
        st.info("🔄 **Please refresh the page (Press F5)** to see the theme changes.")
        
        # Add a JavaScript refresh button
        st.markdown("""
        <style>
        .refresh-button {
            display: inline-block;
            padding: 0.5rem 1rem;
            background-color: #FF4B4B;
            color: white;
            text-decoration: none;
            border-radius: 0.5rem;
            font-weight: bold;
            cursor: pointer;
        }
        .refresh-button:hover {
            background-color: #FF6B6B;
        }
        </style>
        <a href="javascript:window.location.reload();" class="refresh-button">🔄 Refresh Page Now</a>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"❌ Failed to apply theme: {str(e)}")

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

def apply_theme(theme_name: str):
    """Apply the selected theme by updating the config.toml file."""
    from pathlib import Path
    import os
    
    config_dir = Path(".streamlit")
    config_path = config_dir / "config.toml"
    
    # Ensure directory exists
    config_dir.mkdir(exist_ok=True)
    
    if theme_name == "light":
        # Light theme configuration
        config_content = """# Streamlit Theme Configuration for Insyte AI
# Light Theme - Clean and Professional

[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
fileWatcherType = "auto"
"""
    else:  # dark theme
        # Dark theme configuration (as shown in your screenshot)
        config_content = """# Streamlit Theme Configuration for Insyte AI
# Dark Theme - Modern and Eye-Friendly

[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"
font = "sans serif"

[server]
fileWatcherType = "auto"
"""
    
    # Write the configuration
    try:
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        st.success(f"✅ {theme_name.capitalize()} theme applied successfully!")
        st.info("🔄 **Please refresh the page (Press F5)** to see the theme changes.")
        
        # Add a JavaScript refresh button
        st.markdown("""
        <style>
        .refresh-button {
            display: inline-block;
            padding: 0.5rem 1rem;
            background-color: #FF4B4B;
            color: white;
            text-decoration: none;
            border-radius: 0.5rem;
            font-weight: bold;
            cursor: pointer;
        }
        .refresh-button:hover {
            background-color: #FF6B6B;
        }
        </style>
        <a href="javascript:window.location.reload();" class="refresh-button">🔄 Refresh Page Now</a>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"❌ Failed to apply theme: {str(e)}")

if __name__ == "__main__":
    main()

