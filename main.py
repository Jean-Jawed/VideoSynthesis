"""
VideoSynthesis - Main Application
Copyright © Jawed Tahir 2025
"""

import customtkinter as ctk
import tkinter as tk
import sys
import os
from ui.settings_tab import SettingsTab
from ui.download_tab import DownloadTab
from ui.videototext_tab import VideoToTextTab
from ui.transcription_results_tab import TranscriptionResultsTab
from ui.synthesis_tab import SynthesisTab
from core.transcription_manager import TranscriptionManager
from utils.logger import setup_logger
import webbrowser

# Fix for PyInstaller --noconsole: redirect stdout/stderr to avoid crashes
if sys.stdout is None:
    sys.stdout = open(os.devnull, 'w')
if sys.stderr is None:
    sys.stderr = open(os.devnull, 'w')

# Set appearance and color theme
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class VideoSynthesisApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Setup logger
        self.logger = setup_logger()
        self.logger.info("Application started")
        
        # Window configuration
        self.title("VideoSynthesis")
        self.geometry("1200x800")
        self.minsize(1000, 650)
        self.resizable(True, True)
        
        # Shared application state
        self.app_state = {
            'requirements': {
                'ffmpeg': False,
                'whisper': False
            },
            'api_keys': {},  # Stored in memory during session
            'downloaded_file_path': None,  # Set by Download tab
            'transcribed_text': None  # Set by VideoToText tab
        }
        
        # Create main container with grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Create canvas for scrolling
        self.canvas = tk.Canvas(
            self,
            bg='#F0F0F0',  # Light gray background matching CTk light theme
            highlightthickness=0
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        # Create scrollbar
        self.scrollbar = ctk.CTkScrollbar(
            self,
            orientation="vertical",
            command=self.canvas.yview
        )
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Configure canvas to use scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Create scrollable frame inside canvas
        self.scrollable_frame = ctk.CTkFrame(self.canvas, fg_color="transparent")
        
        # Create window in canvas
        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw"
        )
        
        # Configure scroll region when frame changes size
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Bind canvas resize to adjust scrollable frame width
        self.canvas.bind(
            "<Configure>",
            self._on_canvas_configure
        )
        
        # Enable mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)  # Linux scroll up
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)  # Linux scroll down
        
        # Configure scrollable_frame grid
        self.scrollable_frame.grid_rowconfigure(0, weight=1)
        self.scrollable_frame.grid_rowconfigure(1, weight=0)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # Create tab view in scrollable frame
        self.tabview = ctk.CTkTabview(self.scrollable_frame, corner_radius=10)
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=20, pady=(20, 10))
        
        # Add tabs
        self.tabview.add("Settings")
        self.tabview.add("Download Video")
        self.tabview.add("Video to Text")
        self.tabview.add("Transcription Results")
        self.tabview.add("Synthesis")
        
        # Create shared transcription manager
        self.transcription_manager = TranscriptionManager(self.logger)
        
        # Initialize tab contents
        self.settings_tab = SettingsTab(
            self.tabview.tab("Settings"),
            self.app_state,
            self.logger
        )
        
        self.download_tab = DownloadTab(
            self.tabview.tab("Download Video"),
            self.app_state,
            self.logger
        )
        
        self.videototext_tab = VideoToTextTab(
            self.tabview.tab("Video to Text"),
            self.transcription_manager,
            self.logger
        )
        
        self.transcription_results_tab = TranscriptionResultsTab(
            self.tabview.tab("Transcription Results"),
            self.transcription_manager,
            self.logger
        )
        
        self.synthesis_tab = SynthesisTab(
            self.tabview.tab("Synthesis"),
            self.app_state,
            self.logger
        )
        
        # Create footer in scrollable frame
        self.create_footer(self.scrollable_frame)
        
        # Initial requirements check
        self.settings_tab.check_requirements()
    
    def _on_canvas_configure(self, event):
        """Adjust the scrollable frame width when canvas is resized"""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        # Windows and MacOS
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
        else:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
    def create_footer(self, parent):
        """Create footer with copyright and link"""
        footer_frame = ctk.CTkFrame(parent, fg_color="transparent", height=40)
        footer_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        footer_frame.grid_columnconfigure(0, weight=1)
        
        # Copyright text
        copyright_label = ctk.CTkLabel(
            footer_frame,
            text="Copyright © Jawed Tahir 2025",
            font=("Arial", 11)
        )
        copyright_label.grid(row=0, column=0, sticky="w", padx=10)
        
        # Website link button
        link_button = ctk.CTkButton(
            footer_frame,
            text="Visit Website",
            font=("Arial", 11),
            width=120,
            height=28,
            corner_radius=6,
            command=lambda: webbrowser.open("https://javed.fr")
        )
        link_button.grid(row=0, column=1, sticky="e", padx=10)
    
    def on_closing(self):
        """Handle application closing"""
        self.logger.info("Application closed")
        self.destroy()


if __name__ == "__main__":
    app = VideoSynthesisApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()