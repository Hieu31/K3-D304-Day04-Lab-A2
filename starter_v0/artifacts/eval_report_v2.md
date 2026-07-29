# Báo Cáo Phân Tích & Đánh Giá Phiên Bản Version 2 (v2)

> **File báo cáo tổng hợp kết quả đánh giá cho cả 2 bộ Eval (`base` và `group`) dựa trên log thực tế trong thư mục `runs/`**:
> - **Log Base Eval v2**: [runs/v2_B_base_gemini_20260729T120525756241.json](file:///d:/K3-D304-Day04-Lab-A2/starter_v0/runs/v2_B_base_gemini_20260729T120525756241.json)
> - **Log Group Eval v2**: [runs/v2_B_base_gemini_20260729T121005738701.json](file:///d:/K3-D304-Day04-Lab-A2/starter_v0/runs/v2_B_base_gemini_20260729T121005738701.json)
> - **Model Provider**: `gemini` (`gemini-3.5-flash-lite`)

---

## 📊 1. Bảng Tổng quan Metrics Phiên bản `v2`

| Chỉ số Metric | Base Eval (20 Cases) | Group Eval (10 Cases) | Tổng hợp Toàn bộ v2 |
|---|---|---|---|
| **Run ID** | `v2_B_base_gemini_20260729T120525756241` | `v2_B_base_gemini_20260729T121005738701` | - |
| **Prompt Hash** | `ed5bef0f7bee...` | `ed5bef0f7bee...` | Đồng bộ System Prompt |
| **Tools Hash** | `a2235b98b7db...` | `a2235b98b7db...` | Đồng bộ Tools mới |
| **Total Cases** | 20 | 10 | 30 Cases |
| **Measured Cases** | 20 | 10 | 30 Cases |
| **Provider Error Cases** | 0 | 0 | 0 (Đã khắc phục hoàn toàn) |
| **Passed Cases** | **20** | **7** | **27 Cases PASS** |
| **Case Accuracy** | **100.0%** (`20 / 20`) 🎯 | **70.0%** (`7 / 10`) | **90.0%** (`27 / 30`) |
| **Tool Routing Accuracy** | **100.0%** (`20 / 20`) | **90.0%** (`9 / 10`) | **96.67%** (`29 / 30`) |
| **Argument Accuracy** | **100.0%** (`20 / 20`) | **70.0%** (`7 / 10`) | **90.0%** (`27 / 30`) |
| **Multiturn Accuracy** | **100.0%** (`6 / 6`) | **80.0%** (`4 / 5`) | **90.91%** (`10 / 11`) |

---

## 🎯 2. Đánh Giá Bộ Base Eval (20 Cases) - Đạt Điểm Tuyệt Đối 100%

Nhờ bổ sung các chỉ thị thắt chặt trong `system_prompt.md` và `tools.yaml` ở phiên bản v2:
1. **Khắc phục 100% nhóm lỗi `missing_info`**: Agent không còn quên tham số `response_type="text"` khi gọi `clarify` (`R10`, `R11`, `M01`).
2. **Khắc phục 100% nhóm lỗi `wrong_boundary`**: Agent đã dùng đúng `clarify(response_type="yes_no")` trước khi thực thi action nhạy cảm `send` (`R12`).
3. **Khắc phục 100% nhóm lỗi gọi tool song song**: Agent phát ra đồng thời cả `lookup` và `social_search` khi gặp câu hỏi đa nguồn (`R13`).
4. **Hạ tầng ổn định**: Nhờ thêm delay giữa các lượt gọi, không còn trường hợp nào bị dính lỗi API Rate Limit `429`.

---

## ❌ 3. Chi tiết các Case Thất Bại ở Bộ Group Eval (3 Failures in Group Eval)

Bộ `data/eval_group.json` được thiết kế để "làm khó" Agent với các tool mới và các tình huống nâng cao. Kết quả đạt **7/10 PASS (70%)**, 3 case bị FAIL có nguyên nhân như sau:

### 1. `G01_single_search_translate_chain`
- **Loại lỗi**: `wrong_tool` (Thực chất là `wrong_arg_value`)
- **Expected**: `translate_text(text="Deep learning...", target_lang="vi")`
- **Actual**: `translate_text(text="Deep learning...")`
- **Log Error**: `failures: ["target_lang: expected 'vi', got None"]`
- **Phân tích nguyên nhân**: Agent đã routing chính xác sang tool `translate_text`, nhưng bị thiếu tham số `target_lang="vi"`. Tool `translate_text` mặc định vẫn dịch ra tiếng Việt tốt, nhưng đối chiếu schema eval bị thiếu key `target_lang`.

---

### 2. `G06_multi_clarify_handle_then_timeline` (Multi-turn)
- **Loại lỗi**: `missing_info` (Thực chất là `wrong_arg_value`)
- **Input**: Turn 1 user yêu cầu *"5 bài đăng gần nhất của Tim Cook"*, Turn 2 assistant hỏi handle, Turn 3 user đưa handle `tim_cook`.
- **Expected**: `timeline(screenname="tim_cook", limit=5)`
- **Actual**: `timeline(screenname="tim_cook")`
- **Log Error**: `failures: ["limit: expected 5, got None"]`
- **Phân tích nguyên nhân**: Khi kế thừa sang lượt 3, Agent điền đúng `screenname="tim_cook"` nhưng bị quên giữ lại (carryover) tham số `limit=5` đã xuất hiện ở lượt 1.

---

### 3. `G09_multi_clarify_url_then_fetch` (Multi-turn)
- **Loại lỗi**: `missing_info`
- **Input**: User đưa link `https://arxiv.org/abs/2301.00001` và bảo đọc bài nghiên cứu.
- **Expected**: `fetch(url="https://arxiv.org/abs/2301.00001")`
- **Actual**: `paper_text(arxiv_url="https://arxiv.org/abs/2301.00001")`
- **Log Error**: `failures: ["missing tool call fetch", "extra tool call paper_text"]`
- **Phân tích nguyên nhân**: Model nhận diện được đường link `arxiv.org` là một bài báo khoa học nên đã "thông minh quá mức" khi gọi ngay tool chuyên dụng `paper_text` thay vì dùng tool đọc URL tổng quát `fetch`.

---

## 🛠️ 4. Định Hướng Tối Ưu Cho Phiên Bản `v3`
1. Bổ sung chỉ thị cho `translate_text`: Bắt buộc truyền `target_lang` khi người dùng yêu cầu dịch sang một ngôn ngữ cụ thể.
2. Củng cố quy tắc Carryover: Đảm bảo các tham số số lượng (như `limit`) ở lượt 1 được giữ nguyên khi user bổ sung thông tin ở các lượt sau.
3. Quy định ranh giới đọc URL: Khi yêu cầu tổng quát là "đọc link/đọc bài viết này", ưu tiên dùng `fetch` trừ khi user yêu cầu đích danh đọc bài báo arXiv.
