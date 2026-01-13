"""
Video Downloader - Download videos using yt-dlp
"""

import os
from threading import Thread
from utils.ffmpeg_manager import FFmpegManager


class VideoDownloader:
    def __init__(self, logger):
        self.logger = logger
        self.ffmpeg_manager = FFmpegManager(logger)
    
    def download(self, url, output_path, progress_callback=None, completion_callback=None):
        """
        Download video/audio from URL using yt-dlp
        
        Args:
            url: Video URL
            output_path: Destination folder
            progress_callback: Function to call with progress messages
            completion_callback: Function to call when complete (success, output_file, message)
        """
        
        def _download():
            try:
                import yt_dlp
                
                output_file = None
                
                # Get FFmpeg path
                ffmpeg_path = self.ffmpeg_manager.get_path()
                
                # yt-dlp options
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                    'ffmpeg_location': ffmpeg_path,
                    'quiet': False,
                    'no_warnings': False,
                }
                
                # Progress hook
                def progress_hook(d):
                    if progress_callback:
                        if d['status'] == 'downloading':
                            percent = d.get('_percent_str', 'N/A')
                            speed = d.get('_speed_str', 'N/A')
                            eta = d.get('_eta_str', 'N/A')
                            progress_callback(f"Downloading: {percent} | Speed: {speed} | ETA: {eta}")
                        elif d['status'] == 'finished':
                            progress_callback("Download finished, now converting to mp3...")
                        elif d['status'] == 'error':
                            progress_callback(f"Error: {d.get('error', 'Unknown error')}")
                
                ydl_opts['progress_hooks'] = [progress_hook]
                
                # Download
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    if progress_callback:
                        progress_callback("Extracting video information...")
                    
                    info = ydl.extract_info(url, download=True)
                    
                    # Get the output filename
                    title = info.get('title', 'audio')
                    # Clean title for filename
                    title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
                    output_file = os.path.join(output_path, f"{title}.mp3")
                    
                    self.logger.info(f"Download successful: {output_file}")
                    
                    if completion_callback:
                        completion_callback(True, output_file, "Download completed successfully")
                        
            except Exception as e:
                error_msg = str(e)
                self.logger.error(f"Download failed: {error_msg}")
                
                # Parse common errors
                if "Private video" in error_msg or "not available" in error_msg:
                    error_msg = "This video is private, unavailable, or region-blocked."
                elif "Invalid URL" in error_msg or "Unsupported URL" in error_msg:
                    error_msg = "Invalid or unsupported URL."
                
                if completion_callback:
                    completion_callback(False, None, error_msg)
        
        # Start download in separate thread
        thread = Thread(target=_download, daemon=True)
        thread.start()
