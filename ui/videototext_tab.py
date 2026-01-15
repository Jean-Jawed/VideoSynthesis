"""
Video to Text Tab - Transcribe multiple audio/video files using Whisper
"""

import customtkinter as ctk
import time
from tkinter import messagebox
from ui.widgets import FileInputList, StatusLog


class VideoToTextTab:
    def __init__(self, parent, transcription_manager, logger):
        self.parent = parent
        self.transcription_manager = transcription_manager
        self.logger = logger
        
        # Set callback for status updates
        self.transcription_manager.add_status_callback(self.update_status_display)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Create the Video to Text tab UI"""
        
        # Main container
        container = ctk.CTkFrame(self.parent, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Configure grid
        container.grid_rowconfigure(3, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            container,
            text="Video to Text Transcription",
            font=("Arial", 20, "bold")
        )
        title_label.grid(row=0, column=0, sticky="w", pady=(0, 20))
        
        # File Selection Section
        file_frame = ctk.CTkFrame(container, corner_radius=10)
        file_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        # File Input List Widget
        self.file_list = FileInputList(file_frame, fg_color="transparent")
        self.file_list.pack(fill="x", padx=20, pady=15)
        
        # Transcribe Button
        self.transcribe_btn = ctk.CTkButton(
            container,
            text="Transcribe All Files",
            height=45,
            corner_radius=10,
            font=("Arial", 14, "bold"),
            command=self.start_transcriptions
        )
        self.transcribe_btn.grid(row=2, column=0, sticky="ew", pady=15)
        
        # Status Log Section
        self.status_log = StatusLog(container, title="Transcription Status:")
        self.status_log.grid(row=3, column=0, sticky="nsew", pady=(0, 10))
        
        # Action buttons
        action_frame = ctk.CTkFrame(container, fg_color="transparent")
        action_frame.grid(row=4, column=0, sticky="ew", pady=(0, 10))
        
        # Info label
        info_label = ctk.CTkLabel(
            action_frame,
            text="💡 Completed transcriptions appear in the 'Transcription Results' tab",
            font=("Arial", 11),
            text_color="gray50"
        )
        info_label.pack(side="left")
        
        clear_btn = ctk.CTkButton(
            action_frame,
            text="Clear Completed",
            width=140,
            height=32,
            corner_radius=8,
            command=self.clear_completed
        )
        clear_btn.pack(side="right")
    
    def check_prerequisites(self):
        """Check if FFmpeg and Whisper are installed"""
        # Access app_state from parent's parent (main app)
        try:
            app_state = self.parent.master.master.app_state
            missing = []
            
            if not app_state['requirements']['ffmpeg']:
                missing.append("FFmpeg")
            
            if not app_state['requirements']['whisper']:
                missing.append("Whisper model")
            
            if missing:
                messagebox.showwarning(
                    "Missing Requirements",
                    f"Missing: {', '.join(missing)}\n\nPlease download them in the Settings tab first."
                )
                return False
            
            return True
        except:
            # If we can't access app_state, assume prerequisites are met
            return True
    
    def start_transcriptions(self):
        """Start transcribing all files"""
        
        # Check prerequisites
        if not self.check_prerequisites():
            return
        
        # Get files
        files = self.file_list.get_files()
        if not files:
            messagebox.showerror("Error", "Please select at least one audio/video file")
            return
        
        # Add all transcriptions to manager
        self.logger.info(f"Starting {len(files)} transcriptions")
        
        for file_info in files:
            task_id = self.transcription_manager.add_transcription(
                file_info['path'],
                file_info['name']
            )
        
        # Update button text
        self.update_transcribe_button()
        
        # Show info message
        messagebox.showinfo(
            "Transcriptions Started",
            f"Added {len(files)} file(s) to the transcription queue.\n\nResults will appear in the 'Transcription Results' tab as they complete."
        )
    
    def update_status_display(self):
        """Update the status log display (called from transcription manager)"""
        # Rate limit UI updates
        now = time.time()
        if hasattr(self, '_last_update') and now - self._last_update < 0.1:
            return
        self._last_update = now
        
        # This needs to run on the main thread
        try:
            self.parent.after(0, self._update_status_display_impl)
        except:
            pass
    
    def _update_status_display_impl(self):
        """Implementation of status display update"""
        try:
            # Get all tasks
            tasks = self.transcription_manager.get_all_tasks()
            
            # Update each task in the log
            for task in tasks:
                # Get queue position if queued
                queue_pos = self.transcription_manager.get_queue_position(task.id)
                message = task.message
                if queue_pos:
                    message = f"Queued (position {queue_pos})"
                
                self.status_log.update_task(
                    task.id,
                    task.status.value,
                    message,
                    name=task.filename,
                    progress=task.progress
                )
            
            # Update summary
            summary = self.transcription_manager.get_summary()
            self.status_log.set_summary_from_stats(summary)
            
            # Update button
            self.update_transcribe_button()
            
            # Force UI update to show changes immediately
            try:
                self.parent.update_idletasks()
            except:
                pass
            
        except Exception as e:
            self.logger.error(f"Error updating status display: {e}")
    
    def update_transcribe_button(self):
        """Update transcribe button text based on file count"""
        file_count = self.file_list.get_count()
        if file_count == 0:
            self.transcribe_btn.configure(text="Transcribe All Files")
        elif file_count == 1:
            self.transcribe_btn.configure(text="Transcribe Audio (1 file)")
        else:
            self.transcribe_btn.configure(text=f"Transcribe All Files ({file_count} files)")
    
    def clear_completed(self):
        """Clear completed and failed transcriptions from status log"""
        self.transcription_manager.clear_completed()
        self.update_status_display()