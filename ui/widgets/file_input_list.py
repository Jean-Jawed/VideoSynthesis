"""
File Input List Widget - Dynamic list of file input fields
"""

import customtkinter as ctk
from tkinter import filedialog
import os


class FileInputList(ctk.CTkFrame):
    """Widget for managing a dynamic list of file inputs"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.file_entries = []
        self.max_files = 20
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        
        # Header with title and add button
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="Select Audio/Video Files:",
            font=("Arial", 14, "bold")
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        self.add_btn = ctk.CTkButton(
            header_frame,
            text="+ Add File",
            width=100,
            height=28,
            corner_radius=6,
            command=self.add_file_field
        )
        self.add_btn.grid(row=0, column=1, sticky="e")
        
        # Container for file fields
        self.fields_container = ctk.CTkFrame(self, fg_color="transparent")
        self.fields_container.grid(row=1, column=0, sticky="ew")
        self.fields_container.grid_columnconfigure(0, weight=1)
        
        # Add initial field
        self.add_file_field()
    
    def add_file_field(self):
        """Add a new file input field"""
        if len(self.file_entries) >= self.max_files:
            return
        
        row = len(self.file_entries)
        
        # Create frame for this file field
        field_frame = ctk.CTkFrame(self.fields_container, fg_color="transparent")
        field_frame.grid(row=row, column=0, sticky="ew", pady=5)
        field_frame.grid_columnconfigure(0, weight=1)
        
        # File entry
        file_entry = ctk.CTkEntry(
            field_frame,
            placeholder_text="No file selected...",
            height=35,
            corner_radius=8,
            font=("Arial", 11)
        )
        file_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        # Browse button
        browse_btn = ctk.CTkButton(
            field_frame,
            text="Browse",
            width=80,
            height=35,
            corner_radius=8,
            command=lambda idx=row: self.browse_file(idx)
        )
        browse_btn.grid(row=0, column=1, padx=(0, 10))
        
        # Delete button
        delete_btn = ctk.CTkButton(
            field_frame,
            text="🗑️",
            width=35,
            height=35,
            corner_radius=8,
            fg_color="#d32f2f",
            hover_color="#b71c1c",
            command=lambda: self.remove_file_field(row)
        )
        delete_btn.grid(row=0, column=2)
        
        # Store references
        self.file_entries.append({
            'frame': field_frame,
            'entry': file_entry,
            'browse_btn': browse_btn,
            'delete_btn': delete_btn,
            'file_path': None
        })
        
        # Update delete button visibility
        self._update_delete_buttons()
    
    def browse_file(self, index):
        """Open file browser for a specific field"""
        filetypes = [
            ("Media files", "*.mp3 *.mp4 *.wav *.m4a *.avi *.mkv *.flac"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Audio/Video File",
            filetypes=filetypes
        )
        
        if filename:
            # Normalize path
            filename = os.path.normpath(filename)
            
            # Update entry
            self.file_entries[index]['entry'].delete(0, 'end')
            self.file_entries[index]['entry'].insert(0, filename)
            self.file_entries[index]['file_path'] = filename
    
    def remove_file_field(self, index):
        """Remove a file input field"""
        if len(self.file_entries) <= 1:
            return
        
        # Destroy the frame
        self.file_entries[index]['frame'].destroy()
        
        # Remove from list
        del self.file_entries[index]
        
        # Re-grid remaining fields
        for i, entry_data in enumerate(self.file_entries):
            entry_data['frame'].grid(row=i, column=0, sticky="ew", pady=5)
            # Update button commands
            entry_data['browse_btn'].configure(command=lambda idx=i: self.browse_file(idx))
            entry_data['delete_btn'].configure(command=lambda idx=i: self.remove_file_field(idx))
        
        # Update delete button visibility
        self._update_delete_buttons()
    
    def _update_delete_buttons(self):
        """Update visibility of delete buttons"""
        show_delete = len(self.file_entries) > 1
        for entry_data in self.file_entries:
            if show_delete:
                entry_data['delete_btn'].grid()
            else:
                entry_data['delete_btn'].grid_remove()
    
    def get_files(self):
        """Get list of selected file paths with filenames"""
        files = []
        for entry_data in self.file_entries:
            file_path = entry_data['entry'].get().strip()
            if file_path and os.path.exists(file_path):
                filename = os.path.basename(file_path)
                files.append({
                    'path': file_path,
                    'name': filename
                })
        return files
    
    def clear_all(self):
        """Clear all file fields"""
        for entry_data in self.file_entries:
            entry_data['entry'].delete(0, 'end')
            entry_data['file_path'] = None
    
    def get_count(self):
        """Get number of selected files"""
        return len(self.get_files())
