import os
from pathlib import Path
from typing import Dict, Any

class DatabaseDetector:
    """Detects database types from files using magic bytes and heuristics."""
    
    @staticmethod
    def detect_db_type(path: Path) -> Dict[str, Any]:
        """
        Detects database type from a file path
        Args:
            path: Path to database file
        Returns:
            Dict with detected type and relevant metadata
        """
        result: Dict[str, Any] = {"original_path": str(path), "filename": path.name}

        # Initial hint from extension
        ext = path.suffix.lower()
        if ext in (".sqlite", ".db", ".sqlite3"):
            result["likely_type"] = "sqlite"
        elif ext == ".sql":
            result["likely_type"] = "sql_dump"
        elif ext == ".dump":
            result["likely_type"] = "postgres_dump"

        # Read header for magic bytes and text patterns
        try:
            with open(path, "rb") as f:
                header = f.read(100)
                # SQLite
                if header.startswith(b"SQLite format 3"):
                    result["db_type"] = "sqlite"
                    return result
                # MySQL binlog
                if len(header) >= 4 and header[:4] == b"\xfe\x62\x69\x6e":
                    result["db_type"] = "mysql_binlog"
                    return result
                # SQL dump (MySQL or Postgres)
                if b"CREATE TABLE" in header or b"INSERT INTO" in header or b"COPY " in header:
                    if b"PostgreSQL database dump" in header:
                        result["db_type"] = "postgres_dump"
                    else:
                        result["db_type"] = "sql_dump"
                    return result
        except Exception as e:
            result["error"] = str(e)

        # Fallback to likely type or unknown
        result["db_type"] = result.get("likely_type", "unknown")
        return result
