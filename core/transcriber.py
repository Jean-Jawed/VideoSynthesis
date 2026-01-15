"""
Audio Transcriber - Transcribe audio using Whisper
"""

import os
from threading import Thread
from utils.whisper_manager import WhisperManager
from utils.ffmpeg_manager import FFmpegManager


class AudioTranscriber:
    def __init__(self, logger):
        self.logger = logger
        self.whisper_manager = WhisperManager(logger)
        self.ffmpeg_manager = FFmpegManager(logger)
    
    def transcribe(self, audio_file, progress_callback=None, completion_callback=None):
        """
        Transcribe audio file using Whisper with live progress tracking
        
        Args:
            audio_file: Path to audio/video file
            progress_callback: Function to call with progress (percent, message)
            completion_callback: Function to call when complete (success, text, message)
        """
        
        def _transcribe():
            try:
                # Add FFmpeg to PATH for Whisper to find it
                ffmpeg_path = self.ffmpeg_manager.get_path()
                if ffmpeg_path:
                    ffmpeg_dir = os.path.dirname(ffmpeg_path)
                    # Add FFmpeg directory to PATH temporarily
                    os.environ['PATH'] = ffmpeg_dir + os.pathsep + os.environ.get('PATH', '')
                    self.logger.info(f"Added FFmpeg to PATH: {ffmpeg_dir}")
                
                # Normalize path
                audio_file_normalized = os.path.normpath(audio_file)
                
                # Verify file exists
                if not os.path.exists(audio_file_normalized):
                    raise FileNotFoundError(f"Audio file not found: {audio_file_normalized}")
                
                if progress_callback:
                    progress_callback(5, "Analyzing audio duration...")
                
                # Get audio duration
                duration = self.ffmpeg_manager.get_audio_duration(audio_file_normalized)
                self.logger.info(f"Audio duration: {duration}s")
                
                if progress_callback:
                    progress_callback(10, "Loading Whisper model...")
                
                # Get installed model
                model_name = self.whisper_manager.get_installed_model()
                if not model_name:
                    raise Exception("No Whisper model installed")
                
                self.logger.info(f"Loading Whisper model: {model_name}")
                model = self.whisper_manager.load_model(model_name)
                
                if progress_callback:
                    progress_callback(25, f"Starting transcription ({model_name})...")
                
                self.logger.info(f"Starting transcription of: {audio_file_normalized}")
                
                # Custom stream to capture stdout segments
                import sys
                import io
                import re
                
                class ProgressStream(io.StringIO):
                    def __init__(self, callback, total_duration, original_stdout):
                        super().__init__()
                        self.callback = callback
                        self.total_duration = total_duration
                        self.original_stdout = original_stdout
                        # Robust regex for [HH:MM:SS.mmm --> HH:MM:SS.mmm] or [MM:SS.mmm --> MM:SS.mmm]
                        self.pattern = re.compile(r"\[(?:(\d+):)?(\d{2}):(\d{2})\.(\d{3})\s*-->\s*(?:(\d+):)?(\d{2}):(\d{2})\.(\d{3})\]")

                    def write(self, s):
                        # Still write to the real stdout so user can see it in terminal
                        self.original_stdout.write(s)
                        
                        if not s.strip():
                            return
                        
                        # Parse timestamps to estimate progress
                        match = self.pattern.search(s)
                        if match and self.total_duration > 0:
                            # Group 4 is ms, but we need the END timestamp (Group 5-8)
                            h = int(match.group(5)) if match.group(5) else 0
                            m = int(match.group(6))
                            s_val = int(match.group(7))
                            current_time = h * 3600 + m * 60 + s_val
                            
                            # Initial 25% is loading, remaining 75% is transcription
                            percent = 25 + (current_time / self.total_duration * 75)
                            percent = min(99, percent)
                            
                            # Extract the text part of the segment
                            segment_text = s.split("]")[-1].strip()
                            if self.callback:
                                self.callback(percent, f"Transcribing: {segment_text[:50]}...")

                # Intercept stdout during transcription
                original_stdout = sys.stdout
                progress_stream = ProgressStream(progress_callback, duration, original_stdout)
                sys.stdout = progress_stream
                
                try:
                    result = model.transcribe(
                        audio_file_normalized,
                        language=None,  # Auto-detect
                        verbose=True    # MUST be True to see segments in stdout
                    )
                finally:
                    # Restore stdout
                    sys.stdout = original_stdout
                
                transcribed_text = result["text"]
                
                if progress_callback:
                    progress_callback(100, "Transcription complete!")
                
                self.logger.info(f"Transcription successful. Length: {len(transcribed_text)} characters")
                
                if completion_callback:
                    completion_callback(True, transcribed_text, "Success")
                    
            except Exception as e:
                error_msg = f"Transcription failed: {str(e)}"
                self.logger.error(error_msg)
                
                if completion_callback:
                    completion_callback(False, "", error_msg)
        
        # Start transcription in separate thread
        thread = Thread(target=_transcribe, daemon=True)
        thread.start()