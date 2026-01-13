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
        Transcribe audio file using Whisper
        
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
                    progress_callback(10, "Loading Whisper model...")
                
                # Get installed model
                model_name = self.whisper_manager.get_installed_model()
                if not model_name:
                    raise Exception("No Whisper model installed")
                
                self.logger.info(f"Loading Whisper model: {model_name}")
                model = self.whisper_manager.load_model(model_name)
                
                if progress_callback:
                    progress_callback(30, f"Transcribing with {model_name} model...")
                
                self.logger.info(f"Starting transcription of: {audio_file_normalized}")
                
                # Transcribe
                # Note: Whisper doesn't provide built-in progress callbacks
                # For long files, we could split into chunks, but for v1 we'll keep it simple
                result = model.transcribe(
                    audio_file_normalized,
                    language=None,  # Auto-detect
                    verbose=False
                )
                
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