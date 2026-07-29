from __future__ import annotations

import csv
import html
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import now_iso, run_model_tool_loop, safe_slug, trim_history, write_transcript
from env_loader import load_lab_env
from providers import make_provider
from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
DATA_DIR = ROOT / "data"
RUNS_DIR = ROOT / "runs"
TRANSCRIPTS_DIR = ROOT / "transcripts"

load_lab_env(ROOT)

PROVIDERS = ["groq", "openrouter", "openai", "anthropic", "gemini"]
PROVIDER_ENV = {
    "groq": "GROQ_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
}
MODEL_HINTS = {
    "groq": "openai/gpt-oss-120b",
    "openrouter": "openai/gpt-4o-mini",
    "openai": "gpt-4o-mini",
    "anthropic": "claude-haiku-4-5-20251001",
    "gemini": "gemini-3.5-flash",
}
SUGGESTED_PROMPTS = [
    "Tìm tin tức mới nhất về AI hôm nay và tóm tắt thành 5 gạch đầu dòng.",
    "Tóm tắt URL này: https://example.com",
    "Tìm các bài đăng mới nhất về OpenAI trên mạng xã hội.",
    "Đăng lên Telegram: Bản tin AI hôm nay đã sẵn sàng.",
]


st.set_page_config(
    page_title="Research Agent",
    page_icon="✦",
    layout="centered",
    initial_sidebar_state="collapsed",
)


def inject_css() -> None:
    st.markdown(
        """
<style>
    :root {
        --bg: #050711;
        --glass: rgba(255, 255, 255, 0.075);
        --glass-strong: rgba(255, 255, 255, 0.12);
        --line: rgba(255, 255, 255, 0.16);
        --text: #F8FAFC;
        --muted: #AAB4C8;
        --accent: #A78BFA;
        --accent-2: #22D3EE;
        --good: #34D399;
        --warn: #FBBF24;
        --bad: #FB7185;
    }

    header[data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    [data-testid="stDeployButton"],
    #MainMenu,
    footer {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }

    html, body, [data-testid="stAppViewContainer"], .main {
        color: var(--text);
        background:
            radial-gradient(circle at 18% 8%, rgba(167, 139, 250, 0.24), transparent 30%),
            radial-gradient(circle at 88% 16%, rgba(34, 211, 238, 0.16), transparent 26%),
            radial-gradient(circle at 50% 95%, rgba(59, 130, 246, 0.14), transparent 34%),
            linear-gradient(145deg, #050711, #0B1020 55%, #020617);
    }

    .block-container {
        max-width: 1180px;
        padding-top: 1.25rem;
        padding-bottom: 6rem;
    }

    .app-title {
        margin: 0.6rem 0 0.2rem;
        font-size: 2.35rem;
        line-height: 1.05;
        font-weight: 820;
        letter-spacing: -0.055em;
        text-align: left;
    }

    .app-subtitle {
        margin: 0 0 1rem;
        max-width: 680px;
        color: var(--muted);
        text-align: left;
        font-size: 1rem;
    }

    .meta-row {
        display: flex;
        flex-wrap: wrap;
        justify-content: flex-start;
        gap: 0.45rem;
        margin: 0.85rem 0 1.1rem;
    }

    .pill {
        display: inline-flex;
        align-items: center;
        border: 1px solid var(--line);
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.07);
        color: var(--muted);
        padding: 0.32rem 0.68rem;
        font-size: 0.78rem;
        font-weight: 680;
        backdrop-filter: blur(14px);
    }
    .pill.good { color: var(--good); }
    .pill.warn { color: var(--warn); }
    .pill.bad { color: var(--bad); }

    .glass-note {
        border: 1px solid var(--line);
        border-radius: 24px;
        background: linear-gradient(135deg, rgba(255,255,255,0.10), rgba(255,255,255,0.045));
        box-shadow: 0 20px 70px rgba(0,0,0,0.28);
        backdrop-filter: blur(18px);
        padding: 0.85rem 1rem;
        margin: 0.8rem 0;
    }

    .side-panel-title {
        color: var(--text);
        font-size: 0.94rem;
        font-weight: 760;
        letter-spacing: -0.015em;
        margin: 0.15rem 0 0.75rem;
    }

    .side-panel-caption {
        color: var(--muted);
        font-size: 0.8rem;
        line-height: 1.45;
        margin-bottom: 0.8rem;
    }

    div[data-testid="stChatMessage"] {
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 24px;
        background: rgba(255,255,255,0.055);
        backdrop-filter: blur(16px);
        padding: 0.72rem 0.82rem;
        margin-bottom: 0.78rem;
        width: fit-content;
        max-width: min(78%, 720px);
        box-shadow: 0 18px 54px rgba(0,0,0,0.22);
    }

    div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        margin-left: auto;
        margin-right: 0;
        border-bottom-right-radius: 8px;
        background: linear-gradient(135deg, rgba(167,139,250,0.16), rgba(34,211,238,0.10));
    }

    div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        margin-left: 0;
        margin-right: auto;
        border-bottom-left-radius: 8px;
    }

    div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {
        line-height: 1.55;
    }

    .chat-row {
        display: flex;
        width: 100%;
        margin: 0.85rem 0;
    }

    .chat-row.user {
        justify-content: flex-end;
    }

    .chat-row.assistant {
        justify-content: flex-start;
    }

    .chat-bubble {
        max-width: min(78%, 720px);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 24px;
        padding: 0.85rem 1rem;
        line-height: 1.58;
        color: var(--text);
        box-shadow: 0 18px 54px rgba(0,0,0,0.22);
        word-break: break-word;
    }

    .chat-bubble.user {
        border-bottom-right-radius: 8px;
        background: linear-gradient(135deg, rgba(167,139,250,0.34), rgba(34,211,238,0.18));
        margin-left: auto;
    }

    .chat-bubble.assistant {
        border-bottom-left-radius: 8px;
        background: rgba(255,255,255,0.065);
        backdrop-filter: blur(16px);
        margin-right: auto;
    }

    .chat-role {
        display: block;
        margin-bottom: 0.35rem;
        color: var(--muted);
        font-size: 0.68rem;
        font-weight: 760;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }

    .trace-details {
        margin-top: 0.7rem;
        border-top: 1px solid rgba(255,255,255,0.11);
        padding-top: 0.55rem;
        color: var(--muted);
        font-size: 0.84rem;
    }

    .trace-details summary {
        cursor: pointer;
        color: #CFFAFE;
        font-weight: 720;
    }

    .trace-details pre {
        max-height: 260px;
        overflow: auto;
        white-space: pre-wrap;
        word-break: break-word;
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 16px;
        background: rgba(2, 6, 23, 0.46);
        color: #DDE7F3;
        padding: 0.72rem;
    }

    .loading-lines {
        margin-top: 0.35rem;
        color: var(--muted);
        font-size: 0.86rem;
    }

    .loading-line {
        display: flex;
        align-items: center;
        gap: 0.48rem;
        margin-top: 0.26rem;
    }

    .loading-dot {
        width: 0.48rem;
        height: 0.48rem;
        border-radius: 999px;
        background: var(--accent-2);
        box-shadow: 0 0 18px rgba(34,211,238,0.46);
        animation: pulse-dot 1.15s infinite ease-in-out;
    }

    .loading-line:nth-child(2) .loading-dot { animation-delay: 0.16s; background: var(--accent); }
    .loading-line:nth-child(3) .loading-dot { animation-delay: 0.32s; }

    @keyframes pulse-dot {
        0%, 100% { opacity: 0.35; transform: scale(0.82); }
        50% { opacity: 1; transform: scale(1.12); }
    }

    .stTextInput input,
    div[data-baseweb="select"] > div {
        border-radius: 16px !important;
        border-color: rgba(255,255,255,0.15) !important;
        background: rgba(255,255,255,0.07) !important;
        color: var(--text) !important;
    }

    div[data-testid="stChatInput"] {
        border-radius: 999px !important;
        background: transparent !important;
    }

    div[data-testid="stChatInput"] > div {
        border: 1px solid rgba(255,255,255,0.20) !important;
        border-radius: 999px !important;
        background:
            linear-gradient(135deg, rgba(255,255,255,0.14), rgba(255,255,255,0.06)) !important;
        box-shadow:
            0 18px 60px rgba(0,0,0,0.32),
            inset 0 1px 0 rgba(255,255,255,0.18);
        backdrop-filter: blur(18px);
        overflow: hidden;
    }

    div[data-testid="stChatInput"] textarea,
    div[data-testid="stChatInput"] [contenteditable="true"] {
        background: transparent !important;
        color: var(--text) !important;
        border-radius: 999px !important;
        box-shadow: none !important;
        border: 0 !important;
    }

    div[data-testid="stChatInput"] textarea::placeholder {
        color: rgba(248,250,252,0.52) !important;
    }

    .stButton button {
        border-radius: 999px;
        border: 1px solid rgba(255,255,255,0.16);
        background: rgba(255,255,255,0.07);
        color: var(--text);
        min-height: 2.25rem;
    }

    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, var(--accent), var(--accent-2)) !important;
        color: white !important;
    }

    div[data-testid="stExpander"] {
        border-radius: 20px !important;
        border-color: rgba(255,255,255,0.13) !important;
        background: rgba(255,255,255,0.055) !important;
        backdrop-filter: blur(16px);
    }

    div[data-testid="stMetric"] {
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 18px;
        background: rgba(255,255,255,0.055);
        padding: 0.55rem 0.7rem;
    }

    .small-muted {
        color: var(--muted);
        font-size: 0.84rem;
    }
</style>
""",
        unsafe_allow_html=True,
    )


def compact_json(value: Any, *, max_chars: int = 8000) -> str:
    text = json.dumps(value, ensure_ascii=False, indent=2, default=str)
    if len(text) > max_chars:
        return text[:max_chars] + "\n...<truncated>"
    return text


def short_hash(value: str | None) -> str:
    return (value or "")[:12]


def load_artifacts(version: str) -> dict[str, Any]:
    system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"
    system_prompt = system_prompt_path.read_text(encoding="utf-8")
    declarations = load_tool_declarations(tools_path)
    return {
        "system_prompt_path": system_prompt_path,
        "tools_path": tools_path,
        "system_prompt": system_prompt,
        "declarations": declarations,
        "openai_tools": to_openai_tools(declarations),
        "artifact_version": build_artifact_version(version, system_prompt_path, tools_path),
    }


def make_transcript(provider_name: str, selected_model: str | None, version: str, history_window: int, max_tool_rounds: int) -> None:
    artifacts = load_artifacts(version)
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([safe_slug(version), safe_slug(provider_name), timestamp])
    st.session_state.transcript_path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
    st.session_state.transcript_signature = {
        "provider": provider_name,
        "model": selected_model,
        "version": version,
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
    }
    st.session_state.transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifacts["artifact_version"]),
        "provider": provider_name,
        "model": selected_model,
        "system_prompt": str(artifacts["system_prompt_path"]),
        "tools": str(artifacts["tools_path"]),
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
        "source": "streamlit_app",
    }


def ensure_transcript(provider_name: str, selected_model: str | None, version: str, history_window: int, max_tool_rounds: int) -> None:
    signature = {
        "provider": provider_name,
        "model": selected_model,
        "version": version,
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
    }
    if (
        not st.session_state.get("transcript")
        or not st.session_state.get("transcript_path")
        or st.session_state.get("transcript_signature") != signature
    ):
        make_transcript(provider_name, selected_model, version, history_window, max_tool_rounds)


def init_state() -> None:
    st.session_state.setdefault("messages", [
        {
            "role": "assistant",
            "content": "Chào bạn. Mình có thể tìm tin mới, đọc URL, tìm social posts, tra policy/paper, dịch và tổng hợp thành digest.",
        }
    ])
    st.session_state.setdefault("history", [])
    st.session_state.setdefault("turns", [])
    st.session_state.setdefault("last_run", None)
    st.session_state.setdefault("pending_request", None)
    st.session_state.setdefault("transcript", None)
    st.session_state.setdefault("transcript_path", None)
    st.session_state.setdefault("transcript_signature", None)
    st.session_state.setdefault("selected_prompt", None)


def reset_chat() -> None:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Đã bắt đầu session mới. Bạn gửi research request tiếp theo nhé.",
        }
    ]
    st.session_state.history = []
    st.session_state.turns = []
    st.session_state.last_run = None
    st.session_state.pending_request = None
    st.session_state.transcript = None
    st.session_state.transcript_path = None
    st.session_state.transcript_signature = None


def tool_error_count(events: list[dict[str, Any]]) -> int:
    total = 0
    for event in events:
        result = event.get("result")
        if isinstance(result, dict) and result.get("error"):
            total += 1
    return total


def tool_names(events: list[dict[str, Any]]) -> str:
    if not events:
        return "none"
    names = [event.get("tool", "unknown") for event in events]
    head = ", ".join(names[:4])
    return head if len(names) <= 4 else f"{head}, +{len(names) - 4}"


def run_agent_turn(
    user_text: str,
    *,
    provider_name: str,
    model_override: str,
    version: str,
    history_window: int,
    max_tool_rounds: int,
) -> dict[str, Any]:
    started = time.time()
    artifacts = load_artifacts(version)
    provider = make_provider(provider_name)
    model = model_override.strip() or None
    selected_model = model or getattr(provider, "default_model", None)

    ensure_transcript(provider_name, selected_model, version, history_window, max_tool_rounds)

    messages = [
        {"role": "system", "content": artifacts["system_prompt"]},
        *trim_history(st.session_state.history, history_window),
        {"role": "user", "content": user_text},
    ]

    turn_record: dict[str, Any] = {
        "turn_index": len(st.session_state.turns) + 1,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    result = run_model_tool_loop(
        provider=provider,
        messages=messages,
        tools=artifacts["openai_tools"],
        model=model,
        max_tool_rounds=max_tool_rounds,
    )
    assistant_text = result.get("assistant_text", "")
    latency_ms = (time.time() - started) * 1000
    turn_record.update(result)
    turn_record["ended_at"] = now_iso()

    st.session_state.history.append({"role": "user", "content": user_text})
    st.session_state.history.append({"role": "assistant", "content": assistant_text})
    st.session_state.turns.append(turn_record)
    st.session_state.transcript["turns"].append(turn_record)
    write_transcript(Path(st.session_state.transcript_path), st.session_state.transcript)

    run_info = {
        "status": result.get("status", "unknown"),
        "provider": provider_name,
        "model": selected_model,
        "version": version,
        **artifact_version_dict(artifacts["artifact_version"]),
        "latency_ms": latency_ms,
        "rounds": result.get("rounds", []),
        "tool_events": result.get("tool_events", []),
        "tool_count": len(result.get("tool_events", [])),
        "tool_error_count": tool_error_count(result.get("tool_events", [])),
        "transcript_path": str(st.session_state.transcript_path),
    }
    return {"role": "assistant", "content": assistant_text, "run": run_info}


def render_run_trace(run: dict[str, Any]) -> None:
    status = run.get("status", "unknown")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Status", str(status).upper())
    c2.metric("Tool calls", run.get("tool_count", 0))
    c3.metric("Tool errors", run.get("tool_error_count", 0))
    c4.metric("Latency", f"{run.get('latency_ms', 0):.0f} ms")

    st.caption(
        f"Provider: {run.get('provider')} · Model: {run.get('model')} · "
        f"Artifact: {run.get('artifact_version')}"
    )

    if run.get("transcript_path"):
        st.caption(f"Transcript: {run['transcript_path']}")

    rounds = run.get("rounds", [])
    if not rounds:
        st.caption("No tool trace for this turn.")
        return

    for round_record in rounds:
        label = f"Round {round_record.get('round', '?')}"
        calls = round_record.get("tool_calls", [])
        if calls:
            label += " · " + ", ".join(call.get("name", "unknown") for call in calls)
        with st.expander(label, expanded=False):
            if round_record.get("assistant_text"):
                st.markdown(round_record["assistant_text"])
            if calls:
                st.caption("Tool calls")
                st.json(calls)
            if round_record.get("tool_results"):
                st.caption("Tool results")
                st.json(round_record["tool_results"])


def message_text_html(text: str) -> str:
    safe = html.escape(text or "")
    return safe.replace("\n", "<br>")


def run_trace_html(run: dict[str, Any]) -> str:
    status = html.escape(str(run.get("status", "unknown")).upper())
    provider = html.escape(str(run.get("provider", "")))
    model = html.escape(str(run.get("model", "")))
    artifact = html.escape(str(run.get("artifact_version", "")))
    transcript = html.escape(str(run.get("transcript_path", "")))
    tools = html.escape(compact_json(run.get("tool_events", []), max_chars=5000))
    rounds = html.escape(compact_json(run.get("rounds", []), max_chars=5000))
    errors = run.get("tool_error_count", 0)
    tool_count = run.get("tool_count", 0)
    latency = run.get("latency_ms", 0)
    return f"""
<details class="trace-details">
  <summary>Research trace · {status} · {tool_count} tools · {errors} errors · {latency:.0f}ms</summary>
  <p>Provider: {provider}<br>Model: {model}<br>Artifact: {artifact}<br>Transcript: {transcript}</p>
  <p>Tool events</p>
  <pre>{tools}</pre>
  <p>Rounds</p>
  <pre>{rounds}</pre>
</details>
"""


def message_bubble_html(message: dict[str, Any]) -> str:
    if message.get("status") == "pending":
        return loading_bubble_html(
            message.get("provider", st.session_state.get("provider_name", "provider")),
            message.get("phase", "queued"),
        )
    role = message.get("role", "assistant")
    role_label = "You" if role == "user" else "Research Agent"
    trace = run_trace_html(message["run"]) if message.get("run") else ""
    return f"""
<div class="chat-row {role}">
  <div class="chat-bubble {role}">
    <span class="chat-role">{role_label}</span>
    {message_text_html(message.get("content", ""))}
    {trace}
  </div>
</div>
"""


def loading_bubble_html(provider_name: str, phase: str = "queued") -> str:
    provider = html.escape(provider_name)
    phase_messages = {
        "queued": "Queued your request and preparing the agent context.",
        "preparing": "Loading prompt, tool declarations, provider, and conversation history.",
        "running_model_tool_loop": "Calling the model and executing any selected tools.",
        "saving": "Saving transcript and preparing the final response.",
    }
    phase_text = html.escape(phase_messages.get(phase, phase_messages["queued"]))
    return f"""
<div class="chat-row assistant">
  <div class="chat-bubble assistant">
    <span class="chat-role">Research Agent</span>
    Researching with <strong>{provider}</strong>…
    <div class="loading-lines">
      <div class="loading-line"><span class="loading-dot"></span><span>{phase_text}</span></div>
    </div>
  </div>
</div>
"""


def render_messages() -> None:
    for message in st.session_state.messages:
        st.markdown(message_bubble_html(message), unsafe_allow_html=True)


def provider_key_status(provider_name: str) -> tuple[bool, str]:
    env_name = PROVIDER_ENV.get(provider_name, "")
    return bool(env_name and os.getenv(env_name)), env_name


def render_header(provider_name: str, version: str, artifact: Any) -> None:
    key_ready, env_name = provider_key_status(provider_name)
    key_class = "good" if key_ready else "warn"
    st.markdown(
        f"""
<h1 class="app-title">Research Agent</h1>
<div class="app-subtitle">
  A live tool-using research assistant. Ask naturally; tool calls and evidence stay available when needed.
</div>
<div class="meta-row">
  <span class="pill">provider · {provider_name}</span>
  <span class="pill">version · {version}</span>
  <span class="pill">artifact · {artifact.artifact_version}</span>
  <span class="pill {key_class}">{env_name or 'provider key'} · {'configured' if key_ready else 'missing'}</span>
</div>
""",
        unsafe_allow_html=True,
    )


def render_settings() -> tuple[str, str, str, int, int]:
    provider_name = st.session_state.get("provider_name", "groq")
    version = st.session_state.get("version", "v3")
    model_override = st.session_state.get("model_override", "")
    max_tool_rounds = st.session_state.get("max_tool_rounds", 4)
    history_window = st.session_state.get("history_window", 5)

    st.markdown('<div class="side-panel-title">Settings</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="side-panel-caption">Runtime controls for the live agent. Keep defaults for demo unless you need a specific provider/model.</div>',
        unsafe_allow_html=True,
    )
    provider_name = st.selectbox("Provider", PROVIDERS, index=PROVIDERS.index(provider_name), key="provider_name")
    model_override = st.text_input(
        "Model override",
        value=model_override,
        placeholder=MODEL_HINTS.get(provider_name, ""),
        key="model_override",
    )
    version = st.text_input("Version", value=version, key="version")
    max_tool_rounds = st.slider("Tool rounds", 1, 8, max_tool_rounds, key="max_tool_rounds")
    history_window = st.slider("History", 0, 10, history_window, key="history_window")

    ready, env_name = provider_key_status(provider_name)
    status_class = "good" if ready else "warn"
    st.markdown(
        f'<span class="pill {status_class}">{env_name}: {"configured" if ready else "missing"}</span>',
        unsafe_allow_html=True,
    )
    st.caption(f"Default model: {MODEL_HINTS.get(provider_name)}")

    if st.button("Clear chat", use_container_width=True):
        reset_chat()
        st.rerun()

    return provider_name, model_override, version.strip() or "v3", history_window, max_tool_rounds


def render_compact_lab_evidence() -> None:
    payloads = load_run_payloads()
    base_versions = sorted({payload.get("version") for _, payload in payloads if payload.get("suite") == "base"})
    total, single, multi = eval_group_counts()
    transcripts = list(TRANSCRIPTS_DIR.glob("*.transcript.json")) if TRANSCRIPTS_DIR.exists() else []
    issues = tool_sync_issues()

    st.markdown('<div class="side-panel-title">Lab evidence</div>', unsafe_allow_html=True)
    st.caption(f"Runs: {len(payloads)} · Base versions: {', '.join(base_versions) or 'none'}")
    if "v3" not in base_versions:
        st.warning("Missing v3 base run.")
    st.caption(f"Group eval: {total} cases ({single} single / {multi} multi)")
    st.caption(f"Transcripts: {len(transcripts)}")
    if issues:
        st.warning("Tool sync issue")
        for issue in issues[:3]:
            st.caption(issue)
    else:
        st.caption("Tool sync: OK")


def set_pending_phase(request_id: str, phase: str) -> None:
    for message in st.session_state.messages:
        if message.get("request_id") == request_id and message.get("status") == "pending":
            message["phase"] = phase
            break


def replace_pending_message(request_id: str, assistant_message: dict[str, Any]) -> None:
    for index, message in enumerate(st.session_state.messages):
        if message.get("request_id") == request_id:
            st.session_state.messages[index] = assistant_message
            return
    st.session_state.messages.append(assistant_message)


def process_pending_request() -> bool:
    pending = st.session_state.get("pending_request")
    if not pending:
        return False

    request_id = pending["request_id"]
    phase = pending.get("phase", "queued")

    if phase == "queued":
        pending["phase"] = "running_model_tool_loop"
        set_pending_phase(request_id, "running_model_tool_loop")
        st.rerun()

    try:
        assistant_message = run_agent_turn(
            pending["user_text"],
            provider_name=pending["provider_name"],
            model_override=pending["model_override"],
            version=pending["version"],
            history_window=pending["history_window"],
            max_tool_rounds=pending["max_tool_rounds"],
        )
    except Exception as exc:
        assistant_message = {
            "role": "assistant",
            "content": "Mình gặp lỗi khi xử lý request. Kiểm tra provider key, quota hoặc cấu hình tool.",
            "run": {
                "status": "error",
                "provider": pending["provider_name"],
                "model": pending["model_override"] or MODEL_HINTS.get(pending["provider_name"]),
                "version": pending["version"],
                "error": f"{type(exc).__name__}: {exc}",
                "rounds": [],
                "tool_events": [],
                "tool_count": 0,
                "tool_error_count": 1,
                "latency_ms": 0,
            },
        }

    replace_pending_message(request_id, assistant_message)
    st.session_state.last_run = assistant_message.get("run")
    st.session_state.pending_request = None
    st.rerun()
    return True


def load_run_payloads() -> list[tuple[Path, dict[str, Any]]]:
    if not RUNS_DIR.exists():
        return []
    payloads: list[tuple[Path, dict[str, Any]]] = []
    for path in sorted(RUNS_DIR.glob("*.json")):
        try:
            payloads.append((path, json.loads(path.read_text(encoding="utf-8"))))
        except Exception:
            continue
    return payloads


def render_run_evidence() -> None:
    payloads = load_run_payloads()
    if not payloads:
        st.info("No run JSON found in runs/.")
        return

    rows: list[dict[str, Any]] = []
    for path, payload in payloads:
        summary = payload.get("summary", {})
        rows.append({
            "file": path.name,
            "version": payload.get("version"),
            "suite": payload.get("suite"),
            "provider": payload.get("provider"),
            "model": payload.get("model"),
            "measured": f"{summary.get('measured_cases')}/{summary.get('total_cases')}",
            "provider_errors": summary.get("provider_error_cases"),
            "passed": summary.get("passed_cases"),
            "case_accuracy": summary.get("case_accuracy"),
            "routing": summary.get("tool_routing_accuracy"),
            "args": summary.get("argument_accuracy"),
            "multiturn": summary.get("multiturn_accuracy"),
        })
    st.dataframe(rows, use_container_width=True, hide_index=True)

    base_versions = {payload.get("version") for _, payload in payloads if payload.get("suite") == "base"}
    if "v3" not in base_versions:
        st.warning("Missing base eval run for v3.")

    all_case_ids = sorted({
        result.get("id")
        for _, payload in payloads
        for result in payload.get("results", [])
        if result.get("id")
    })
    if all_case_ids:
        selected_case = st.selectbox("Compare one eval case across versions", all_case_ids)
        comparison: list[dict[str, Any]] = []
        for path, payload in payloads:
            for result in payload.get("results", []):
                if result.get("id") == selected_case:
                    result_payload = result.get("result", {})
                    comparison.append({
                        "file": path.name,
                        "version": payload.get("version"),
                        "passed": result_payload.get("passed"),
                        "observed": result_payload.get("observed_mismatch"),
                        "calls": result_payload.get("actual_tool_calls"),
                        "failures": result_payload.get("failures"),
                    })
        st.json(comparison)


def eval_group_counts() -> tuple[int, int, int]:
    path = DATA_DIR / "eval_group.json"
    if not path.exists():
        return 0, 0, 0
    try:
        cases = json.loads(path.read_text(encoding="utf-8")).get("cases", [])
    except Exception:
        return 0, 0, 0
    return len(cases), sum(1 for case in cases if "query" in case), sum(1 for case in cases if "turns" in case)


def version_log_versions() -> set[str]:
    path = ARTIFACTS_DIR / "version_log.csv"
    if not path.exists():
        return set()
    rows = csv.DictReader(path.read_text(encoding="utf-8").splitlines())
    return {row.get("version", "") for row in rows if row.get("version")}


def tool_sync_issues() -> list[str]:
    try:
        declared = {item["name"] for item in load_tool_declarations(ARTIFACTS_DIR / "tools.yaml")}
    except Exception as exc:
        return [f"Cannot read tools.yaml: {exc}"]
    implemented = set(TOOL_FUNCTIONS)
    issues = [f"{name} declared but not implemented" for name in sorted(declared - implemented)]
    issues += [f"{name} implemented but not declared" for name in sorted(implemented - declared)]
    return issues


def render_readiness() -> None:
    payloads = load_run_payloads()
    base_versions = {payload.get("version") for _, payload in payloads if payload.get("suite") == "base"}
    group_runs = [path.name for path, payload in payloads if payload.get("suite") == "group"]
    total, single, multi = eval_group_counts()
    log_versions = version_log_versions()
    transcripts = list(TRANSCRIPTS_DIR.glob("*.transcript.json")) if TRANSCRIPTS_DIR.exists() else []
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    issues = tool_sync_issues()

    checks = [
        ("UI entrypoint", (ROOT / "app.py").exists(), "app.py"),
        ("Streamlit dependency", "streamlit" in requirements.lower(), "requirements.txt"),
        ("Base runs v0-v3", {"v0", "v1", "v2", "v3"}.issubset(base_versions), ", ".join(sorted(base_versions)) or "none"),
        ("Group eval data", total == 10 and single == 5 and multi == 5, f"{total} cases · {single} single · {multi} multi"),
        ("Group eval run", bool(group_runs), ", ".join(group_runs) or "missing"),
        ("Version log v0-v3", {"v0", "v1", "v2", "v3"}.issubset(log_versions), ", ".join(sorted(log_versions)) or "none"),
        ("Live transcript", bool(transcripts), f"{len(transcripts)} transcript(s)"),
        ("Tool sync", not issues, "; ".join(issues) if issues else "OK"),
    ]
    for label, ok, detail in checks:
        css = "good" if ok else "warn"
        state = "PASS" if ok else "TODO"
        st.markdown(f'<span class="pill {css}">{state}</span> **{label}** — {detail}', unsafe_allow_html=True)


def render_artifacts(version: str) -> None:
    artifacts = load_artifacts(version)
    artifact = artifacts["artifact_version"]
    st.caption(f"Artifact version: {artifact.artifact_version}")
    st.caption(f"Prompt hash: {short_hash(artifact.prompt_hash)} · Tools hash: {short_hash(artifact.tools_hash)}")

    tool_rows = [
        {
            "tool": item.get("name"),
            "required": ", ".join(item.get("parameters", {}).get("required", [])),
            "description": (item.get("description") or "").strip()[:180],
        }
        for item in artifacts["declarations"]
    ]
    st.dataframe(tool_rows, use_container_width=True, hide_index=True)

    with st.expander("System prompt"):
        st.code(artifacts["system_prompt"], language="markdown")
    with st.expander("version_log.csv"):
        path = ARTIFACTS_DIR / "version_log.csv"
        st.code(path.read_text(encoding="utf-8") if path.exists() else "missing", language="csv")


def main() -> None:
    inject_css()
    init_state()

    chat_col, settings_col = st.columns([0.72, 0.28], gap="large")

    with settings_col:
        with st.container(border=True):
            provider_name, model_override, version, history_window, max_tool_rounds = render_settings()

        latest = st.session_state.get("last_run")
        if latest:
            with st.container(border=True):
                st.markdown('<div class="side-panel-title">Latest turn</div>', unsafe_allow_html=True)
                st.metric("Status", str(latest.get("status", "unknown")).upper())
                st.metric("Tools", latest.get("tool_count", 0))
                st.caption(f"Errors: {latest.get('tool_error_count', 0)}")
                if latest.get("transcript_path"):
                    st.caption(f"Transcript: {latest.get('transcript_path')}")

        with st.expander("Lab evidence", expanded=False):
            render_compact_lab_evidence()

    with chat_col:
        artifact = load_artifacts(version)["artifact_version"]
        render_header(provider_name, version, artifact)

        st.markdown(
            """
<div class="glass-note small-muted">
  Ask a research question below. The assistant uses this project’s current agent/model/tool loop; open Research trace only when you need execution evidence.
</div>
""",
            unsafe_allow_html=True,
        )

        render_messages()

        prompt_from_button = None
        if len(st.session_state.messages) <= 1:
            st.caption("Try one")
            cols = st.columns(2)
            for index, sample in enumerate(SUGGESTED_PROMPTS):
                with cols[index % 2]:
                    if st.button(sample, use_container_width=True):
                        prompt_from_button = sample

        pending_active = st.session_state.get("pending_request") is not None
        prompt = st.chat_input("Ask the research agent…", disabled=pending_active)
        user_text = prompt or prompt_from_button
        if user_text:
            request_id = f"req-{time.time_ns()}"
            user_message = {"role": "user", "content": user_text}
            st.session_state.messages.append(user_message)
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Researching…",
                "status": "pending",
                "phase": "queued",
                "provider": provider_name,
                "request_id": request_id,
            })
            st.session_state.pending_request = {
                "request_id": request_id,
                "phase": "queued",
                "user_text": user_text,
                "provider_name": provider_name,
                "model_override": model_override,
                "version": version,
                "history_window": history_window,
                "max_tool_rounds": max_tool_rounds,
            }
            st.rerun()

        process_pending_request()



if __name__ == "__main__":
    main()
