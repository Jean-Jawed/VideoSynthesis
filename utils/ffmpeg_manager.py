"""
FFmpeg Manager - Download and manage FFmpeg executable
"""

import os
import sys
import platform
import requests
import zipfile
import stat
from pathlib import Path
from threading import Thread


class FFmpegManager:
    def __init__(self, logger):
        self.logger = logger
        
        # Determine FFmpeg path and download URL based on OS
        system = platform.system()
        self.logger.info(f"Detected OS: {system}")
        
        if system == 'Windows':
            self.ffmpeg_dir = Path(os.getenv('APPDATA', os.path.expanduser('~'))) / 'VideoSynthesis'
            self.ffmpeg_path = self.ffmpeg_dir / 'ffmpeg.exe'
            self.download_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        elif system == 'Darwin':  # macOS
            self.ffmpeg_dir = Path.home() / '.VideoSynthesis'
            self.ffmpeg_path = self.ffmpeg_dir / 'ffmpeg'
            self.download_url = "https://evermeet.cx/ffmpeg/get/zip"
        else:  # Linux
            self.ffmpeg_dir = Path.home() / '.VideoSynthesis'
            self.ffmpeg_path = self.ffmpeg_dir / 'ffmpeg'
            # Default to a generic static build source if needed, otherwise leave as Windows URL as placeholder or handle Linux specifically
            self.download_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz"
        
        self.ffmpeg_dir.mkdir(parents=True, exist_ok=True)
    
    def is_installed(self):
        """Check if FFmpeg is installed"""
        installed = self.ffmpeg_path.exists()
        self.logger.debug(f"FFmpeg installed: {installed}")
        return installed
    
    def get_path(self):
        """Get FFmpeg executable path"""
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            # Check if FFmpeg is bundled
            base_path = sys._MEIPASS
            ffmpeg_exe = 'ffmpeg.exe' if platform.system() == 'Windows' else 'ffmpeg'
            bundled_ffmpeg = Path(base_path) / ffmpeg_exe
            if bundled_ffmpeg.exists():
                return str(bundled_ffmpeg)
        
        # Return downloaded FFmpeg path
        return str(self.ffmpeg_path) if self.is_installed() else None
    
    def get_audio_duration(self, file_path):
        """
        Get duration of audio/video file in seconds using ffmpeg
        
        Args:
            file_path: Path to media file
            
        Returns:
            float: Duration in seconds, or 0.0 if failed
        """
        import subprocess
        import re
        
        ffmpeg_path = self.get_path()
        if not ffmpeg_path:
            return 0.0
            
        try:
            # Use ffmpeg -i to get info (faster than full scan)
            # We use subprocess.PIPE to capture stderr where ffmpeg puts metadata info
            cmd = [ffmpeg_path, '-i', file_path]
            # On Windows, hide the console window
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore', startupinfo=startupinfo)
            
            # Look for Duration: 00:00:00.00
            match = re.search(r"Duration:\s(\d+):(\d+):(\d+\.\d+)", result.stderr)
            if match:
                hours = int(match.group(1))
                minutes = int(match.group(2))
                seconds = float(match.group(3))
                duration = hours * 3600 + minutes * 60 + seconds
                self.logger.debug(f"File duration: {duration}s - {file_path}")
                return duration
                
        except Exception as e:
            self.logger.error(f"Failed to get duration for {file_path}: {e}")
            
        return 0.0
    
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
                
                # Extract ffmpeg from zip based on OS structure
                system = platform.system()
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    if system == 'Windows':
                        # Find ffmpeg.exe in the archive (usually in bin/ folder)
                        for file_info in zip_ref.filelist:
                            if file_info.filename.endswith('bin/ffmpeg.exe'):
                                with zip_ref.open(file_info) as source:
                                    with open(self.ffmpeg_path, 'wb') as target:
                                        target.write(source.read())
                                break
                    elif system == 'Darwin':
                        # Evermeet zip usually contains just 'ffmpeg' at the root
                        for file_info in zip_ref.filelist:
                            if file_info.filename == 'ffmpeg' or file_info.filename.endswith('/ffmpeg'):
                                with zip_ref.open(file_info) as source:
                                    with open(self.ffmpeg_path, 'wb') as target:
                                        target.write(source.read())
                                # Make executable on macOS/Linux
                                os.chmod(self.ffmpeg_path, os.stat(self.ffmpeg_path).st_mode | stat.S_IEXEC)
                                break
                    else:
                        # Fallback or Linux zip handling (if zip)
                        for file_info in zip_ref.filelist:
                            if file_info.filename.endswith('ffmpeg'):
                                with zip_ref.open(file_info) as source:
                                    with open(self.ffmpeg_path, 'wb') as target:
                                        target.write(source.read())
                                os.chmod(self.ffmpeg_path, os.stat(self.ffmpeg_path).st_mode | stat.S_IEXEC)
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
