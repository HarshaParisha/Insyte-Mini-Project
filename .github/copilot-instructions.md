# Insyte AI - Copilot Instructions

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

## Project Context

This is Insyte AI, a self-hosted offline AI productivity assistant with the following architecture:

### Core Components

- **AI Models**: Falcon RW-1B LLM, Whisper speech recognition, SentenceTransformers embeddings
- **Data**: SQLite database, FAISS vector search, JSON datasets
- **Interface**: Streamlit dashboard with multiple tabs/features
- **Privacy**: 100% offline, no cloud dependencies

### Code Style Guidelines

- Use clear, descriptive function and variable names
- Include comprehensive docstrings for all classes and methods
- Handle exceptions gracefully with proper logging
- Follow Python PEP 8 conventions
- Add type hints where appropriate

### Architecture Patterns

- **Manager Classes**: Each AI component has a dedicated manager (LLMManager, VoiceManager, etc.)
- **Database First**: All user data stored in SQLite with proper normalization
- **Lazy Loading**: Models loaded on-demand to save memory
- **Error Resilience**: Graceful degradation when components fail

### Dependencies

- PyTorch ecosystem for ML models
- Streamlit for web interface
- SQLite for data persistence
- FAISS for vector search
- No cloud APIs or external services

### Security Considerations

- All data processing happens locally
- No network requests except for initial model downloads
- Secure file handling for uploads
- Input validation for all user inputs

When suggesting code changes:

1. Maintain the offline-first architecture
2. Ensure compatibility with existing manager classes
3. Include proper error handling and logging
4. Follow the established patterns for database operations
5. Consider memory efficiency for model operations
