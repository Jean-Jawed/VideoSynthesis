"""
Video to Text Tab - Transcribe audio/video files using Whisper
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from core.transcriber import AudioTranscriber
import os


class VideoToTextTab:
    def __init__(self, parent, app_state, logger):
        self.parent = parent
        self.app_state = app_state
        self.logger = logger
        
        self.transcriber = AudioTranscriber(logger)
        self.current_file = None
        
        self.setup_ui()
        
        # Check periodically for downloaded files
        self.check_downloaded_file()
    
    def setup_ui(self):
        """Create the Video to Text tab UI"""
        
        # Main container
        container = ctk.CTkFrame(self.parent, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            container,
            text="Video to Text Transcription",
            font=("Arial", 20, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # File Selection Section
        file_frame = ctk.CTkFrame(container, corner_radius=10)
        file_frame.pack(fill="x", pady=10)
        
        file_label = ctk.CTkLabel(
            file_frame,
            text="Select Audio/Video File:",
            font=("Arial", 14)
        )
        file_label.pack(anchor="w", padx=20, pady=(15, 5))
        
        file_input_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
        file_input_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.file_entry = ctk.CTkEntry(
            file_input_frame,
            placeholder_text="No file selected...",
            height=40,
            corner_radius=8,
            font=("Arial", 12)
        )
        self.file_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        browse_btn = ctk.CTkButton(
            file_input_frame,
            text="Browse",
            width=100,
            height=40,
            corner_radius=8,
            command=self.browse_file
        )
        browse_btn.pack(side="right")
        
        # Transcribe Button
        self.transcribe_btn = ctk.CTkButton(
            container,
            text="Transcribe Audio (~15 min per hour of audio)",
            height=45,
            corner_radius=10,
            font=("Arial", 14, "bold"),
            command=self.start_transcription
        )
        self.transcribe_btn.pack(fill="x", pady=15)
        
        # Progress Section
        self.progress_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.progress_frame.pack(fill="x")
        self.progress_frame.pack_forget()  # Hidden initially
        
        self.progress_bar = ctk.CTkProgressBar(
            self.progress_frame,
            height=20,
            corner_radius=10
        )
        self.progress_bar.pack(fill="x", pady=(0, 10))
        
        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="",
            font=("Arial", 12)
        )
        self.progress_label.pack()
        
        # Transcription Output Section
        output_frame = ctk.CTkFrame(container, corner_radius=10)
        output_frame.pack(fill="both", expand=True, pady=10)
        
        output_header = ctk.CTkFrame(output_frame, fg_color="transparent")
        output_header.pack(fill="x", padx=20, pady=(15, 5))
        
        output_label = ctk.CTkLabel(
            output_header,
            text="Transcribed Text:",
            font=("Arial", 14)
        )
        output_label.pack(side="left")
        
        # Copy button
        self.copy_btn = ctk.CTkButton(
            output_header,
            text="Copy Text",
            width=100,
            height=28,
            corner_radius=6,
            command=self.copy_text,
            state="disabled"
        )
        self.copy_btn.pack(side="right")
        
        # Send to Synthesis button
        self.send_synthesis_btn = ctk.CTkButton(
            output_header,
            text="Send to Synthesis",
            width=140,
            height=28,
            corner_radius=6,
            command=self.send_to_synthesis,
            state="disabled"
        )
        self.send_synthesis_btn.pack(side="right", padx=(0, 10))
        
        self.text_output = ctk.CTkTextbox(
            output_frame,
            font=("Arial", 12),
            corner_radius=8,
            wrap="word"
        )
        self.text_output.pack(fill="both", expand=True, padx=20, pady=(0, 15))
    
    def browse_file(self):
        """Open file browser for audio/video file"""
        filetypes = [
            ("Media files", "*.mp3 *.mp4 *.wav *.m4a *.avi *.mkv *.flac"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Audio/Video File",
            filetypes=filetypes
        )
        
        if filename:
            # Normalize path to handle Windows/Linux differences
            filename = os.path.normpath(filename)
            self.file_entry.delete(0, "end")
            self.file_entry.insert(0, filename)
            self.current_file = filename
    
    def check_downloaded_file(self):
        """Check if a file was downloaded and auto-fill"""
        if self.app_state.get('downloaded_file_path'):
            filepath = self.app_state['downloaded_file_path']
            if os.path.exists(filepath):
                self.file_entry.delete(0, "end")
                self.file_entry.insert(0, filepath)
                self.current_file = filepath
                
                # Check if we should auto-switch to this tab
                if self.app_state.get('switch_to_transcribe'):
                    self.app_state['switch_to_transcribe'] = False
            
            # Clear the flag
            self.app_state['downloaded_file_path'] = None
        
        # Check again in 500ms
        self.parent.after(500, self.check_downloaded_file)
    
    def check_prerequisites(self):
        """Check if FFmpeg and Whisper are installed"""
        missing = []
        
        if not self.app_state['requirements']['ffmpeg']:
            missing.append("FFmpeg")
        
        if not self.app_state['requirements']['whisper']:
            missing.append("Whisper model")
        
        if missing:
            messagebox.showwarning(
                "Missing Requirements",
                f"Missing: {', '.join(missing)}\n\nPlease download them in the Settings tab first."
            )
            return False
        
        return True
    
    def start_transcription(self):
        """Start audio transcription"""
        
        # Check prerequisites
        if not self.check_prerequisites():
            return
        
        # Get file path from entry field (more reliable)
        file_path = self.file_entry.get().strip()
        
        # Normalize path (handle Windows/Linux differences)
        if file_path:
            file_path = os.path.normpath(file_path)
            self.current_file = file_path
        
        # Validate file
        if not self.current_file:
            messagebox.showerror("Error", "Please select an audio/video file")
            return
        
        if not os.path.exists(self.current_file):
            messagebox.showerror(
                "Error", 
                f"File not found:\n{self.current_file}\n\nPlease check the file path."
            )
            return
        
        # Clear previous output
        self.text_output.delete("1.0", "end")
        
        # Show progress
        self.progress_frame.pack(fill="x", pady=(0, 10))
        self.progress_bar.set(0)
        self.progress_label.configure(text="Initializing transcription...")
        
        # Disable buttons
        self.transcribe_btn.configure(state="disabled", text="Transcribing...")
        self.copy_btn.configure(state="disabled")
        self.send_synthesis_btn.configure(state="disabled")
        
        self.logger.info(f"Starting transcription: {self.current_file}")
        
        def progress_callback(percent, message):
            self.progress_bar.set(percent / 100)
            self.progress_label.configure(text=message)
        
        def completion_callback(success, text, message):
            self.transcribe_btn.configure(state="normal", text="Transcribe Audio")
            
            if success:
                self.progress_label.configure(text="✓ Transcription complete!", text_color="green")
                self.text_output.insert("1.0", text)
                self.copy_btn.configure(state="normal")
                self.send_synthesis_btn.configure(state="normal")
                
                # Store in app state
                self.app_state['transcribed_text'] = text
                
                messagebox.showinfo(
                    "Transcription Complete",
                    f"Transcription completed successfully!\n\nWord count: {len(text.split())} words"
                )
            else:
                self.progress_label.configure(text=f"✗ {message}", text_color="red")
                messagebox.showerror("Transcription Failed", message)
        
        # Start transcription
        self.transcriber.transcribe(
            self.current_file,
            progress_callback,
            completion_callback
        )
    
    def copy_text(self):
        """Copy transcribed text to clipboard"""
        text = self.text_output.get("1.0", "end-1c")
        if text.strip():
            self.parent.clipboard_clear()
            self.parent.clipboard_append(text)
            messagebox.showinfo("Copied", "Text copied to clipboard!")
    
    def send_to_synthesis(self):
        """Send transcribed text to Synthesis tab"""
        text = self.text_output.get("1.0", "end-1c")
        if text.strip():
            self.app_state['transcribed_text'] = text
            messagebox.showinfo(
                "Text Sent",
                "Transcribed text has been sent to the Synthesis tab.\n\nPlease switch to the Synthesis tab to generate a summary."
            )