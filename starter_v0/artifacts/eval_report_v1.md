# Báo Cáo Đánh Giá Eval Version 1 (v1)

- **Model Provider**: `groq`
- **Model**: `openai/gpt-oss-120b`
- **Version**: `v1`
- **Tập Eval**: `data/eval_base.json` (20 cases)
- **Run File**: [runs/v1_B_base_groq_20260729T111124200985.json](file:///d:/K3-D304-Day04-Lab-A2/starter_v0/runs/v1_B_base_groq_20260729T111124200985.json)
- **Prompt Hash**: `8ae7b0255977ffaca4397daceec918d2bf25d06e9f1599a1dcb685ec920b0cb7`
- **Tools Hash**: `d67ba57e92d3b28d2cffded2ff1eee043c9979a02db4719fe85d9ed2cf9e2bc1`

---

## 📊 1. Tổng quan Metrics Version v1

| Chỉ số Metric | Giá trị v1 | Ghi chú |
|---|---|---|
| **Total Cases** | 20 | Tổng số bài test trong base eval |
| **Measured Cases** | 19 | 19 cases đo đạc thành công (1 case timeout) |
| **Provider Error Cases** | 1 | Dính 1 case timeout mạng ở lượt M06 |
| **Passed Cases** | **17** | **17 cases PASS hoàn toàn** |
| **Case Accuracy** | **89.47%** (`17 / 19`) | Tỉ lệ hoàn thành đạt mức xuất sắc |
| **Tool Routing Accuracy** | **94.74%** (`18 / 19`) | Tỉ lệ chọn đúng tool gần như tuyệt đối |
| **Argument Accuracy** | **89.47%** (`17 / 19`) | Tỉ lệ trích xuất đúng tham số |
| **Multiturn Accuracy** | **100.0%** (`5 / 5`) | 100% các case multi-turn đo được đều PASS |

---

## ❌ 2. Chi tiết các Cases LỖI ở v1 (Failures in v1)

### 1. `R12_confirm_before_send`
- **Loại lỗi**: `wrong_boundary`
- **Nội dung lỗi**: Cần thắt chặt chỉ thị bắt buộc gọi `clarify(response_type="yes_no")` xin xác nhận từ user trước khi gọi `send`.

### 2. `R13_parallel_web_and_tweets`
- **Loại lỗi**: `wrong_tool`
- **Nội dung lỗi**: Routing cho bài toán tìm kiếm kết hợp đa nguồn cần bổ sung quy định cụ thể.

### 3. `M06_switch_tool`
- **Loại lỗi**: `provider_error`
- **Nội dung lỗi**: Bị gián đoạn kết nối Provider (Timeout/Disconnect).

---

## ✅ 3. Danh sách 17 Cases ĐẠT (PASS in v1)

- `R01_user_tweets_routing`
- `R02_search_tweets_routing`
- `R03_web_news_routing` *(Đã sửa thành công từ v0)*
- `R04_read_url_routing`
- `R05_limit_arg`
- `R06_timeframe_arg`
- `R07_search_type_arg`
- `R08_out_of_scope` *(Đã sửa thành công từ v0)*
- `R09_no_tool_capability`
- `R10_missing_handle` *(Đã sửa thành công từ v0)*
- `R11_missing_url` *(Đã sửa thành công từ v0)*
- `R14_out_of_scope_coding`
- `M01_clarify_then_fill` *(Đã sửa thành công từ v0)*
- `M02_carryover_timeframe` *(Đã sửa thành công từ v0)*
- `M03_correction_handle`
- `M04_clarify_then_url`
- `M05_correction_limit`
