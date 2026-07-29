---
name: translate_text
track: custom
kind: compute
requires_env: []
inputs: [text, target_lang]
outputs: [translated_text, error]
side_effect: false
---
# translate_text

Dịch một đoạn văn bản ngoại ngữ sang ngôn ngữ đích (thường là tiếng Việt).
Hữu ích khi agent đọc được các bài báo/tweet tiếng Anh và cần tóm tắt lại bằng tiếng Việt cho người dùng.
