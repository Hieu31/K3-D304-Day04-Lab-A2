# Day 04 Lab v2 Report — Research Agent

> File báo cáo chính thức của Nhóm, tổng hợp đầy đủ Phần A (Giới thiệu) và Phần B (Bằng chứng đánh giá v0–v3).

## Team

- **Team**: NHÓM A2 (Day 04 Lab)
- **Author**: dlhdwan (Hoàng Danh)
- **Members**:
  - Đinh Lê Hoàng Danh - MSSV: 2A202601890 (Trưởng nhóm / Author)
  - Nguyễn Văn Hiếu - MSSV: 2A202601831
  - Đỗ Ngọc Anh - MSSV: 2A202601343
  - Lưu Nhân Triệu Dương - MSSV: 2A202601695
- **Provider/model**: `gemini` (`gemini-3.5-flash-lite`)

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research Agent đa năng hỗ trợ tra cứu tin tức web, tìm kiếm thảo luận trên Twitter, đọc và phân tích nội dung bài viết từ URL, dịch thuật đa ngôn ngữ, trích xuất từ khóa chính và tự động lưu trữ ghi chú tóm tắt nghiên cứu vào file Markdown.

**Link dùng thử (truy cập được trong showdown):**

> URL: Streamlit App running locally on `http://localhost:8501`

---

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| `clarify` | Hỏi lại người dùng khi thiếu thông tin hoặc cần xin xác nhận Có/Không | Không |
| `lookup` | Tìm kiếm thông tin web, tin tức báo chí theo từ khóa, chủ đề và thời gian | Không |
| `fetch` | Đọc và trích xuất nội dung văn bản trực tiếp từ một địa chỉ URL | Không |
| `social_search` | Tìm kiếm bài đăng, thảo luận trên mạng xã hội Twitter theo từ khóa | Không |
| `timeline` | Lấy các bài đăng gần đây từ một tài khoản Twitter cụ thể (`screenname`) | Không |
| `format` | Định dạng dữ liệu thành báo cáo/digest trình bày sạch đẹp | Không |
| `send` | Gửi bản tin/tin nhắn (yêu cầu xin xác nhận trước) | Không |
| `translate_text` | Dịch đoạn văn bản ngoại ngữ sang ngôn ngữ đích (ví dụ: tiếng Việt `vi`) | **Có** |
| `extract_keywords` | Trích xuất các từ khóa và thực thể chính từ đoạn văn bản dài với số lượng tùy chỉnh | **Có** |
| `save_note` | Lưu trữ ghi chú, tóm tắt nghiên cứu vào file văn bản Markdown (`.md`) | **Có** |
| `papers` | Tìm kiếm các bài báo nghiên cứu khoa học trên thư viện arXiv | Không  |
| `paper_text` | Trích xuất nội dung văn bản chi tiết của bài báo khoa học từ arXiv | Không  |
| `policy` | Tra cứu các quy định, chính sách nội bộ của hệ thống | Không  |

---

## A3. Câu hỏi mẫu để thử

1. **Tra cứu đa nguồn song song**: *"Tìm tin tức báo chí hôm nay về Gemini 1.5 và tìm luôn các thảo luận trên Twitter về Gemini 1.5."*
2. **Hỏi xin thông tin khi thiếu**: *"Cho mình xem 5 bài đăng gần nhất của Sam Altman."* ➔ *(Agent sẽ hỏi xin Twitter handle `@sama` trước khi thực thi)*.
3. **Dịch thuật & Trích xuất từ khóa**: *"Trích xuất 3 từ khóa chính và dịch đoạn văn này sang tiếng Việt: 'Transformer models utilize self-attention mechanisms.'"*
4. **Lưu ghi chú nghiên cứu**: *"Lưu lại dòng tóm tắt 'Hệ thống Agent đã tối ưu hóa latency API' vào file notes.md giúp mình."*

---

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Câu chuyện cải thiện version | Fallback run/transcript |
|---|---|---|---|
| **Scenario 1: Thiếu Twitter Handle (`R10`)** | `clarify(question="...", response_type="text")` ➔ `timeline(screenname="sama")` | ở **v0** Agent tự gọi thẳng `timeline` không có handle. Từ **v1**, Agent biết gọi `clarify` để hỏi xin handle trước. | `runs/v3_B_base_gemini_20260729T123027021294.json` |
| **Scenario 2: Tìm kiếm kết hợp đa nguồn (`G03`)** | `lookup` + `social_search` (Parallel calls) | ở **v0/v1** Agent bị lỗi Single Tool Bias (chỉ gọi 1 tool). Ở **v3**, Agent phát ra đồng thời cả 2 tool call song song. | `runs/v3_B_group_gemini_20260729T122325678855.json` |
| **Scenario 3: Dịch thuật tự động (`G01`)** | `translate_text(text="...", target_lang="vi")` | Ở **v2**, Agent gọi `translate_text` nhưng bỏ quên `target_lang`. Ở **v3**, Agent truyền đầy đủ `target_lang="vi"`. | `runs/v3_B_group_gemini_20260729T122325678855.json` |
| **Scenario 4: Xác nhận trước khi gửi (`R12`)** | `clarify(response_type="yes_no")` | Ở **v0**, Agent tự ý gửi thẳng. Từ **v2**, Agent bắt buộc xin xác nhận yes/no trước khi thực thi lệnh `send`. | `runs/v3_B_base_gemini_20260729T123027021294.json` |

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version evidence

| Version | Prompt/tool change | Hypothesis | Metric name | Before | After | Run File |
|---|---|---|---|---:|---:|---|
| **v0** | Baseline prompt & tools | Đánh giá năng lực gốc của LLM | Base Case Accuracy | - | **55.0%** (`11/20`) | `runs/v0_B_base_groq_20260729T101251117761.json` |
| **v1** | Bổ sung quy tắc `clarify` khi thiếu handle/URL & lọc từ thừa `query` | Bắt buộc hỏi lại khi thiếu tham số sẽ làm giảm lỗi `missing_info` | Base Case Accuracy | 55.0% | **89.47%** (`17/19`) | `runs/v1_B_base_groq_20260729T111124200985.json` |
| **v2** | Chuyển sang Gemini 3.5 Flash Lite + Thêm delay 5s chống 429 API | Ép ranh giới `yes_no` cho `send` & sửa lỗi rate limit | Base Case Accuracy <br> Group Case Accuracy | 89.47% <br> - | **100.0%** (`20/20`) <br> **70.0%** (`7/10`) | `runs/v2_B_base_gemini_20260729T120525756241.json` <br> `runs/v2_B_base_gemini_20260729T121005738701.json` |
| **v3** | Thắt chặt `required: [target_lang]`, quy tắc carryover `limit` & cắt `@` ở screenname | Sửa toàn bộ các lỗi còn tồn đọng ở Group Eval | Base Case Accuracy <br> Group Case Accuracy | 100.0% <br> 70.0% | **100.0%** (`20/20`) 🎯 <br> **100.0%** (`10/10`) 🎯 | `runs/v3_B_base_gemini_20260729T123027021294.json` <br> `runs/v3_B_group_gemini_20260729T122325678855.json` |

---

## B2. Failure analysis

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| `R10_missing_handle` | `missing_info` | `timeline(screenname="Sam Altman")` | Agent tự đoán người dùng mà không gọi `clarify` xin handle. | Bổ sung chỉ thị trong `system_prompt.md` yêu cầu bắt buộc gọi `clarify` khi thiếu handle. *(Đã fix ở v1)* |
| `R03_web_news_routing` | `wrong_arg_value` | `lookup(query="AI news")` | Agent nối từ thừa `"news"` vào `query`. | Cập nhật `tools.yaml` tách biệt rõ `query="AI"` và `topic="news"`. *(Đã fix ở v1)* |
| `R12_confirm_before_send` | `wrong_boundary` | `send(...)` | Agent gửi tin trực tiếp không hỏi xin phép. | Đưa ranh giới `clarify(response_type="yes_no")` lên ưu tiên cao nhất trước mọi action `send`. *(Đã fix ở v2)* |
| `G01_search_translate` | `wrong_arg_value` | `translate_text(text="...")` | Bỏ quên tham số `target_lang="vi"`. | Đưa `target_lang` vào danh sách `required: [text, target_lang]` trong `tools.yaml`. *(Đã fix ở v3)* |
| `G06_multi_clarify_handle` | `missing_info` | `timeline(screenname="tim_cook")` | Quên giữ lại tham số `limit=5` ở lượt 1 khi bổ sung handle ở lượt 3. | Cập nhật quy tắc Carryover Context trong `system_prompt.md` để duy trì `limit`. *(Đã fix ở v3)* |
| `G08_multi_correction` | `wrong_arg_value` | `timeline(screenname="@elonmusk")` | Truyền nguyên ký tự `@` phía trước screenname. | Thêm quy tắc tự động cắt bỏ ký tự `@` ở đầu handle trong `system_prompt.md`. *(Đã fix ở v3)* |

---

## B3. Team eval cases

Bảng 10 cases tự thiết kế trong file `data/eval_group.json` (đạt kết quả **10/10 PASS (100%)** ở phiên bản v3):

| Case ID | What It Tests | Expected Tool/Behavior | Result (v3) |
|---|---|---|---|
| `G01_single_search_translate_chain` | Dịch thuật câu tiếng Anh sang tiếng Việt | `translate_text(text="...", target_lang="vi")` | ✅ PASS |
| `G02_single_keywords_from_text` | Trích xuất đúng 3 từ khóa chính | `extract_keywords(text="...", max_keywords=3)` | ✅ PASS |
| `G03_single_parallel_news_and_social` | Tìm kiếm đa nguồn (Web & Twitter) | `lookup` + `social_search` (Parallel calls) | ✅ PASS |
| `G04_single_save_note_file` | Lưu tóm tắt ghi chú vào file markdown | `save_note(note_content="...", filename="notes.md")` | ✅ PASS |
| `G05_single_confirm_send_telegram` | Xin xác nhận trước khi đăng bài Telegram | `clarify(response_type="yes_no")` | ✅ PASS |
| `G06_multi_clarify_handle_then_timeline` | Multi-turn: Hỏi handle và giữ nguyên limit=5 | `timeline(screenname="tim_cook", limit=5)` | ✅ PASS |
| `G07_multi_carryover_topic_search` | Multi-turn: Cập nhật query sạch và timeframe=week | `lookup(query="chip AI Nvidia", topic="news", timeframe="week")` | ✅ PASS |
| `G08_multi_correction_limit_and_screenname` | Multi-turn: Đính chính handle và limit=3 | `timeline(screenname="elonmusk", limit=3)` | ✅ PASS |
| `G09_multi_clarify_url_then_fetch` | Multi-turn: Hỏi xin URL và gọi fetch | `fetch(url="https://arxiv.org/abs/2301.00001")` | ✅ PASS |
| `G10_multi_switch_from_social_to_save_note` | Multi-turn: Chuyển đổi ý định từ social sang lưu file | `save_note(note_content="...", filename="attention_summary.md")` | ✅ PASS |

---

## B4. Live chat evidence

Bảng bằng chứng thực thi thoại đa lượt (Multi-turn Evidence) trích xuất từ log chạy v3:

| Scenario/Turn | Version | Tool Calls + Args | Transcript/Run | Outcome |
|---|---|---|---|---|
| `M01_clarify_then_fill` (Turn 1) | v3 | `clarify(question="...", response_type="text")` | `runs/v3_B_base_gemini_20260729T123027021294.json` | Hỏi thành công handle thiếu ở lượt 1 |
| `M01_clarify_then_fill` (Turn 2) | v3 | `timeline(screenname="sama")` | `runs/v3_B_base_gemini_20260729T123027021294.json` | Điền handle ở lượt 2 và lấy đúng 5 tweet |
| `G06_multi_clarify_handle` (Turn 3) | v3 | `timeline(screenname="tim_cook", limit=5)` | `runs/v3_B_group_gemini_20260729T122325678855.json` | Nhận handle lượt 3 và kế thừa thành công `limit=5` |
| `G10_multi_switch` (Turn 3) | v3 | `save_note(note_content="...", filename="attention_summary.md")` | `runs/v3_B_group_gemini_20260729T122325678855.json` | Chuyển đổi ý định mượt mà sang lưu file ghi chú |
