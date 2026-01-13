"""
Synthesis Tab - Generate summaries using various LLM APIs
"""

import customtkinter as ctk
from tkinter import messagebox
from core.synthesizer import TextSynthesizer


class SynthesisTab:
    def __init__(self, parent, app_state, logger):
        self.parent = parent
        self.app_state = app_state
        self.logger = logger
        
        self.synthesizer = TextSynthesizer(logger)
        
        self.setup_ui()
        
        # Check periodically for transcribed text
        self.check_transcribed_text()
    
    def setup_ui(self):
        """Create the Synthesis tab UI"""
        
        # Main container
        container = ctk.CTkFrame(self.parent, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            container,
            text="Text Synthesis",
            font=("Arial", 20, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Input Section
        input_frame = ctk.CTkFrame(container, corner_radius=10)
        input_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        input_header = ctk.CTkFrame(input_frame, fg_color="transparent")
        input_header.pack(fill="x", padx=20, pady=(15, 5))
        
        input_label = ctk.CTkLabel(
            input_header,
            text="Input Text:",
            font=("Arial", 14)
        )
        input_label.pack(side="left")
        
        # Clear button
        clear_btn = ctk.CTkButton(
            input_header,
            text="Clear",
            width=80,
            height=28,
            corner_radius=6,
            command=self.clear_input
        )
        clear_btn.pack(side="right")
        
        self.input_text = ctk.CTkTextbox(
            input_frame,
            font=("Arial", 12),
            corner_radius=8,
            wrap="word",
            height=200
        )
        self.input_text.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        # API Configuration Section
        config_frame = ctk.CTkFrame(container, corner_radius=10)
        config_frame.pack(fill="x", pady=10)
        
        config_inner = ctk.CTkFrame(config_frame, fg_color="transparent")
        config_inner.pack(fill="x", padx=20, pady=15)
        
        # API Selector
        api_label = ctk.CTkLabel(
            config_inner,
            text="AI Provider:",
            font=("Arial", 13)
        )
        api_label.grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        self.api_var = ctk.StringVar(value="Claude")
        self.api_menu = ctk.CTkOptionMenu(
            config_inner,
            values=["Claude", "OpenAI", "Gemini", "DeepSeek"],
            variable=self.api_var,
            width=150,
            height=32,
            corner_radius=8,
            command=self.on_api_change
        )
        self.api_menu.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=(0, 10))
        
        # API Key Input
        key_label = ctk.CTkLabel(
            config_inner,
            text="API Key:",
            font=("Arial", 13)
        )
        key_label.grid(row=1, column=0, sticky="w")
        
        self.api_key_entry = ctk.CTkEntry(
            config_inner,
            placeholder_text="Enter your API key...",
            show="•",
            height=32,
            corner_radius=8,
            font=("Arial", 12),
            width=400
        )
        self.api_key_entry.grid(row=1, column=1, columnspan=2, sticky="ew", padx=(10, 0))
        
        config_inner.grid_columnconfigure(2, weight=1)
        
        # Generate Button
        self.generate_btn = ctk.CTkButton(
            container,
            text="Generate Summary",
            height=45,
            corner_radius=10,
            font=("Arial", 14, "bold"),
            command=self.generate_summary
        )
        self.generate_btn.pack(fill="x", pady=15)
        
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
        
        # Output Section
        output_frame = ctk.CTkFrame(container, corner_radius=10)
        output_frame.pack(fill="both", expand=True, pady=10)
        
        output_header = ctk.CTkFrame(output_frame, fg_color="transparent")
        output_header.pack(fill="x", padx=20, pady=(15, 5))
        
        output_label = ctk.CTkLabel(
            output_header,
            text="Summary:",
            font=("Arial", 14)
        )
        output_label.pack(side="left")
        
        # Copy button
        self.copy_btn = ctk.CTkButton(
            output_header,
            text="Copy Summary",
            width=120,
            height=28,
            corner_radius=6,
            command=self.copy_summary,
            state="disabled"
        )
        self.copy_btn.pack(side="right")
        
        self.output_text = ctk.CTkTextbox(
            output_frame,
            font=("Arial", 12),
            corner_radius=8,
            wrap="word",
            height=200
        )
        self.output_text.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        self.output_text.configure(state="disabled")
    
    def on_api_change(self, choice):
        """Handle API provider change"""
        # Update placeholder based on provider
        placeholders = {
            "Claude": "sk-ant-...",
            "OpenAI": "sk-...",
            "Gemini": "AIza...",
            "DeepSeek": "sk-..."
        }
        self.api_key_entry.configure(placeholder_text=placeholders.get(choice, "Enter API key..."))
        
        # Clear API key when changing provider
        self.api_key_entry.delete(0, "end")
    
    def check_transcribed_text(self):
        """Check if text was transcribed and auto-fill"""
        if self.app_state.get('transcribed_text'):
            text = self.app_state['transcribed_text']
            current_text = self.input_text.get("1.0", "end-1c")
            
            # Only fill if input is empty
            if not current_text.strip():
                self.input_text.delete("1.0", "end")
                self.input_text.insert("1.0", text)
            
            # Clear the flag
            self.app_state['transcribed_text'] = None
        
        # Check again in 500ms
        self.parent.after(500, self.check_transcribed_text)
    
    def clear_input(self):
        """Clear input text"""
        self.input_text.delete("1.0", "end")
    
    def generate_summary(self):
        """Generate summary using selected API"""
        
        # Get input text
        input_text = self.input_text.get("1.0", "end-1c").strip()
        if not input_text:
            messagebox.showerror("Error", "Please enter text to summarize")
            return
        
        # Get API key
        api_key = self.api_key_entry.get().strip()
        if not api_key:
            messagebox.showerror("Error", "Please enter your API key")
            return
        
        # Get selected provider
        provider = self.api_var.get()
        
        # Store API key in app state (session memory)
        self.app_state['api_keys'][provider] = api_key
        
        # Clear previous output
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.configure(state="disabled")
        
        # Show progress
        self.progress_frame.pack(fill="x", pady=(0, 10))
        self.progress_bar.set(0)
        self.progress_label.configure(text="Preparing text...")
        
        # Disable buttons
        self.generate_btn.configure(state="disabled", text="Generating...")
        self.copy_btn.configure(state="disabled")
        
        word_count = len(input_text.split())
        self.logger.info(f"Starting synthesis with {provider}. Input: {word_count} words")
        
        def progress_callback(percent, message):
            self.progress_bar.set(percent / 100)
            self.progress_label.configure(text=message)
        
        def completion_callback(success, summary, message):
            self.generate_btn.configure(state="normal", text="Generate Summary")
            
            if success:
                self.progress_label.configure(text="✓ Summary generated!", text_color="green")
                self.output_text.configure(state="normal")
                self.output_text.insert("1.0", summary)
                self.output_text.configure(state="disabled")
                self.copy_btn.configure(state="normal")
                
                messagebox.showinfo(
                    "Summary Complete",
                    f"Summary generated successfully!\n\nOriginal: {len(input_text.split())} words\nSummary: {len(summary.split())} words"
                )
            else:
                self.progress_label.configure(text=f"✗ {message}", text_color="red")
                messagebox.showerror("Generation Failed", message)
        
        # Start synthesis
        self.synthesizer.synthesize(
            input_text,
            provider,
            api_key,
            progress_callback,
            completion_callback
        )
    
    def copy_summary(self):
        """Copy summary to clipboard"""
        text = self.output_text.get("1.0", "end-1c")
        if text.strip():
            self.parent.clipboard_clear()
            self.parent.clipboard_append(text)
            messagebox.showinfo("Copied", "Summary copied to clipboard!")