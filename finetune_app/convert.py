"""
Script to convert output_beta.jsonl to match the format of Trainingdata.jsonl.
The script reads output_beta.jsonl and creates a new file with the same format as Trainingdata.jsonl.
"""

import json
import os

def convert_jsonl_format(input_file, output_file):
    """
    Convert the format of output_beta.jsonl to match Trainingdata.jsonl.
    
    Args:
        input_file (str): Path to the input file (output_beta.jsonl)
        output_file (str): Path to the output file to be created
    """
    print(f"Converting {input_file} to {output_file}...")
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Read input file and convert format
    converted_data = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                # Parse the JSON line
                data = json.loads(line.strip())
                
                # Create the new format
                new_format = {
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant"},
                        {"role": "user", "content": data["instruction"]},
                        {"role": "assistant", "content": data["output"]}
                    ]
                }
                
                # Add to converted data
                converted_data.append(new_format)
            except json.JSONDecodeError as e:
                print(f"Error parsing line: {line.strip()}")
                print(f"Error details: {e}")
            except KeyError as e:
                print(f"Missing key in data: {e}")
                print(f"Data: {data}")
    
    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in converted_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    print(f"Conversion complete. Converted {len(converted_data)} entries.")

if __name__ == "__main__":
    # File paths
    input_file = "finetune_app/output_beta.jsonl"
    output_file = "finetune_app/output_converted.jsonl"
    
    # Convert the file
    convert_jsonl_format(input_file, output_file)