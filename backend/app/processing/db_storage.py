import os
import json
import uuid
import shutil
from pathlib import Path
from typing import List, Dict, Any

class DatabaseStorageManager:
    """Manages storage of database files and configurations."""
    def __init__(self, storage_base: str = "db_storage"):
        self.storage_base = Path(storage_base)
        self.storage_base.mkdir(parents=True, exist_ok=True)

    def get_chatbot_dir(self, chatbot_id: str) -> Path:
        bot_dir = self.storage_base / chatbot_id
        bot_dir.mkdir(parents=True, exist_ok=True)
        return bot_dir

    def clean_old_files(self, chatbot_id: str, keep_filenames: List[str]) -> List[str]:
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
        config_path = self.get_chatbot_dir(chatbot_id) / "config.json"
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        return config_path

    def load_config(self, chatbot_id: str) -> Dict[str, Any]:
        config_path = self.get_chatbot_dir(chatbot_id) / "config.json"
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
