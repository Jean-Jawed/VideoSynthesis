"""
Download Video Tab - Download videos from URLs using yt-dlp
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from core.downloader import VideoDownloader


class DownloadTab:
    def __init__(self, parent, app_state, logger):
        self.parent = parent
        self.app_state = app_state
        self.logger = logger
        
        self.downloader = VideoDownloader(logger)
        self.download_path = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Create the Download Video tab UI"""
        
        # Main container
        container = ctk.CTkFrame(self.parent, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            container,
            text="Download Video",
            font=("Arial", 20, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # URL Input Section
        url_frame = ctk.CTkFrame(container, corner_radius=10)
        url_frame.pack(fill="x", pady=10)
        
        url_label = ctk.CTkLabel(
            url_frame,
            text="Video URL:",
            font=("Arial", 14)
        )
        url_label.pack(anchor="w", padx=20, pady=(15, 5))
        
        self.url_entry = ctk.CTkEntry(
            url_frame,
            placeholder_text="https://www.youtube.com/watch?v=...",
            height=40,
            corner_radius=8,
            font=("Arial", 12)
        )
        self.url_entry.pack(fill="x", padx=20, pady=(0, 15))
        
        # Destination Section
        dest_frame = ctk.CTkFrame(container, corner_radius=10)
        dest_frame.pack(fill="x", pady=10)
        
        dest_label = ctk.CTkLabel(
            dest_frame,
            text="Save Location:",
            font=("Arial", 14)
        )
        dest_label.pack(anchor="w", padx=20, pady=(15, 5))
        
        dest_input_frame = ctk.CTkFrame(dest_frame, fg_color="transparent")
        dest_input_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.dest_entry = ctk.CTkEntry(
            dest_input_frame,
            placeholder_text="Select destination folder...",
            height=40,
            corner_radius=8,
            font=("Arial", 12)
        )
        self.dest_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        browse_btn = ctk.CTkButton(
            dest_input_frame,
            text="Browse",
            width=100,
            height=40,
            corner_radius=8,
            command=self.browse_destination
        )
        browse_btn.pack(side="right")
        
        # Download Button
        self.download_btn = ctk.CTkButton(
            container,
            text="Download Audio",
            height=45,
            corner_radius=10,
            font=("Arial", 14, "bold"),
            command=self.start_download
        )
        self.download_btn.pack(fill="x", pady=15)
        
        # Log Section
        log_frame = ctk.CTkFrame(container, corner_radius=10)
        log_frame.pack(fill="both", expand=True, pady=10)
        
        log_label = ctk.CTkLabel(
            log_frame,
            text="Download Log:",
            font=("Arial", 14)
        )
        log_label.pack(anchor="w", padx=20, pady=(15, 5))
        
        self.log_text = ctk.CTkTextbox(
            log_frame,
            font=("Courier", 11),
            corner_radius=8,
            wrap="word"
        )
        self.log_text.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        self.log_text.configure(state="disabled")
    
    def browse_destination(self):
        """Open folder browser for destination"""
        folder = filedialog.askdirectory(title="Select Destination Folder")
        if folder:
            self.dest_entry.delete(0, "end")
            self.dest_entry.insert(0, folder)
            self.download_path = folder
    
    def append_log(self, message):
        """Append message to log textbox"""
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")
    
    def check_prerequisites(self):
        """Check if FFmpeg is installed"""
        if not self.app_state['requirements']['ffmpeg']:
            messagebox.showwarning(
                "Missing Requirements",
                "FFmpeg is not installed.\n\nPlease download it in the Settings tab first."
            )
            return False
        return True
    
    def start_download(self):
        """Start video download process"""
        
        # Check prerequisites
        if not self.check_prerequisites():
            return
        
        # Validate inputs
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a video URL")
            return
        
        if not self.download_path:
            messagebox.showerror("Error", "Please select a destination folder")
            return
        
        # Clear log
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")
        
        # Disable download button
        self.download_btn.configure(state="disabled", text="Downloading...")
        
        self.logger.info(f"Starting download: {url}")
        self.append_log(f"Starting download from: {url}")
        self.append_log(f"Destination: {self.download_path}\n")
        
        def progress_callback(message):
            self.append_log(message)
        
        def completion_callback(success, output_file, message):
            self.download_btn.configure(state="normal", text="Download Audio")
            
            if success:
                self.append_log("\n" + "="*50)
                self.append_log(f"✓ Download successful!")
                self.append_log(f"File saved: {output_file}")
                self.append_log("="*50)
                
                # Store the downloaded file path in app state
                self.app_state['downloaded_file_path'] = output_file
                
                # Ask if user wants to transcribe now
                result = messagebox.askyesno(
                    "Download Complete",
                    "Download completed successfully!\n\nWould you like to transcribe this file now?"
                )
                
                if result:
                    # Switch to VideoToText tab
                    # Note: This requires access to the main app's tabview
                    # We'll handle this through the app_state
                    self.app_state['switch_to_transcribe'] = True
            else:
                self.append_log("\n" + "="*50)
                self.append_log(f"✗ Download failed: {message}")
                self.append_log("="*50)
                messagebox.showerror("Download Failed", message)
        
        # Start download
        self.downloader.download(
            url,
            self.download_path,
            progress_callback,
            completion_callback
        )