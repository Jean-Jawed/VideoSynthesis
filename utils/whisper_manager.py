"""
Whisper Manager - Download and manage Whisper models
"""

import os
import whisper
from pathlib import Path
from threading import Thread


class WhisperManager:
    def __init__(self, logger):
        self.logger = logger
        
        # Whisper cache directory (default: ~/.cache/whisper)
        self.cache_dir = Path.home() / ".cache" / "whisper"
        
        # Available models
        self.models = {
            'base': {'size': '150 MB', 'file': 'base.pt'},
            'medium': {'size': '1.5 GB', 'file': 'medium.pt'},
            'large': {'size': '3 GB', 'file': 'large-v3.pt'}  # Whisper v3
        }
    
    def is_installed(self, model_name='base'):
        """Check if a specific Whisper model is installed"""
        if model_name not in self.models:
            return False
        
        model_file = self.models[model_name]['file']
        model_path = self.cache_dir / model_file
        
        installed = model_path.exists()
        self.logger.debug(f"Whisper model '{model_name}' installed: {installed}")
        return installed
    
    def get_installed_model(self):
        """Get the first installed model, or None"""
        for model_name in ['base', 'medium', 'large']:
            if self.is_installed(model_name):
                return model_name
        return None
    
    def download(self, model_name='base', progress_callback=None, completion_callback=None):
        """
        Download a Whisper model in a separate thread
        
        Args:
            model_name: 'base', 'medium', or 'large'
            progress_callback: Function to call with progress (percentage, status_message)
            completion_callback: Function to call when complete (success, message)
        """
        if model_name not in self.models:
            if completion_callback:
                completion_callback(False, f"Invalid model: {model_name}")
            return
        
        def _download():
            try:
                self.logger.info(f"Starting Whisper '{model_name}' model download")
                
                if progress_callback:
                    progress_callback(0, f"Downloading Whisper {model_name} model...")
                
                # This will automatically download the model to cache
                # Whisper handles the download internally
                model = whisper.load_model(model_name, download_root=str(self.cache_dir))
                
                self.logger.info(f"Whisper '{model_name}' model downloaded successfully")
                
                if progress_callback:
                    progress_callback(100, f"Whisper {model_name} model installed!")
                
                if completion_callback:
                    completion_callback(True, f"Whisper {model_name} model installed successfully!")
                    
            except Exception as e:
                error_msg = f"Failed to download Whisper model: {str(e)}"
                self.logger.error(error_msg)
                
                if completion_callback:
                    completion_callback(False, error_msg)
        
        # Start download in separate thread
        thread = Thread(target=_download, daemon=True)
        thread.start()
    
    def load_model(self, model_name='base'):
        """Load a Whisper model for transcription"""
        try:
            self.logger.info(f"Loading Whisper model: {model_name}")
            model = whisper.load_model(model_name, download_root=str(self.cache_dir))
            return model
        except Exception as e:
            self.logger.error(f"Failed to load Whisper model: {str(e)}")
            raise
