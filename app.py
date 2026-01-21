import os
import textwrap
from typing import Any, Dict, List, Optional

import streamlit as st
import yaml
import altair as alt

# External LLM clients
import google.generativeai as genai
from openai import OpenAI
import anthropic

# =========================
# Page & Session Setup
# =========================

st.set_page_config(
    page_title="Artistic Intelligence Workspace v2.0",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------
# Constants & Config
# -------------------------

PAINTER_STYLES = [
    "van_gogh",
    "monet",
    "picasso",
    "dali",
    "kahlo",
    "hokusai",
    "turner",
    "pollock",
    "klimt",
    "matisse",
    "chagall",
    "cezanne",
    "rembrandt",
    "vermeer",
    "warhol",
    "banksy",
    "miro",
    "basquiat",
    "rothko",
]

# Painter CSS variables (simplified version of the Next.js mapping)
PAINTER_CSS: Dict[str, Dict[str, str]] = {
    "van_gogh": {
        "bg": "radial-gradient(circle at 0% 0%, #0f172a 0%, #020617 55%, #02010a 100%)",
        "fg": "#fefce8",
        "accent": "#facc15",
        "accent_soft": "rgba(250, 204, 21, 0.15)",
        "card_bg": "rgba(15, 23, 42, 0.88)",
    },
    "monet": {
        "bg": "radial-gradient(circle at 10% 0%, #0f172a 0%, #1d3557 35%, #020617 100%)",
        "fg": "#f9fafb",
        "accent": "#38bdf8",
        "accent_soft": "rgba(56, 189, 248, 0.16)",
        "card_bg": "rgba(15, 23, 42, 0.86)",
    },
    "picasso": {
        "bg": "radial-gradient(circle at 0 0, #020617 0%, #0b1120 30%, #1e293b 80%)",
        "fg": "#e5e7eb",
        "accent": "#fb7185",
        "accent_soft": "rgba(251, 113, 133, 0.18)",
        "card_bg": "rgba(15, 23, 42, 0.9)",
    },
    "dali": {
        "bg": "radial-gradient(circle at 100% 0%, #020617 0%, #0f172a 35%, #581c87 100%)",
        "fg": "#f9fafb",
        "accent": "#a855f7",
        "accent_soft": "rgba(168, 85, 247, 0.16)",
        "card_bg": "rgba(15, 23, 42, 0.9)",
    },
    "kahlo": {
        "bg": "radial-gradient(circle at 0% 0%, #020617 0%, #14532d 40%, #020617 100%)",
        "fg": "#ecfdf3",
        "accent": "#22c55e",
        "accent_soft": "rgba(34, 197, 94, 0.18)",
        "card_bg": "rgba(5, 46, 22, 0.9)",
    },
    "hokusai": {
        "bg": "radial-gradient(circle at 10% 0%, #0b1120 0%, #075985 40%, #020617 100%)",
        "fg": "#e5f2ff",
        "accent": "#38bdf8",
        "accent_soft": "rgba(56, 189, 248, 0.2)",
        "card_bg": "rgba(15, 23, 42, 0.9)",
    },
    "turner": {
        "bg": "radial-gradient(circle at 0% 100%, #0f172a 0%, #ca8a04 40%, #020617 100%)",
        "fg": "#fef9c3",
        "accent": "#facc15",
        "accent_soft": "rgba(250, 204, 21, 0.2)",
        "card_bg": "rgba(15, 23, 42, 0.9)",
    },
    "pollock": {
        "bg": "radial-gradient(circle at 50% 0%, #020617 0%, #111827 45%, #000000 100%)",
        "fg": "#f9fafb",
        "accent": "#f97316",
        "accent_soft": "rgba(249, 115, 22, 0.22)",
        "card_bg": "rgba(15, 23, 42, 0.95)",
    },
    "klimt": {
        "bg": "radial-gradient(circle at 0% 0%, #0f172a 0%, #92400e 50%, #020617 100%)",
        "fg": "#fefce8",
        "accent": "#facc15",
        "accent_soft": "rgba(250, 204, 21, 0.22)",
        "card_bg": "rgba(24, 16, 7, 0.92)",
    },
    "matisse": {
        "bg": "radial-gradient(circle at 100% 0%, #0f172a 0%, #1d4ed8 40%, #020617 100%)",
        "fg": "#eff6ff",
        "accent": "#fb7185",
        "accent_soft": "rgba(251, 113, 133, 0.2)",
        "card_bg": "rgba(15, 23, 42, 0.9)",
    },
    "chagall": {
        "bg": "radial-gradient(circle at 0% 0%, #020617 0%, #1d4ed8 35%, #4c1d95 100%)",
        "fg": "#e5e7eb",
        "accent": "#a855f7",
        "accent_soft": "rgba(168, 85, 247, 0.2)",
        "card_bg": "rgba(15, 23, 42, 0.92)",
    },
    "cezanne": {
        "bg": "radial-gradient(circle at 0% 0%, #0f172a 0%, #0369a1 35%, #0f172a 100%)",
        "fg": "#e5f2ff",
        "accent": "#22c55e",
        "accent_soft": "rgba(34, 197, 94, 0.22)",
        "card_bg": "rgba(15, 23, 42, 0.9)",
    },
    "rembrandt": {
        "bg": "radial-gradient(circle at 0% 100%, #020617 0%, #1f2937 40%, #000000 100%)",
        "fg": "#f9fafb",
        "accent": "#f97316",
        "accent_soft": "rgba(249, 115, 22, 0.2)",
        "card_bg": "rgba(15, 23, 42, 0.95)",
    },
    "vermeer": {
        "bg": "radial-gradient(circle at 100% 0%, #020617 0%, #0ea5e9 40%, #050816 100%)",
        "fg": "#f9fafb",
        "accent": "#facc15",
        "accent_soft": "rgba(250, 204, 21, 0.2)",
        "card_bg": "rgba(15, 23, 42, 0.92)",
    },
    "warhol": {
        "bg": "radial-gradient(circle at 0% 0%, #0f172a 0%, #e11d48 35%, #4f46e5 100%)",
        "fg": "#fdf2f8",
        "accent": "#22c55e",
        "accent_soft": "rgba(34, 197, 94, 0.22)",
        "card_bg": "rgba(15, 23, 42, 0.9)",
    },
    "banksy": {
        "bg": "radial-gradient(circle at 0% 0%, #020617 0%, #111827 40%, #000000 100%)",
        "fg": "#f9fafb",
        "accent": "#ef4444",
        "accent_soft": "rgba(239, 68, 68, 0.24)",
        "card_bg": "rgba(15, 23, 42, 0.95)",
    },
    "miro": {
        "bg": "radial-gradient(circle at 100% 0%, #0f172a 0%, #1d4ed8 40%, #6d28d9 100%)",
        "fg": "#eff6ff",
        "accent": "#f97316",
        "accent_soft": "rgba(249, 115, 22, 0.22)",
        "card_bg": "rgba(15, 23, 42, 0.9)",
    },
    "basquiat": {
        "bg": "radial-gradient(circle at 0% 0%, #020617 0%, #1f2937 35%, #111827 100%)",
        "fg": "#f9fafb",
        "accent": "#facc15",
        "accent_soft": "rgba(250, 204, 21, 0.24)",
        "card_bg": "rgba(15, 23, 42, 0.95)",
    },
    "rothko": {
        "bg": "radial-gradient(circle at 50% 0%, #0f172a 0%, #7c2d12 35%, #111827 100%)",
        "fg": "#fef9c3",
        "accent": "#f97316",
        "accent_soft": "rgba(249, 115, 22, 0.24)",
        "card_bg": "rgba(24, 16, 7, 0.92)",
    },
}

# Supported models
MODEL_OPTIONS = [
    "gpt-4o-mini",
    "gpt-4.1-mini",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-3-pro-preview",
    "claude-3-5-sonnet-20241022",
    "claude-3-opus-20240229",
    "grok-4-fast-reasoning",
    "grok-3-mini",
]

# Metrics / charts (mock)
MOCK_METRICS = {
    "total_runs": 1289,
    "active_agents": 7,
    "avg_latency_ms": 1432,
}
TOKEN_TRENDS = [
    {"day": "Mon", "tokens": 12000},
    {"day": "Tue", "tokens": 18500},
    {"day": "Wed", "tokens": 16200},
    {"day": "Thu", "tokens": 23400},
    {"day": "Fri", "tokens": 29120},
    {"day": "Sat", "tokens": 15210},
    {"day": "Sun", "tokens": 19875},
]
MODEL_DISTRIBUTION = [
    {"model": "gemini-2.5-flash", "runs": 420},
    {"model": "gemini-3-pro-preview", "runs": 180},
    {"model": "gpt-4o-mini", "runs": 230},
    {"model": "gpt-4.1-mini", "runs": 145},
    {"model": "anthropic-claude", "runs": 110},
    {"model": "grok", "runs": 75},
]

# i18n labels
LABELS = {
    "en": {
        "app_title": "Artistic Intelligence Workspace v2.0",
        "view_dashboard": "Dashboard",
        "view_agent_studio": "Agent Studio",
        "view_doc_intel": "Document Intelligence",
        "theme": "Theme",
        "light": "Light",
        "dark": "Dark",
        "language": "Language",
        "painter_style": "Painter Style",
        "jackpot": "Jackpot!",
        "api_keys": "API Keys",
        "gemini_key": "Gemini API Key",
        "openai_key": "OpenAI API Key",
        "anthropic_key": "Anthropic API Key",
        "grok_key": "Grok API Key",
        "status_operational": "Operational",
        "status_missing": "Key Missing",
        "dashboard_title": "Control Center",
        "dashboard_subtitle": "Real-time overview of your artistic AI workspace.",
        "total_runs": "Total Runs",
        "active_agents": "Active Agents",
        "avg_latency": "Avg. Latency",
        "token_trends": "Token Usage Trends",
        "model_distribution": "Model Distribution",
        "agent_studio_title": "Agent Studio",
        "select_agent": "Select Agent",
        "select_model": "Select Model",
        "override_model": "Override model (optional)",
        "max_tokens": "Max tokens",
        "prompt": "Prompt",
        "run_agent": "Run Agent",
        "running": "Running...",
        "output": "Output",
        "copy": "Copy",
        "copied": "Copied",
        "use_as_input": "Use as next input",
        "view_mode": "View mode",
        "text_view": "Text",
        "markdown_view": "Markdown",
        "yaml_title": "agents.yaml",
        "skill_title": "SKILL.md",
        "upload_yaml": "Upload YAML",
        "download_yaml": "Download YAML",
        "ai_repair": "AI Repair & Normalize",
        "upload_skill": "Upload SKILL.md",
        "download_skill": "Download SKILL.md",
        "doc_title": "Document Intelligence",
        "doc_subtitle": "Summarize, distill, and reinterpret your documents with AI.",
        "paste_tab": "Paste Text",
        "upload_tab": "Upload File",
        "paste_placeholder": "Paste or type your document content here...",
        "upload_prompt": "Upload .txt, .md or .pdf document",
        "process_doc": "Process Document",
        "summary": "AI Summary",
        "font_size": "Font size",
        "download_md": "Download .md",
        "download_txt": "Download .txt",
    },
    "tc": {
        "app_title": "藝術智慧工作室 v2.0",
        "view_dashboard": "儀表板",
        "view_agent_studio": "代理工作室",
        "view_doc_intel": "文件智慧",
        "theme": "主題模式",
        "light": "亮色",
        "dark": "深色",
        "language": "語言",
        "painter_style": "畫家風格主題",
        "jackpot": "隨機驚喜！",
        "api_keys": "API 金鑰",
        "gemini_key": "Gemini API 金鑰",
        "openai_key": "OpenAI API 金鑰",
        "anthropic_key": "Anthropic API 金鑰",
        "grok_key": "Grok API 金鑰",
        "status_operational": "運作中",
        "status_missing": "尚未設定金鑰",
        "dashboard_title": "控制中心",
        "dashboard_subtitle": "即時掌握你的藝術 AI 工作室狀態。",
        "total_runs": "總執行次數",
        "active_agents": "啟用代理數",
        "avg_latency": "平均延遲",
        "token_trends": "Token 使用趨勢",
        "model_distribution": "模型使用分佈",
        "agent_studio_title": "代理工作室",
        "select_agent": "選擇代理",
        "select_model": "選擇模型",
        "override_model": "覆寫模型（選填）",
        "max_tokens": "最大 Token 數",
        "prompt": "提示詞",
        "run_agent": "執行代理",
        "running": "執行中...",
        "output": "輸出結果",
        "copy": "複製",
        "copied": "已複製",
        "use_as_input": "作為下一個輸入",
        "view_mode": "檢視模式",
        "text_view": "文字",
        "markdown_view": "Markdown",
        "yaml_title": "agents.yaml",
        "skill_title": "SKILL.md",
        "upload_yaml": "上傳 YAML",
        "download_yaml": "下載 YAML",
        "ai_repair": "AI 修復與標準化",
        "upload_skill": "上傳 SKILL.md",
        "download_skill": "下載 SKILL.md",
        "doc_title": "文件智慧",
        "doc_subtitle": "以 AI 快速萃取與重構文件內容。",
        "paste_tab": "貼上文字",
        "upload_tab": "上傳檔案",
        "paste_placeholder": "在此貼上或輸入文件內容...",
        "upload_prompt": "上傳 .txt, .md 或 .pdf 文件",
        "process_doc": "處理文件",
        "summary": "AI 摘要",
        "font_size": "字體大小",
        "download_md": "下載 .md",
        "download_txt": "下載 .txt",
    },
}

# Default agents (used if agents.yaml missing)
DEFAULT_AGENTS = [
    {
        "id": "creative-writer",
        "name": "Creative Writer",
        "description": "Long-form creative writing with painterly metaphors.",
        "model": "gemini-2.5-flash",
        "maxTokens": 8000,
        "temperature": 0.9,
        "systemPrompt": (
            "You are a world-class creative writer who uses imagery inspired "
            "by classic painters, while remaining precise and concise on request."
        ),
        "tags": ["writing", "creativity", "narrative"],
    },
    {
        "id": "yaml-architect",
        "name": "YAML Architect",
        "description": "Designs and validates complex agents.yaml configurations.",
        "model": "gemini-2.5-flash",
        "maxTokens": 6000,
        "temperature": 0.4,
        "systemPrompt": (
            "You are an expert in YAML schemas for multi-agent systems. "
            "Produce strictly valid, standardized agents.yaml structures."
        ),
        "tags": ["yaml", "config", "tooling"],
    },
    {
        "id": "doc-summarizer",
        "name": "Document Summarizer",
        "description": "Summarizes long documents into concise briefs.",
        "model": "gemini-2.5-flash",
        "maxTokens": 4000,
        "temperature": 0.3,
        "systemPrompt": (
            "You create faithful, structured summaries (overview, key points, "
            "risks, next steps)."
        ),
        "tags": ["summarization", "documents", "analysis"],
    },
    {
        "id": "code-assistant",
        "name": "Code Assistant",
        "description": "Multi-language code assistant focused on safety and clarity.",
        "model": "gemini-2.5-flash",
        "maxTokens": 12000,
        "temperature": 0.45,
        "systemPrompt": (
            "You are a senior software engineer. Prefer step-by-step reasoning, "
            "explicit tradeoffs, and production-ready examples."
        ),
        "tags": ["coding", "engineering", "debugging"],
    },
]

DEFAULT_SKILL_MD = textwrap.dedent(
    """
    # Artistic Intelligence Workspace – SKILL Library

    This file documents shared skills, patterns, and constraints that agents can reuse.

    ---

    ## Shared Principles

    - **Truthfulness first**: Prefer "I don't know" to hallucination.
    - **Deterministic structure**: When asked for structured output, use stable headings and bullet lists.
    - **Respect tokens**: When `maxTokens` is constrained, compress responsibly.

    ---

    ## Skill: Painterly Metaphors

    Used primarily by `creative-writer`.

    - When the user does **not** request technical precision:
      - Enrich descriptions with color, light, and motion metaphors.
      - Optionally reference painter styles that match the selected UI theme.
    - When the user requests "dry" or "business" style:
      - Remove metaphors and use clear, neutral language.

    Prompt scaffold:

    > Use at most one visual metaphor per paragraph.
    > Avoid mixing more than two painters' styles in a single paragraph.

    ---

    ## Skill: YAML Normalization

    Used by `yaml-architect`.

    - Normalize any partial or ad-hoc config into:

    ```yaml
    agents:
      - id: string
        name: string
        description: string
        model: string
        maxTokens: number
        temperature: number
        systemPrompt: string
        tags: [string, ...]
    ```

    - Ensure:
      - No duplicate IDs.
      - Name is human-readable.
      - Description is 1–2 sentences.
      - Tags are lower-kebab-case.

    ---

    ## Skill: Executive Summaries

    Used by `doc-summarizer`.

    - For long documents, compress into:
      1. Executive Overview (3–5 sentences)
      2. Key Insights (bulleted)
      3. Risks / Unknowns (bulleted)
      4. Recommended Next Steps (bulleted, action-oriented)

    ---

    ## Skill: Safe Coding Assistant

    Used by `code-assistant`.

    - Always:
      - Warn when suggestions interact with security, privacy, or production data.
      - Suggest tests or validation checks.
      - Prefer smallest working example.
    """
).strip()


# =========================
# Helper Functions
# =========================

def init_session_state():
    ss = st.session_state
    ss.setdefault("language", "en")
    ss.setdefault("theme", "dark")
    ss.setdefault("painter_style", "van_gogh")
    ss.setdefault("view", "dashboard")
    ss.setdefault("agents", load_agents())
    ss.setdefault("yaml_text", dump_agents_yaml(ss["agents"]))
    ss.setdefault("skill_md", load_skill_md())
    ss.setdefault("agent_prompt", "")
    ss.setdefault("agent_output", "")
    ss.setdefault("agent_model", "gemini-2.5-flash")
    ss.setdefault("agent_override_model", "")
    ss.setdefault("agent_max_tokens", 12000)
    ss.setdefault("agent_view_mode", "Text")
    # API keys (user-supplied)
    ss.setdefault("gemini_key_user", "")
    ss.setdefault("openai_key_user", "")
    ss.setdefault("anthropic_key_user", "")
    ss.setdefault("grok_key_user", "")


def load_agents() -> List[Dict[str, Any]]:
    path = "agents.yaml"
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            if isinstance(data, dict) and isinstance(data.get("agents"), list):
                return data["agents"]
            if isinstance(data, list):
                return data
        except Exception:
            pass
    return DEFAULT_AGENTS


def dump_agents_yaml(agents: List[Dict[str, Any]]) -> str:
    return yaml.safe_dump({"agents": agents}, sort_keys=False, allow_unicode=True)


def load_skill_md() -> str:
    path = "SKILL.md"
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            pass
    return DEFAULT_SKILL_MD


def apply_wow_theme():
    lang = st.session_state["language"]
    labels = LABELS[lang]
    style_key = st.session_state["painter_style"]
    style = PAINTER_CSS.get(style_key, PAINTER_CSS["van_gogh"])
    theme = st.session_state["theme"]

    # Slight variation for light/dark
    bg = style["bg"]
    fg = style["fg"] if theme == "dark" else "#0f172a"
    accent = style["accent"]
    accent_soft = style["accent_soft"]
    card_bg = style["card_bg"]

    css = f"""
    <style>
    body {{
        background: {bg} !important;
        color: {fg} !important;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    .stApp {{
        background: transparent !important;
    }}
    .wow-card {{
        background: {card_bg};
        border-radius: 1.2rem;
        border: 1px solid rgba(148, 163, 184, 0.6);
        box-shadow: 0 18px 40px rgba(0, 0, 0, 0.35);
        padding: 1rem 1.1rem;
    }}
    .wow-badge {{
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        border-radius: 999px;
        padding: 0.1rem 0.5rem;
        font-size: 0.7rem;
        font-weight: 500;
        background: {accent_soft};
        color: {fg};
    }}
    .wow-pill {{
        border-radius: 999px;
        padding: 0.2rem 0.7rem;
        background: rgba(15, 23, 42, 0.8);
        font-size: 0.75rem;
    }}
    .wow-accent-text {{
        color: {accent};
    }}
    .wow-primary-button button {{
        background: {accent} !important;
        color: black !important;
        border-radius: 0.8rem !important;
        border: none !important;
    }}
    .wow-primary-button button:hover {{
        filter: brightness(1.1);
    }}
    .wow-outline-button button {{
        border-radius: 0.8rem !important;
        border: 1px solid rgba(148, 163, 184, 0.7) !important;
        background: rgba(15, 23, 42, 0.7) !important;
    }}
    .wow-tag {{
        border-radius: 999px;
        padding: 0.05rem 0.45rem;
        font-size: 0.65rem;
        background: rgba(15, 23, 42, 0.7);
    }}
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.3rem;
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 999px !important;
        padding: 0.2rem 0.9rem !important;
    }}
    .wow-subtitle {{
        font-size: 0.8rem;
        opacity: 0.75;
    }}
    .wow-label {{
        font-size: 0.8rem;
        opacity: 0.8;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    st.markdown(f"### {labels['app_title']}")


def get_language_labels() -> Dict[str, str]:
    return LABELS[st.session_state["language"]]


def get_api_keys() -> Dict[str, str]:
    return {
        "gemini": os.getenv("GEMINI_API_KEY") or st.session_state["gemini_key_user"],
        "openai": os.getenv("OPENAI_API_KEY") or st.session_state["openai_key_user"],
        "anthropic": os.getenv("ANTHROPIC_API_KEY") or st.session_state["anthropic_key_user"],
        "grok": os.getenv("GROK_API_KEY") or st.session_state["grok_key_user"],
    }


def detect_provider(model: str) -> str:
    m = model.lower()
    if m.startswith("gemini"):
        return "gemini"
    if m.startswith("gpt") or "gpt-" in m or "o1" in m:
        return "openai"
    if "grok" in m:
        return "grok"
    if "claude" in m or "anthropic" in m:
        return "anthropic"
    # Fallback: default to gemini
    return "gemini"


def call_llm(
    prompt: str,
    system_prompt: Optional[str],
    model: str,
    max_tokens: int,
) -> str:
    provider = detect_provider(model)
    keys = get_api_keys()
    api_key = keys.get(provider)

    if not api_key:
        raise RuntimeError(f"No API key available for provider '{provider}'.")

    if provider == "gemini":
        genai.configure(api_key=api_key)
        gm = genai.GenerativeModel(model)
        full_prompt = prompt
        if system_prompt:
            full_prompt = system_prompt.strip() + "\n\nUser:\n" + prompt
        resp = gm.generate_content(
            full_prompt,
            generation_config={"max_output_tokens": max_tokens or 1024},
        )
        return resp.text or ""

    if provider == "openai":
        client = OpenAI(api_key=api_key)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens or 1024,
        )
        return resp.choices[0].message.content or ""

    if provider == "anthropic":
        client = anthropic.Anthropic(api_key=api_key)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        resp = client.messages.create(
            model=model,
            max_tokens=max_tokens or 1024,
            messages=messages,
        )
        chunks = []
        for block in resp.content:
            if getattr(block, "type", None) == "text":
                chunks.append(block.text)
        return "".join(chunks)

    if provider == "grok":
        # xAI Grok: OpenAI-compatible base URL
        client = OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens or 1024,
        )
        return resp.choices[0].message.content or ""

    raise RuntimeError(f"Unsupported provider: {provider}")


def ai_repair_yaml(yaml_text: str, model: str) -> str:
    system_prompt = textwrap.dedent(
        """
        You are a world-class YAML engineer.

        Task:
        - Take the user-provided text that should be an agents.yaml configuration.
        - If it is invalid YAML or inconsistent, repair it.
        - Normalize into a standard structure:

        agents:
          - id: string
            name: string
            description: string
            model: string
            maxTokens: number
            temperature: number
            systemPrompt: string
            tags: [string, ...]

        Rules:
        - Always return ONLY valid YAML.
        - Do not wrap in backticks or any other fencing.
        - Preserve as much semantic meaning as possible.
        """
    ).strip()

    prompt = f"Here is the possibly invalid agents.yaml text:\n\n{yaml_text}"
    return call_llm(prompt=prompt, system_prompt=system_prompt, model=model, max_tokens=4096).strip()


def summarize_document(text: str, model: str) -> str:
    system_prompt = textwrap.dedent(
        """
        You are a precise summarization engine for arbitrary documents.

        Produce a concise, structured summary with:

        - Overview (2–3 sentences)
        - Key points (bullet list)
        - Risks or caveats (if any)
        - Suggested next steps

        Write clearly and avoid hallucinations. If content is very short, still respect the structure.
        """
    ).strip()
    return call_llm(prompt=text, system_prompt=system_prompt, model=model, max_tokens=2048).strip()


def safe_parse_yaml_agents(yaml_text: str) -> Optional[List[Dict[str, Any]]]:
    try:
        data = yaml.safe_load(yaml_text) or {}
        if isinstance(data, dict) and isinstance(data.get("agents"), list):
            return data["agents"]
        if isinstance(data, list):
            return data
        # attempt to treat as dict of agents
        if isinstance(data, dict):
            return list(data.values())
    except Exception:
        return None
    return None


# =========================
# Sidebar: Controls & Keys
# =========================

def render_sidebar():
    init_session_state()
    labels = get_language_labels()

    with st.sidebar:
        # WOW header
        st.markdown("#### 🎨 Artistic Intelligence Workspace")
        st.caption("Multi-agent AI studio with painter-style theming")

        # View selection
        view = st.radio(
            "View",
            options=["dashboard", "agent_studio", "doc_intel"],
            format_func=lambda v: {
                "dashboard": labels["view_dashboard"],
                "agent_studio": labels["view_agent_studio"],
                "doc_intel": labels["view_doc_intel"],
            }[v],
            index=["dashboard", "agent_studio", "doc_intel"].index(
                st.session_state["view"]
            ),
        )
        st.session_state["view"] = view

        st.markdown("---")
        st.markdown(f"**{labels['language']}**")
        lang = st.radio(
            "Language",
            options=["en", "tc"],
            format_func=lambda v: "EN" if v == "en" else "繁體中文",
            index=["en", "tc"].index(st.session_state["language"]),
        )
        st.session_state["language"] = lang
        labels = get_language_labels()

        st.markdown(f"**{labels['theme']}**")
        theme = st.radio(
            "Theme",
            options=["dark", "light"],
            format_func=lambda v: labels["dark"] if v == "dark" else labels["light"],
            index=["dark", "light"].index(st.session_state["theme"]),
        )
        st.session_state["theme"] = theme

        st.markdown(f"**{labels['painter_style']}**")
        col1, col2 = st.columns([3, 1])
        with col1:
            style = st.selectbox(
                "Painter",
                options=PAINTER_STYLES,
                index=PAINTER_STYLES.index(st.session_state["painter_style"]),
            )
            st.session_state["painter_style"] = style
        with col2:
            if st.button(labels["jackpot"]):
                import random

                st.session_state["painter_style"] = random.choice(PAINTER_STYLES)

        st.markdown("---")
        st.markdown(f"**{labels['api_keys']}**")

        env_keys = {
            "gemini": bool(os.getenv("GEMINI_API_KEY")),
            "openai": bool(os.getenv("OPENAI_API_KEY")),
            "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
            "grok": bool(os.getenv("GROK_API_KEY")),
        }

        def api_key_row(name: str, env_present: bool, state_key: str, label_key: str):
            st.markdown(f"_{labels[label_key]}_")
            if env_present:
                st.text_input(
                    labels[label_key],
                    value="(using environment key)",
                    type="password",
                    disabled=True,
                )
                st.markdown(
                    f"<span class='wow-badge'>🔒 {labels['status_operational']}</span>",
                    unsafe_allow_html=True,
                )
            else:
                val = st.text_input(
                    labels[label_key],
                    value=st.session_state[state_key],
                    type="password",
                )
                st.session_state[state_key] = val
                if val:
                    st.markdown(
                        f"<span class='wow-badge'>🟢 {labels['status_operational']}</span>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"<span class='wow-badge'>🔴 {labels['status_missing']}</span>",
                        unsafe_allow_html=True,
                    )

        api_key_row("gemini", env_keys["gemini"], "gemini_key_user", "gemini_key")
        api_key_row("openai", env_keys["openai"], "openai_key_user", "openai_key")
        api_key_row("anthropic", env_keys["anthropic"], "anthropic_key_user", "anthropic_key")
        api_key_row("grok", env_keys["grok"], "grok_key_user", "grok_key")


# =========================
# Views
# =========================

def render_dashboard():
    labels = get_language_labels()
    apply_wow_theme()

    st.markdown(
        f"<div class='wow-card'>"
        f"<div style='display:flex;justify-content:space-between;align-items:flex-start;'>"
        f"<div><h4>{labels['dashboard_title']}</h4>"
        f"<div class='wow-subtitle'>{labels['dashboard_subtitle']}</div></div>"
        f"<div class='wow-badge'>📡 API status: "
        f"{'OK' if any(get_api_keys().values()) else 'Missing keys'}</div>"
        f"</div></div>",
        unsafe_allow_html=True,
    )

    st.write("")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"<div class='wow-card'><div class='wow-label'>{labels['total_runs']}</div>"
            f"<h3>{MOCK_METRICS['total_runs']}</h3>"
            f"<div class='wow-subtitle'>+18% this week</div></div>",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"<div class='wow-card'><div class='wow-label'>{labels['active_agents']}</div>"
            f"<h3>{MOCK_METRICS['active_agents']}</h3>"
            f"<div class='wow-subtitle'>4 high-priority</div></div>",
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"<div class='wow-card'><div class='wow-label'>{labels['avg_latency']}</div>"
            f"<h3>{MOCK_METRICS['avg_latency_ms']} ms</h3>"
            f"<div class='wow-subtitle'>-7% vs last week</div></div>",
            unsafe_allow_html=True,
        )

    st.write("")
    c1, c2 = st.columns(2)

    with c1:
        st.markdown(
            f"<div class='wow-label'>{labels['token_trends']}</div>", unsafe_allow_html=True
        )
        chart_data = alt.Chart(alt.Data(values=TOKEN_TRENDS)).mark_line(point=False).encode(
            x="day:O",
            y="tokens:Q",
        )
        st.altair_chart(chart_data.properties(height=260), use_container_width=True)

    with c2:
        st.markdown(
            f"<div class='wow-label'>{labels['model_distribution']}</div>",
            unsafe_allow_html=True,
        )
        chart_data = alt.Chart(alt.Data(values=MODEL_DISTRIBUTION)).mark_bar().encode(
            x="model:N",
            y="runs:Q",
        )
        st.altair_chart(chart_data.properties(height=260), use_container_width=True)


def render_agent_studio():
    labels = get_language_labels()
    apply_wow_theme()

    agents = st.session_state["agents"]
    if not agents:
        st.warning("No agents defined. Please configure agents.yaml.")
        return

    st.markdown(
        f"<div class='wow-card'><h4>{labels['agent_studio_title']}</h4>"
        f"<div class='wow-subtitle'>Run and manage your agents, chains, and skills.</div></div>",
        unsafe_allow_html=True,
    )
    st.write("")

    tabs = st.tabs(
        [
            labels["view_agent_studio"] + " – " + labels["run_agent"],
            labels["yaml_title"] + " / " + labels["skill_title"],
        ]
    )

    # ---------- Run Tab ----------
    with tabs[0]:
        st.write("")
        col_left, col_right = st.columns([1, 2])

        with col_left:
            # Agent selection
            agent_names = [f"{a['name']} ({a['id']})" for a in agents]
            agent_ids = [a["id"] for a in agents]
            selected_index = 0
            if "selected_agent_id" in st.session_state:
                try:
                    selected_index = agent_ids.index(st.session_state["selected_agent_id"])
                except ValueError:
                    selected_index = 0

            agent_label = st.selectbox(
                labels["select_agent"],
                options=agent_names,
                index=selected_index,
            )
            selected_agent = agents[agent_names.index(agent_label)]
            st.session_state["selected_agent_id"] = selected_agent["id"]

            # Model selection
            model = st.selectbox(
                labels["select_model"],
                options=MODEL_OPTIONS,
                index=MODEL_OPTIONS.index(st.session_state["agent_model"])
                if st.session_state["agent_model"] in MODEL_OPTIONS
                else 2,
            )
            st.session_state["agent_model"] = model

            override_model = st.text_input(
                labels["override_model"], value=st.session_state["agent_override_model"]
            )
            st.session_state["agent_override_model"] = override_model

            max_tokens = st.number_input(
                labels["max_tokens"],
                min_value=256,
                max_value=32768,
                value=int(st.session_state["agent_max_tokens"]),
                step=256,
            )
            st.session_state["agent_max_tokens"] = max_tokens

            st.markdown(f"<div class='wow-label'>{labels['view_mode']}</div>", unsafe_allow_html=True)
            view_mode = st.radio(
                labels["view_mode"],
                options=[labels["text_view"], labels["markdown_view"]],
                index=0 if st.session_state["agent_view_mode"] == "Text" else 1,
                horizontal=True,
            )
            st.session_state["agent_view_mode"] = (
                "Text" if view_mode == labels["text_view"] else "Markdown"
            )

        with col_right:
            # Prompt & output
            st.markdown(f"**{labels['prompt']}**")
            prompt = st.text_area(
                labels["prompt"],
                value=st.session_state["agent_prompt"],
                height=180,
            )
            st.session_state["agent_prompt"] = prompt

            col_buttons = st.columns([1, 1, 1])
            with col_buttons[0]:
                run_clicked = st.button(labels["run_agent"])
            with col_buttons[1]:
                copy_clicked = st.button(labels["copy"])
            with col_buttons[2]:
                use_as_input = st.button(labels["use_as_input"])

            if copy_clicked and st.session_state["agent_output"]:
                st.session_state["copy_feedback"] = labels["copied"]
                st.success(labels["copied"])
            if use_as_input and st.session_state["agent_output"]:
                st.session_state["agent_prompt"] = st.session_state["agent_output"]

            if run_clicked:
                if not prompt.strip():
                    st.warning("Prompt is empty.")
                else:
                    try:
                        with st.spinner(labels["running"]):
                            run_model = override_model or model or selected_agent["model"]
                            system_prompt = selected_agent.get("systemPrompt", "")
                            out = call_llm(
                                prompt=prompt,
                                system_prompt=system_prompt,
                                model=run_model,
                                max_tokens=max_tokens,
                            )
                            st.session_state["agent_output"] = out
                    except Exception as e:
                        st.error(f"Error: {e}")

            st.markdown(f"**{labels['output']}**")
            if st.session_state["agent_output"]:
                if st.session_state["agent_view_mode"] == "Markdown":
                    st.markdown(st.session_state["agent_output"])
                else:
                    st.text_area(
                        labels["output"],
                        value=st.session_state["agent_output"],
                        height=220,
                    )
            else:
                st.info("Agent output will appear here.")

    # ---------- Manage Tab ----------
    with tabs[1]:
        st.write("")
        c1, c2 = st.columns(2)

        # agents.yaml
        with c1:
            st.markdown(f"**{labels['yaml_title']}**")
            yaml_text = st.text_area(
                labels["yaml_title"],
                value=st.session_state["yaml_text"],
                height=300,
            )
            st.session_state["yaml_text"] = yaml_text

            col_u, col_d, col_ai = st.columns(3)
            with col_u:
                uploaded_yaml = st.file_uploader(
                    labels["upload_yaml"], type=["yml", "yaml"], key="upload_yaml"
                )
            with col_d:
                st.download_button(
                    labels["download_yaml"],
                    data=st.session_state["yaml_text"],
                    file_name="agents.yaml",
                    mime="text/yaml",
                )
            with col_ai:
                if st.button(labels["ai_repair"]):
                    try:
                        model = st.session_state["agent_model"] or "gemini-2.5-flash"
                        repaired = ai_repair_yaml(st.session_state["yaml_text"], model=model)
                        st.session_state["yaml_text"] = repaired
                        parsed = safe_parse_yaml_agents(repaired)
                        if parsed is not None:
                            st.session_state["agents"] = parsed
                            st.success("YAML repaired and agents updated.")
                        else:
                            st.warning("Repaired YAML could not be parsed into agents; please review.")
                    except Exception as e:
                        st.error(f"AI repair failed: {e}")

            if uploaded_yaml is not None:
                try:
                    text = uploaded_yaml.read().decode("utf-8")
                    st.session_state["yaml_text"] = text
                    parsed = safe_parse_yaml_agents(text)
                    if parsed is not None:
                        st.session_state["agents"] = parsed
                        st.success("Uploaded YAML loaded and normalized.")
                    else:
                        st.warning(
                            "Uploaded YAML could not be parsed into standard agents. "
                            "Use AI Repair & Normalize."
                        )
                except Exception as e:
                    st.error(f"Failed to read YAML: {e}")

        # SKILL.md
        with c2:
            st.markdown(f"**{labels['skill_title']}**")
            skill_md = st.text_area(
                labels["skill_title"],
                value=st.session_state["skill_md"],
                height=300,
            )
            st.session_state["skill_md"] = skill_md

            col_u2, col_d2 = st.columns(2)
            with col_u2:
                uploaded_skill = st.file_uploader(
                    labels["upload_skill"], type=["md", "markdown", "txt"], key="upload_skill"
                )
            with col_d2:
                st.download_button(
                    labels["download_skill"],
                    data=st.session_state["skill_md"],
                    file_name="SKILL.md",
                    mime="text/markdown",
                )

            if uploaded_skill is not None:
                try:
                    text = uploaded_skill.read().decode("utf-8")
                    st.session_state["skill_md"] = text
                    st.success("SKILL.md uploaded.")
                except Exception as e:
                    st.error(f"Failed to read SKILL.md: {e}")


def render_doc_intel():
    labels = get_language_labels()
    apply_wow_theme()

    st.markdown(
        f"<div class='wow-card'><h4>{labels['doc_title']}</h4>"
        f"<div class='wow-subtitle'>{labels['doc_subtitle']}</div></div>",
        unsafe_allow_html=True,
    )
    st.write("")

    tabs = st.tabs([labels["paste_tab"], labels["upload_tab"]])
    doc_text = ""
    upload_file = None

    with tabs[0]:
        doc_text = st.text_area(
            labels["paste_tab"],
            placeholder=labels["paste_placeholder"],
            height=260,
        )

    with tabs[1]:
        st.markdown(labels["upload_prompt"])
        upload_file = st.file_uploader(
            labels["upload_tab"], type=["txt", "md", "pdf"], key="doc_file"
        )

    col_left, col_right = st.columns([1, 1])

    with col_left:
        model = st.selectbox(
            "Model",
            options=MODEL_OPTIONS,
            index=MODEL_OPTIONS.index(st.session_state["agent_model"])
            if st.session_state["agent_model"] in MODEL_OPTIONS
            else 2,
        )
        font_size = st.slider(labels["font_size"], min_value=11, max_value=20, value=13)

        if st.button(labels["process_doc"]):
            text = doc_text.strip()
            if upload_file is not None:
                if upload_file.type in ("text/plain", "text/markdown"):
                    text = upload_file.read().decode("utf-8")
                elif upload_file.type == "application/pdf":
                    try:
                        from pypdf import PdfReader

                        reader = PdfReader(upload_file)
                        pages = [p.extract_text() or "" for p in reader.pages]
                        text = "\n\n".join(pages)
                    except Exception as e:
                        st.error(f"Could not extract text from PDF: {e}")
                        text = ""
                else:
                    st.warning("Unsupported file type; please use txt/md/pdf.")

            if not text:
                st.warning("No content to summarize.")
            else:
                try:
                    with st.spinner(labels["process_doc"]):
                        summary = summarize_document(text, model=model)
                        st.session_state["doc_summary"] = summary
                except Exception as e:
                    st.error(f"Error: {e}")

    with col_right:
        summary = st.session_state.get("doc_summary", "")
        st.markdown(f"**{labels['summary']}**")
        if summary:
            # Editable area
            new_summary = st.text_area(
                labels["summary"],
                value=summary,
                height=260,
                key="summary_edit",
            )
            st.session_state["doc_summary"] = new_summary

            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.download_button(
                    labels["download_md"],
                    data=new_summary,
                    file_name="summary.md",
                    mime="text/markdown",
                )
            with col_d2:
                st.download_button(
                    labels["download_txt"],
                    data=new_summary,
                    file_name="summary.txt",
                    mime="text/plain",
                )
        else:
            st.info("Summary will appear here.")


# =========================
# Main App
# =========================

def main():
    render_sidebar()

    view = st.session_state["view"]
    if view == "dashboard":
        render_dashboard()
    elif view == "agent_studio":
        render_agent_studio()
    elif view == "doc_intel":
        render_doc_intel()
    else:
        st.error("Unknown view")


if __name__ == "__main__":
    main()
