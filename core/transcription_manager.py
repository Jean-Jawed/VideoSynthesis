"""
Transcription Manager - Manage sequential transcription queue
"""

import uuid
from threading import Thread, Lock
from enum import Enum
from dataclasses import dataclass
from typing import Callable, Optional, Dict, List
from core.transcriber import AudioTranscriber


class TranscriptionStatus(Enum):
    """Transcription task status"""
    QUEUED = "queued"
    TRANSCRIBING = "transcribing"
    DONE = "done"
    FAILED = "failed"


@dataclass
class TranscriptionTask:
    """Represents a transcription task"""
    id: str
    file_path: str
    filename: str
    status: TranscriptionStatus
    progress: float = 0.0
    message: str = ""
    text: Optional[str] = None
    error: Optional[str] = None


class TranscriptionManager:
    """Manages sequential transcription queue (one at a time)"""
    
    def __init__(self, logger):
        """
        Initialize transcription manager
        
        Args:
            logger: Application logger
        """
        self.logger = logger
        self.transcriber = AudioTranscriber(logger)
        
        # Task storage
        self.tasks: Dict[str, TranscriptionTask] = {}
        self.task_order: List[str] = []  # Maintains insertion order
        
        # Queue management
        self.lock = Lock()
        self.queue: List[str] = []
        self.current_task_id: Optional[str] = None
        self.is_processing = False
        
        # Callbacks (multiple listeners supported)
        self.status_callbacks: List[Callable] = []
    
    def add_status_callback(self, callback: Callable):
        """Add a callback for status updates"""
        if callback not in self.status_callbacks:
            self.status_callbacks.append(callback)
    
    def add_transcription(self, file_path: str, filename: str) -> str:
        """
        Add a transcription to the queue
        
        Args:
            file_path: Path to audio/video file
            filename: Display name for the file
            
        Returns:
            Task ID
        """
        task_id = str(uuid.uuid4())
        
        task = TranscriptionTask(
            id=task_id,
            file_path=file_path,
            filename=filename,
            status=TranscriptionStatus.QUEUED,
            message="Waiting in queue..."
        )
        
        with self.lock:
            self.tasks[task_id] = task
            self.task_order.append(task_id)
            self.queue.append(task_id)
        
        self.logger.info(f"Added transcription task: {task_id} - {filename}")
        self._notify_status_change()
        
        # Try to start processing if not already running
        self._process_queue()
        
        return task_id
    
    def _process_queue(self):
        """Process the queue sequentially"""
        with self.lock:
            # If already processing or queue is empty, return
            if self.is_processing or not self.queue:
                return
            
            # Mark as processing
            self.is_processing = True
            
            # Get next task
            task_id = self.queue.pop(0)
            self.current_task_id = task_id
        
        # Start transcription in separate thread
        thread = Thread(target=self._start_transcription, args=(task_id,), daemon=True)
        thread.start()
    
    def _start_transcription(self, task_id: str):
        """Start a transcription task"""
        task = self.tasks.get(task_id)
        if not task:
            with self.lock:
                self.is_processing = False
            return
        
        # Update status
        with self.lock:
            task.status = TranscriptionStatus.TRANSCRIBING
            task.message = "Starting transcription..."
        
        self.logger.info(f"Starting transcription: {task_id}")
        self._notify_status_change()
        
        # Progress callback
        def progress_callback(percent: float, message: str):
            # Update task data with lock
            with self.lock:
                if task_id in self.tasks:
                    self.tasks[task_id].progress = percent
                    self.tasks[task_id].message = message
            # Notify AFTER releasing lock
            self._notify_status_change()
        
        # Completion callback
        def completion_callback(success: bool, text: str, message: str):
            # Update task data with lock
            with self.lock:
                if task_id in self.tasks:
                    if success:
                        self.tasks[task_id].status = TranscriptionStatus.DONE
                        self.tasks[task_id].text = text
                        self.tasks[task_id].progress = 100.0
                        self.tasks[task_id].message = "Transcription complete!"
                    else:
                        self.tasks[task_id].status = TranscriptionStatus.FAILED
                        self.tasks[task_id].error = message
                        self.tasks[task_id].message = f"Failed: {message}"
                
                # Mark as not processing
                self.is_processing = False
                self.current_task_id = None
            
            # Log, notify, and process queue AFTER releasing lock
            self.logger.info(f"Transcription {'completed' if success else 'failed'}: {task_id}")
            self._notify_status_change()
            self._process_queue()
        
        # Start transcription
        self.transcriber.transcribe(
            task.file_path,
            progress_callback,
            completion_callback
        )
    
    def get_all_tasks(self) -> List[TranscriptionTask]:
        """Get all tasks in order"""
        with self.lock:
            return [self.tasks[task_id] for task_id in self.task_order if task_id in self.tasks]
    
    def get_task(self, task_id: str) -> Optional[TranscriptionTask]:
        """Get a specific task"""
        with self.lock:
            return self.tasks.get(task_id)
    
    def get_queue_position(self, task_id: str) -> Optional[int]:
        """Get position in queue (1-indexed), None if not in queue"""
        with self.lock:
            if task_id in self.queue:
                return self.queue.index(task_id) + 1
            return None
    
    def get_summary(self) -> Dict:
        """Get summary statistics"""
        with self.lock:
            total = len(self.tasks)
            queued = len(self.queue)
            active = 1 if self.is_processing else 0
            done = sum(1 for t in self.tasks.values() if t.status == TranscriptionStatus.DONE)
            failed = sum(1 for t in self.tasks.values() if t.status == TranscriptionStatus.FAILED)
            
            return {
                'total': total,
                'queued': queued,
                'active': active,
                'done': done,
                'failed': failed
            }
    
    def clear_completed(self):
        """Clear completed and failed tasks"""
        with self.lock:
            # Remove completed/failed tasks
            to_remove = [
                task_id for task_id, task in self.tasks.items()
                if task.status in [TranscriptionStatus.DONE, TranscriptionStatus.FAILED]
            ]
            
            for task_id in to_remove:
                del self.tasks[task_id]
                if task_id in self.task_order:
                    self.task_order.remove(task_id)
        
        self.logger.info(f"Cleared {len(to_remove)} completed tasks")
        self._notify_status_change()
    
    def _notify_status_change(self):
        """Notify all status callbacks of changes"""
        for callback in self.status_callbacks:
            try:
                callback()
            except Exception as e:
                self.logger.error(f"Error in status callback: {e}")
