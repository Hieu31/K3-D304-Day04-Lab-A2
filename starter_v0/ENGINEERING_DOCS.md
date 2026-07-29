# Engineering Docs — Research Agent Tool Eval

Ngày rà soát: 2026-07-29  
Phạm vi: README.md, TEAM_WORKFLOW.md, `starter_v0/`, code agent/eval/tool/provider, artifacts và run evidence hiện có.

## 1. Mục tiêu project

Project này là một research agent có tool-use thật. Mục tiêu không chỉ là chatbot trả lời tốt, mà là một vòng lặp engineering có evidence:

1. Agent nhận request từ user.
2. Model quyết định có gọi tool hay không.
3. Code local execute tool thật với arguments model cung cấp.
4. Kết quả tool được đưa lại vào model context.
5. Hệ thống lưu run/transcript JSON.
6. Team đọc log để sửa prompt/tool declaration qua nhiều version.
7. Eval đo routing, argument correctness, multi-turn behavior và boundary handling.
8. UI hiển thị được chat + tool trace + version evidence để demo/chấm bài.

Deliverable core gồm:

- Agent chạy được với provider thật.
- Ít nhất 5 tool trong `artifacts/tools.yaml`.
- Ít nhất 1 tool mới do team thêm, có implementation + declaration + documentation.
- Base eval v0, v1, v2, v3.
- `artifacts/version_log.csv` ghi hypothesis/metric theo version.
- `data/eval_group.json` có đúng 10 team-authored cases: 5 single-turn + 5 multi-turn.
- `artifacts/REPORT.md` hoàn chỉnh bằng log thật.
- UI chạy được và hiển thị đủ evidence.

## 2. Hiện trạng project

### Đã có

- Core runtime:
  - `agent.py`: chạy một lượt provider completion và execute tool calls.
  - `chat.py`: interactive multi-turn loop, hỗ trợ nhiều tool round, lưu transcript.
  - `run_eval.py`: chạy eval suite, chấm tool routing/args, ghi run JSON.
  - `versioning.py`: tính `artifact_version`, `prompt_hash`, `tools_hash`.
  - `env_loader.py`: load `.env` hoặc `DAY04_ENV_FILE`.
- Provider layer:
  - `providers/base.py`: dataclass/Protocol chuẩn `ToolCall`, `ModelResponse`, `Provider`.
  - `providers/__init__.py`: factory `make_provider`.
  - Provider hiện có: OpenAI, OpenRouter, Anthropic, Gemini, Groq.
- Tool system:
  - `tools/__init__.py`: registry `TOOL_FUNCTIONS`, loader YAML, converter sang OpenAI tool schema.
  - `artifacts/tools.yaml`: đang declare 13 tool.
  - Mỗi tool nằm trong `tools/<tool_name>/tool.py` và có `TOOL.md`.
- Artifacts:
  - `artifacts/system_prompt.md`
  - `artifacts/tools.yaml`
  - `artifacts/version_log.csv`
  - `artifacts/REPORT.md`
- Eval data:
  - `data/eval_base.json`
  - `data/eval_research_extension.json`
  - `data/eval_group.json`
- Evidence hiện có:
  - `runs/v0_B_base_groq_20260729T101251117761.json`
  - `runs/v1_B_base_groq_20260729T111124200985.json`
  - `runs/v2_B_base_groq_20260729T110519584948.json`

### Chưa có hoặc chưa hoàn chỉnh

- Chưa có `starter_v0/app.py`.
- `requirements.txt` chưa có `streamlit>=1.30.0`.
- `data/eval_group.json` còn trống.
- `artifacts/version_log.csv` mới có header.
- `artifacts/REPORT.md` vẫn là template.
- Chưa có run v3.
- Chưa có group eval run.
- Chưa thấy `transcripts/*.transcript.json`.
- Chưa có UI URL/local demo evidence trong report.

## 3. Cấu trúc thư mục

```text
starter_v0/
  agent.py                  # single-pass agent wrapper cho eval
  chat.py                   # multi-turn chat + tool loop + transcript
  run_eval.py               # eval runner + grader + run JSON writer
  versioning.py             # artifact hash/version
  env_loader.py             # .env loader
  smoke_test.py             # smoke test tool cơ bản
  requirements.txt          # Python dependencies
  artifacts/
    system_prompt.md        # instruction chính cho model
    tools.yaml              # public tool interface model nhìn thấy
    version_log.csv         # version/hypothesis/metric log
    REPORT.md               # report nộp bài
  data/
    eval_base.json          # fixed base eval
    eval_group.json         # 10 team-authored eval cases
    eval_research_extension.json
  providers/
    base.py                 # provider protocol
    *_provider.py           # vendor adapters
  tools/
    __init__.py             # registry + declaration loader
    <tool_name>/
      TOOL.md               # tool docs
      tool.py               # tool implementation
  runs/
    *.json                  # eval evidence
  transcripts/
    *.transcript.json       # live chat evidence, cần tạo
```

## 4. Runtime architecture

### 4.1 Eval runtime

Eval dùng `run_eval.py` và `ResearchAgent` trong `agent.py`.

```text
run_eval.py
  -> load_lab_env(ROOT)
  -> read system_prompt.md
  -> build_artifact_version(...)
  -> make_provider(provider)
  -> load eval cases
  -> load tools.yaml
  -> validate expected tools against tools.yaml + TOOL_FUNCTIONS
  -> to_openai_tools(...)
  -> for each case:
       ResearchAgent.run(...)
         -> provider.complete(...)
         -> execute local TOOL_FUNCTIONS[tool_name](**args)
       evaluate_phase_b(...)
  -> summarize(...)
  -> write runs/<run_id>.json
```

Eval scoring hiện tập trung vào:

- Có gọi đúng tool không.
- Arguments có match expected subset không.
- Có gọi tool thừa không.
- Với `expect.no_tool`, model không được gọi tool.
- Provider error được tách riêng khỏi measured cases.

Lưu ý quan trọng: trong eval, nếu case expect tool, `tool_choice="required"` được truyền vào provider. Vì vậy base/group eval đang ép model phải gọi tool cho các case có expected tool call.

### 4.2 Chat/runtime UI

Chat live dùng `chat.py`, cụ thể là `run_model_tool_loop`.

```text
chat.py / app.py
  -> system prompt + trimmed history + latest user message
  -> provider.complete(...)
  -> nếu không có tool call:
       return answered
  -> nếu có tool call:
       execute_tool_call(...)
       nếu result.awaiting_user:
          return waiting_for_user
       append TOOL_RESULTS_JSON vào messages
       tiếp tục round sau
  -> nếu quá max_tool_rounds:
       return max_tool_rounds
```

Đây là contract nên dùng cho UI. Không nên viết lại agent loop riêng trong `app.py`.

Shape result từ `run_model_tool_loop`:

```python
{
    "status": "answered" | "waiting_for_user" | "max_tool_rounds",
    "assistant_text": "...",
    "rounds": [
        {
            "round": 1,
            "assistant_text": "...",
            "tool_calls": [{"name": "...", "args": {...}}],
            "tool_results": [{"tool": "...", "args": {...}, "result": {...}}],
        }
    ],
    "tool_events": [{"tool": "...", "args": {...}, "result": {...}}],
}
```

## 5. Provider và environment

Provider được tạo bằng:

```python
from providers import make_provider
provider = make_provider("groq")
```

Provider được hỗ trợ trong CLI:

- Eval: `openai`, `openrouter`, `anthropic`, `gemini`, `groq`.
- Chat: `openrouter`, `openai`, `anthropic`, `gemini`.

Nên đồng bộ chat CLI và UI để có cùng provider options. Nếu UI hỗ trợ `groq`, cần kiểm tra `chat.py` cũng nên nhận `groq` hoặc UI gọi trực tiếp `make_provider("groq")`.

Environment loading:

- Default: đọc `starter_v0/.env`.
- Override: nếu có `DAY04_ENV_FILE`, đọc file đó.
- Không commit `.env`.
- UI chỉ được hiển thị trạng thái key có/không, không render giá trị secret.

Các env var đáng chú ý:

| Capability | Env var |
|---|---|
| OpenAI provider | tùy implementation trong `providers/openai_provider.py` |
| OpenRouter provider | tùy implementation trong `providers/openrouter_provider.py` |
| Anthropic provider | tùy implementation trong `providers/anthropic_provider.py` |
| Gemini provider | tùy implementation trong `providers/gemini_provider.py` |
| Groq provider | tùy implementation trong `providers/groq_provider.py` |
| Web search `lookup` | `TAVILY_API_KEY` |
| URL scrape `fetch` | `FIRECRAWL_API_KEY` |
| Social tools | `RAPIDAPI_KEY`, optional `RAPIDAPI_TWITTER_HOST` |
| Telegram send | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` |

## 6. Tool system

Tool có 3 mặt phải sync:

1. Declaration cho model: `artifacts/tools.yaml`.
2. Implementation local: `tools/<tool_name>/tool.py`.
3. Registry runtime: `tools/__init__.py` trong `TOOL_FUNCTIONS`.

Nếu rename hoặc thêm tool, cần kiểm tra thêm:

- `artifacts/system_prompt.md`
- `data/eval_base.json`
- `data/eval_research_extension.json`
- `data/eval_group.json`
- `artifacts/REPORT.md`
- Demo script/UI copy

Tool inventory hiện tại:

| Tool | Implementation | Loại | Ghi chú engineering |
|---|---|---|---|
| `clarify` | `tools/clarify/tool.py` | Core | Trả `awaiting_user=True`; chat/UI phải pause và hỏi user. |
| `timeline` | `tools/timeline/tool.py` | Core | Gọi RapidAPI Twitter timeline. |
| `social_search` | `tools/social_search/tool.py` | Core | Gọi RapidAPI Twitter search. |
| `lookup` | `tools/lookup/tool.py` | Core | Gọi Tavily; dùng cho web/news search. |
| `fetch` | `tools/fetch/tool.py` | Core | Gọi Firecrawl; chỉ dùng khi user có URL. |
| `format` | `tools/format/tool.py` | Core | Pure local markdown formatter. |
| `send` | `tools/send/tool.py` | Optional/action | Phải confirmation trước; có thể gửi Telegram thật nếu env có key. |
| `policy` | `tools/policy/tool.py` | Optional/local-ish | Search policy markdown nội bộ. |
| `papers` | `tools/papers/tool.py` | Optional/research | Search arXiv. |
| `paper_text` | `tools/paper_text/tool.py` | Optional/research | Extract arXiv PDF text. |
| `extract_keywords` | `tools/extract_keywords/tool.py` | Team-added | Pure local keyword extraction. |
| `translate_text` | `tools/translate_text/tool.py` | Team-added | Gọi MyMemory public translation API. |
| `save_note` | `tools/save_note/tool.py` | Team-added/action-ish | Append note vào file local theo `Path.cwd()`. Cần guard filename/path. |

Hiện code đã có 3 tool tự thêm (`extract_keywords`, `translate_text`, `save_note`), nhưng evidence bắt buộc vẫn cần được ghi bằng eval/report:

- `TOOL.md` tương ứng.
- Declaration trong `tools.yaml`.
- Registry trong `tools/__init__.py`.
- Smoke/eval/demo evidence.
- Report phân loại tool mới bắt buộc/bonus nếu team muốn tính bonus.

## 7. Prompt và tool declaration strategy

`artifacts/system_prompt.md` đang định nghĩa routing policy chính:

- Khi nào dùng `lookup`, `fetch`, `social_search`, `timeline`, `clarify`, `send`.
- Preserve query.
- Không lookup nếu user cung cấp URL.
- Không gửi/publish trực tiếp nếu chưa confirmation.
- Không gọi tool nếu out-of-scope.
- Multi-turn state: lượt sau là update task hiện tại.

`artifacts/tools.yaml` là interface model nhìn thấy:

- Tool name.
- Description.
- Parameters schema.
- Required fields.
- Enum/default conventions.

Nguyên tắc sửa:

- Nếu model chọn sai tool vì thiếu policy/routing rule, sửa `system_prompt.md`.
- Nếu model truyền sai args vì schema/mô tả chưa rõ, sửa `tools.yaml`.
- Mỗi version chỉ nên sửa một hypothesis chính để metric sau đó có ý nghĩa.
- Không sửa fixed eval case để làm metric đẹp, trừ rename tool đồng bộ theo README.

## 8. Eval architecture và dữ liệu

### 8.1 Case schema

`run_eval.py` đọc `data/*.json` theo shape:

```json
{
  "dataset_id": "...",
  "dataset_role": "...",
  "description": "...",
  "cases": [
    {
      "id": "case_id",
      "phase": "B",
      "failure_type": "wrong_tool",
      "query": "single-turn user request",
      "expect": {
        "tool_calls": [
          {"name": "lookup", "args": {"query": "AI"}}
        ]
      },
      "metadata": {"what_it_tests": "..."}
    }
  ]
}
```

Multi-turn dùng `turns` thay vì `query`:

```json
{
  "id": "team_multi_1",
  "phase": "B",
  "failure_type": "missing_info",
  "turns": [
    {"role": "user", "content": "Tóm tắt URL này giúp tôi"},
    {"role": "assistant", "content": "Bạn gửi URL cần tóm tắt nhé."},
    {"role": "user", "content": "https://example.com"}
  ],
  "expect": {
    "tool_calls": [
      {"name": "fetch", "args": {"url": "https://example.com"}}
    ]
  },
  "metadata": {"what_it_tests": "Carry context after clarification"}
}
```

Allowed `failure_type`:

- `wrong_tool`
- `wrong_arg_value`
- `wrong_boundary`
- `unnecessary_tool`
- `out_of_scope`
- `missing_info`

### 8.2 Metrics hiện có

Các run base hiện có:

| Version | Provider/model | Measured | Provider errors | Passed | Case accuracy | Routing | Args | Multiturn |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| v0 | groq / openai/gpt-oss-120b | 20/20 | 0 | 11 | 0.55 | 0.65 | 0.55 | 0.6667 |
| v1 | groq / openai/gpt-oss-120b | 19/20 | 1 | 17 | 0.8947 | 0.9474 | 0.8947 | 1.0 |
| v2 | groq / openai/gpt-oss-120b | 20/20 | 0 | 18 | 0.9 | 0.95 | 0.9 | 1.0 |

Các lỗi còn lại ở v2:

- `R12_confirm_before_send`: model gọi `clarify` nhưng `response_type` là `text`, expected `yes_no`.
- `R13_parallel_web_and_tweets`: thiếu tool call `social_search`, chỉ gọi `lookup`.

Điều này gợi ý v3 nên tập trung vào:

- Ràng buộc rõ `send` confirmation phải dùng `clarify(response_type="yes_no")`.
- Ràng buộc multi-source request phải gọi song song `lookup` + `social_search` nếu user yêu cầu web/news và social posts.

## 9. Versioning và artifact evidence

`build_artifact_version(version, system_prompt_path, tools_path)` tạo:

```text
<version>+p<prompt_hash_12>+t<tools_hash_12>
```

Run JSON lưu:

- `run_id`
- `version`
- `artifact_version`
- `prompt_hash`
- `tools_hash`
- `provider`
- `model`
- `system_prompt`
- `tools`
- `eval_cases`
- `summary`
- `results[*].expect`
- `results[*].result`
- `results[*].tool_results`

`version_log.csv` cần ghi ít nhất v0–v3 với header:

```csv
version,author,changed_artifact,artifact_version,prompt_hash,tools_hash,reason,hypothesis,metric_name,metric_before,metric_after,run_file
```

Quy tắc evidence:

- Run có `provider_error_cases > 0` không nên là evidence chính.
- Tool result có `error` phải được review thủ công.
- Metric routing PASS không chứng minh external tool execution đã thành công.

## 10. UI engineering

UI định hướng mới là một product-like live research agent: thân thiện với user như các chatbot AI hiện đại, nhưng vẫn giữ trace/evidence đủ cho lab. Màn hình mặc định không giống dashboard kỹ thuật. Chat là trung tâm; settings và lab evidence nằm trong panel phải gọn, tool trace nằm trực tiếp trong assistant bubble dưới dạng collapsible details.

Visual direction:

- Glassmorphism + minimalistic/futuristic aesthetic.
- Nền dark gradient mềm, các card bán trong suốt, blur, viền sáng mỏng.
- Chat surface centered, ít control, dùng native `st.chat_message` và `st.chat_input`.
- User/assistant chat bubble tách hai phía rõ ràng.
- Chat input bo tròn hiện đại với glass effect.
- Assistant response đọc được ngay; tool trace nằm trong “Research trace” details ngay trong bubble.
- Status/metadata xuất hiện dạng pill nhỏ, không chiếm trọng tâm.
- Không copy custom chat shell/control panel từ project Day03.

### 10.1 UI runtime contract

UI nên dùng:

```python
from chat import run_model_tool_loop, trim_history, write_transcript, now_iso, safe_slug
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version
```

Không nên duplicate logic:

- Tool loop.
- Clarification pause.
- Transcript shape.
- Artifact version/hash.

### 10.2 UI state model

Nên lưu trong `st.session_state`:

- `history`: context gửi vào model.
- `turns`: dữ liệu render chat/tool trace.
- `transcript`: JSON object tương thích CLI.
- `transcript_path`: file đang ghi trong `transcripts/`.
- `provider_name`, `model`, `version`.
- `history_window`, `max_tool_rounds`.

### 10.3 Layout hiện tại

Primary flow:

- Header ngắn: “Live Research Agent”.
- Subtitle nói rõ agent có thể search, fetch URL, đọc policy/paper, format digest.
- Compact settings panel bên phải:
  - provider,
  - model optional,
  - version,
  - max tool rounds,
  - history window,
  - clear session.
- Compact lab evidence bên phải:
  - số run hiện có,
  - base versions,
  - group eval count,
  - transcript count,
  - tool sync status.
- Native chat ở giữa màn hình:
  - user/assistant messages qua `st.chat_message`,
  - mỗi assistant bubble có status summary và collapsible `Research trace`.
- Prompt composer đơn giản ở dưới:
  - `st.chat_input`,
  - vài sample prompts.

Detailed run/artifact/readiness helpers remain available in code, but the default UI only surfaces compact lab evidence to keep the product chat clean.

### 10.4 UI acceptance criteria

- `streamlit run app.py` chạy từ `starter_v0/`.
- Mở được `http://localhost:8501`.
- Chat dùng `run_model_tool_loop`.
- Mỗi turn hiển thị final answer và full tool trace.
- `clarify` hiển thị câu hỏi và giữ context cho lượt sau.
- Tool error không crash UI.
- Transcript JSON được lưu sau mỗi turn.
- Runs tab so sánh được v0–v3.
- UI cảnh báo nếu thiếu v3, group eval, version log, report.
- Theme glassmorphism nhất quán: background gradient, translucent panels, blur, minimal controls.
- Default view đủ thân thiện cho user không cần hiểu eval/tool internals.

## 11. Reporting

`artifacts/REPORT.md` có 2 phần:

- Phần A: giới thiệu agent để demo nhanh.
- Phần B: evidence chi tiết bằng run/transcript thật.

Nguồn dữ liệu report:

- Tool list: `artifacts/tools.yaml` + `tools/__init__.py`.
- Version evidence: `artifacts/version_log.csv` + `runs/*.json`.
- Failure analysis: `results[*].result.failures`.
- Live chat evidence: `transcripts/*.transcript.json`.
- UI URL: local hoặc Cloudflare Tunnel.

Report không nên ghi theo cảm giác. Mỗi claim quan trọng cần trỏ được về run/transcript/artifact.

## 12. Security và operational guardrails

- Không commit `.env`, API key, `.venv`, cache/build output.
- Không render secret values trong UI.
- Không screenshot log có secret.
- `send` là action tool; luôn cần confirmation yes/no trước khi gửi.
- `save_note` ghi file local; cần validate filename nếu expose cho demo.
- External tools có thể fail vì thiếu key/quota/network; UI/report phải phân biệt routing success và execution success.
- Public tunnel chỉ dùng tạm; không mở UI chứa dữ liệu nhạy cảm.

## 13. Development workflow khuyến nghị

Thứ tự triển khai còn lại:

1. Chốt v3 hypothesis từ lỗi v2:
   - `send` confirmation phải là `yes_no`.
   - request nhiều nguồn phải gọi đủ `lookup` + `social_search`.
2. Sửa đúng một hypothesis trong `system_prompt.md` hoặc `tools.yaml`.
3. Chạy:

   ```bash
   python run_eval.py --provider groq --version v3 --suite base --eval-cases data/eval_base.json
   ```

4. Viết `data/eval_group.json` đủ 10 cases.
5. Chạy:

   ```bash
   python run_eval.py --provider groq --version v3 --suite group --eval-cases data/eval_group.json
   ```

6. Điền `artifacts/version_log.csv`.
7. Implement `app.py` Streamlit.
8. Thêm `streamlit>=1.30.0` vào `requirements.txt`.
9. Chạy UI local:

   ```bash
   streamlit run app.py
   ```

10. Tạo transcript live bằng UI hoặc:

   ```bash
   python chat.py --provider openrouter --version v3
   ```

11. Điền `artifacts/REPORT.md`.
12. Nếu cần public test URL:

   ```bash
   cloudflared tunnel --url http://localhost:8501
   ```

## 14. Definition of Done tổng thể

Project đủ điều kiện hoàn chỉnh khi:

- Provider preflight pass.
- Base eval có v0, v1, v2, v3.
- v3 base run có `provider_error_cases == 0`.
- `data/eval_group.json` có đúng 10 cases, gồm 5 single-turn và 5 multi-turn.
- Group eval v3 đã chạy và có run JSON.
- `version_log.csv` có v0–v3, kèm artifact hash, hypothesis, metric before/after, run file.
- Tool mới có:
  - folder `tools/<tool>/`,
  - `TOOL.md`,
  - `tool.py`,
  - registry trong `tools/__init__.py`,
  - declaration trong `artifacts/tools.yaml`,
  - smoke/eval/report evidence.
- UI chạy được, hiển thị chat + tool trace + run/version evidence.
- Transcript live đã được lưu.
- `REPORT.md` hoàn chỉnh bằng evidence thật.
- Không có `.env`, API keys, `.venv`, cache/build output trong submission.
