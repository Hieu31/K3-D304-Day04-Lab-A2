---
name: extract_keywords
track: custom
kind: compute
requires_env: []
inputs: [text, max_keywords]
outputs: [keywords, error]
side_effect: false
---
# extract_keywords

Trích xuất các từ khóa (keywords) và thực thể chính từ một đoạn văn bản (ví dụ: nội dung bài báo, tweet).
Công cụ này hữu ích khi cần tìm ra chủ đề cốt lõi của một nội dung dài để tiếp tục tra cứu hoặc gắn thẻ bản tin.
