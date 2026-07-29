# Báo Cáo Đánh Giá Eval Baseline (v0)

- **Model Provider**: `groq`
- **Model**: `openai/gpt-oss-120b`
- **Version**: `v0`
- **Tập Eval**: `data/eval_base.json` (20 cases)
- **Run File**: [runs/v0_B_base_groq_20260729T101251117761.json](file:///d:/K3-D304-Day04-Lab-A2/starter_v0/runs/v0_B_base_groq_20260729T101251117761.json)
- **Prompt Hash**: `f0c107a9d7a14032c948d642d7c36f2a85cb6d69a099530093a874c94d472446`
- **Tools Hash**: `011c271ef0bbad1e19a5d7b660b2ed481b7d72950f1faa8a0798c3bdd8784ee1`

---

## 📊 1. Tổng quan Metrics Baseline v0

| Chỉ số Metric | Giá trị v0 | Ghi chú |
|---|---|---|
| **Total Cases** | 20 | Tổng số bài test trong base eval |
| **Measured Cases** | 20 | Số case đo đạc thành công (100%) |
| **Provider Error Cases** | 0 | Không bị lỗi API / timeout |
| **Passed Cases** | 11 | Số case đạt yêu cầu |
| **Case Accuracy** | **55.0%** (`11 / 20`) | Tỉ lệ hoàn thành đúng tổng thể |
| **Tool Routing Accuracy** | **65.0%** (`13 / 20`) | Tỉ lệ chọn đúng tool |
| **Argument Accuracy** | **55.0%** (`11 / 20`) | Tỉ lệ truyền đúng tham số |
| **Multiturn Accuracy** | **66.67%** (`4 / 6`) | Tỉ lệ thoại multi-turn đạt chuẩn |

---

## ❌ 2. Chi tiết 9 Cases LỖI (Failures in v0)

### 1. `R03_web_news_routing`
- **Loại lỗi**: `wrong_arg_value`
- **Lỗi ở đâu**: Agent truyền tham số `query` chứa từ thừa.
- **Mismatch**: Expected `query: 'AI'`, got `query: 'AI news'`.

### 2. `R08_out_of_scope`
- **Loại lỗi**: `out_of_scope` / `wrong_tool`
- **Lỗi ở đâu**: Câu hỏi ngoài phạm vi nhưng Agent vẫn tự ý gọi tool thay vì trả lời `no_tool`.

### 3. `R10_missing_handle`
- **Loại lỗi**: `missing_info`
- **Lỗi ở đâu**: Yêu cầu xem bài đăng nhưng chưa có handle. Agent gọi trực tiếp `timeline` thay vì gọi `clarify` để hỏi xin handle.

### 4. `R11_missing_url`
- **Loại lỗi**: `missing_info`
- **Lỗi ở đâu**: Yêu cầu đọc trang web nhưng thiếu URL. Agent gọi thẳng `fetch` thay vì gọi `clarify` để xin link URL.

### 5. `R12_confirm_before_send`
- **Loại lỗi**: `wrong_boundary`
- **Lỗi ở đâu**: Action gửi tin nhắn nhạy cảm. Agent gọi trực tiếp `send` mà không dùng `clarify(response_type="yes_no")` để chờ xác nhận.

### 6. `R13_parallel_web_and_tweets`
- **Loại lỗi**: `wrong_tool`
- **Lỗi ở đâu**: Yêu cầu tra cứu kết hợp web & social chưa chọn được routing tối ưu.

### 7. `M01_clarify_then_fill` (Multi-turn)
- **Loại lỗi**: `missing_info`
- **Lỗi ở đâu**: Chưa thực hiện bước hỏi xin thông tin ở lượt đầu tiên.

### 8. `M02_carryover_timeframe` (Multi-turn)
- **Loại lỗi**: `wrong_arg_value`
- **Lỗi ở đâu**: Khi hỏi nối tiếp, Agent tự thêm từ thừa (`latest robotics news today`) vào query thay vì giữ nguyên keyword cốt lõi (`robotics`).

---

## ✅ 3. Danh sách 11 Cases ĐẠT (PASS in v0)

- `R01_user_tweets_routing`
- `R02_search_tweets_routing`
- `R04_read_url_routing`
- `R05_limit_arg`
- `R06_timeframe_arg`
- `R07_search_type_arg`
- `R09_no_tool_capability`
- `R14_out_of_scope_coding`
- `M03_correction_handle`
- `M04_clarify_then_url`
- `M05_correction_limit`
