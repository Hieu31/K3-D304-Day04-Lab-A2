from __future__ import annotations
from typing import Any
import re
from collections import Counter

def extract_keys(text: str, max_keywords: int = 5) -> dict[str, Any]:
    """Extracts top keywords from text based on frequency, ignoring common stop words."""
    if not text:
        return {"error": "Text is required", "keywords": []}
    
    try:
        # Very basic stop words for both EN and VI
        stop_words = {"the", "a", "an", "and", "or", "but", "is", "are", "was", "were", 
                      "in", "on", "at", "to", "for", "with", "of", "this", "that", "it",
                      "và", "là", "của", "có", "trong", "cho", "với", "để", "một", "những",
                      "các", "không", "thì", "mà", "như", "khi", "tại", "sẽ"}
                      
        # Clean text and split into words
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter out stop words and short words
        filtered_words = [w for w in words if w not in stop_words and len(w) > 2]
        
        # Count frequencies
        counts = Counter(filtered_words)
        
        # Get top N keywords
        top_words = [word for word, count in counts.most_common(max_keywords)]
        
        return {
            "keywords": top_words,
            "error": None
        }
    except Exception as e:
        return {
            "keywords": [],
            "error": str(e)
        }
