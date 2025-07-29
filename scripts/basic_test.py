"""
Simple test to verify basic functionality without model loading
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_imports():
    """Test that all modules can be imported."""
    print("🧪 Testing module imports...")
    
    try:
        from data.data_manager import DataManager
        print("✅ DataManager import successful")
    except Exception as e:
        print(f"❌ DataManager import failed: {e}")
        return False
    
    try:
        from data.data_loader import DataLoader
        print("✅ DataLoader import successful")
    except Exception as e:
        print(f"❌ DataLoader import failed: {e}")
        return False
    
    try:
        from ai.llm_manager import LLMManager
        print("✅ LLMManager import successful")
    except Exception as e:
        print(f"❌ LLMManager import failed: {e}")
        return False
    
    try:
        from ai.voice_manager import VoiceManager
        print("✅ VoiceManager import successful")
    except Exception as e:
        print(f"❌ VoiceManager import failed: {e}")
        return False
        
    try:
        from ai.search_manager import SearchManager
        print("✅ SearchManager import successful")
    except Exception as e:
        print(f"❌ SearchManager import failed: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic functionality without model loading."""
    print("\n🧪 Testing basic functionality...")
    
    try:
        from data.data_manager import DataManager
        from data.data_loader import DataLoader
        
        # Test DataManager
        data_manager = DataManager()
        success = data_manager.initialize_database()
        
        if success:
            print("✅ Database initialization successful")
        else:
            print("❌ Database initialization failed")
            return False
        
        # Test DataLoader
        data_loader = DataLoader()
        success = data_loader.create_sample_datasets()
        
        if success:
            print("✅ Sample datasets created successfully")
            
            # List datasets
            datasets = data_loader.list_datasets()
            print(f"📊 Created {len(datasets)} datasets:")
            for dataset in datasets:
                print(f"   - {dataset['filename']}: {dataset.get('record_count', 'Unknown')} records")
        else:
            print("❌ Sample dataset creation failed")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧠 Insyte AI - Basic System Test")
    print("=" * 40)
    
    # Test imports
    import_success = test_imports()
    
    if not import_success:
        print("\n❌ Import tests failed. Please check your Python environment.")
        return
    
    # Test basic functionality
    basic_success = test_basic_functionality()
    
    if basic_success:
        print("\n🎉 Basic system tests passed!")
        print("\n🚀 Next steps:")
        print("1. Install missing dependencies: pip install -r requirements.txt")
        print("2. Run full setup: python scripts/setup_and_test.py")
        print("3. Start dashboard: streamlit run src/dashboard/main.py")
    else:
        print("\n❌ Basic functionality tests failed.")

if __name__ == "__main__":
    main()
