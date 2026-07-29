import sys
from pathlib import Path
from env_loader import load_lab_env

load_lab_env(Path.cwd())
from tools import TOOL_FUNCTIONS as T

print("--- TESTING CORE TOOLS SMOKE TEST ---")

for tool_name in ['lookup', 'fetch', 'timeline', 'social_search', 'extract_keywords', 'translate_text', 'save_note']:
    if tool_name in T:
        try:
            if tool_name == 'lookup':
                res = T[tool_name]('AI', max_results=1)
            elif tool_name == 'fetch':
                res = T[tool_name]('https://example.com')
            elif tool_name == 'timeline':
                res = T[tool_name]('sama', limit=1)
            elif tool_name == 'social_search':
                res = T[tool_name]('OpenAI', limit=1)
            elif tool_name == 'extract_keywords':
                res = T[tool_name]('Trí tuệ nhân tạo (AI) đang phát triển rất mạnh mẽ trong năm 2026.')
            elif tool_name == 'translate_text':
                res = T[tool_name]('Artificial Intelligence is transforming the world very fast.')
            elif tool_name == 'save_note':
                res = T[tool_name]('Đây là một note thử nghiệm.')
            
            items = res.get('items') or [] if isinstance(res, dict) and 'items' in res else []
            error = res.get('error') if isinstance(res, dict) else None
            result = res.get('keywords') or res.get('translated_text') or res.get('status') if isinstance(res, dict) else None
            
            # Print status
            if tool_name in ['extract_keywords', 'translate_text', 'save_note']:
                print(f"[{tool_name.upper()}] error: {error}, result: {result}")
            else:
                print(f"[{tool_name.upper()}] error: {error}, items: {len(items)}")
        except Exception as e:
            print(f"[{tool_name.upper()}] EXCEPTION: {e}")
    else:
        print(f"[{tool_name.upper()}] NOT FOUND IN TOOL_FUNCTIONS")
