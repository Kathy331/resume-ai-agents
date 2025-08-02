"""
Shared utility functions for the resume AI agents project
"""

import os
import logging
from typing import Any
from datetime import datetime


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger"""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        # Configure logger if not already configured
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger


def create_outputs_directory(subdirectory: str = "") -> str:
    """
    Create outputs directory if it doesn't exist
    
    Args:
        subdirectory: Optional subdirectory under outputs/
        
    Returns:
        Full path to the created directory
    """
    if subdirectory:
        outputs_dir = os.path.join("outputs", subdirectory)
    else:
        outputs_dir = "outputs"
    
    os.makedirs(outputs_dir, exist_ok=True)
    return outputs_dir


def format_timestamp(dt: datetime = None) -> str:
    """Format datetime for filenames"""
    if dt is None:
        dt = datetime.now()
    return dt.strftime('%Y%m%d_%H%M%S')


def safe_filename(text: str, max_length: int = 100) -> str:
    """Create a safe filename from text"""
    # Remove or replace unsafe characters
    safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
    filename = ''.join(c if c in safe_chars else '_' for c in text)
    
    # Remove multiple consecutive underscores
    while '__' in filename:
        filename = filename.replace('__', '_')
    
    # Trim to max length
    if len(filename) > max_length:
        filename = filename[:max_length]
    
    # Remove trailing underscore
    filename = filename.strip('_')
    
    return filename or 'unnamed'