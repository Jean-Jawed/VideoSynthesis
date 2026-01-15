"""
Status Log Widget - Real-time status display for tasks
"""

import customtkinter as ctk


class StatusLog(ctk.CTkFrame):
    """Widget for displaying real-time task status"""
    
    # Status icons and colors
    STATUS_ICONS = {
        'queued': '🟡',
        'downloading': '🔵',
        'transcribing': '🔵',
        'done': '🟢',
        'failed': '🔴'
    }
    
    STATUS_COLORS = {
        'queued': 'gray',
        'downloading': '#2196F3',
        'transcribing': '#2196F3',
        'done': '#4CAF50',
        'failed': '#f44336'
    }
    
    def __init__(self, parent, title="Status:", **kwargs):
        super().__init__(parent, corner_radius=10, **kwargs)
        
        self.task_labels = {}  # {task_id: label_widget}
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        
        # Header
        header_label = ctk.CTkLabel(
            self,
            text=title,
            font=("Arial", 14, "bold")
        )
        header_label.grid(row=0, column=0, sticky="w", padx=20, pady=(15, 5))
        
        # Scrollable frame for status entries
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            height=200,
            fg_color="transparent"
        )
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 10))
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        
        # Summary label
        self.summary_label = ctk.CTkLabel(
            self,
            text="No tasks",
            font=("Arial", 11),
            text_color="gray"
        )
        self.summary_label.grid(row=2, column=0, sticky="w", padx=20, pady=(0, 15))
        
        # Configure row weights
        self.grid_rowconfigure(1, weight=1)
    
    def update_task(self, task_id, status, message, name="", progress=None):
        """
        Update or add a task status
        
        Args:
            task_id: Unique task identifier
            status: Status string ('queued', 'downloading', 'done', etc.)
            message: Status message
            name: Optional task name/filename
            progress: Optional progress percentage (0-100)
        """
        icon = self.STATUS_ICONS.get(status, '⚪')
        color = self.STATUS_COLORS.get(status, 'gray')
        
        # Build status text
        if name:
            status_text = f"{icon} {name} - {message}"
        else:
            status_text = f"{icon} {message}"
        
        # Add progress if available
        if progress is not None and status in ['downloading', 'transcribing']:
            status_text += f" ({progress:.0f}%)"
        
        # Create or update label
        if task_id not in self.task_labels:
            label = ctk.CTkLabel(
                self.scroll_frame,
                text=status_text,
                font=("Arial", 11),
                text_color=color,
                anchor="w"
            )
            row = len(self.task_labels)
            label.grid(row=row, column=0, sticky="ew", pady=2)
            self.task_labels[task_id] = label
        else:
            self.task_labels[task_id].configure(text=status_text, text_color=color)
    
    def remove_task(self, task_id):
        """Remove a task from the log"""
        if task_id in self.task_labels:
            self.task_labels[task_id].destroy()
            del self.task_labels[task_id]
            
            # Re-grid remaining labels
            for i, label in enumerate(self.task_labels.values()):
                label.grid(row=i, column=0, sticky="ew", pady=2)
    
    def clear_all(self):
        """Clear all tasks"""
        for label in self.task_labels.values():
            label.destroy()
        self.task_labels.clear()
        self.update_summary("No tasks")
    
    def update_summary(self, summary_text):
        """Update the summary label"""
        self.summary_label.configure(text=summary_text)
    
    def set_summary_from_stats(self, stats):
        """
        Update summary from statistics dict
        
        Args:
            stats: Dict with keys 'total', 'queued', 'active', 'done', 'failed'
        """
        total = stats.get('total', 0)
        queued = stats.get('queued', 0)
        active = stats.get('active', 0)
        done = stats.get('done', 0)
        failed = stats.get('failed', 0)
        
        if total == 0:
            summary = "No tasks"
        else:
            parts = [f"{done}/{total} completed"]
            if active > 0:
                parts.append(f"{active} active")
            if queued > 0:
                parts.append(f"{queued} queued")
            if failed > 0:
                parts.append(f"{failed} failed")
            
            summary = "Progress: " + " | ".join(parts)
        
        self.update_summary(summary)
