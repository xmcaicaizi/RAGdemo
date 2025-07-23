"""
Tests for the fine-tuning package.
"""

import os
import unittest
from unittest.mock import patch

from finetune_app.finetune_module import FineTuneManager


class TestFineTuneManager(unittest.TestCase):
    """Test cases for the FineTuneManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a test instance with mocked dependencies
        with patch('finetune_app.finetune_module.os.makedirs'):
            self.manager = FineTuneManager()
    
    def test_prepare_data(self):
        """Test the data preparation functionality."""
        with patch('finetune_app.finetune_module.os.path.exists', return_value=True):
            output_dir = self.manager.prepare_data("dummy_data.json")
            self.assertIsNotNone(output_dir)
    
    def test_load_model(self):
        """Test the model loading functionality."""
        # Mock the model loading to avoid actual downloads
        with patch('finetune_app.finetune_module.print'):
            self.manager.load_model("test_model")
            # In a real test, we would assert that the model and tokenizer are properly loaded
    
    def test_fine_tune(self):
        """Test the fine-tuning process."""
        with patch('finetune_app.finetune_module.print'):
            output_path = self.manager.fine_tune()
            self.assertIsNotNone(output_path)
    
    def test_evaluate(self):
        """Test the model evaluation functionality."""
        with patch('finetune_app.finetune_module.print'):
            metrics = self.manager.evaluate()
            self.assertIsInstance(metrics, dict)
            self.assertIn('accuracy', metrics)


if __name__ == '__main__':
    unittest.main()