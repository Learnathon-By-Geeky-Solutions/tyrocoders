import os
import json
import uuid
import shutil
from pathlib import Path
from typing import List, Dict, Any

class DatabaseStorageManager:
    """Manages storage of database files and configurations for chatbots.
    
    This class provides functionality to handle file storage operations related to chatbot
    databases, including saving and retrieving configuration files, managing uploaded files,
    and cleaning up obsolete files when they are no longer needed.
    
    Attributes:
        storage_base (Path): Base directory path where all chatbot data is stored.
            Each chatbot gets its own subdirectory identified by its chatbot_id.
    
    Example usage:
        # Initialize storage manager
        storage_mgr = DatabaseStorageManager(storage_base="custom_storage")
        
        # Save configuration for a specific chatbot
        storage_mgr.save_config("bot123", {"name": "MyBot", "model": "gpt4"})
        
        # Save an uploaded file
        with open("example.csv", "rb") as f:
            storage_mgr.save_uploaded_file("bot123", f, "example.csv")
            
        # Clean up old files
        storage_mgr.clean_old_files("bot123", ["example.csv", "config.json"])
    """
    
    def __init__(self, storage_base: str = "db_storage"):
        """Initialize the database storage manager.
        
        Args:
            storage_base (str): Path to the base storage directory. Defaults to "db_storage".
                The directory will be created if it doesn't exist.
        """
        self.storage_base = Path(storage_base)
        self.storage_base.mkdir(parents=True, exist_ok=True)
        
    def get_chatbot_dir(self, chatbot_id: str) -> Path:
        """Get the directory for a specific chatbot, creating it if necessary.
        
        Args:
            chatbot_id (str): Unique identifier for the chatbot.
            
        Returns:
            Path: Path object representing the chatbot's directory.
        """
        bot_dir = self.storage_base / chatbot_id
        bot_dir.mkdir(parents=True, exist_ok=True)
        return bot_dir
        
    def clean_old_files(self, chatbot_id: str, keep_filenames: List[str]) -> List[str]:
        """Remove files for a chatbot that aren't in the keep_filenames list.
        
        Looks at all files in the chatbot's directory that follow the naming pattern
        "{uuid}_{original_filename}" and removes those where the original_filename
        is not in the keep_filenames list.
        
        Args:
            chatbot_id (str): ID of the chatbot whose files should be cleaned.
            keep_filenames (List[str]): List of original filenames to keep.
            
        Returns:
            List[str]: List of original filenames that were removed.
        """
        db_dir = self.get_chatbot_dir(chatbot_id)
        removed: List[str] = []
        existing: Dict[str, str] = {}
        
        for f in os.listdir(db_dir):
            if "_" in f:
                parts = f.split("_", 1)
                if len(parts) == 2:
                    existing[parts[1]] = f
                    
        for orig, fname in existing.items():
            if orig not in keep_filenames:
                (db_dir / fname).unlink()
                removed.append(orig)
                
        return removed
        
    def save_uploaded_file(self, chatbot_id: str, file_obj, original_filename: str) -> Path:
        """Save an uploaded file for a specific chatbot.
        
        The file is saved with a UUID prefix to ensure uniqueness while preserving
        the original filename.
        
        Args:
            chatbot_id (str): ID of the chatbot this file belongs to.
            file_obj: File-like object with read() method.
            original_filename (str): Original name of the file.
            
        Returns:
            Path: Path where the file was saved.
        """
        db_dir = self.get_chatbot_dir(chatbot_id)
        new_filename = f"{uuid.uuid4()}_{original_filename}"
        dest_path = db_dir / new_filename
        
        # Atomic write
        tmp = dest_path.with_suffix(dest_path.suffix + ".tmp")
        with open(tmp, "wb") as buf:
            shutil.copyfileobj(file_obj, buf)
        tmp.rename(dest_path)
        
        return dest_path
        
    def save_config(self, chatbot_id: str, config: Dict[str, Any]) -> Path:
        """Save configuration data for a chatbot.
        
        Args:
            chatbot_id (str): ID of the chatbot.
            config (Dict[str, Any]): Configuration data to save.
            
        Returns:
            Path: Path where the configuration was saved.
        """
        config_path = self.get_chatbot_dir(chatbot_id) / "config.json"
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        return config_path
        
    def load_config(self, chatbot_id: str) -> Dict[str, Any]:
        """Load configuration data for a chatbot.
        
        Args:
            chatbot_id (str): ID of the chatbot.
            
        Returns:
            Dict[str, Any]: Configuration data as a dictionary. Returns empty dict if
            no configuration exists.
        """
        config_path = self.get_chatbot_dir(chatbot_id) / "config.json"
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}