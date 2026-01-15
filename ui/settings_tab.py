"""
Settings Tab - Manage FFmpeg and Whisper downloads
"""

import customtkinter as ctk
from utils.ffmpeg_manager import FFmpegManager
from utils.whisper_manager import WhisperManager


class SettingsTab:
    def __init__(self, parent, app_state, logger):
        self.parent = parent
        self.app_state = app_state
        self.logger = logger
        
        # Initialize managers
        self.ffmpeg_manager = FFmpegManager(logger)
        self.whisper_manager = WhisperManager(logger)
        
        # Selected Whisper model
        self.selected_model = ctk.StringVar(value="base")
        
        # Setup UI
        self.setup_ui()
    
    def setup_ui(self):
        """Create the Settings tab UI"""
        
        # Main container
        container = ctk.CTkFrame(self.parent, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            container,
            text="Settings - Required Components: Download only at first use",
            font=("Arial", 20, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # FFmpeg Section
        self.create_ffmpeg_section(container)
        
        # Separator
        separator = ctk.CTkFrame(container, height=2, fg_color=("gray70", "gray30"))
        separator.pack(fill="x", pady=20)
        
        # Whisper Section
        self.create_whisper_section(container)
        
        # Separator
        separator2 = ctk.CTkFrame(container, height=2, fg_color=("gray70", "gray30"))
        separator2.pack(fill="x", pady=20)
        
        # Clean Computer Section
        self.create_cleanup_section(container)
        
        # Progress Section
        self.create_progress_section(container)
    
    def create_ffmpeg_section(self, parent):
        """Create FFmpeg download section"""
        
        ffmpeg_frame = ctk.CTkFrame(parent, corner_radius=10)
        ffmpeg_frame.pack(fill="x", pady=10)
        
        # Header
        header_frame = ctk.CTkFrame(ffmpeg_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=15)
        
        title = ctk.CTkLabel(
            header_frame,
            text="FFmpeg",
            font=("Arial", 16, "bold")
        )
        title.pack(side="left")
        
        # Status label
        self.ffmpeg_status = ctk.CTkLabel(
            header_frame,
            text="● Not installed",
            font=("Arial", 12),
            text_color="red"
        )
        self.ffmpeg_status.pack(side="left", padx=20)
        
        # Download button
        self.ffmpeg_btn = ctk.CTkButton(
            header_frame,
            text="Download",
            width=120,
            height=32,
            corner_radius=8,
            command=self.download_ffmpeg
        )
        self.ffmpeg_btn.pack(side="right")
        
        # Info
        info = ctk.CTkLabel(
            ffmpeg_frame,
            text="Size: ~120 MB • Required for video/audio processing • Estimated time : 10 min",
            font=("Arial", 11),
            text_color="gray"
        )
        info.pack(padx=20, pady=(0, 15))
    
    def create_whisper_section(self, parent):
        """Create Whisper model download section"""
        
        whisper_frame = ctk.CTkFrame(parent, corner_radius=10)
        whisper_frame.pack(fill="x", pady=10)
        
        # Header
        header_frame = ctk.CTkFrame(whisper_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=15)
        
        title = ctk.CTkLabel(
            header_frame,
            text="Whisper Model",
            font=("Arial", 16, "bold")
        )
        title.pack(side="left")
        
        # Status label
        self.whisper_status = ctk.CTkLabel(
            header_frame,
            text="● Not installed",
            font=("Arial", 12),
            text_color="red"
        )
        self.whisper_status.pack(side="left", padx=20)
        
        # Download button
        self.whisper_btn = ctk.CTkButton(
            header_frame,
            text="Download",
            width=120,
            height=32,
            corner_radius=8,
            command=self.download_whisper
        )
        self.whisper_btn.pack(side="right")
        
        # Model selection
        model_frame = ctk.CTkFrame(whisper_frame, fg_color="transparent")
        model_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        model_label = ctk.CTkLabel(
            model_frame,
            text="Model:",
            font=("Arial", 12)
        )
        model_label.pack(side="left", padx=(0, 10))
        
        self.model_menu = ctk.CTkOptionMenu(
            model_frame,
            values=["base", "medium", "large"],
            variable=self.selected_model,
            width=120,
            height=28,
            corner_radius=6,
            command=self.on_model_change
        )
        self.model_menu.pack(side="left")
        
        # Size info
        self.model_size_label = ctk.CTkLabel(
            model_frame,
            text="150 MB",
            font=("Arial", 11),
            text_color="gray"
        )
        self.model_size_label.pack(side="left", padx=10)
        
        # Info
        info = ctk.CTkLabel(
            whisper_frame,
            text="Required for audio transcription • Larger models = better accuracy • Estimated time : 2 min",
            font=("Arial", 11),
            text_color="gray"
        )
        info.pack(padx=20, pady=(0, 15))
    
    def create_progress_section(self, parent):
        """Create progress bar section"""
        
        progress_frame = ctk.CTkFrame(parent, fg_color="transparent")
        progress_frame.pack(fill="x", pady=(20, 0))
        
        self.progress_bar = ctk.CTkProgressBar(
            progress_frame,
            height=20,
            corner_radius=10
        )
        self.progress_bar.pack(fill="x", pady=(0, 10))
        self.progress_bar.set(0)
        self.progress_bar.pack_forget()  # Hide initially
        
        self.progress_label = ctk.CTkLabel(
            progress_frame,
            text="",
            font=("Arial", 11)
        )
        self.progress_label.pack()
        self.progress_label.pack_forget()  # Hide initially
    
    def create_cleanup_section(self, parent):
        """Create cleanup section with Clean Computer button"""
        
        cleanup_frame = ctk.CTkFrame(parent, corner_radius=10)
        cleanup_frame.pack(fill="x", pady=10)
        
        # Header
        header_frame = ctk.CTkFrame(cleanup_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=15)
        
        title = ctk.CTkLabel(
            header_frame,
            text="Clean Computer",
            font=("Arial", 16, "bold")
        )
        title.pack(side="left")
        
        # Clean button
        self.clean_btn = ctk.CTkButton(
            header_frame,
            text="Remove All Downloads",
            width=180,
            height=32,
            corner_radius=8,
            fg_color="#d32f2f",
            hover_color="#b71c1c",
            command=self.clean_computer
        )
        self.clean_btn.pack(side="right")
        
        # Info
        info = ctk.CTkLabel(
            cleanup_frame,
            text="Remove FFmpeg and Whisper models to free up disk space. You can re-download them anytime.",
            font=("Arial", 11),
            text_color="gray"
        )
        info.pack(padx=20, pady=(0, 15))
    
    def clean_computer(self):
        """Clean computer by removing FFmpeg and Whisper models"""
        from tkinter import messagebox
        
        # Calculate sizes
        ffmpeg_size = self.ffmpeg_manager.get_size()
        whisper_size = self.whisper_manager.get_size()
        total_size = ffmpeg_size + whisper_size
        
        if total_size == 0:
            messagebox.showinfo(
                "Nothing to Clean",
                "No FFmpeg or Whisper models are currently installed."
            )
            return
        
        # Build message
        items_to_remove = []
        if ffmpeg_size > 0:
            items_to_remove.append(f"• FFmpeg ({ffmpeg_size:.1f} MB)")
        if whisper_size > 0:
            items_to_remove.append(f"• Whisper models ({whisper_size:.1f} MB)")
        
        message = "The following items will be removed:\n\n"
        message += "\n".join(items_to_remove)
        message += f"\n\nTotal space to free: {total_size:.1f} MB"
        message += "\n\nAre you sure you want to continue?"
        
        # Confirm with user
        result = messagebox.askyesno(
            "Confirm Cleanup",
            message,
            icon='warning'
        )
        
        if not result:
            return
        
        # Perform cleanup
        success_messages = []
        error_messages = []
        
        # Remove FFmpeg
        if ffmpeg_size > 0:
            success, msg = self.ffmpeg_manager.uninstall()
            if success:
                success_messages.append(msg)
            else:
                error_messages.append(msg)
        
        # Remove Whisper
        if whisper_size > 0:
            success, msg, models = self.whisper_manager.uninstall()
            if success:
                success_messages.append(msg)
            else:
                error_messages.append(msg)
        
        # Update UI
        self.check_requirements()
        
        # Show result
        if success_messages and not error_messages:
            messagebox.showinfo(
                "Cleanup Complete",
                "\n".join(success_messages) + f"\n\nFreed {total_size:.1f} MB of disk space!"
            )
        elif error_messages:
            messagebox.showerror(
                "Cleanup Failed",
                "\n".join(error_messages)
            )
    
    def on_model_change(self, choice):
        """Handle model selection change"""
        sizes = {
            'base': '150 MB',
            'medium': '1.5 GB',
            'large': '3 GB'
        }
        self.model_size_label.configure(text=sizes.get(choice, ''))
        self.check_requirements()
    
    def check_requirements(self):
        """Check if requirements are installed and update UI"""
        
        # Check FFmpeg
        ffmpeg_installed = self.ffmpeg_manager.is_installed()
        self.app_state['requirements']['ffmpeg'] = ffmpeg_installed
        
        if ffmpeg_installed:
            self.ffmpeg_status.configure(
                text="✓ Installed",
                text_color="green"
            )
            self.ffmpeg_btn.configure(state="disabled", text="Installed")
        else:
            self.ffmpeg_status.configure(
                text="● Not installed",
                text_color="red"
            )
            self.ffmpeg_btn.configure(state="normal", text="Download")
        
        # Check Whisper
        model_name = self.selected_model.get()
        whisper_installed = self.whisper_manager.is_installed(model_name)
        self.app_state['requirements']['whisper'] = whisper_installed
        
        if whisper_installed:
            self.whisper_status.configure(
                text=f"✓ {model_name.capitalize()} installed",
                text_color="green"
            )
            self.whisper_btn.configure(state="disabled", text="Installed")
        else:
            # Check if any model is installed
            installed_model = self.whisper_manager.get_installed_model()
            if installed_model:
                self.whisper_status.configure(
                    text=f"● {installed_model.capitalize()} installed, {model_name} not installed",
                    text_color="orange"
                )
                self.whisper_btn.configure(state="normal", text="Download")
            else:
                self.whisper_status.configure(
                    text="● Not installed",
                    text_color="red"
                )
                self.whisper_btn.configure(state="normal", text="Download")
        
        self.logger.info(f"Requirements check: FFmpeg={ffmpeg_installed}, Whisper={whisper_installed}")
    
    def download_ffmpeg(self):
        """Start FFmpeg download"""
        self.logger.info("User initiated FFmpeg download")
        
        self.ffmpeg_btn.configure(state="disabled", text="Downloading...")
        self.progress_bar.pack(fill="x", pady=(0, 10))
        self.progress_label.pack()
        self.progress_bar.set(0)
        
        def progress_callback(percent, message):
            self.progress_bar.set(percent / 100)
            self.progress_label.configure(text=message)
        
        def completion_callback(success, message):
            if success:
                self.progress_label.configure(text=message, text_color="green")
                self.check_requirements()
            else:
                self.progress_label.configure(text=message, text_color="red")
                self.ffmpeg_btn.configure(state="normal", text="Retry")
        
        self.ffmpeg_manager.download(progress_callback, completion_callback)
    
    def download_whisper(self):
        """Start Whisper model download"""
        model_name = self.selected_model.get()
        self.logger.info(f"User initiated Whisper '{model_name}' download")
        
        self.whisper_btn.configure(state="disabled", text="Downloading...")
        self.progress_bar.pack(fill="x", pady=(0, 10))
        self.progress_label.pack()
        self.progress_bar.set(0)
        
        def progress_callback(percent, message):
            self.progress_bar.set(percent / 100)
            self.progress_label.configure(text=message)
        
        def completion_callback(success, message):
            if success:
                self.progress_label.configure(text=message, text_color="green")
                self.check_requirements()
            else:
                self.progress_label.configure(text=message, text_color="red")
                self.whisper_btn.configure(state="normal", text="Retry")
        
        self.whisper_manager.download(model_name, progress_callback, completion_callback)