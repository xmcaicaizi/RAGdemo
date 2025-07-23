"""
Test script for the Knowledge Graph module.
This script demonstrates how to use the KGManager to build and query a knowledge graph.
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_app.kg_module import KGManager


async def test_kg_functionality():
    """Test the knowledge graph functionality."""
    print("Testing Knowledge Graph functionality...")
    
    # Initialize the KG manager
    kg_manager = KGManager()
    
    try:
        # Initialize LightRAG
        await kg_manager.initialize()
        print("✓ LightRAG initialized successfully")
        
        # Insert sample text
        sample_text = """
        Alan Turing was a British mathematician, computer scientist, logician, cryptanalyst, 
        philosopher, and theoretical biologist. He was highly influential in the development 
        of theoretical computer science, providing a formalisation of the concepts of algorithm 
        and computation with the Turing machine. Turing is widely considered to be the father 
        of theoretical computer science and artificial intelligence.
        """
        
        kg_manager.insert_text(sample_text)
        print("✓ Sample text inserted into knowledge graph")
        
        # Query the knowledge graph
        query_result = kg_manager.query("Who was Alan Turing?", mode="hybrid")
        print("✓ Knowledge graph query executed successfully")
        print("Query result:", query_result["result"])
        
        print("\nAll tests passed! Knowledge Graph module is working correctly.")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(test_kg_functionality())