from __future__ import annotations
from typing import Any
from pathlib import Path
import datetime

def save(note_content: str, filename: str = "research_notes.md") -> dict[str, Any]:
    """Appends notes to a local markdown file."""
    if not note_content:
        return {"error": "Note content is required", "status": None}
    
    try:
        # Lưu file trong thư mục chạy
        save_path = Path.cwd() / filename
        
        # Thêm timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"\n\n## Note added at {timestamp}\n{note_content}\n"
        
        with open(save_path, "a", encoding="utf-8") as f:
            f.write(entry)
            
        return {
            "status": f"Successfully appended to {filename}",
            "error": None
        }
    except Exception as e:
        return {
            "status": None,
            "error": str(e)
        }
