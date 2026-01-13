"""
Logger utility for VideoSynthesis
"""

import logging
import os
from pathlib import Path
from datetime import datetime


def setup_logger():
    """Setup application logger with file handler"""
    
    # Create logs directory in AppData
    if os.name == 'nt':  # Windows
        log_dir = Path(os.getenv('APPDATA')) / 'VideoSynthesis'
    else:  # Linux/Mac (for development)
        log_dir = Path.home() / '.VideoSynthesis'
    
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'app.log'
    
    # Configure logger
    logger = logging.getLogger('VideoSynthesis')
    logger.setLevel(logging.DEBUG)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # File handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler (for development)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.info(f"Logger initialized. Log file: {log_file}")
    
    return logger
