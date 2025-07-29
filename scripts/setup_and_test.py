"""
Insyte AI - Setup and Testing Script
Initializes the complete AI system and runs basic tests.
"""

import sys
import os
import logging
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from ai.llm_manager import LLMManager
from ai.voice_manager import VoiceManager
from ai.search_manager import SearchManager
from data.data_manager import DataManager
from data.data_loader import DataLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('insyte_setup.log'),
        logging.StreamHandler()
    ]
)

def test_llm_loading():
    """Test LLM loading and basic functionality."""
    print("\n🤖 Testing LLM Manager...")
    
    llm_manager = LLMManager(model_name="tiiuae/falcon-rw-1b")
    
    # Load model
    print("Loading model (this may take a few minutes)...")
    success = llm_manager.load_model(use_4bit=True)
    
    if success:
        print("✅ LLM loaded successfully!")
        
        # Test generation
        test_prompt = "How can I improve my productivity at work?"
        print(f"\nTesting with prompt: '{test_prompt}'")
        
        response = llm_manager.generate_response(test_prompt, max_length=256)
        print(f"Response: {response[:200]}...")
        
        # Get model info
        info = llm_manager.get_model_info()
        print(f"Model info: {info}")
        
        return True
    else:
        print("❌ Failed to load LLM")
        return False

def test_voice_manager():
    """Test voice manager loading."""
    print("\n🎤 Testing Voice Manager...")
    
    voice_manager = VoiceManager(model_size="base")
    
    # Load model
    print("Loading Whisper model...")
    success = voice_manager.load_model()
    
    if success:
        print("✅ Voice model loaded successfully!")
        
        # Get model info
        info = voice_manager.get_model_info()
        print(f"Model info: {info}")
        
        return True
    else:
        print("❌ Failed to load voice model")
        return False

def test_search_manager():
    """Test search manager functionality."""
    print("\n🔍 Testing Search Manager...")
    
    search_manager = SearchManager()
    
    # Load embedding model
    print("Loading embedding model...")
    embedding_success = search_manager.load_embedding_model()
    
    if not embedding_success:
        print("❌ Failed to load embedding model")
        return False
    
    # Create index
    print("Creating search index...")
    index_success = search_manager.create_index()
    
    if not index_success:
        print("❌ Failed to create search index")
        return False
    
    # Test with sample documents
    sample_docs = [
        "The Pomodoro Technique is a time management method that uses 25-minute work intervals.",
        "Getting Things Done (GTD) is a productivity system by David Allen.",
        "Mindfulness meditation can improve focus and reduce stress at work."
    ]
    
    metadata = [
        {"title": "Pomodoro Technique", "category": "time-management"},
        {"title": "GTD Method", "category": "productivity"},
        {"title": "Mindfulness", "category": "wellness"}
    ]
    
    print("Adding sample documents...")
    add_success = search_manager.add_documents(sample_docs, metadata)
    
    if add_success:
        print("✅ Documents added successfully!")
        
        # Test search
        query = "time management techniques"
        print(f"Testing search with query: '{query}'")
        
        results = search_manager.search(query, k=2)
        print(f"Found {len(results)} results:")
        
        for i, result in enumerate(results, 1):
            print(f"  {i}. Score: {result['score']:.3f} - {result['document'][:50]}...")
        
        # Save index
        save_success = search_manager.save_index()
        if save_success:
            print("✅ Search index saved!")
        
        return True
    else:
        print("❌ Failed to add documents to search index")
        return False

def test_data_manager():
    """Test database functionality."""
    print("\n🗄️ Testing Data Manager...")
    
    data_manager = DataManager()
    
    # Initialize database
    print("Initializing database...")
    db_success = data_manager.initialize_database()
    
    if not db_success:
        print("❌ Failed to initialize database")
        return False
    
    print("✅ Database initialized successfully!")
    
    # Test saving data
    session_id = f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Save conversation
    conv_id = data_manager.save_conversation(
        session_id,
        "How can I be more productive?",
        "Try using time-blocking and the Pomodoro Technique for better focus.",
        {"test": True}
    )
    
    if conv_id:
        print(f"✅ Saved conversation with ID: {conv_id}")
    else:
        print("❌ Failed to save conversation")
        return False
    
    # Save document
    doc_id = data_manager.save_document(
        "Test Productivity Note",
        "This is a test note about productivity techniques.",
        "note",
        ["productivity", "test"],
        {"created_by": "setup_script"}
    )
    
    if doc_id:
        print(f"✅ Saved document with ID: {doc_id}")
    else:
        print("❌ Failed to save document")
        return False
    
    # Save productivity metric
    metric_id = data_manager.save_productivity_metric(
        datetime.now().strftime('%Y-%m-%d'),
        "test_metric",
        5.0,
        "Test metric from setup script"
    )
    
    if metric_id:
        print(f"✅ Saved productivity metric with ID: {metric_id}")
    else:
        print("❌ Failed to save productivity metric")
        return False
    
    # Get database stats
    stats = data_manager.get_database_stats()
    print(f"Database stats: {stats}")
    
    return True

def test_data_loader():
    """Test data loading functionality."""
    print("\n📊 Testing Data Loader...")
    
    data_loader = DataLoader()
    
    # Create sample datasets
    print("Creating sample datasets...")
    success = data_loader.create_sample_datasets()
    
    if not success:
        print("❌ Failed to create sample datasets")
        return False
    
    print("✅ Sample datasets created!")
    
    # Test loading datasets
    print("Testing dataset loading...")
    
    # Load prompt-response pairs
    prompts = data_loader.load_prompt_response_pairs()
    print(f"Loaded {len(prompts)} prompt-response pairs")
    
    # Load documents for indexing
    documents = data_loader.load_documents_for_indexing()
    print(f"Loaded {len(documents)} documents for indexing")
    
    # List all datasets
    datasets = data_loader.list_datasets()
    print(f"Available datasets: {[d['filename'] for d in datasets]}")
    
    return True

def main():
    """Run complete system setup and testing."""
    print("🧠 Insyte AI - System Setup and Testing")
    print("=" * 50)
    
    test_results = {}
    
    try:
        # Test data components first (they don't require large downloads)
        test_results['data_manager'] = test_data_manager()
        test_results['data_loader'] = test_data_loader()
        
        # Test search (requires downloading embedding model)
        test_results['search_manager'] = test_search_manager()
        
        # Test voice (requires downloading Whisper model)
        test_results['voice_manager'] = test_voice_manager()
        
        # Test LLM last (largest download)
        print("\n⚠️  LLM testing requires downloading a large model (~1GB)")
        user_input = input("Do you want to test LLM loading? (y/N): ").lower().strip()
        
        if user_input in ['y', 'yes']:
            test_results['llm_manager'] = test_llm_loading()
        else:
            print("⏭️  Skipping LLM test")
            test_results['llm_manager'] = None
        
        # Summary
        print("\n" + "=" * 50)
        print("🎯 SETUP SUMMARY")
        print("=" * 50)
        
        for component, result in test_results.items():
            if result is True:
                print(f"✅ {component}: PASSED")
            elif result is False:
                print(f"❌ {component}: FAILED")
            else:
                print(f"⏭️  {component}: SKIPPED")
        
        # Overall status
        passed_tests = sum(1 for r in test_results.values() if r is True)
        total_tests = sum(1 for r in test_results.values() if r is not None)
        
        if total_tests > 0:
            print(f"\n📊 Tests passed: {passed_tests}/{total_tests}")
            
            if passed_tests == total_tests:
                print("🎉 All tests passed! Your Insyte AI system is ready!")
                print("\n🚀 Next steps:")
                print("1. Run 'streamlit run src/dashboard/main.py' to start the dashboard")
                print("2. Load the AI models in the Settings tab")
                print("3. Start chatting with your AI assistant!")
            else:
                print("⚠️  Some tests failed. Check the logs for details.")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Setup interrupted by user")
    except Exception as e:
        print(f"\n❌ Setup failed with error: {str(e)}")
        logging.error(f"Setup failed: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()
