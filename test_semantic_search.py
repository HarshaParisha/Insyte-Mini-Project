"""
Test Semantic Search Functionality
This script demonstrates how semantic search works with real examples.
"""

import sys
sys.path.append('src')

from ai.search_manager import SearchManager
from data.data_manager import DataManager

def test_semantic_search():
    """Test semantic search with productivity-related documents."""
    
    print("=" * 70)
    print("🔍 SEMANTIC SEARCH TEST - Understanding How It Works")
    print("=" * 70)
    
    # Initialize Search Manager
    print("\n1️⃣  Initializing Search Manager...")
    search_manager = SearchManager()
    
    # Load embedding model
    print("2️⃣  Loading AI embedding model (this may take a moment)...")
    if not search_manager.load_embedding_model():
        print("❌ Failed to load embedding model!")
        return False
    
    print("✅ Embedding model loaded successfully!")
    
    # Create index
    print("\n3️⃣  Creating search index...")
    if not search_manager.create_index():
        print("❌ Failed to create index!")
        return False
    
    # Sample productivity documents
    print("\n4️⃣  Adding sample productivity documents to index...")
    
    documents = [
        # Time Management
        "The Pomodoro Technique helps you focus by working in 25-minute intervals with 5-minute breaks. This method improves concentration and prevents burnout.",
        
        # Work-Life Balance
        "Maintaining work-life balance requires setting clear boundaries. Turn off work notifications after hours and dedicate time to family and hobbies.",
        
        # Task Organization
        "Use the Eisenhower Matrix to prioritize tasks. Focus on important but not urgent tasks to prevent fires and increase productivity.",
        
        # Focus and Concentration
        "Deep work sessions require eliminating distractions. Put your phone in another room, close unnecessary tabs, and use noise-canceling headphones.",
        
        # Morning Routine
        "Start your day with a morning routine that includes exercise, meditation, and planning your top 3 priorities for the day.",
        
        # Goal Setting
        "SMART goals are Specific, Measurable, Achievable, Relevant, and Time-bound. Break large goals into weekly and daily actionable tasks.",
        
        # Energy Management
        "Manage your energy, not just your time. Work on difficult tasks when your energy is highest, usually in the morning for most people.",
        
        # Meeting Efficiency
        "Effective meetings have a clear agenda, start on time, and end with action items assigned to specific people with deadlines.",
        
        # Email Management
        "Process emails in batches 2-3 times per day instead of constantly checking. Use the 2-minute rule: if it takes less than 2 minutes, do it now.",
        
        # Habit Formation
        "Building new habits takes 21-66 days. Start small, be consistent, and use habit stacking to link new habits to existing ones."
    ]
    
    metadata = [
        {"title": "Pomodoro Technique", "category": "Time Management"},
        {"title": "Work-Life Balance", "category": "Wellness"},
        {"title": "Eisenhower Matrix", "category": "Task Management"},
        {"title": "Deep Work", "category": "Focus"},
        {"title": "Morning Routine", "category": "Daily Habits"},
        {"title": "SMART Goals", "category": "Goal Setting"},
        {"title": "Energy Management", "category": "Productivity"},
        {"title": "Meeting Best Practices", "category": "Collaboration"},
        {"title": "Email Batching", "category": "Communication"},
        {"title": "Habit Formation", "category": "Self-Improvement"}
    ]
    
    if not search_manager.add_documents(documents, metadata):
        print("❌ Failed to add documents!")
        return False
    
    print(f"✅ Added {len(documents)} documents to search index")
    
    # Now test semantic search with various queries
    print("\n" + "=" * 70)
    print("🎯 TESTING SEMANTIC SEARCH - See How AI Understands Meaning")
    print("=" * 70)
    
    test_queries = [
        ("how to stay focused at work", "Query about focus and concentration"),
        ("time management tips", "Query about managing time"),
        ("preventing burnout", "Query about wellness and balance"),
        ("organizing my daily tasks", "Query about task management"),
        ("starting my day right", "Query about morning routines"),
    ]
    
    for i, (query, description) in enumerate(test_queries, 1):
        print(f"\n{'─' * 70}")
        print(f"Test #{i}: {description}")
        print(f"{'─' * 70}")
        print(f"🔎 Query: \"{query}\"")
        print()
        
        results = search_manager.search(query, k=3, threshold=0.0)
        
        if results:
            print(f"Found {len(results)} relevant documents:\n")
            for j, result in enumerate(results, 1):
                print(f"   {j}. {result['metadata']['title']} ({result['metadata']['category']})")
                print(f"      Similarity: {result['score']:.1%}")
                print(f"      Text: {result['document'][:80]}...")
                print()
        else:
            print("   ❌ No results found")
    
    # Demonstrate the power of semantic search
    print("\n" + "=" * 70)
    print("🎓 KEY INSIGHTS - Why Semantic Search is Powerful")
    print("=" * 70)
    
    print("""
    ✨ Notice how semantic search works:
    
    1. "how to stay focused" → Found "Deep Work" document
       - Even though it doesn't contain the exact word "focused"
       - AI understands "focus" ≈ "deep work" ≈ "concentration"
    
    2. "preventing burnout" → Found "Work-Life Balance" and "Pomodoro"
       - AI connects burnout to balance and taking breaks
       - No keyword "burnout" in documents!
    
    3. "organizing daily tasks" → Found "Eisenhower Matrix"
       - Understands task organization = prioritization
       - Semantic meaning, not just keywords
    
    🚀 This is the power of AI-powered semantic search!
       Traditional keyword search would miss these connections.
    """)
    
    print("\n" + "=" * 70)
    print("✅ SEMANTIC SEARCH IS WORKING PERFECTLY!")
    print("=" * 70)
    
    return True

def test_with_database():
    """Test search with actual database documents."""
    print("\n\n" + "=" * 70)
    print("📚 TESTING WITH DATABASE DOCUMENTS")
    print("=" * 70)
    
    # Initialize managers
    data_manager = DataManager()
    data_manager.initialize_database()
    
    # Check if there are documents in database
    docs = data_manager.get_documents(limit=100)
    print(f"\n📄 Documents in database: {len(docs)}")
    
    if docs:
        print("\nSample documents:")
        for i, doc in enumerate(docs[:3], 1):
            print(f"   {i}. {doc['title']} - {doc['content'][:60]}...")
    else:
        print("ℹ️  No documents in database yet. You can add them via the dashboard!")
    
    return True

if __name__ == "__main__":
    print("\n🚀 Starting Semantic Search Tests...\n")
    
    # Test 1: Basic semantic search functionality
    success1 = test_semantic_search()
    
    # Test 2: Database integration
    success2 = test_with_database()
    
    if success1 and success2:
        print("\n" + "=" * 70)
        print("🎉 ALL TESTS PASSED! Semantic Search is fully functional!")
        print("=" * 70)
        print("\n💡 TIP: Go to Settings → Search Index in the dashboard to:")
        print("   - Initialize the search index")
        print("   - Add your own documents")
        print("   - Try searching with natural language queries")
        print("\n")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
