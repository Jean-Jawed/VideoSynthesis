"""
Transcription Results Tab - View and export transcription results
"""

import customtkinter as ctk
from ui.widgets import TranscriptionResultCard


class TranscriptionResultsTab:
    def __init__(self, parent, transcription_manager, logger):
        self.parent = parent
        self.transcription_manager = transcription_manager
        self.logger = logger
        
        # Store result cards
        self.result_cards = {}  # {task_id: TranscriptionResultCard}
        
        # Set callback for transcription manager updates
        self.transcription_manager.add_status_callback(self.update_results_display)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Create the Transcription Results tab UI"""
        
        # Main container (regular Frame, using the global scrollbar from main.py)
        container = ctk.CTkFrame(self.parent, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Configure grid
        container.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            container,
            text="Transcription Results",
            font=("Arial", 20, "bold")
        )
        title_label.grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        # Info text
        info_label = ctk.CTkLabel(
            container,
            text="Completed transcriptions appear here. You can copy or export each result individually.",
            font=("Arial", 12),
            text_color="gray50"
        )
        info_label.grid(row=1, column=0, sticky="w", pady=(0, 20))
        
        # Action buttons
        action_frame = ctk.CTkFrame(container, fg_color="transparent")
        action_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        
        self.count_label = ctk.CTkLabel(
            action_frame,
            text="No results yet",
            font=("Arial", 12),
            text_color="gray"
        )
        self.count_label.pack(side="left")
        
        clear_btn = ctk.CTkButton(
            action_frame,
            text="Clear All Results",
            width=140,
            height=32,
            corner_radius=8,
            fg_color="#d32f2f",
            hover_color="#b71c1c",
            command=self.clear_all_results
        )
        clear_btn.pack(side="right")
        
        # Results container (direct children, no nested scroll)
        self.results_container = ctk.CTkFrame(container, fg_color="transparent")
        self.results_container.grid(row=3, column=0, sticky="ew")
        self.results_container.grid_columnconfigure(0, weight=1)
        
        # Store container reference for later
        self.container = container
        
        # Initial check for existing results
        self.update_results_display()
    
    def update_results_display(self):
        """Update the results display (called from transcription manager)"""
        # This needs to run on the main thread
        try:
            self.parent.after(0, self._update_results_display_impl)
        except:
            # If parent is not available yet, skip
            pass
    
    def _update_results_display_impl(self):
        """Implementation of results display update"""
        try:
            # Get all tasks
            tasks = self.transcription_manager.get_all_tasks()
            
            # Create result cards for completed transcriptions
            for task in tasks:
                if task.status.value == 'done' and task.id not in self.result_cards:
                    self.create_result_card(task)
            
            # Update count label
            completed_count = sum(1 for t in tasks if t.status.value == 'done')
            if completed_count == 0:
                self.count_label.configure(text="No results yet")
            elif completed_count == 1:
                self.count_label.configure(text="1 result")
            else:
                self.count_label.configure(text=f"{completed_count} results")
            
        except Exception as e:
            self.logger.error(f"Error updating results display: {e}")
    
    def create_result_card(self, task):
        """Create a result card for a completed transcription"""
        try:
            card = TranscriptionResultCard(
                self.results_container,
                task.filename,
                task.text
            )
            
            # Add to grid
            row = len(self.result_cards)
            card.grid(row=row, column=0, sticky="ew", pady=10)
            
            # Store reference
            self.result_cards[task.id] = card
            
            self.logger.info(f"Created result card for {task.filename}")
            
        except Exception as e:
            self.logger.error(f"Error creating result card: {e}")
    
    def clear_all_results(self):
        """Clear all result cards"""
        from tkinter import messagebox
        
        if not self.result_cards:
            messagebox.showinfo("No Results", "There are no results to clear.")
            return
        
        # Confirm with user
        result = messagebox.askyesno(
            "Clear All Results",
            f"Are you sure you want to clear all {len(self.result_cards)} result(s)?\n\nThis will also remove them from the transcription manager.",
            icon='warning'
        )
        
        if not result:
            return
        
        # Get task IDs to remove
        task_ids = list(self.result_cards.keys())
        
        # Remove result cards
        for card in self.result_cards.values():
            card.destroy()
        self.result_cards.clear()
        
        # Clear from transcription manager
        self.transcription_manager.clear_completed()
        
        # Update display
        self.update_results_display()
        
        self.logger.info(f"Cleared {len(task_ids)} results")
