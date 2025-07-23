"""
Configuration settings for the fine-tuning package.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Global Configuration ---
# Directory for saving fine-tuned models
MODELS_DIR = "./models"

# --- Training Configuration ---
TRAINING_CONFIG = {
    "batch_size": 8,
    "learning_rate": 2e-5,
    "epochs": 3,
    "max_length": 512,
    "warmup_steps": 500,
    "weight_decay": 0.01,
    "gradient_accumulation_steps": 4,
    "evaluation_strategy": "steps",
    "eval_steps": 500,
    "save_steps": 1000,
    "logging_steps": 100,
}

# --- Model Configuration ---
MODEL_CONFIG = {
    "base_model": "Qwen/Qwen1.5-7B",  # Default base model
    "lora_r": 8,
    "lora_alpha": 16,
    "lora_dropout": 0.05,
    "use_lora": True,  # Whether to use LoRA for fine-tuning
}

# --- Data Configuration ---
DATA_CONFIG = {
    "train_file": "train.json",
    "validation_file": "validation.json",
    "test_file": "test.json",
    "data_dir": "./data",
}

# --- Validation function ---
def validate_config():
    """Validate the configuration settings."""
    # Create directories if they don't exist
    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(DATA_CONFIG["data_dir"], exist_ok=True)
    
    print("Fine-tuning configuration validated.")

# Validate configuration when module is loaded
try:
    validate_config()
except Exception as e:
    print(f"Configuration validation error: {e}")