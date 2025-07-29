# 🧠 Insyte AI - Self-Hosted Productivity Assistant

**Version:** 1.0.0  
**Status:** Phase 1 - LLM Setup Complete ✅  
**License:** MIT

## 🎯 Project Overview

Insyte AI is a fully offline, self-hosted AI assistant designed for productivity tracking and personal knowledge management. Built with privacy and local control in mind, it runs entirely on your machine without requiring any cloud services.

### 🔧 Core Components

- **🤖 Custom LLM**: Falcon RW-1B for conversational AI
- **🎤 Voice Recognition**: OpenAI Whisper for offline transcription
- **🔍 Semantic Search**: FAISS + SentenceTransformers for document retrieval
- **🗄️ Local Database**: SQLite for secure data storage
- **📊 Dashboard**: Streamlit interface for interaction and analytics

## 🚀 Quick Start (2-Hour Setup)

### Prerequisites

- Python 3.8+ installed
- 8GB+ RAM recommended
- 10GB+ free disk space
- GPU optional (CUDA for faster inference)

### Windows Setup

```bash
# Run the automated setup script
scripts\setup.bat
```

### Linux/macOS Setup

```bash
# Make setup script executable and run
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### Manual Setup

```bash
# 1. Create and activate virtual environment
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Initialize system
python scripts/setup_and_test.py

# 4. Start the dashboard
streamlit run src/dashboard/main.py
```

## 📁 Project Structure

```
Insyte/
├── 📂 src/                     # Source code
│   ├── 📂 ai/                  # AI components
│   │   ├── llm_manager.py      # Language model handling
│   │   ├── voice_manager.py    # Speech recognition
│   │   └── search_manager.py   # Semantic search
│   ├── 📂 data/                # Data management
│   │   ├── data_manager.py     # SQLite operations
│   │   └── data_loader.py      # Dataset loading
│   └── 📂 dashboard/           # Web interface
│       └── main.py             # Streamlit app
├── 📂 data/                    # Data storage
│   ├── 📂 datasets/            # Training data
│   ├── 📂 models/              # Downloaded models
│   └── 📂 database/            # SQLite files
├── 📂 scripts/                 # Setup and utilities
│   ├── setup.bat               # Windows setup
│   ├── setup.sh                # Unix setup
│   └── setup_and_test.py       # System testing
└── 📂 tests/                   # Unit tests
```

## 🎯 Phase 1 Checklist

### ✅ Completed Features

- [x] Project structure created
- [x] Virtual environment setup
- [x] All dependencies installed
- [x] LLM Manager (Falcon RW-1B support)
- [x] Voice Manager (Whisper integration)
- [x] Search Manager (FAISS + embeddings)
- [x] Data Manager (SQLite operations)
- [x] Data Loader (JSON dataset handling)
- [x] Streamlit Dashboard (basic UI)
- [x] Sample datasets created
- [x] Testing framework
- [x] Setup automation scripts

### 🔄 Next Phase Goals

- [ ] Fine-tuning pipeline for custom data
- [ ] Advanced productivity metrics
- [ ] Voice command processing
- [ ] Document OCR integration
- [ ] Advanced visualization
- [ ] Mobile-responsive UI
- [ ] Backup/restore functionality

## 🛠️ Usage Guide

### Starting the System

1. **Activate Environment**: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Unix)
2. **Launch Dashboard**: `streamlit run src/dashboard/main.py`
3. **Open Browser**: Navigate to `http://localhost:8501`

### First-Time Setup

1. **Load Models**: Go to Settings → AI Models → Load LLM Model
2. **Initialize Search**: Settings → Search Index → Initialize Search
3. **Create Sample Data**: Settings → Data → Create Sample Datasets
4. **Start Chatting**: Navigate to AI Chat tab

### Key Features

- **💬 AI Chat**: Conversational interface with the LLM
- **📊 Analytics**: Productivity metrics and visualizations
- **🔍 Search**: Semantic search through your documents
- **🎤 Voice**: Audio transcription capabilities
- **⚙️ Settings**: Model management and system configuration

## 🔧 Configuration

### Model Settings

- **LLM Model**: `tiiuae/falcon-rw-1b` (lightweight, good performance)
- **Whisper Model**: `base` (balance of speed/accuracy)
- **Embedding Model**: `all-MiniLM-L6-v2` (384-dim, fast)

### Hardware Requirements

- **Minimum**: 4GB RAM, CPU-only inference
- **Recommended**: 8GB+ RAM, NVIDIA GPU with 4GB+ VRAM
- **Optimal**: 16GB+ RAM, RTX 3070+ or equivalent

### Performance Tuning

- Enable 4-bit quantization for memory efficiency
- Use GPU acceleration when available
- Adjust batch sizes based on available RAM

## 📊 Sample Data

The system includes sample datasets for immediate testing:

### Productivity Prompts (`productivity_prompts.json`)

- Focus improvement techniques
- Task organization methods
- Work-life balance strategies

### Knowledge Base (`knowledge_base.json`)

- Pomodoro Technique guide
- Getting Things Done overview
- Mindfulness and productivity tips

## 🛡️ Privacy & Security

- **100% Offline**: No data leaves your machine
- **Local Storage**: All data stored in SQLite locally
- **No Telemetry**: No tracking or analytics sent anywhere
- **Open Source**: Full transparency in code and functionality

## 🐛 Troubleshooting

### Common Issues

**Model Loading Fails**

- Ensure sufficient RAM available
- Check internet connection for initial model download
- Try smaller model variants (e.g., "tiny" Whisper model)

**Slow Performance**

- Enable GPU acceleration if available
- Use 4-bit quantization for LLM
- Reduce max_length for text generation

**Import Errors**

- Verify virtual environment is activated
- Reinstall requirements: `pip install -r requirements.txt --force-reinstall`

### Logs and Debugging

- Setup logs: `insyte_setup.log`
- Application logs: Check terminal output
- Enable debug logging in code for detailed information

## 🤝 Contributing

This is a self-contained project designed for personal use. However, contributions and improvements are welcome:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request with detailed description

## 📝 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- **Hugging Face**: Transformers library and model hosting
- **OpenAI**: Whisper speech recognition model
- **Facebook**: FAISS vector search library
- **Streamlit**: Web application framework

---

**Built with ❤️ for productivity enthusiasts who value privacy and control over their AI tools.**

_Last Updated: July 29, 2025_
