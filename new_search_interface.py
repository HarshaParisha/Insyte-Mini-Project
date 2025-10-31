"""
Project-based Document Search Interface
This is the new implementation for show_search_interface() function.
Copy this code to replace the existing function in main.py
"""

def show_search_interface():
    """Project-based document search - Upload files, organize in projects, search with AI."""
    
    st.title("🔍 AI Document Search")
    st.markdown("*Organize documents in projects, upload files (PDF/DOCX/TXT), search with AI*")
    
    # Initialize document processor
    if 'doc_processor' not in st.session_state:
        from src.utils.document_processor import DocumentProcessor
        st.session_state.doc_processor = DocumentProcessor()
    
    # Initialize project tables
    st.session_state.data_manager.create_project_tables()
    
    # Sidebar: Project Management
    with st.sidebar:
        st.header("📁 Projects")
        
        # Create new project
        with st.expander("➕ Create New Project", expanded=False):
            new_project_name = st.text_input("Project Name", key="new_proj_name", 
                                            placeholder="e.g., Marketing Research")
            new_project_desc = st.text_area("Description (optional)", key="new_proj_desc",
                                           placeholder="What this project is about...")
            if st.button("Create Project", type="primary", use_container_width=True):
                if new_project_name.strip():
                    project_id = st.session_state.data_manager.create_project(
                        new_project_name.strip(), 
                        new_project_desc.strip()
                    )
                    if project_id:
                        st.success(f"✅ Created: {new_project_name}")
                        st.rerun()
                    else:
                        st.error("❌ Project already exists!")
                else:
                    st.warning("⚠️ Enter a project name")
        
        st.markdown("---")
        
        # List all projects
        projects = st.session_state.data_manager.get_all_projects()
        
        if projects:
            st.markdown("### Your Projects")
            for proj in projects:
                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.button(
                        f"📁 {proj['name']} ({proj['doc_count']} docs)", 
                        key=f"proj_{proj['id']}",
                        use_container_width=True
                    ):
                        st.session_state.selected_project = proj['id']
                        st.rerun()
                with col2:
                    if st.button("🗑️", key=f"del_{proj['id']}", help="Delete project"):
                        st.session_state.data_manager.delete_project(proj['id'])
                        if st.session_state.get('selected_project') == proj['id']:
                            st.session_state.selected_project = None
                        st.rerun()
        else:
            st.info("👆 Create your first project to start organizing documents!")
    
    # Main Content Area
    if not projects:
        # Welcome screen when no projects exist
        st.markdown("""
        ## Welcome to AI Document Search! 🚀
        
        ### Getting Started:
        
        1. **Create a Project** 📁
           - Click "Create New Project" in the sidebar
           - Give it a name like "Research Papers", "Meeting Notes", or "Technical Docs"
        
        2. **Upload Documents** 📄
           - Upload PDF, DOCX, or TXT files
           - Each project keeps its documents organized
        
        3. **Search with AI** 🔍
           - Ask questions in natural language
           - AI finds relevant information across all your documents
           - Get instant answers with source references
        
        ### Why This is Powerful:
        
        - **🎯 Semantic Understanding**: AI understands meaning, not just keywords
        - **📚 Multiple Formats**: PDF, Word documents, text files
        - **🔒 100% Private**: All processing happens offline on your computer
        - **⚡ Lightning Fast**: FAISS vector search for instant results
        - **📁 Organized**: Keep different projects separate
        
        ---
        
        ### Example Use Cases:
        
        - **📚 Research**: Upload papers, search for specific topics
        - **💼 Work**: Meeting notes, reports, documentation
        - **📖 Learning**: Study materials, course notes
        - **📝 Writing**: Reference materials, sources
        - **🎯 Projects**: Keep project documents organized and searchable
        """)
        return
    
    # Project selected - show project interface
    selected_proj_id = st.session_state.get('selected_project')
    
    if not selected_proj_id and projects:
        # Auto-select first project
        st.session_state.selected_project = projects[0]['id']
        selected_proj_id = projects[0]['id']
    
    if selected_proj_id:
        project = st.session_state.data_manager.get_project_by_id(selected_proj_id)
        
        if not project:
            st.error("❌ Project not found!")
            st.session_state.selected_project = None
            st.rerun()
            return
        
        # Project header
        st.markdown(f"## 📁 {project['name']}")
        if project['description']:
            st.markdown(f"*{project['description']}*")
        st.markdown("---")
        
        # Tabs for different actions
        tab1, tab2, tab3 = st.tabs(["🔍 Search", "📤 Upload Documents", "📚 View Documents"])
        
        # TAB 1: SEARCH
        with tab1:
            documents = st.session_state.data_manager.get_project_documents(selected_proj_id)
            
            if not documents:
                st.info(f"📄 No documents in this project yet. Upload some documents in the '📤 Upload Documents' tab!")
            else:
                # Build search index for this project
                with st.spinner("🔄 Building search index..."):
                    success = st.session_state.search_manager.build_project_index(documents)
                
                if not success:
                    st.error("❌ Failed to build search index. Check logs for details.")
                    return
                
                st.success(f"✅ Ready to search {len(documents)} documents in this project!")
                
                st.markdown("---")
                
                # Search interface
                query = st.text_input(
                    "🔍 What would you like to find?",
                    placeholder="e.g., 'summary of Q4 results' or 'technical specifications'",
                    help="Ask in natural language - AI understands what you mean!"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    max_results = st.slider("Max Results", 1, 20, 5)
                with col2:
                    min_similarity = st.slider("Min Similarity (%)", 0, 100, 25, 5)
                
                if st.button("🔍 Search", type="primary", use_container_width=True) and query:
                    with st.spinner("🤖 AI is analyzing your documents..."):
                        results = st.session_state.search_manager.search_project(
                            query, k=max_results, threshold=min_similarity/100
                        )
                    
                    if results:
                        st.markdown(f"### Found {len(results)} relevant results")
                        st.markdown("---")
                        
                        for i, result in enumerate(results, 1):
                            # Beautiful card layout
                            emoji = result['relevance_emoji']
                            similarity = result['similarity_percentage']
                            filename = result['metadata']['filename']
                            file_type = result['metadata']['file_type']
                            
                            # Color based on relevance
                            if similarity >= 70:
                                border_color = "#4CAF50"  # Green
                            elif similarity >= 50:
                                border_color = "#2196F3"  # Blue
                            elif similarity >= 30:
                                border_color = "#FF9800"  # Orange
                            else:
                                border_color = "#9E9E9E"  # Gray
                            
                            with st.container():
                                st.markdown(f"""
                                <div style="background-color: #1e1e1e; padding: 20px; border-radius: 10px; 
                                            border-left: 5px solid {border_color}; margin-bottom: 20px;">
                                    <div style="display: flex; justify-content: space-between; align-items: center;">
                                        <h3 style="color: #ffffff; margin: 0;">
                                            {emoji} {filename}
                                        </h3>
                                        <span style="background-color: {border_color}; color: white; 
                                                    padding: 5px 15px; border-radius: 20px; font-weight: bold;">
                                            {similarity}% Match
                                        </span>
                                    </div>
                                    <p style="color: #888888; margin: 10px 0 5px 0;">
                                        📎 {file_type.upper()} File
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Show relevant excerpt
                                with st.expander("📖 View Relevant Content", expanded=(i == 1)):
                                    content = result['document']
                                    # Show first 500 characters
                                    if len(content) > 500:
                                        st.markdown(f"```\n{content[:500]}...\n```")
                                        if st.button(f"Show Full Content", key=f"full_{i}"):
                                            st.markdown(f"```\n{content}\n```")
                                    else:
                                        st.markdown(f"```\n{content}\n```")
                        
                    else:
                        st.warning("😕 No results found. Try:")
                        st.markdown("- Lowering the similarity threshold")
                        st.markdown("- Using different keywords")
                        st.markdown("- Uploading more relevant documents")
        
        # TAB 2: UPLOAD
        with tab2:
            st.markdown("### 📤 Upload Documents")
            st.markdown("Supported formats: **PDF**, **DOCX**, **TXT**")
            
            uploaded_files = st.file_uploader(
                "Choose files",
                type=['pdf', 'docx', 'doc', 'txt'],
                accept_multiple_files=True,
                help="Upload multiple documents at once!"
            )
            
            if uploaded_files:
                st.markdown(f"**{len(uploaded_files)} file(s) selected**")
                
                if st.button("📥 Process and Upload All", type="primary", use_container_width=True):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    success_count = 0
                    fail_count = 0
                    
                    for idx, uploaded_file in enumerate(uploaded_files):
                        status_text.text(f"Processing {uploaded_file.name}...")
                        
                        try:
                            # Read file
                            file_content = uploaded_file.read()
                            
                            # Process file
                            text_content, metadata = st.session_state.doc_processor.process_file(
                                file_content, uploaded_file.name
                            )
                            
                            if text_content:
                                # Save to database
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
                                    success_count += 1
                                else:
                                    fail_count += 1
                            else:
                                fail_count += 1
                                st.error(f"❌ Could not extract text from {uploaded_file.name}")
                        
                        except Exception as e:
                            fail_count += 1
                            st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
                        
                        progress_bar.progress((idx + 1) / len(uploaded_files))
                    
                    status_text.empty()
                    progress_bar.empty()
                    
                    if success_count > 0:
                        st.success(f"✅ Successfully uploaded {success_count} document(s)!")
                    if fail_count > 0:
                        st.warning(f"⚠️ Failed to upload {fail_count} document(s)")
                    
                    if success_count > 0:
                        st.balloons()
                        st.rerun()
        
        # TAB 3: VIEW DOCUMENTS
        with tab3:
            documents = st.session_state.data_manager.get_project_documents(selected_proj_id)
            
            if not documents:
                st.info("📄 No documents in this project yet.")
            else:
                st.markdown(f"### 📚 {len(documents)} Document(s) in this project")
                
                for doc in documents:
                    with st.expander(f"📄 {doc['original_filename']} - {doc['file_type'].upper()}"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("📏 Size", f"{doc['file_size'] / 1024:.1f} KB")
                        with col2:
                            if doc['page_count'] > 0:
                                st.metric("📄 Pages", doc['page_count'])
                        with col3:
                            upload_date = doc['upload_date'].split()[0] if doc['upload_date'] else "Unknown"
                            st.metric("📅 Uploaded", upload_date)
                        
                        st.markdown("**Content Preview:**")
                        preview = doc['content'][:500]
                        st.text(preview + "..." if len(doc['content']) > 500 else preview)
                        
                        if st.button(f"🗑️ Delete Document", key=f"del_doc_{doc['id']}"):
                            if st.session_state.data_manager.delete_project_document(doc['id']):
                                st.success("✅ Document deleted")
                                st.rerun()
