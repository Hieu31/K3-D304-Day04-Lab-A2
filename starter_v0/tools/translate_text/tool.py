from __future__ import annotations
from typing import Any
import requests
import urllib.parse

def translate(text: str, target_lang: str = "vi") -> dict[str, Any]:
    """
    Dịch văn bản sử dụng MyMemory Translation API (Free, không cần API key).
    Hỗ trợ dịch chuẩn xác các đoạn văn bản tin tức sang tiếng Việt.
    """
    if not text:
        return {"error": "Text is required", "translated_text": None}
    
    try:
        # Detect source language automatically by default in MyMemory
        # langpair format: "autodetect|vi"
        langpair = f"autodetect|{target_lang}"
        
        url = "https://api.mymemory.translated.net/get"
        params = {
            "q": text,
            "langpair": langpair
        }
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        
        if data and "responseData" in data and "translatedText" in data["responseData"]:
            translated = data["responseData"]["translatedText"]
            
            # API trả về lỗi (quota) dưới dạng text nếu bị giới hạn
            if "MYMEMORY WARNING:" in translated:
                return {
                    "translated_text": None,
                    "error": f"API Quota limit reached: {translated}"
                }
                
            return {
                "translated_text": translated,
                "error": None
            }
        else:
            return {
                "translated_text": None,
                "error": "Invalid response format from translation API"
            }
            
    except requests.RequestException as e:
        return {
            "translated_text": None,
            "error": f"Network error during translation: {str(e)}"
        }
    except Exception as e:
        return {
            "translated_text": None,
            "error": f"Translation failed: {str(e)}"
        }
