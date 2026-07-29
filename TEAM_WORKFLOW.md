# Hướng dẫn Triển khai Lab 04 - Kế hoạch Chạy đua Chi tiết (Micro-level)

Tài liệu này cung cấp **hướng dẫn cầm tay chỉ việc** cho từng thành viên trong nhóm, với các file cụ thể cần mở, các hàm cần viết và các trường JSON cần đọc.

---

## 👥 Phân vai (Roles)
- **👨‍🚀 P1 - Prompt & Eval Lead:** Trực tiếp tương tác với model qua prompt.
- **👨‍💻 P2 - Tool & Core Dev:** Viết logic Python cho tool mới.
- **🎨 P3 - UI & Deploy Engineer:** Xây dựng Streamlit app.
- **📝 P4 - QA, Data & Report:** Viết JSON eval và document báo cáo.

---

## 🕒 Phase 1: Setup & Baseline (09:15 – 09:40)
**Mục tiêu:** Mọi người đều có `.venv` chạy được, có điểm xuất phát `v0`.

### 👨‍🚀 P1 - Prompt & Eval
1. Mở file `starter_v0/.env`, điền `PROVIDER_API_KEY_OPENROUTER=...`
2. Mở terminal, chạy: `python scripts/preflight_provider.py --provider openrouter`. Phải thấy chữ PASS xanh.
3. Chạy lệnh: `python run_eval.py --provider openrouter --version v0 --suite base --eval-cases data/eval_base.json`
4. Lệnh trên sinh ra file log trong thư mục `runs/` (ví dụ: `runs/run_openrouter_v0_base_xxxx.json`).
5. Đọc nộp cho P4 4 chỉ số in ra cuối màn hình (case_accuracy, tool_routing_accuracy, argument_accuracy, multiturn_accuracy).

### 👨‍💻 P2 - Tool Dev
1. Quyết định nhanh làm tool gì (VD: `weather`, `calculator`, `get_stock_price`). Thống nhất lấy `calculator` làm ví dụ.
2. Tạo thư mục `tools/calculator/`.
3. Tạo file `tools/calculator/TOOL.md`. Viết nháp cấu trúc: Tên tool, mô tả, các tham số đầu vào.
4. Tạo file `tools/calculator/__init__.py`. Viết khung hàm:
   ```python
   def run(args: dict) -> str:
       # logic tính toán
       return str(result)
   ```

### 🎨 P3 - UI Dev
1. Tạo môi trường nếu chưa có. Chạy: `pip install streamlit>=1.30.0`
2. Tạo file `starter_v0/app.py`.
3. Import thử: `from chat import run_model_tool_loop`.
4. Viết khung Streamlit cơ bản:
   ```python
   import streamlit as st
   st.title("Research Agent")
   prompt = st.chat_input("Nhập câu hỏi...")
   if prompt:
       st.chat_message("user").write(prompt)
   ```

### 📝 P4 - QA & Docs
1. Mở file `artifacts/version_log.csv`. Nếu chưa có, tạo mới với header y hệt trong README:
   `version,author,changed_artifact,artifact_version,prompt_hash,tools_hash,reason,hypothesis,metric_name,metric_before,metric_after,run_file`
2. Thêm dòng v0, điền 4 metric nhận được từ P1 vào. Cột `metric_after` điền giá trị hiện tại.
3. Mở `starter_v0/samples/eval_group.schema.example.json` để học cấu trúc JSON cần viết.

---

## 🕒 Phase 2: Tool Mới & Tối ưu v1 (09:40 – 10:15)
**Mục tiêu:** Agent dùng được tool mới, và sửa được 1 lỗi ngớ ngẩn của v0.

### 👨‍🚀 P1 - Prompt & Eval
1. Mở file JSON sinh ra ở v0 (`runs/run_openrouter_v0...`).
2. Search chữ `"failures":`. Xem case nào fail. 
   - *Ví dụ:* Model gọi `social_search` nhưng thiếu tham số `query`.
3. Mở `artifacts/system_prompt.md`. Thêm rule: *"Khi dùng social_search, luôn phải truyền tham số query chứa từ khóa."*
4. Mở `artifacts/tools.yaml`. Kiểm tra mô tả của `social_search`, sửa cho rõ ràng hơn.
5. P2 đưa tool mới, P1 copy định dạng YAML (tên, input schema) vào file `artifacts/tools.yaml`.
6. Chạy eval v1: `python run_eval.py --provider openrouter --version v1 --suite base --eval-cases data/eval_base.json`

### 👨‍💻 P2 - Tool Dev
1. Code logic Python cho `calculator` trong `__init__.py`.
2. Mở `tools/__init__.py`. Import hàm run của `calculator` và thêm vào dict `AVAILABLE_TOOLS`. Ví dụ:
   ```python
   from tools.calculator import run as run_calc
   AVAILABLE_TOOLS = {
       "clarify": run_clarify,
       "calculator": run_calc
   }
   ```
3. Test bằng cách tự tạo 1 file `test.py` gọi hàm `run_calc({"expression": "1+1"})` xem ra đúng "2" không. Đưa thông tin cho P1 thêm vào YAML.

### 🎨 P3 - UI Dev
1. Triển khai gọi `run_model_tool_loop(prompt, ...)` trong `app.py`.
2. Hàm này trả về một generator (yield ra các event). Dùng vòng lặp for hứng event:
   ```python
   for event in run_model_tool_loop(...):
       if event["type"] == "tool_call":
           with st.expander(f"🛠 Gọi tool: {event['tool_name']}"):
               st.json(event["args"])
       elif event["type"] == "tool_result":
           with st.expander("✅ Kết quả tool"):
               st.write(event["result"])
       elif event["type"] == "text":
           st.chat_message("assistant").write(event["content"])
   ```
3. Chạy thử: `streamlit run app.py` ở local.

### 📝 P4 - QA & Docs
1. Mở file `data/eval_group.json`. Gõ ngoặc vuông `[]`.
2. Bắt đầu viết 5 case single-turn (không có `turns`, chỉ có `query`).
   ```json
   {
      "id": "team_single_1",
      "phase": "B",
      "failure_type": "wrong_tool",
      "query": "Tìm các bài viết về AI trên mạng xã hội",
      "expect": {"tool_calls": [{"name": "social_search", "arguments": {"query": "AI"}}]},
      "metadata": {"what_it_tests": "Test xem agent có gọi social_search thay vì lookup không"}
   }
   ```
3. Cập nhật `v1` vào `version_log.csv`. Điền rõ lý do (hypothesis) mà P1 đã dùng để sửa prompt.

---

## 🕒 Phase 3: Tối ưu v2, Hoàn thiện UI & Eval Data (10:15 – 11:05)

### 👨‍🚀 P1 - Prompt & Eval
1. Đọc file run JSON của v1. Xem lỗi tiếp theo.
2. *Ví dụ:* Model gọi tool dư thừa khi người dùng chỉ chào hỏi. -> Sửa prompt: *"Nếu người dùng chỉ chào hỏi, không gọi bất kỳ tool nào, hãy trả về text ngay."*
3. Chạy eval v2: `python run_eval.py --provider openrouter --version v2 --suite base --eval-cases data/eval_base.json`

### 👨‍💻 P2 - Tool Dev
1. Viết tiếp các case khó phụ P4. Đặc biệt là phần multi-turn (nhiều lượt chat) trong `eval_group.json`.
   - Multi-turn phải dùng `"turns": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, {"role": "user", "content": "..."}]` thay vì `"query"`.
2. Double check xem tất cả các tool trong thư mục `tools/` đã khớp 100% tên với `artifacts/tools.yaml` chưa. Nếu sai chữ cái hoa/thường, eval sẽ báo lỗi.

### 🎨 P3 - UI Dev
1. Trau chuốt UI: Thêm sidebar hiển thị Version đang chạy, và hiển thị "Mô tả Agent" (System Prompt).
2. Tích hợp Cloudflare Tunnel để đưa ra ngoài:
   - Cài Cloudflare (nếu dùng Windows tải file .exe, Mac/Linux dùng brew/apt).
   - Mở terminal khác: `cloudflared tunnel --url http://localhost:8501`.
   - Lấy link `https://xxxx.trycloudflare.com` gửi cho team.

### 📝 P4 - QA & Docs
1. Hoàn thành toàn bộ 10 case trong `data/eval_group.json` (5 single, 5 multi).
2. Tạo file `artifacts/REPORT.md`.
3. Viết xong **Phần A (Giới thiệu Agent)**:
   - Tên Agent.
   - Danh sách Tool (tên + mô tả ngắn).
   - Paste link Cloudflare Tunnel của P3 vào.

---

## 🕒 Phase 4: Sẵn sàng Demo & Report A (11:05 – 11:30)

### 👨‍🚀 P1 & 🎨 P3 (Rehearsal/Diễn tập)
1. P3 bật UI. P1 đóng vai trò User.
2. P1 chat 3 kịch bản:
   - **Kịch bản 1:** "Tìm kiếm bài viết mới nhất trên tài khoản X của công ty" -> Xem tool `timeline` có chạy đúng không.
   - **Kịch bản 2:** "Đăng bài: Khuyến mãi tháng này" -> Xem tool `clarify` có chặn lại hỏi "Bạn có chắc chắn muốn đăng không?" (Boundary nhạy cảm).
   - **Kịch bản 3:** Thử tool mới của P2.

### 👨‍💻 P2
1. Trực chiến. Nếu UI lúc P1/P3 test mà gọi tool bị báo lỗi "Crash Python", P2 lao vào fix file trong `tools/` ngay lập tức.

### 📝 P4
1. Kiểm tra lại format `REPORT.md`. Đảm bảo file được trình bày đẹp, gọn gàng. Dùng Markdown Table nếu cần.

---

## 🕒 Phase 5: Showdown & Chốt v3, Nộp bài (11:30 – 12:40)

### 🎨 P3 (Lead Demo - 11:30)
1. Mở tab browser to, share màn hình. Giới thiệu nhanh Agent dựa trên nội dung Phần A của P4.
2. Thực hiện Live Chat trực tiếp.

### 👨‍🚀 P1 & 👨‍💻 P2 (Chốt v3 - 12:15)
1. Dựa trên lỗi lòi ra lúc Demo, P1 sửa prompt lần cuối. P2 hỗ trợ nếu cần sửa file YAML.
2. P1 chạy v3 (base eval). 
3. **Quan trọng:** P2 chạy cái team eval để ra minh chứng:
   `python run_eval.py --provider openrouter --version v3 --suite group --eval-cases data/eval_group.json`

### 📝 P4 (Report B & Nộp Bài - 12:30)
1. Mở file `REPORT.md` (Phần B). 
2. Viết kết luận: Bảng so sánh 4 phiên bản v0, v1, v2, v3 (chỉ số tăng/giảm ra sao). Lỗi nào sửa mãi không được? Bài học rút ra?
3. **12:35**: Chạy lệnh xóa môi trường ảo: `rm -rf .venv`.
4. Mở `.env` xóa trắng API Key.
5. Zip folder `starter_v0/` nộp theo yêu cầu của Giảng viên.
