"""
URL Input List Widget - Dynamic list of URL input fields
"""

import customtkinter as ctk


class URLInputList(ctk.CTkFrame):
    """Widget for managing a dynamic list of URL inputs"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.url_entries = []
        self.max_urls = 20
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        
        # Header with title and add button
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="Video URLs:",
            font=("Arial", 14, "bold")
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        self.add_btn = ctk.CTkButton(
            header_frame,
            text="+ Add URL",
            width=100,
            height=28,
            corner_radius=6,
            command=self.add_url_field
        )
        self.add_btn.grid(row=0, column=1, sticky="e")
        
        # Container for URL fields
        self.fields_container = ctk.CTkFrame(self, fg_color="transparent")
        self.fields_container.grid(row=1, column=0, sticky="ew")
        self.fields_container.grid_columnconfigure(0, weight=1)
        
        # Add initial field
        self.add_url_field()
    
    def add_url_field(self):
        """Add a new URL input field"""
        if len(self.url_entries) >= self.max_urls:
            return
        
        row = len(self.url_entries)
        
        # Create frame for this URL field
        field_frame = ctk.CTkFrame(self.fields_container, fg_color="transparent")
        field_frame.grid(row=row, column=0, sticky="ew", pady=5)
        field_frame.grid_columnconfigure(0, weight=1)
        
        # URL entry
        url_entry = ctk.CTkEntry(
            field_frame,
            placeholder_text="https://www.youtube.com/watch?v=...",
            height=35,
            corner_radius=8,
            font=("Arial", 11)
        )
        url_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        # Delete button (only show if more than 1 field)
        delete_btn = ctk.CTkButton(
            field_frame,
            text="🗑️",
            width=35,
            height=35,
            corner_radius=8,
            fg_color="#d32f2f",
            hover_color="#b71c1c",
            command=lambda: self.remove_url_field(row)
        )
        delete_btn.grid(row=0, column=1)
        
        # Store references
        self.url_entries.append({
            'frame': field_frame,
            'entry': url_entry,
            'delete_btn': delete_btn
        })
        
        # Update delete button visibility
        self._update_delete_buttons()
    
    def remove_url_field(self, index):
        """Remove a URL input field"""
        if len(self.url_entries) <= 1:
            return
        
        # Destroy the frame
        self.url_entries[index]['frame'].destroy()
        
        # Remove from list
        del self.url_entries[index]
        
        # Re-grid remaining fields
        for i, entry_data in enumerate(self.url_entries):
            entry_data['frame'].grid(row=i, column=0, sticky="ew", pady=5)
            # Update delete button command
            entry_data['delete_btn'].configure(command=lambda idx=i: self.remove_url_field(idx))
        
        # Update delete button visibility
        self._update_delete_buttons()
    
    def _update_delete_buttons(self):
        """Update visibility of delete buttons"""
        show_delete = len(self.url_entries) > 1
        for entry_data in self.url_entries:
            if show_delete:
                entry_data['delete_btn'].grid()
            else:
                entry_data['delete_btn'].grid_remove()
    
    def get_urls(self):
        """Get list of non-empty URLs"""
        urls = []
        for entry_data in self.url_entries:
            url = entry_data['entry'].get().strip()
            if url:
                urls.append(url)
        return urls
    
    def clear_all(self):
        """Clear all URL fields"""
        for entry_data in self.url_entries:
            entry_data['entry'].delete(0, 'end')
    
    def get_count(self):
        """Get number of non-empty URLs"""
        return len(self.get_urls())
