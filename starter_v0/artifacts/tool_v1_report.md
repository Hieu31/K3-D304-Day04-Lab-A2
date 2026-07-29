# Báo cáo V1 - Bổ sung Tool mới cho Research Agent

Nhằm mở rộng tính năng cho hệ thống và thỏa mãn tiêu chí Bonus của Lab (tạo hơn 3 tool mới), nhóm đã quyết định phân tích lại domain của **Research & News Briefing Agent** và bổ sung thêm 3 công cụ cực kỳ hữu ích sau:

### 1. `extract_keywords` (Trích xuất từ khóa)
* **Lý do thêm:** Các bài báo hoặc chuỗi tweet thường rất dài. Để Agent lọc thông tin chuẩn xác và tìm kiếm chéo (cross-reference) tốt hơn, Agent cần trích xuất các thực thể và từ khóa cốt lõi thay vì ném cả đoạn văn bản dài vào ô tìm kiếm.
* **Cơ chế:** Lọc bỏ các "stop words" tiếng Anh/Việt và đếm tần suất để trả về danh sách keywords.
* **Inputs/Outputs:** Nhận `text`, trả về `keywords`.

### 2. `translate_text` (Dịch thuật bản tin)
* **Lý do thêm:** Nguồn tin tức AI và công nghệ đa phần là tiếng Anh (từ các trang như OpenAI, tài khoản @sama, v.v.). Để Agent có thể tổng hợp bản tin gửi cho người dùng Việt Nam, nó cần một công cụ dịch thuật tích hợp.
* **Cơ chế:** Dịch đoạn văn bản sang ngôn ngữ đích (hiện tại đang dùng giả lập - mock implementation để test flow, có thể cắm API dịch thật vào sau).
* **Inputs/Outputs:** Nhận `text` và `target_lang`, trả về `translated_text`.

### 3. `save_note` (Lưu trữ ghi chú nội bộ)
* **Lý do thêm:** Agent nghiên cứu thường phải xử lý chuỗi công việc dài (nhiều turn). Việc lưu trữ các "insight" hoặc tin tức hay vào một file markdown nội bộ (ví dụ: `research_notes.md`) giúp Agent tích lũy kiến thức trong suốt phiên làm việc.
* **Cơ chế:** Mở file local (append mode) và ghi nối thêm nội dung kèm thời gian (timestamp).
* **Inputs/Outputs:** Nhận `note_content`, trả về `status` (thành công/thất bại).

---

### Kết quả triển khai & Smoke-test:
- Cả 3 tool đều có file `TOOL.md` và `tool.py` đúng chuẩn.
- Đã khai báo thành công vào hệ thống (`tools/__init__.py` và `artifacts/tools.yaml`).
- Đã chạy quicktest qua `smoke_test.py` và đều hoạt động mượt mà, không gặp lỗi crash.
- Sẵn sàng để sử dụng vào **10 câu test mở rộng của nhóm** trong `eval_group.json`!
