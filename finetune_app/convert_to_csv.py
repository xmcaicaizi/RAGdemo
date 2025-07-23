"""
Script to convert JSONL files to CSV format with 'Prompt' and 'Completion' columns.
This script reads a JSONL file (either Trainingdata.jsonl or output_converted.jsonl)
and creates a CSV file with two columns: Prompt and Completion.
"""

import json
import csv
import os

def convert_jsonl_to_csv(input_file, output_file):
    """
    Convert JSONL file to CSV with 'Prompt' and 'Completion' columns.
    
    Args:
        input_file (str): Path to the input JSONL file
        output_file (str): Path to the output CSV file
    """
    print(f"Converting {input_file} to {output_file}...")
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Read input file and extract prompts and completions
    data = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                # Parse the JSON line
                json_data = json.loads(line.strip())
                
                # Extract user message (prompt) and assistant message (completion)
                messages = json_data.get("messages", [])
                prompt = ""
                completion = ""
                
                for message in messages:
                    if message.get("role") == "user":
                        prompt = message.get("content", "")
                    elif message.get("role") == "assistant":
                        completion = message.get("content", "")
                
                if prompt and completion:
                    data.append({"Prompt": prompt, "Completion": completion})
                
            except json.JSONDecodeError as e:
                print(f"Error parsing line: {line.strip()}")
                print(f"Error details: {e}")
    
    # Write to CSV file
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        # Write header
        writer.writerow(["Prompt", "Completion"])
        # Write data
        for item in data:
            writer.writerow([item["Prompt"], item["Completion"]])
    
    print(f"Conversion complete. Converted {len(data)} entries to CSV format.")

if __name__ == "__main__":
    # File paths
    input_files = [
        "finetune_app/output_converted.jsonl",
        "finetune_app/Trainingdata.jsonl"
    ]
    
    for input_file in input_files:
        # Generate output filename by replacing .jsonl with .csv
        base_name = os.path.basename(input_file).replace('.jsonl', '')
        output_file = f"finetune_app/{base_name}_test.csv"
        
        # Convert the file
        convert_jsonl_to_csv(input_file, output_file)