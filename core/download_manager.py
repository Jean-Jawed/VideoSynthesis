"""
Download Manager - Manage multiple parallel downloads with queue
"""

import uuid
from threading import Thread, Lock
from queue import Queue
from enum import Enum
from dataclasses import dataclass
from typing import Callable, Optional, Dict, List
from core.downloader import VideoDownloader


class DownloadStatus(Enum):
    """Download task status"""
    QUEUED = "queued"
    DOWNLOADING = "downloading"
    DONE = "done"
    FAILED = "failed"


@dataclass
class DownloadTask:
    """Represents a download task"""
    id: str
    url: str
    output_path: str
    status: DownloadStatus
    progress: float = 0.0
    message: str = ""
    output_file: Optional[str] = None
    error: Optional[str] = None


class DownloadManager:
    """Manages multiple parallel downloads with a queue system"""
    
    def __init__(self, logger, max_concurrent=3):
        """
        Initialize download manager
        
        Args:
            logger: Application logger
            max_concurrent: Maximum number of simultaneous downloads (default: 3)
        """
        self.logger = logger
        self.max_concurrent = max_concurrent
        self.downloader = VideoDownloader(logger)
        
        # Task storage
        self.tasks: Dict[str, DownloadTask] = {}
        self.task_order: List[str] = []  # Maintains insertion order
        
        # Thread management
        self.lock = Lock()
        self.active_downloads: List[str] = []
        self.queue: Queue = Queue()
        
        # Callbacks
        self.status_callback: Optional[Callable] = None
    
    def set_status_callback(self, callback: Callable):
        """Set callback for status updates"""
        self.status_callback = callback
    
    def add_download(self, url: str, output_path: str) -> str:
        """
        Add a download to the queue
        
        Args:
            url: Video URL
            output_path: Destination folder
            
        Returns:
            Task ID
        """
        task_id = str(uuid.uuid4())
        
        task = DownloadTask(
            id=task_id,
            url=url,
            output_path=output_path,
            status=DownloadStatus.QUEUED,
            message="Waiting in queue..."
        )
        
        with self.lock:
            self.tasks[task_id] = task
            self.task_order.append(task_id)
            self.queue.put(task_id)
        
        self.logger.info(f"Added download task: {task_id} - {url}")
        self._notify_status_change()
        
        # Try to start download if slots available
        self._process_queue()
        
        return task_id
    
    def _process_queue(self):
        """Process the queue and start downloads if slots available"""
        with self.lock:
            while len(self.active_downloads) < self.max_concurrent and not self.queue.empty():
                task_id = self.queue.get()
                self._start_download(task_id)
    
    def _start_download(self, task_id: str):
        """Start a download task"""
        task = self.tasks.get(task_id)
        if not task:
            return
        
        task.status = DownloadStatus.DOWNLOADING
        task.message = "Starting download..."
        self.active_downloads.append(task_id)
        
        self.logger.info(f"Starting download: {task_id}")
        self._notify_status_change()
        
        # Progress callback
        # Progress callback
        def progress_callback(message: str):
            # Update task data with lock
            with self.lock:
                if task_id in self.tasks:
                    # Update message
                    self.tasks[task_id].message = message
                    
                    # Try to extract percentage from message
                    if "%" in message:
                        try:
                            # Standard yt-dlp percent format: " 10.5%"
                            percent_str = message.split("%")[0].split()[-1]
                            self.tasks[task_id].progress = float(percent_str)
                        except (IndexError, ValueError):
                            pass
            
            # Notify UI - the callback itself should handle thread switching (e.g. via after())
            self._notify_status_change()
        
        # Completion callback
        def completion_callback(success: bool, output_file: Optional[str], message: str):
            # Update task data with lock
            with self.lock:
                if task_id in self.tasks:
                    if success:
                        self.tasks[task_id].status = DownloadStatus.DONE
                        self.tasks[task_id].output_file = output_file
                        self.tasks[task_id].progress = 100.0
                        self.tasks[task_id].message = "Download complete!"
                    else:
                        self.tasks[task_id].status = DownloadStatus.FAILED
                        self.tasks[task_id].error = message
                        self.tasks[task_id].message = f"Failed: {message}"
                    
                    # Remove from active downloads
                    if task_id in self.active_downloads:
                        self.active_downloads.remove(task_id)
            
            # Log, notify, and process queue AFTER releasing lock
            self.logger.info(f"Download {'completed' if success else 'failed'}: {task_id}")
            self._notify_status_change()
            self._process_queue()
        
        # Start download in separate thread
        self.downloader.download(
            task.url,
            task.output_path,
            progress_callback,
            completion_callback
        )
    
    def get_all_tasks(self) -> List[DownloadTask]:
        """Get all tasks in order"""
        with self.lock:
            return [self.tasks[task_id] for task_id in self.task_order if task_id in self.tasks]
    
    def get_task(self, task_id: str) -> Optional[DownloadTask]:
        """Get a specific task"""
        with self.lock:
            return self.tasks.get(task_id)
    
    def get_summary(self) -> Dict:
        """Get summary statistics"""
        with self.lock:
            total = len(self.tasks)
            queued = sum(1 for t in self.tasks.values() if t.status == DownloadStatus.QUEUED)
            active = len(self.active_downloads)
            done = sum(1 for t in self.tasks.values() if t.status == DownloadStatus.DONE)
            failed = sum(1 for t in self.tasks.values() if t.status == DownloadStatus.FAILED)
            
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
                if task.status in [DownloadStatus.DONE, DownloadStatus.FAILED]
            ]
            
            for task_id in to_remove:
                del self.tasks[task_id]
                if task_id in self.task_order:
                    self.task_order.remove(task_id)
        
        self.logger.info(f"Cleared {len(to_remove)} completed tasks")
        self._notify_status_change()
    
    def _notify_status_change(self):
        """Notify status callback of changes"""
        if self.status_callback:
            try:
                self.status_callback()
            except Exception as e:
                self.logger.error(f"Error in status callback: {e}")
