"""
FFmpeg Manager - Download and manage FFmpeg executable
"""

import os
import sys
import requests
import zipfile
from pathlib import Path
from threading import Thread


class FFmpegManager:
    def __init__(self, logger):
        self.logger = logger
        
        # Determine FFmpeg path
        if os.name == 'nt':  # Windows
            self.ffmpeg_dir = Path(os.getenv('APPDATA')) / 'VideoSynthesis'
        else:  # Linux/Mac
            self.ffmpeg_dir = Path.home() / '.VideoSynthesis'
        
        self.ffmpeg_dir.mkdir(parents=True, exist_ok=True)
        self.ffmpeg_path = self.ffmpeg_dir / 'ffmpeg.exe'
        
        # FFmpeg download URL (Windows 64-bit)
        self.download_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    
    def is_installed(self):
        """Check if FFmpeg is installed"""
        installed = self.ffmpeg_path.exists()
        self.logger.debug(f"FFmpeg installed: {installed}")
        return installed
    
    def get_path(self):
        """Get FFmpeg executable path"""
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            # Check if FFmpeg is bundled (shouldn't be in our case)
            base_path = sys._MEIPASS
            bundled_ffmpeg = Path(base_path) / 'ffmpeg.exe'
            if bundled_ffmpeg.exists():
                return str(bundled_ffmpeg)
        
        # Return downloaded FFmpeg path
        return str(self.ffmpeg_path) if self.is_installed() else None
    
    def download(self, progress_callback=None, completion_callback=None):
        """
        Download FFmpeg in a separate thread
        
        Args:
            progress_callback: Function to call with progress (percentage, status_message)
            completion_callback: Function to call when complete (success, message)
        """
        def _download():
            try:
                self.logger.info(f"Starting FFmpeg download from {self.download_url}")
                
                # Download zip file
                if progress_callback:
                    progress_callback(0, "Connecting to server...")
                
                response = requests.get(self.download_url, stream=True)
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                zip_path = self.ffmpeg_dir / 'ffmpeg.zip'
                
                downloaded = 0
                chunk_size = 8192
                
                with open(zip_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            if progress_callback and total_size > 0:
                                percent = int((downloaded / total_size) * 80)  # Reserve 20% for extraction
                                progress_callback(percent, f"Downloading... {downloaded // 1024 // 1024}MB / {total_size // 1024 // 1024}MB")
                
                self.logger.info("Download complete. Extracting...")
                
                if progress_callback:
                    progress_callback(85, "Extracting FFmpeg...")
                
                # Extract ffmpeg.exe from zip
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    # Find ffmpeg.exe in the archive
                    for file_info in zip_ref.filelist:
                        if file_info.filename.endswith('bin/ffmpeg.exe'):
                            # Extract just the ffmpeg.exe file
                            with zip_ref.open(file_info) as source:
                                with open(self.ffmpeg_path, 'wb') as target:
                                    target.write(source.read())
                            break
                
                # Clean up zip file
                zip_path.unlink()
                
                self.logger.info(f"FFmpeg installed successfully at {self.ffmpeg_path}")
                
                if progress_callback:
                    progress_callback(100, "FFmpeg installed successfully!")
                
                if completion_callback:
                    completion_callback(True, "FFmpeg installed successfully!")
                    
            except Exception as e:
                error_msg = f"Failed to download FFmpeg: {str(e)}"
                self.logger.error(error_msg)
                
                if completion_callback:
                    completion_callback(False, error_msg)
        
        # Start download in separate thread
        thread = Thread(target=_download, daemon=True)
        thread.start()
    
    def uninstall(self):
        """
        Uninstall FFmpeg by removing the executable and directory
        
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            if not self.is_installed():
                return (False, "FFmpeg is not installed")
            
            # Remove FFmpeg executable
            if self.ffmpeg_path.exists():
                self.ffmpeg_path.unlink()
                self.logger.info(f"Removed FFmpeg executable: {self.ffmpeg_path}")
            
            # Remove directory if empty
            if self.ffmpeg_dir.exists() and not any(self.ffmpeg_dir.iterdir()):
                self.ffmpeg_dir.rmdir()
                self.logger.info(f"Removed empty directory: {self.ffmpeg_dir}")
            
            return (True, "FFmpeg uninstalled successfully")
            
        except Exception as e:
            error_msg = f"Failed to uninstall FFmpeg: {str(e)}"
            self.logger.error(error_msg)
            return (False, error_msg)
    
    def get_size(self):
        """
        Get the size of FFmpeg installation in MB
        
        Returns:
            float: Size in MB, or 0 if not installed
        """
        try:
            if self.ffmpeg_path.exists():
                size_bytes = self.ffmpeg_path.stat().st_size
                return size_bytes / (1024 * 1024)  # Convert to MB
            return 0
        except Exception:
            return 0
