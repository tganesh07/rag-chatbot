import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from app.settings import settings
from app.core.ingestion import processor
from app.core.database import vector_db

class DocumentEventHandler(FileSystemEventHandler):
    """Handles file system events for the data directory."""
    
    def on_created(self, event):
        if event.is_directory:
            return
        self._process_file(event.src_path, "created")

    def on_modified(self, event):
        if event.is_directory:
            return
        self._process_file(event.src_path, "modified")
        
    def on_deleted(self, event):
        if event.is_directory:
            return
        print(f"File deleted: {event.src_path}")
        vector_db.delete_file_documents(event.src_path)

    def _process_file(self, file_path: str, event_type: str):
        path = Path(file_path)
        # Ignore hidden files or temp files
        if path.name.startswith('.'):
            return
            
        print(f"File {event_type}: {path}")
        try:
            # 1. Load Document
            docs = processor.load_file(path)
            if not docs:
                print(f"No content extracted from {path}")
                return
                
            # 2. Split Document
            chunks = processor.chunk_documents(docs)
            print(f"Generated {len(chunks)} chunks from {path}")
            
            # 3. Update Vector DB
            # For extraction, we treat modify as a full re-index of the file
            vector_db.update_file(str(path), chunks)
            print(f"Successfully indexed {path}")
            
        except Exception as e:
            print(f"Error extracting {path}: {e}")

class FileWatcher:
    def __init__(self):
        self.observer = Observer()
        self.handler = DocumentEventHandler()
        self.directory = str(settings.DATA_PATH)

    def index_initial_files(self):
        print(f"Indexing existing files in {self.directory}...")
        path = Path(self.directory)
        if not path.exists():
            return
        for file_path in path.rglob('*'):
            if file_path.is_file():
                self.handler._process_file(str(file_path), "initial_index")

    def start(self):
        print(f"Starting file watcher on: {self.directory}")
        if not Path(self.directory).exists():
             Path(self.directory).mkdir(parents=True, exist_ok=True)
             
        self.observer.schedule(self.handler, self.directory, recursive=True)
        self.observer.start()
        
    def stop(self):
        self.observer.stop()
        self.observer.join()

# Global instance
file_watcher = FileWatcher()
