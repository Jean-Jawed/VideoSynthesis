"""
Download Video Tab - Download multiple videos from URLs using yt-dlp
"""

import customtkinter as ctk
import time
from tkinter import filedialog, messagebox
from core.download_manager import DownloadManager
from ui.widgets import URLInputList, StatusLog


class DownloadTab:
    def __init__(self, parent, app_state, logger):
        self.parent = parent
        self.app_state = app_state
        self.logger = logger
        
        # Initialize download manager
        self.download_manager = DownloadManager(logger, max_concurrent=3)
        self.download_manager.set_status_callback(self.update_status_display)
        
        self.download_path = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Create the Download Video tab UI"""
        
        # Main container
        container = ctk.CTkFrame(self.parent, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Configure grid
        container.grid_rowconfigure(3, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            container,
            text="Download Videos",
            font=("Arial", 20, "bold")
        )
        title_label.grid(row=0, column=0, sticky="w", pady=(0, 20))
        
        # URL Input Section
        url_frame = ctk.CTkFrame(container, corner_radius=10)
        url_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        # URL Input List Widget
        self.url_list = URLInputList(url_frame, fg_color="transparent")
        self.url_list.pack(fill="x", padx=20, pady=15)
        
        # Destination Section
        dest_frame = ctk.CTkFrame(container, corner_radius=10)
        dest_frame.grid(row=2, column=0, sticky="ew", pady=10)
        
        dest_inner = ctk.CTkFrame(dest_frame, fg_color="transparent")
        dest_inner.pack(fill="x", padx=20, pady=15)
        dest_inner.grid_columnconfigure(0, weight=1)
        
        dest_label = ctk.CTkLabel(
            dest_inner,
            text="Save Location:",
            font=("Arial", 14)
        )
        dest_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        dest_input_frame = ctk.CTkFrame(dest_inner, fg_color="transparent")
        dest_input_frame.grid(row=1, column=0, sticky="ew")
        dest_input_frame.grid_columnconfigure(0, weight=1)
        
        self.dest_entry = ctk.CTkEntry(
            dest_input_frame,
            placeholder_text="Select destination folder...",
            height=35,
            corner_radius=8,
            font=("Arial", 11)
        )
        self.dest_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        browse_btn = ctk.CTkButton(
            dest_input_frame,
            text="Browse",
            width=100,
            height=35,
            corner_radius=8,
            command=self.browse_destination
        )
        browse_btn.grid(row=0, column=1)
        
        # Download Button
        self.download_btn = ctk.CTkButton(
            container,
            text="Download All Audio",
            height=45,
            corner_radius=10,
            font=("Arial", 14, "bold"),
            command=self.start_downloads
        )
        self.download_btn.grid(row=3, column=0, sticky="ew", pady=15)
        
        # Status Log Section
        self.status_log = StatusLog(container, title="Download Status:")
        self.status_log.grid(row=4, column=0, sticky="nsew", pady=(0, 10))
        
        # Action buttons
        action_frame = ctk.CTkFrame(container, fg_color="transparent")
        action_frame.grid(row=5, column=0, sticky="ew")
        
        clear_btn = ctk.CTkButton(
            action_frame,
            text="Clear Completed",
            width=140,
            height=32,
            corner_radius=8,
            command=self.clear_completed
        )
        clear_btn.pack(side="right")
    
    def browse_destination(self):
        """Open folder browser for destination"""
        folder = filedialog.askdirectory(title="Select Destination Folder")
        if folder:
            self.dest_entry.delete(0, "end")
            self.dest_entry.insert(0, folder)
            self.download_path = folder
    
    def check_prerequisites(self):
        """Check if FFmpeg is installed"""
        if not self.app_state['requirements']['ffmpeg']:
            messagebox.showwarning(
                "Missing Requirements",
                "FFmpeg is not installed.\n\nPlease download it in the Settings tab first."
            )
            return False
        return True
    
    def start_downloads(self):
        """Start downloading all URLs"""
        
        # Check prerequisites
        if not self.check_prerequisites():
            return
        
        # Get URLs
        urls = self.url_list.get_urls()
        if not urls:
            messagebox.showerror("Error", "Please enter at least one video URL")
            return
        
        # Check destination
        if not self.download_path:
            messagebox.showerror("Error", "Please select a destination folder")
            return
        
        # Add all downloads to manager
        self.logger.info(f"Starting {len(urls)} downloads")
        
        for url in urls:
            self.download_manager.add_download(url, self.download_path)
        
        # Update button text
        self.update_download_button()
    
    def update_status_display(self):
        """Update the status log display (called from download manager)"""
        # Rate limit UI updates to avoid freezing (max every 100ms)
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
            tasks = self.download_manager.get_all_tasks()
            
            # Update each task in the log
            for task in tasks:
                self.status_log.update_task(
                    task.id,
                    task.status.value,
                    task.message,
                    name=f"URL {tasks.index(task) + 1}",
                    progress=task.progress
                )
            
            # Update summary
            summary = self.download_manager.get_summary()
            self.status_log.set_summary_from_stats(summary)
            
            # Update button
            self.update_download_button()
            
            # Force UI update to show changes immediately
            try:
                self.parent.update_idletasks()
            except:
                pass
            
        except Exception as e:
            self.logger.error(f"Error updating status display: {e}")
    
    def update_download_button(self):
        """Update download button text based on URL count"""
        url_count = self.url_list.get_count()
        if url_count == 0:
            self.download_btn.configure(text="Download All Audio")
        elif url_count == 1:
            self.download_btn.configure(text="Download Audio (1 URL)")
        else:
            self.download_btn.configure(text=f"Download All Audio ({url_count} URLs)")
    
    def clear_completed(self):
        """Clear completed and failed downloads"""
        self.download_manager.clear_completed()
        self.update_status_display()