"""
Text Synthesizer - Generate summaries using various LLM APIs
Supports chunking for long texts
"""

import re
from threading import Thread


class TextSynthesizer:
    def __init__(self, logger):
        self.logger = logger
        self.chunk_size = 4000  # words per chunk
    
    def count_words(self, text):
        """Count words in text"""
        return len(text.split())
    
    def split_into_chunks(self, text, chunk_size=4000):
        """Split text into chunks of approximately chunk_size words"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)
        
        return chunks
    
    def synthesize(self, text, provider, api_key, progress_callback=None, completion_callback=None):
        """
        Synthesize text using specified API provider
        Handles chunking for long texts
        
        Args:
            text: Input text to summarize
            provider: API provider (Claude, OpenAI, Gemini, DeepSeek)
            api_key: API key for the provider
            progress_callback: Function to call with progress (percent, message)
            completion_callback: Function to call when complete (success, summary, message)
        """
        
        def _synthesize():
            try:
                word_count = self.count_words(text)
                self.logger.info(f"Text length: {word_count} words")
                
                if word_count <= self.chunk_size:
                    # Text is short enough, synthesize directly
                    if progress_callback:
                        progress_callback(50, "Generating summary...")
                    
                    summary = self._call_api(text, provider, api_key, mode='direct')
                    
                    if progress_callback:
                        progress_callback(100, "Summary complete!")
                    
                    if completion_callback:
                        completion_callback(True, summary, "Success")
                else:
                    # Text is too long, need to chunk
                    chunks = self.split_into_chunks(text, self.chunk_size)
                    num_chunks = len(chunks)
                    
                    self.logger.info(f"Split into {num_chunks} chunks")
                    
                    # Step 1: Summarize each chunk
                    chunk_summaries = []
                    for i, chunk in enumerate(chunks):
                        if progress_callback:
                            percent = int(((i + 1) / num_chunks) * 80)  # Reserve 20% for final synthesis
                            progress_callback(percent, f"Summarizing chunk {i+1}/{num_chunks}...")
                        
                        summary = self._call_api(chunk, provider, api_key, mode='chunk')
                        chunk_summaries.append(summary)
                        
                        self.logger.info(f"Chunk {i+1}/{num_chunks} summarized")
                    
                    # Step 2: Combine chunk summaries
                    combined_text = '\n\n'.join(chunk_summaries)
                    
                    if progress_callback:
                        progress_callback(90, "Creating final coherent summary...")
                    
                    # Step 3: Generate final coherent summary
                    final_summary = self._call_api(combined_text, provider, api_key, mode='final')
                    
                    if progress_callback:
                        progress_callback(100, "Summary complete!")
                    
                    if completion_callback:
                        completion_callback(True, final_summary, "Success")
                        
            except Exception as e:
                error_msg = f"Synthesis failed: {str(e)}"
                self.logger.error(error_msg)
                
                if completion_callback:
                    completion_callback(False, "", error_msg)
        
        # Start synthesis in separate thread
        thread = Thread(target=_synthesize, daemon=True)
        thread.start()
    
    def _call_api(self, text, provider, api_key, mode='direct'):
        """
        Call the appropriate API to generate summary
        
        Args:
            text: Text to summarize
            provider: API provider
            api_key: API key
            mode: 'direct', 'chunk', or 'final'
        """
        
        # Prepare prompt based on mode
        if mode == 'chunk':
            prompt = f"Provide a comprehensive summary of the following text. Keep all important details and key points. IMPORTANT: Your response must be in the same language as the input text.\n\n{text}"
        elif mode == 'final':
            prompt = f"The following are summaries of different sections of a longer text. Create a single, coherent, well-structured summary that combines these sections. Improve coherence and flow, but do not reduce the content further. IMPORTANT: Your response must be in the same language as the input summaries.\n\n{text}"
        else:  # direct
            prompt = f"Provide a comprehensive and well-structured summary of the following text. IMPORTANT: Your response must be in the same language as the input text.\n\n{text}"
        
        # Call the appropriate API
        if provider == "Claude":
            return self._call_claude(prompt, api_key)
        elif provider == "OpenAI":
            return self._call_openai(prompt, api_key)
        elif provider == "Gemini":
            return self._call_gemini(prompt, api_key)
        elif provider == "DeepSeek":
            return self._call_deepseek(prompt, api_key)
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def _call_claude(self, prompt, api_key):
        """Call Claude API"""
        try:
            from anthropic import Anthropic
            
            client = Anthropic(api_key=api_key)
            
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return message.content[0].text
            
        except Exception as e:
            self.logger.error(f"Claude API error: {str(e)}")
            raise Exception(f"Claude API error: {str(e)}")
    
    def _call_openai(self, prompt, api_key):
        """Call OpenAI API"""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=api_key)
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"OpenAI API error: {str(e)}")
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def _call_gemini(self, prompt, api_key):
        """Call Google Gemini API"""
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            response = model.generate_content(prompt)
            
            return response.text
            
        except Exception as e:
            self.logger.error(f"Gemini API error: {str(e)}")
            raise Exception(f"Gemini API error: {str(e)}")
    
    def _call_deepseek(self, prompt, api_key):
        """Call DeepSeek API"""
        try:
            from openai import OpenAI
            
            # DeepSeek uses OpenAI-compatible API
            client = OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com"
            )
            
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"DeepSeek API error: {str(e)}")
            raise Exception(f"DeepSeek API error: {str(e)}")
