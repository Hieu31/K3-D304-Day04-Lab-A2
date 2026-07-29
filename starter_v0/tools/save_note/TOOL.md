---
name: save_note
track: custom
kind: compute
requires_env: []
inputs: [note_content, filename]
outputs: [status, error]
side_effect: true
---
# save_note

Lưu các ghi chú, tóm tắt hoặc nội dung quan trọng vào một file văn bản.
Giúp Agent ghi nhớ các thông tin tìm được trong suốt phiên làm việc. Cần confirm trước khi lưu nếu ghi đè, nhưng mặc định là append (nối thêm).
