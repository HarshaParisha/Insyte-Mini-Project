"""
Test suite for Insyte AI components
"""

import unittest
import sys
import os
import tempfile
import shutil

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from data.data_manager import DataManager
from data.data_loader import DataLoader

class TestDataManager(unittest.TestCase):
    """Test cases for DataManager class."""
    
    def setUp(self):
        """Set up test database."""
        self.test_db = tempfile.mktemp(suffix='.db')
        self.data_manager = DataManager(db_path=self.test_db)
        self.data_manager.initialize_database()
    
    def tearDown(self):
        """Clean up test database."""
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    def test_database_initialization(self):
        """Test database initialization."""
        stats = self.data_manager.get_database_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn('conversations_count', stats)
    
    def test_save_conversation(self):
        """Test saving conversations."""
        conv_id = self.data_manager.save_conversation(
            "test_session",
            "Hello",
            "Hi there!",
            {"test": True}
        )
        self.assertIsNotNone(conv_id)
        self.assertIsInstance(conv_id, int)
    
    def test_get_conversations(self):
        """Test retrieving conversations."""
        # Save a test conversation
        self.data_manager.save_conversation("test", "Hello", "Hi!")
        
        conversations = self.data_manager.get_conversations(limit=10)
        self.assertIsInstance(conversations, list)
        self.assertGreater(len(conversations), 0)

class TestDataLoader(unittest.TestCase):
    """Test cases for DataLoader class."""
    
    def setUp(self):
        """Set up test data directory."""
        self.test_dir = tempfile.mkdtemp()
        self.data_loader = DataLoader(data_dir=self.test_dir)
    
    def tearDown(self):
        """Clean up test directory."""
        shutil.rmtree(self.test_dir)
    
    def test_create_sample_datasets(self):
        """Test sample dataset creation."""
        success = self.data_loader.create_sample_datasets()
        self.assertTrue(success)
        
        # Check if files were created
        self.assertTrue(os.path.exists(
            os.path.join(self.test_dir, "productivity_prompts.json")
        ))
        self.assertTrue(os.path.exists(
            os.path.join(self.test_dir, "knowledge_base.json")
        ))
    
    def test_load_prompt_response_pairs(self):
        """Test loading prompt-response pairs."""
        # Create sample dataset first
        self.data_loader.create_sample_datasets()
        
        pairs = self.data_loader.load_prompt_response_pairs()
        self.assertIsInstance(pairs, list)
        self.assertGreater(len(pairs), 0)
        
        # Check structure
        if pairs:
            prompt, response = pairs[0]
            self.assertIsInstance(prompt, str)
            self.assertIsInstance(response, str)

if __name__ == '__main__':
    unittest.main()
