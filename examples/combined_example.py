"""
Example script demonstrating how to use both RAG and fine-tuning packages together.
This script shows how to:
1. Build a knowledge base using the RAG package
2. Fine-tune a model using the fine-tuning package
3. Use the fine-tuned model with the RAG system
"""

import os
import json
from typing import Dict, List

from rag_app.rag_module import RAGManager
from finetune_app.finetune_module import FineTuneManager


def main():
    """Main function demonstrating the combined workflow."""
    print("=" * 50)
    print("RAG and Fine-tuning Combined Example")
    print("=" * 50)
    
    # Step 1: Initialize both managers
    print("\n1. Initializing managers...")
    rag_manager = RAGManager()
    ft_manager = FineTuneManager()
    
    # Step 2: Build knowledge base
    print("\n2. Building knowledge base...")
    csv_file = "questions.csv"
    if os.path.exists(csv_file):
        rag_manager.build_from_csv(csv_file)
    else:
        print(f"Warning: {csv_file} not found. Skipping knowledge base building.")
    
    # Step 3: Perform a search to see baseline results
    print("\n3. Performing baseline search...")
    query = "python里怎么定义一个函数？"
    baseline_results = rag_manager.search(query=query, top_k=3)
    print_search_results(baseline_results, "Baseline Search Results")
    
    # Step 4: Prepare fine-tuning data (simulated)
    print("\n4. Preparing fine-tuning data...")
    # In a real scenario, you would have actual training data
    # Here we're just simulating the process
    data_file = "examples/simulated_training_data.json"
    if not os.path.exists("examples"):
        os.makedirs("examples")
    
    # Create a simple simulated training dataset
    create_simulated_training_data(data_file, query)
    
    # Step 5: Fine-tune a model
    print("\n5. Fine-tuning model (simulated)...")
    # In a real scenario, this would actually fine-tune the model
    # Here we're just simulating the process
    ft_manager.prepare_data(data_file)
    ft_manager.load_model()
    model_path = ft_manager.fine_tune()
    
    # Step 6: Evaluate the fine-tuned model
    print("\n6. Evaluating fine-tuned model...")
    metrics = ft_manager.evaluate(model_path)
    print("Evaluation metrics:")
    for metric, value in metrics.items():
        print(f"  - {metric}: {value:.4f}")
    
    # Step 7: Perform reranked search
    print("\n7. Performing reranked search...")
    reranked_results = rag_manager.search_with_rerank(query=query, top_k=3)
    print_search_results(reranked_results, "Reranked Search Results")
    
    print("\n" + "=" * 50)
    print("Example completed successfully!")
    print("=" * 50)


def print_search_results(results: Dict, title: str):
    """Print search results in a readable format."""
    print(f"\n{title}:")
    print(f"Query: {results['query']}")
    print(f"Provider: {results['provider']}")
    
    if 'rerank_strategy' in results:
        print(f"Rerank Strategy: {results['rerank_strategy']}")
    
    print("\nResults:")
    for i, result in enumerate(results['results']):
        print(f"\n  Result {i+1}:")
        print(f"  - ID: {result['id']}")
        print(f"  - Content: {result['content'][:100]}..." if len(result['content']) > 100 else f"  - Content: {result['content']}")
        print(f"  - Distance: {result['distance']:.4f}")
        
        if 'rerank_score' in result:
            print(f"  - Original Rank: {result['original_rank']}")
            print(f"  - Rerank Score: {result['rerank_score']:.4f}")
            print(f"  - Final Rank: {result['final_rank']}")


def create_simulated_training_data(file_path: str, example_query: str):
    """Create a simulated training dataset for demonstration purposes."""
    data = {
        "train": [
            {
                "instruction": "Answer the following programming question",
                "input": example_query,
                "output": "In Python, you define a function using the 'def' keyword followed by the function name and parentheses. For example: def my_function():"
            },
            {
                "instruction": "Explain this programming concept",
                "input": "What is a variable in Python?",
                "output": "A variable in Python is a named location in memory that stores a value. You can assign values to variables using the equals sign (=)."
            }
        ],
        "validation": [
            {
                "instruction": "Answer the following question",
                "input": "How do I create a list in Python?",
                "output": "You can create a list in Python by enclosing comma-separated values in square brackets. For example: my_list = [1, 2, 3]"
            }
        ]
    }
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Simulated training data created at {file_path}")


if __name__ == "__main__":
    main()