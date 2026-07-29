# Build Plan — Minimal Live Research Agent UI

Target project: `C:\Users\ADMIN\Desktop\Code Space\K3-D304-Day04-Lab-A2\starter_v0`

## 1. Decision

UI direction is now a minimal, product-like live research agent, visually closer to modern AI chatbot surfaces than to an engineering dashboard.

Constraints:

- Do not copy the Day03 UI shell.
- Do not use Day03 custom HTML chat component.
- Do not create a heavy two-column engineering dashboard. A compact right settings panel is allowed.
- Do not rewrite backend agent/model/tool logic.
- Chat submit must call the current Day04 `run_model_tool_loop` from `chat.py`.
- Evidence required by README/TEAM_WORKFLOW remains available through progressive disclosure.

## 2. UX structure

Default view:

```text
Left: centered title + metadata pills
Left: native chat messages with user/assistant bubbles split to opposite sides
Native chat input
Sample prompts, only before first user request
Right: compact settings panel

Expandable engineering evidence:
  - Compact Lab evidence in the right panel
```

User-facing priorities:

- natural chat first;
- answer text visible immediately;
- trace hidden unless opened;
- compact artifact/provider metadata;
- compact right settings panel; no heavy control dashboard.

Evaluator-facing priorities:

- every assistant turn can show tool calls, args, results/errors;
- transcript path is visible;
- `runs/*.json` status is summarized compactly;
- artifact version/hash is visible;
- readiness gaps are visible.

## 3. Visual system

Theme: minimal dark glassmorphism.

Key properties:

- wide layout with readable chat column and compact right settings panel;
- deep navy/black radial gradient background;
- translucent cards;
- thin light borders;
- soft blur;
- small metadata pills;
- native Streamlit chat components styled lightly.

## 4. Current implementation files

| File | Purpose |
|---|---|
| `app.py` | Minimal Streamlit product chat UI. |
| `.streamlit/config.toml` | Dark Streamlit theme, headless server, port 8501. |
| `requirements.txt` | Includes `streamlit>=1.30.0`. |
| `.env.example` | Includes provider key names including `GROQ_API_KEY`. |
| `ENGINEERING_DOCS.md` | Overall engineering docs reflecting current UI direction. |

## 5. Runtime contract

`app.py` must keep using current project code:

```python
from chat import now_iso, run_model_tool_loop, safe_slug, trim_history, write_transcript
from env_loader import load_lab_env
from providers import make_provider
from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version
```

Live submit flow:

```text
user submits via st.chat_input
  -> append user message
  -> load system_prompt.md + tools.yaml
  -> make provider
  -> call run_model_tool_loop
  -> append assistant message
  -> store run_info in message
  -> append history for next turn
  -> write transcript JSON
  -> render answer + collapsed Research trace
```

## 6. README/TEAM_WORKFLOW coverage

Requirement mapping:

| Requirement | UI coverage |
|---|---|
| request and final response | Native chat messages. |
| tool trace: name, args, status, result/error | `Research trace` expander on assistant messages. |
| transcript/version/artifact | metadata pills + trace details + transcript path. |
| compare versions | Compact lab evidence shows available base versions; detailed helpers remain in code if needed. |
| demo readiness | Right panel lab evidence summarizes missing run/eval/transcript/tool sync. |
| no duplicate agent loop | submit path calls `run_model_tool_loop`. |

## 7. Remaining project tasks after UI

The UI is only one deliverable. Remaining engineering work:

1. Fix v3 prompt/tool declaration for known v2 failures:
   - `R12_confirm_before_send`: force `clarify(response_type="yes_no")`.
   - `R13_parallel_web_and_tweets`: force `lookup` + `social_search`.
2. Run v3 base eval.
3. Fill `data/eval_group.json` with exactly 10 cases.
4. Run v3 group eval.
5. Fill `artifacts/version_log.csv`.
6. Generate at least one live transcript through UI or `chat.py`.
7. Fill `artifacts/REPORT.md` with real evidence.

## 8. Verification

When Python is available:

```powershell
cd "C:\Users\ADMIN\Desktop\Code Space\K3-D304-Day04-Lab-A2\starter_v0"
python -m py_compile app.py
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Current environment note: `python`, `py`, and `python3` are not available in PATH, so local compile/run verification cannot be completed until Python is installed or activated.
