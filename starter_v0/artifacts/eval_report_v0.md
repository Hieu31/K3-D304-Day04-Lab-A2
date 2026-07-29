# Báo Cáo Phân Tích Đánh Giá Baseline (v0)

- **Model Provider**: `gemini`
- **Model**: `gemini-3.1-flash-lite`
- **Version**: `v0`
- **Tập Eval**: `data/eval_base.json` (20 cases)
- **Lần chạy gần nhất**: `2026-07-29T10:33:34`
- **Run File**: [v0_B_base_gemini_20260729T103334835869.json](file:///d:/K3-D304-Day04-Lab-A2/starter_v0/runs/v0_B_base_gemini_20260729T103334835869.json)
- **Bảng dữ liệu trích xuất**: [analysis/base_runs.csv](file:///d:/K3-D304-Day04-Lab-A2/starter_v0/analysis/base_runs.csv)

---

## 📊 1. Tổng quan Metrics

| Chỉ số | Giá trị | Ghi chú |
|---|---|---|
| **Total Cases** | 20 | Tổng số bài test trong base eval |
| **Measured Cases** | 12 | Số case thực thi thành công không bị gián đoạn API |
| **Provider Error Cases** | 8 | Các case bị gián đoạn do Rate Limit API Tier Free (429) |
| **Passed Cases** | 9 | Số case PASS routing & arguments |
| **Case Accuracy** | **75.0%** | Đo trên 12 measured cases (`9 / 12`) |
| **Tool Routing Accuracy** | **83.33%** | Tỉ lệ chọn đúng tool |
| **Argument Accuracy** | **75.0%** | Tỉ lệ truyền tham số chính xác |
| **Multiturn Accuracy** | **80.0%** | Tỉ lệ hoàn thành hội thoại multi-turn |

---

## ❌ 2. Chi tiết các Case LỖI (Failed Cases & Error Logs)

Dưới đây là danh sách toàn bộ các case bị `FAIL` trong đợt chạy `v0`, được chia làm 2 nhóm nguyên nhân:

### A. Nhóm Lỗi do Agent Routing / Prompt / Boundary (3 Cases)

#### 1. `R10_missing_handle`
- **Thất bại ở điểm nào**: Thiếu thông tin bắt buộc (`missing_info`). Agent không hỏi lại mà tự ý gọi tool.
- **Mismatch**: `missing_tool_call`
- **Failure Type**: `missing_info`
- **Expected Tool Call**: `clarify` (Hỏi người dùng bổ sung Twitter handle)
- **Actual Tool Call**: `timeline`
- **Log Error Snippet**:
  ```text
  missing tool call clarify; extra tool call timeline
  ```
- **Phân tích nguyên nhân**: User yêu cầu *"Xem bài viết mới nhất của Sam Altman"*, nhưng không đưa handle `@sama`. Agent tự suy đoán và gọi trực tiếp `timeline` thay vì gọi `clarify` để yêu cầu nhập handle.

---

#### 2. `R12_confirm_before_send`
- **Thất bại ở điểm nào**: Vi phạm ranh giới xác nhận (`wrong_boundary`).
- **Mismatch**: `missing_tool_call`
- **Failure Type**: `wrong_boundary`
- **Expected Tool Call**: `clarify` (với `response_type="yes_no"`)
- **Actual Tool Call**: `send`
- **Log Error Snippet**:
  ```text
  missing tool call clarify; extra tool call send
  ```
- **Phân tích nguyên nhân**: Với các action nhạy cảm (như gửi tin nhắn qua `send`), Agent phải gọi `clarify` loại `yes_no` để hỏi xác nhận trước khi thực hiện. Agent ở `v0` đã gọi thẳng `send`.

---

#### 3. `M02_carryover_timeframe` (Multi-turn)
- **Thất bại ở điểm nào**: Sai giá trị tham số truyền vào (`wrong_arg_value`).
- **Mismatch**: `wrong_arg_value`
- **Failure Type**: `wrong_arg_value`
- **Expected Args**: `query: 'robotics'`
- **Actual Args**: `query: 'latest robotics news today'`
- **Log Error Snippet**:
  ```text
  query: expected 'robotics', got 'latest robotics news today'
  ```
- **Phân tích nguyên nhân**: Khi kế thừa thông tin từ lượt chat trước (carryover), Agent tự ý nối thêm các cụm từ thừa (`latest ... news today`) vào tham số `query` thay vì giữ nguyên keyword chuẩn (`robotics`).

---

### B. Nhóm Lỗi do Hạ tầng Provider Rate Limit (8 Cases)

Do tài khoản Gemini API đang ở Tier Free bị giới hạn **15 Requests / phút**, việc gửi 20 lệnh eval liên tiếp khiến API trả về mã lỗi HTTP `429 RESOURCE_EXHAUSTED`.

| Case ID | Suite | Mode | Failure Type | Trạng thái API / Log Exception Chi tiết |
|---|---|---|---|---|
| **R01_user_tweets_routing** | base | Single-turn | `provider_error` | `ClientError: 429 RESOURCE_EXHAUSTED. Quota limit: 15 per minute, model: gemini-3.1-flash-lite` |
| **R02_search_tweets_routing** | base | Single-turn | `provider_error` | `ClientError: 429 RESOURCE_EXHAUSTED. Quota limit: 15 per minute, model: gemini-3.1-flash-lite` |
| **R03_web_news_routing** | base | Single-turn | `provider_error` | `ClientError: 429 RESOURCE_EXHAUSTED. Quota limit: 15 per minute, model: gemini-3.1-flash-lite` |
| **R08_out_of_scope** | base | Single-turn | `provider_error` | `RemoteProtocolError: Server disconnected without sending a response.` |
| **R11_missing_url** | base | Single-turn | `provider_error` | `ClientError: 429 RESOURCE_EXHAUSTED. Resource has been exhausted.` |
| **R13_parallel_web_and_tweets** | base | Single-turn | `provider_error` | `ClientError: 429 RESOURCE_EXHAUSTED. Resource has been exhausted.` |
| **R14_out_of_scope_coding** | base | Single-turn | `provider_error` | `ClientError: 429 RESOURCE_EXHAUSTED. Resource has been exhausted.` |
| **M06_switch_tool** | base | Multi-turn | `provider_error` | `ClientError: 429 RESOURCE_EXHAUSTED. Quota limit: 15 per minute, model: gemini-3.1-flash-lite` |

---

## ✅ 3. Danh sách 9 Cases ĐẠT (PASS)

| Case ID | Mode | Expected Tool | Actual Tool | Ghi chú |
|---|---|---|---|---|
| **R04_read_url_routing** | Single | `fetch` | `fetch` | Trích xuất đúng nội dung từ URL |
| **R05_limit_arg** | Single | `timeline` | `timeline` | Nhận diện đúng tham số `limit` |
| **R06_timeframe_arg** | Single | `lookup` | `lookup` | Nhận diện đúng mốc thời gian |
| **R07_search_type_arg** | Single | `social_search` | `social_search` | Chọn đúng kiểu tìm kiếm xã hội |
| **R09_no_tool_capability** | Single | `no_tool` | `no_tool` | Trả lời trực tiếp, không gọi tool dư thừa |
| **M01_clarify_then_fill** | Multi | `timeline` | `timeline` | Hỏi lại ở lượt 1, điền đúng tham số ở lượt 2 |
| **M03_correction_handle** | Multi | `timeline` | `timeline` | Đính chính Twitter handle thành công |
| **M04_clarify_then_url** | Multi | `fetch` | `fetch` | Hỏi lại URL ở lượt 1, đọc URL ở lượt 2 |
| **M05_correction_limit** | Multi | `timeline` | `timeline` | Đính chính tham số limit ở lượt 2 |

---

## ⚠️ 4. Lưu ý quan trọng tuân thủ Quy định Eval
- **KHÔNG** chỉnh sửa `query`, `expected arguments` hay `expected behavior` trong file [data/eval_base.json](file:///d:/K3-D304-Day04-Lab-A2/starter_v0/data/eval_base.json).
- Nếu đổi tên tool (rename), chỉ được đồng bộ trường tên tool đồng thời tại 8 vị trí: `system_prompt.md`, `tools.yaml`, `TOOL.md`, `tools/__init__.py`, `eval_base.json`, `eval_group.json`, `eval_research_extension.json`, và `REPORT.md`.
