"""
Insyte AI - Data Loader
Loads and processes JSON datasets for training and testing.
"""

import json
import os
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
import logging

class DataLoader:
    def __init__(self, data_dir: str = "data/datasets"):
        """
        Initialize the Data Loader.
        
        Args:
            data_dir: Directory containing dataset files
        """
        self.data_dir = data_dir
        self.logger = logging.getLogger(__name__)
        
    def load_json_dataset(self, filename: str) -> Optional[List[Dict]]:
        """
        Load a JSON dataset file.
        
        Args:
            filename: Name of the JSON file to load
            
        Returns:
            List of dictionaries containing the dataset, None if failed
        """
        filepath = os.path.join(self.data_dir, filename)
        
        if not os.path.exists(filepath):
            self.logger.error(f"Dataset file not found: {filepath}")
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.logger.info(f"Loaded {len(data)} records from {filename}")
            return data
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in {filename}: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to load {filename}: {str(e)}")
            return None
    
    def load_prompt_response_pairs(self, filename: str = "productivity_prompts.json") -> List[Tuple[str, str]]:
        """
        Load prompt-response pairs for training/testing.
        
        Args:
            filename: JSON file containing prompt-response pairs
            
        Returns:
            List of (prompt, response) tuples
        """
        data = self.load_json_dataset(filename)
        if not data:
            return []
        
        pairs = []
        for item in data:
            if 'prompt' in item and 'response' in item:
                pairs.append((item['prompt'], item['response']))
            elif 'input' in item and 'output' in item:
                pairs.append((item['input'], item['output']))
            else:
                self.logger.warning(f"Invalid format in dataset item: {item}")
        
        self.logger.info(f"Loaded {len(pairs)} prompt-response pairs")
        return pairs
    
    def load_documents_for_indexing(self, filename: str = "knowledge_base.json") -> List[Dict]:
        """
        Load documents for semantic search indexing.
        
        Args:
            filename: JSON file containing documents
            
        Returns:
            List of document dictionaries
        """
        data = self.load_json_dataset(filename)
        if not data:
            return []
        
        documents = []
        for item in data:
            if 'content' in item:
                doc = {
                    'content': item['content'],
                    'title': item.get('title', 'Untitled'),
                    'category': item.get('category', 'general'),
                    'tags': item.get('tags', []),
                    'metadata': {k: v for k, v in item.items() 
                               if k not in ['content', 'title', 'category', 'tags']}
                }
                documents.append(doc)
            else:
                self.logger.warning(f"Document missing content field: {item}")
        
        self.logger.info(f"Loaded {len(documents)} documents for indexing")
        return documents
    
    def save_json_dataset(self, data: List[Dict], filename: str) -> bool:
        """
        Save data to a JSON dataset file.
        
        Args:
            data: List of dictionaries to save
            filename: Name of the JSON file to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved {len(data)} records to {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save {filename}: {str(e)}")
            return False
    
    def validate_dataset(self, data: List[Dict], required_fields: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate that a dataset has required fields.
        
        Args:
            data: Dataset to validate
            required_fields: List of required field names
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not isinstance(data, list):
            errors.append("Dataset must be a list of dictionaries")
            return False, errors
        
        if not data:
            errors.append("Dataset is empty")
            return False, errors
        
        for i, item in enumerate(data):
            if not isinstance(item, dict):
                errors.append(f"Item {i} is not a dictionary")
                continue
            
            for field in required_fields:
                if field not in item:
                    errors.append(f"Item {i} missing required field: {field}")
                elif not item[field] or (isinstance(item[field], str) and not item[field].strip()):
                    errors.append(f"Item {i} has empty value for field: {field}")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def create_sample_datasets(self) -> bool:
        """
        Create sample datasets for testing and development.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create productivity prompts dataset
            productivity_prompts = [
                {
                    "prompt": "How can I improve my focus during work hours?",
                    "response": "Here are several strategies to improve focus: 1) Use the Pomodoro Technique (25-minute focused work sessions), 2) Eliminate distractions by turning off notifications, 3) Create a dedicated workspace, 4) Take regular breaks to prevent mental fatigue, 5) Practice mindfulness or meditation, 6) Prioritize tasks using methods like Eisenhower Matrix.",
                    "category": "productivity",
                    "tags": ["focus", "concentration", "work", "time-management"]
                },
                {
                    "prompt": "What's the best way to organize my daily tasks?",
                    "response": "Effective task organization involves: 1) Start with a brain dump of all tasks, 2) Categorize by urgency and importance, 3) Use a system like Getting Things Done (GTD) or Kanban, 4) Set specific deadlines and time estimates, 5) Review and adjust your list daily, 6) Use digital tools like Todoist, Notion, or even simple notebooks, 7) Focus on 3-5 high-priority tasks per day.",
                    "category": "productivity",
                    "tags": ["organization", "tasks", "planning", "time-management"]
                },
                {
                    "prompt": "How do I manage work-life balance effectively?",
                    "response": "Achieving work-life balance requires: 1) Set clear boundaries between work and personal time, 2) Create dedicated spaces for work and relaxation, 3) Use time-blocking to allocate time for different activities, 4) Learn to say 'no' to non-essential commitments, 5) Practice self-care and stress management, 6) Communicate your boundaries to colleagues and family, 7) Regularly assess and adjust your priorities.",
                    "category": "wellness",
                    "tags": ["work-life-balance", "boundaries", "stress-management", "well-being"]
                }
            ]
            
            # Create knowledge base dataset
            knowledge_base = [
                {
                    "title": "Pomodoro Technique Guide",
                    "content": "The Pomodoro Technique is a time management method that uses a timer to break work into intervals, traditionally 25 minutes in length, separated by short breaks. These intervals are called pomodoros. The technique was developed by Francesco Cirillo in the late 1980s. The method is based on the idea that frequent breaks can improve mental agility and focus.",
                    "category": "productivity-methods",
                    "tags": ["time-management", "focus", "productivity", "technique"]
                },
                {
                    "title": "Getting Things Done (GTD) Overview",
                    "content": "Getting Things Done (GTD) is a personal productivity system developed by David Allen. The GTD method rests on the idea of moving planned tasks and projects out of the mind by recording them externally and then breaking them into actionable work items. This allows attention to be focused on taking action on tasks, rather than recalling them.",
                    "category": "productivity-methods",
                    "tags": ["gtd", "productivity", "organization", "system"]
                },
                {
                    "title": "Mindfulness and Productivity",
                    "content": "Mindfulness can significantly enhance productivity by improving focus, reducing stress, and increasing self-awareness. Regular meditation practice, even just 10 minutes daily, can help develop better attention control, emotional regulation, and cognitive flexibility. Mindful work practices include single-tasking, regular check-ins with your mental state, and conscious breathing during stressful moments.",
                    "category": "wellness",
                    "tags": ["mindfulness", "meditation", "stress-reduction", "focus"]
                }
            ]
            
            # Save datasets
            success = True
            success &= self.save_json_dataset(productivity_prompts, "productivity_prompts.json")
            success &= self.save_json_dataset(knowledge_base, "knowledge_base.json")
            
            if success:
                self.logger.info("Sample datasets created successfully")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to create sample datasets: {str(e)}")
            return False
    
    def get_dataset_info(self, filename: str) -> Dict[str, Any]:
        """
        Get information about a dataset file.
        
        Args:
            filename: Name of the dataset file
            
        Returns:
            Dictionary with dataset information
        """
        filepath = os.path.join(self.data_dir, filename)
        
        if not os.path.exists(filepath):
            return {"status": "not_found", "filename": filename}
        
        try:
            data = self.load_json_dataset(filename)
            if not data:
                return {"status": "invalid", "filename": filename}
            
            # Analyze dataset structure
            sample_item = data[0] if data else {}
            fields = list(sample_item.keys()) if isinstance(sample_item, dict) else []
            
            file_size = os.path.getsize(filepath) / 1024  # KB
            
            return {
                "status": "valid",
                "filename": filename,
                "record_count": len(data),
                "sample_fields": fields,
                "file_size_kb": round(file_size, 2)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "filename": filename,
                "error": str(e)
            }
    
    def list_datasets(self) -> List[Dict[str, Any]]:
        """
        List all JSON dataset files in the data directory.
        
        Returns:
            List of dataset information dictionaries
        """
        if not os.path.exists(self.data_dir):
            return []
        
        datasets = []
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.json'):
                info = self.get_dataset_info(filename)
                datasets.append(info)
        
        return datasets
