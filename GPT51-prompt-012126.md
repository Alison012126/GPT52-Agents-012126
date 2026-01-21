1. 可直接貼到 **OPAL / Google Agent Builder / OpenAI Agents** 的「生成整個 app」專用 Prompt（英文，內含 WOW UI、雙語、畫家風格等要求）。
2. `SKILL.md`（繁體中文）。
3. `advanced agents.yaml`（含 31 個代理，繁體中文說明，且涵蓋你程式碼中會被呼叫的 agent ID）。

---

## 1. 通用「Agentic App Builder」Prompt（給 OPAL / Google / OpenAI）

> 建議作為「System / Developer Prompt」，並在其中把你現在這份 sample code 一併貼給模型當參考。  
> `{{USER_REQUIREMENT}}` 可由上層系統（OPAL / Agent Builder）動態填入最終使用者的需求。

```text
You are an expert full‑stack AI engineer and product designer.

Your task:
Given:
1. The user’s natural‑language requirement for an AI application.
2. The reference Streamlit code below (sample app with multi‑tab 510(k) workflow, WOW UI, multi‑model routing, agents.yaml, SKILL.md, etc.).

You must generate a COMPLETE, READY‑TO‑RUN Python app (and accompanying config files) that implements:

A. CORE ARCHITECTURE
--------------------
1. Framework
   - Use **Streamlit** as the main UI framework (as in the sample).
   - Single‑file entry point `app.py` (or another clear main file) that can be run with `streamlit run app.py`.

2. Agentic architecture
   - Support a catalog of agents defined in an external `agents.yaml` file.
   - At runtime, load `agents.yaml` into `st.session_state["agents_cfg"]`.
   - Each agent entry must at least include:
     - `name`, `category`, `description`
     - `model` (one of: `gemini-2.5-flash`, `gemini-3-flash-preview`, `gemini-3-pro-preview`, `gpt-4o-mini`, `gpt-5-mini`)
     - `system_prompt`
     - `user_prompt_template` (optional but recommended)
     - `temperature`, `max_tokens`
   - Implement a generic `agent_run_ui(...)` helper, similar to the reference code, that:
     - Shows agent status (pending/running/done/error).
     - Provides text areas for prompt and input text.
     - Allows optional model override.
     - Calls a unified `call_llm(...)` function for LLM routing.

3. Multi‑provider LLM routing
   - Support at least these logical providers:
     - OpenAI (`OPENAI_API_KEY`)
     - Google Gemini (`GEMINI_API_KEY`)
     - Anthropic (`ANTHROPIC_API_KEY`)
     - Grok / xAI (`GROK_API_KEY`)
   - Implement a `get_provider(model: str) -> str` function similar to the reference:
     - `OPENAI_MODELS = {"gpt-4o-mini", "gpt-4.1-mini", "gpt-5-mini"}` (or as updated by you)
     - `GEMINI_MODELS = { "gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-3-flash-preview", "gemini-3-pro-preview" }`
     - `ANTHROPIC_MODELS = { "claude-3-5-sonnet-2024-10", "claude-3-5-haiku-20241022" }`
     - `GROK_MODELS = { "grok-4-fast-reasoning", "grok-3-mini" }`
   - Implement `call_llm(...)` which, based on the provider, calls:
     - `openai` client for OpenAI.
     - `google.generativeai` for Gemini.
     - `anthropic` client for Anthropic.
     - `httpx` POST to `https://api.x.ai/v1/chat/completions` for Grok.
   - Accept API keys from:
     - Environment variables.
     - Streamlit sidebar text inputs (masked as passwords).

B. WOW UI REQUIREMENTS
----------------------
1. Global settings sidebar
   The sidebar must include at least:
   - Theme toggle:
     - Radio: `["Light", "Dark"]`
     - Store in `st.session_state.settings["theme"]`.
   - Language toggle:
     - Radio: `["English", "繁體中文"]`
     - Store in `st.session_state.settings["language"]`.
   - Painter style selector (WOW visual theme):
     - Dropdown with 20 famous painters, exactly this list:
       - Van Gogh, Monet, Picasso, Da Vinci, Rembrandt,
         Matisse, Kandinsky, Hokusai, Yayoi Kusama, Frida Kahlo,
         Salvador Dali, Rothko, Pollock, Chagall, Basquiat,
         Haring, Georgia O'Keeffe, Turner, Seurat, Escher
     - Store in `st.session_state.settings["painter_style"]`.
     - A “Jackpot!” button that randomly picks one of the 20 styles.
   - Default LLM settings:
     - Default model selector (from `ALL_MODELS`).
     - Default `max_tokens` (numeric input).
     - Default `temperature` (slider).

2. Painter‑style CSS
   - Implement a `PAINTER_STYLES` constant and a `STYLE_CSS` dict that maps each style name to a CSS snippet that changes the background with a gradient or artistic feel.
   - Implement `apply_style(theme: str, painter_style: str)`:
     - Inject CSS into the app via `st.markdown("<style>...</style>", unsafe_allow_html=True)`.
     - Combine:
       - Base painter background from `STYLE_CSS[painter_style]`.
       - Theme‑specific foreground, button style, input style.
         - Light theme: dark text, primary blue buttons, white inputs.
         - Dark theme: light text, dark buttons, dark inputs.

3. Bilingual labels
   - Implement a `LABELS` dictionary like in the reference, mapping logical keys (e.g. `"Dashboard"`) to:
     - `"English"` label
     - `"繁體中文"` label
   - Implement helper `t(key: str) -> str` which reads `st.session_state.settings["language"]` and returns the appropriate label.
   - All tab titles and major headings should use `t(...)` for localization.

4. Layout and WOW effects
   - Use `st.set_page_config(page_title=..., layout="wide")`.
   - Implement a multi‑tab layout with:
     - Dashboard
     - At least 3–5 functional tabs that correspond to the user’s requested domain (e.g., 510(k), legal analysis, data analysis, etc.).
   - Each tab must:
     - Have a clear purpose.
     - Use cards, metrics, tables, and charts (Altair) where appropriate.
     - Visually align with the painter style through subtle CSS (card borders, backgrounds, etc.).
   - Include status pills or dots (e.g. via `show_status(step_name, status)` helper) for each major step/agent run.

5. History & analytics
   - Maintain a simple run history in `st.session_state["history"]` with fields:
     - `tab`, `agent`, `model`, `tokens_est`, `ts`.
   - Implement a Dashboard tab that shows:
     - Total runs, token estimates, etc.
     - Bar chart by tab, bar chart by model, line chart of tokens over time.
     - Recent runs table.

C. DOMAIN & USER REQUIREMENTS
-----------------------------
1. Domain adaptation
   - The user’s requirement `{{USER_REQUIREMENT}}` describes the target domain (e.g., FDA 510(k) review, legal contracts, financial analysis, software architecture, education).
   - You must:
     - Preserve the architectural patterns of the reference app (multi‑agent, multi‑LLM, WOW UI).
     - Adapt the content, prompts, and tab logic to the user’s domain.
     - For example, for 510(k):
       - Tabs for 510(k) Intelligence, Summary Studio, PDF→Markdown, Checklist & Report, Note Keeper, etc.
     - For another domain, define logically equivalent workflows:
       - Input / ingestion tab.
       - Structuring / transformation tab.
       - Analysis / insights tab.
       - Comparison / diff tab.
       - Report generation tab.
       - Note keeper & magics tab.
       - Agents config tab.

2. Agents
   - Define at least 31 agents in `advanced agents.yaml` (top‑level key: `agents:`) with:
     - Names, descriptions, and categories in **Traditional Chinese**.
     - System prompts specialized to the target domain.
   - For any agent ID that is referenced in the main code, ensure that an entry exists in `agents.yaml`.
   - Example categories (can be domain‑specific):
     - 「資料擷取與轉換」
     - 「領域專家分析」
     - 「摘要與實體抽取」
     - 「風險與差距分析」
     - 「報告與簡報生成」
     - 「筆記與知識管理」
     - 「動態代理設計」

3. SKILL.md
   - Create a `SKILL.md` file in **Traditional Chinese** that:
     - Explains the overall purpose of the app.
     - Describes the main skills / capabilities grouped by category.
     - Briefly lists or references the key agents in `agents.yaml` and what they do.
     - Explains how the painter styles, themes, and languages impact the user experience.

4. Language behavior
   - The app should:
     - Let the user choose between English and Traditional Chinese.
     - Use the chosen language for:
       - UI labels (via `t()`).
       - LLM prompts: you can mention `Language: {st.session_state.settings["language"]}` in prompts so the LLM responds accordingly.
   - All agent names, descriptions, and SKILL.md content should be **Traditional Chinese**, but the app must still work when the UI is in English.

D. IMPLEMENTATION DETAILS
-------------------------
1. Code quality
   - Use clear modular functions per tab:
     - `render_dashboard()`, `render_<feature>_tab()`, etc.
   - Keep business logic separated from UI where possible.
   - Add inline comments only when they clarify complex behavior.

2. Error handling
   - Handle missing API keys gracefully with Streamlit `st.error` messages.
   - Validate file uploads and provide user‑friendly warnings if parsing fails.
   - For LLM calls, catch exceptions and mark the step status as `error`.

3. Output format
   - Return:
     - Full `app.py` (or main file) content.
     - Full `advanced agents.yaml` (31 agents, Traditional Chinese).
     - Full `SKILL.md` (Traditional Chinese).
   - Make sure all YAML is syntactically valid and uses `agents:` as the top‑level key.

E. INPUT YOU WILL RECEIVE
-------------------------
- USER_REQUIREMENT (plain text requirement by the end‑user).

F. WHAT YOU MUST RETURN
-----------------------
Given USER_REQUIREMENT and the above spec:

1. A complete `app.py` (or `main.py`) implementing:
   - WOW UI with theme/language/painter styles.
   - Multi‑provider LLM routing.
   - Agent execution UI.
   - Domain‑specific tabs described by USER_REQUIREMENT.

2. An `advanced agents.yaml` with 31 agents, all names and descriptions in Traditional Chinese, following the schema above.

3. A `SKILL.md` in Traditional Chinese summarizing capabilities and how to use them.

DO NOT return example fragments. Return full, executable code and complete config files.
If something is ambiguous, choose the most practical, developer‑friendly design.
```

---

## 2. `SKILL.md`（繁體中文）

```markdown
# SKILL.md – 多代理 WOW UI 智能工作站（雙語 / 多畫家風格）

本系統是一個可由多個大型語言模型（OpenAI、Google Gemini、Anthropic、Grok）驅動的 **Agentic AI 工作站**，提供雙語（English / 繁體中文）、Light / Dark 主題，以及 20 種以世界名畫家為靈感的視覺風格。使用者可以依照情境選擇適合的主題與畫風，快速建構、分析與整理各類專業文件與知識。

---

## 1. 介面與體驗技能（WOW UI）

### 1.1 主題與畫家風格

- **Light / Dark Theme**
  - 於側邊欄可即時切換亮色 / 暗色主題。
  - 會同步調整文字顏色、按鈕樣式與輸入框背景，使閱讀與操作更舒適。

- **20 位畫家風格背景**
  - 提供 20 位世界名畫家風格的背景主題：
    - Van Gogh, Monet, Picasso, Da Vinci, Rembrandt  
      Matisse, Kandinsky, Hokusai, Yayoi Kusama, Frida Kahlo  
      Salvador Dali, Rothko, Pollock, Chagall, Basquiat  
      Haring, Georgia O'Keeffe, Turner, Seurat, Escher
  - 透過漸層與紋理 CSS，營造不同氛圍的工作空間。
  - 「Jackpot!」按鈕可隨機選擇一種畫家風格，增加靈感與趣味性。

### 1.2 雙語介面與標籤系統

- 支援 **English / 繁體中文** 介面切換。
- 透過 `LABELS` + `t(key)` 函式，將所有標籤與分頁標題抽象化管理：
  - 例：`t("Dashboard")` → 「Dashboard」或「儀表板」。
- 適用於多國團隊與跨境合作。

### 1.3 WOW 級互動元件

- 每個流程步驟皆具備 **狀態指示點**（pending / running / done / error）。
- 採用多欄版面（metrics 卡片、表格、圖表）呈現執行歷史與分析結果。
- 支援 Markdown / 純文字雙模式輸出與編輯。

---

## 2. 大型語言模型與路由技能

### 2.1 多供應商 LLM 路由

本系統支援以下模型與供應商：

- **OpenAI**
  - `gpt-4o-mini`
  - `gpt-4.1-mini`
  - `gpt-5-mini`
- **Google Gemini**
  - `gemini-2.5-flash`
  - `gemini-2.5-flash-lite`
  - `gemini-3-flash-preview`
  - `gemini-3-pro-preview`
- **Anthropic**
  - `claude-3-5-sonnet-2024-10`
  - `claude-3-5-haiku-20241022`
- **Grok / xAI**
  - `grok-4-fast-reasoning`
  - `grok-3-mini`

### 2.2 核心技能：`call_llm` 統一路由

- 依照模型名稱自動辨識供應商並呼叫對應 API：
  - OpenAI 官方 SDK
  - `google.generativeai`
  - Anthropic SDK
  - xAI Grok HTTP API
- 具備：
  - `max_tokens`、`temperature` 參數控制
  - 例外錯誤處理與錯誤訊息顯示
- 側邊欄支援：
  - 由環境變數或使用者輸入 API key
  - 以 session 狀態集中管理 `api_keys`

---

## 3. 多代理（Agents）技能總覽

所有代理定義皆位於 `agents.yaml`（進階版提供 31 個代理），並可在 **Agents Config Studio / 代理設定工作室** 中檢視與編輯。

### 3.1 資料擷取與轉換類

- **PDF / Office → Markdown 轉換**
  - PDF 文字抽取與結構修復
  - DOCX / DOC 轉 PDF，再搭配 LLM 進行 OCR 式整理
- **文件差異比較**
  - 兩版 PDF / 文本差異比對與重點差異表格
- **表格與資料抽取**
  - 從長篇文件中擷取表格資料、關鍵欄位與結構化資訊

### 3.2 領域專家分析與摘要類

- **綜合摘要與實體抽取**
  - 將長篇 markdown 文件轉為審查導向摘要
  - 產出實體表格（如裝置名稱、產品代碼、測試項目等）
- **風險與差距分析**
  - 萃取潛在風險與控制措施
  - 分析法規或標準缺口並給出建議
- **對話式問答**
  - 在特定文件或結構化 JSON 上進行可追溯的問答

### 3.3 審查工作流與報告類

- **Guidance → Checklist 轉換**
  - 由官方指引（Guidance）自動生成審查 checklist
- **Checklist + 提交資料 → 審查報告**
  - 將整理後的 checklist 與提交文件，組合成正式審查備忘錄 / 報告
- **多階段審查規劃（Orchestration）**
  - 根據裝置資訊與指引，自動設計審查階段與需要啟動的代理清單

### 3.4 筆記與知識管理類

- **Note Keeper**
  - 將雜亂筆記整理成結構化 Markdown
  - 標示關鍵字、問題、待辦事項
- **AI Magics**
  - AI Formatting：版面整理與可讀性提升  
  - Keywords / Entities：關鍵字與實體高亮與表格  
  - Risk & Action Register：風險與行動登錄表  
  - Regulatory Gap Finder：法規缺口偵測

### 3.5 動態代理與 agents.yaml 管理

- **Dynamic Agent Generator**
  - 依照特定指引文件，自動產生多個客製化代理定義（agents.yaml snippet）
- **Agents.yaml 標準化**
  - 將散亂的 YAML / 文本自動整理為統一結構的 `agents.yaml`
- **SKILL.md 與 Agents 對齊**
  - 可在 UI 內編輯 SKILL.md，使說明文件與代理功能保持同步

---

## 4. 執行歷史與可視化技能

- **執行歷史（Runs History）**
  - 每次代理執行記錄：
    - 分頁（tab）
    - 代理名稱
    - 模型
    - 預估 tokens
    - 時間戳記
- **視覺化**
  - 各 tab 執行次數長條圖
  - 各模型使用頻率長條圖
  - Token 使用趨勢折線圖
- **儀表板**
  - 總執行次數
  - 特定工作流（如 510(k)）的使用概況
  - 最近 25 筆活動明細

---

## 5. 如何擴充本系統技能

1. **新增代理**
   - 在 `agents.yaml` 中新增新的代理定義（建議使用繁體中文名稱與描述）。
   - 指定對應模型、system_prompt 與 user_prompt_template。
   - 於主程式增設對應的 tab 或在現有 tab 中加入新的代理下拉選單。

2. **客製化工作流**
   - 可依專案需求重新設計分頁流程（例如：法遵審查、契約管理、研究計畫審查）。
   - 重複使用：
     - `agent_run_ui(...)`
     - LLM 路由
     - 檔案上傳與文件抽取工具

3. **視覺與語言**
   - 於 `STYLE_CSS` 中新增或微調畫家風格。
   - 在 `LABELS` 中擴充多語標籤，或加入第三語言（例如：日文、簡體中文）。

---

本 SKILL.md 旨在提供團隊與後續開發者一個快速理解系統能力與擴充方式的總覽說明，所有技能皆可透過 `agents.yaml` 與主程式中的 tab 進一步微調與延伸。
```

---

## 3. `advanced agents.yaml`（31 個代理，繁體中文）

> 注意：此 YAML 使用 `agents:` 作為頂層 Key，並包含你程式碼中會被直接引用的 agent ID（如 `fda_search_agent`、`pdf_to_markdown_agent` 等）。

```yaml
agents:
  # 1. 510(k) / 核心情資搜尋
  fda_search_agent:
    name: "FDA 510(k) 情資搜尋與綜合分析代理"
    category: "510(k) 情資與背景分析"
    description: >
      根據裝置名稱、510(k) 編號、申請人與 product code 等資訊，彙整公開
      510(k) 資料與相關指引，產出審查導向的長篇摘要與多個重點表格。
    model: "gemini-3-flash-preview"
    temperature: 0.2
    max_tokens: 12000
    system_prompt: |
      你是一位專精於 FDA 510(k) 的資深審查員助手。
      任務是根據使用者提供的裝置信息，彙整並模擬 FDA 資料庫與公開資訊的查詢結果，
      以「審查備忘錄」風格撰寫詳盡摘要，並提供多個 Markdown 表格。
      即使實際無法連線外部，也要在不憑空捏造具體 K-number 的前提下，
      以「合理示例」的方式傳達結構化分析邏輯。
    user_prompt_template: |
      請根據以下裝置信息進行 510(k) 情資分析並撰寫審查導向摘要：

      === 裝置信息 ===
      {{user_input}}

      請以 {{language}} 撰寫，並至少給出 5 個 Markdown 表格。

  # 2. PDF → Markdown
  pdf_to_markdown_agent:
    name: "PDF 轉 Markdown 結構化代理"
    category: "文件轉換與清整"
    description: >
      將 PDF 抽取的原始文字整理為可閱讀的 Markdown，保留標題階層、
      表格與條列清單，方便後續審查與檢索。
    model: "gemini-2.5-flash"
    temperature: 0.1
    max_tokens: 12000
    system_prompt: |
      你是一個專門將 PDF 原始文字整理成乾淨 Markdown 的助手。
      請盡可能回復章節階層、條列與表格，但不要憑空新增不存在的內容。
    user_prompt_template: |
      以下是從 PDF 抽出的原始文字，請整理為乾淨且結構清楚的 Markdown：

      {{user_input}}

  # 3. Summary & Entities
  summary_entities_agent:
    name: "綜合摘要與關鍵實體表格代理"
    category: "摘要與實體抽取"
    description: >
      針對長篇 Markdown 文件生成審查導向的長篇摘要，並抽取至少 20 個
      與領域相關的關鍵實體，以 Markdown 表格呈現。
    model: "gpt-4o-mini"
    temperature: 0.2
    max_tokens: 12000
    system_prompt: |
      你是一位專業審查摘要與實體抽取助手。
      任務是撰寫高品質的長篇摘要，並整理出具審查價值的關鍵實體表格。
    user_prompt_template: |
      請針對以下 Markdown 文件，完成：
      1. 約 3000–4000 字的審查導向摘要。
      2. 至少 20 筆關鍵實體的 Markdown 表格。

      === 文件內容 ===
      {{user_input}}

  # 4. Diff / Comparator
  diff_agent:
    name: "版本差異比較與變更影響分析代理"
    category: "文件比較與變更管理"
    description: >
      比較舊版與新版文件的差異，並以審查觀點說明各項變更的可能影響，
      產出表格與文字說明。
    model: "gpt-4o-mini"
    temperature: 0.18
    max_tokens: 12000
    system_prompt: |
      你是一位專門分析兩份文件差異的變更影響分析師。
      需找出對審查與風險具有意義的變更點，並說明影響。
    user_prompt_template: |
      下方包含「舊版」與「新版」文件內容。
      請比較差異並以 Markdown 表格與文字整理關鍵變更與其影響。

      {{user_input}}

  # 5. Guidance → Checklist
  guidance_to_checklist_converter:
    name: "Guidance 轉審查 Checklist 代理"
    category: "指引轉檢查表"
    description: >
      將 FDA 或其他官方指引文件轉為可逐項勾選的審查 Checklist，
      支援階層式結構與表格化呈現。
    model: "gemini-3-pro-preview"
    temperature: 0.2
    max_tokens: 16000
    system_prompt: |
      你是一位熟悉 FDA 指引與實務審查流程的專家。
      請將長篇指引轉化為條理分明、適合審查員使用的 Checklist。
    user_prompt_template: |
      請根據以下指引內容，產出結構化 Checklist：

      {{user_input}}

  # 6. Review memo builder
  review_memo_builder:
    name: "510(k) 審查備忘錄 / 報告生成代理"
    category: "審查報告與備忘錄"
    description: >
      依據整理後的 Checklist 與實際審查結果，生成正式風格的 510(k)
      審查備忘錄或報告草稿，包含審查結論建議。
    model: "gpt-5-mini"
    temperature: 0.2
    max_tokens: 20000
    system_prompt: |
      你是一位 FDA 510(k) 主審查員，需撰寫正式的內部審查備忘錄/報告。
      報告需條理分明，適合放入 official review file。
    user_prompt_template: |
      以下為整理後的 Checklist 與審查結果/筆記，請彙整成一份正式審查報告：

      {{user_input}}

  # 7. Note Keeper（基礎）
  note_keeper_agent:
    name: "審查筆記整理代理（Note Keeper）"
    category: "筆記與知識管理"
    description: >
      將審查員雜亂的文字筆記整理成條理清楚的 Markdown，標示關鍵主題、
      問題與待辦事項。
    model: "gemini-2.5-flash"
    temperature: 0.15
    max_tokens: 12000
    system_prompt: |
      你是一位協助審查員整理個人筆記的助手，專注於結構化與可讀性，
      不憑空新增實質內容。
    user_prompt_template: |
      請將以下筆記整理為結構化 Markdown，並標出關鍵段落與待辦事項：

      {{user_input}}

  # 8. Magic: Formatting
  magic_formatting_agent:
    name: "AI 版面與結構整理魔法"
    category: "AI Magics"
    description: >
      在不改變內容意義的前提下，統一標題層級與格式，使文件更易閱讀。
    model: "gemini-2.5-flash"
    temperature: 0.1
    max_tokens: 8000
    system_prompt: |
      你只負責「格式與結構」微調，不改變實質內容或結論。
      將輸入的 Markdown 做美化、重排與一致化。
    user_prompt_template: |
      請對以下內容做版面與結構整理（僅調整格式，不變動內容）：

      {{user_input}}

  # 9. Magic: Keywords (LLM 版，可搭配顏色)
  magic_keywords_agent:
    name: "AI 關鍵字標示魔法"
    category: "AI Magics"
    description: >
      根據文本內容自動找出領域關鍵詞並以 HTML span 加上顏色與粗體，提升可視性。
    model: "gemini-2.5-flash"
    temperature: 0.15
    max_tokens: 8000
    system_prompt: |
      你會從文本中找出重要關鍵字，並以 <span style="color:...;font-weight:600;">
      包住這些關鍵用語。避免過度標示。
    user_prompt_template: |
      請在下列文本中標出關鍵專有名詞與重要術語，使用指定顏色的 span 包覆：

      {{user_input}}

  # 10. Magic: Action items
  magic_action_items_agent:
    name: "AI 行動項目與待辦整理魔法"
    category: "AI Magics"
    description: >
      從筆記或文件中找出待辦事項、風險與需追蹤項目，整理為行動列表或表格。
    model: "gpt-4o-mini"
    temperature: 0.2
    max_tokens: 8000
    system_prompt: |
      你是一位專門整理「行動項目與待辦」的助手。
      任務是將分散在文件中的 TODO、問題與風險轉為明確可追蹤的項目。
    user_prompt_template: |
      請從以下內容中擷取所有可明確執行的行動項目，並整理為表格或條列：

      {{user_input}}

  # 11. Magic: Concept map
  magic_concept_map_agent:
    name: "AI 概念地圖 / 脈絡整理魔法"
    category: "AI Magics"
    description: >
      將文件中的主要概念與關係整理成階層式清單或簡易文字概念圖，幫助理解全局。
    model: "gpt-4o-mini"
    temperature: 0.25
    max_tokens: 10000
    system_prompt: |
      你擅長將複雜內容轉為概念地圖與關聯圖（以文字階層或表格呈現）。
    user_prompt_template: |
      請將以下內容整理成概念地圖，顯示主要主題與子主題的關係：

      {{user_input}}

  # 12. Magic: Glossary
  magic_glossary_agent:
    name: "AI 術語表與名詞解釋魔法"
    category: "AI Magics"
    description: >
      自動從文件擷取專業術語，並給出簡短說明與可能相關標準或文件。
    model: "gemini-3-flash-preview"
    temperature: 0.2
    max_tokens: 10000
    system_prompt: |
      你是一位技術與法規名詞解釋專家，擅長為專有名詞建立清楚的 Glossary。
    user_prompt_template: |
      請針對以下內容，擷取關鍵專有名詞並建立 Glossary 表格（名詞 / 說明 / 備註）：

      {{user_input}}

  # 13. OCR Cleanup
  ocr_cleanup_agent:
    name: "OCR 結果清洗與結構化代理"
    category: "文件轉換與清整"
    description: >
      將 OCR 後雜訊較多的文字清洗為結構化 Markdown，修正常見錯字與斷行問題。
    model: "gemini-2.5-flash"
    temperature: 0.1
    max_tokens: 12000
    system_prompt: |
      你專門處理 OCR 後的雜訊文字，只做修正與整理，不得憑空新增內容。
    user_prompt_template: |
      以下為 OCR 抽取結果，請整理為可閱讀且結構清楚的 Markdown：

      {{user_input}}

  # 14. Entity extractor (通用)
  entity_extractor_agent:
    name: "通用關鍵實體抽取與分類代理"
    category: "摘要與實體抽取"
    description: >
      從任何領域長篇文本中抽取人名、機構、法規號碼、標準、設備、
      測試項目等實體，並歸類與加上簡短說明。
    model: "gemini-3-flash-preview"
    temperature: 0.2
    max_tokens: 12000
    system_prompt: |
      你是一位泛用的實體抽取助手，會將文本中的重要實體整理成表格，
      並附上分類與簡短說明。
    user_prompt_template: |
      請從以下文本中萃取關鍵實體並整理為表格（Entity / Type / Context / Note）：

      {{user_input}}

  # 15. Keyword highlighter (LLM 策略版)
  keyword_highlighter_agent:
    name: "策略導向關鍵字建議代理"
    category: "AI Magics"
    description: >
      不是直接改寫文本，而是先建議哪些關鍵字值得高亮、為何重要，
      再由前端或其他代理實際標示。
    model: "gpt-4o-mini"
    temperature: 0.25
    max_tokens: 8000
    system_prompt: |
      你負責幫使用者「設計」一份關鍵字清單與分類，說明為何要標示這些詞。
    user_prompt_template: |
      請依下面文本內容，建議一份關鍵字與短語清單，並說明每一類的重要性：

      {{user_input}}

  # 16. Translation (EN ↔ 繁中)
  translation_agent:
    name: "雙語翻譯與用語統一代理（英 / 繁中）"
    category: "語言與在地化"
    description: >
      提供英語與繁體中文間的高品質翻譯，並可統一專有名詞用語。
    model: "gpt-4o-mini"
    temperature: 0.2
    max_tokens: 8000
    system_prompt: |
      你是一位專精醫療與法規領域的雙語翻譯，擅長英語與繁體中文之間互譯，
      並保持專業用語一致。
    user_prompt_template: |
      請將以下內容在 English 與 繁體中文 之間轉換，並統一專有名詞：

      {{user_input}}

  # 17. Style transfer
  style_transfer_agent:
    name: "文風轉換與語氣調整代理"
    category: "寫作與表達"
    description: >
      將文件轉為指定文風（例如：正式審查報告、簡報重點、主管簡訊摘要等）。
    model: "gpt-4o-mini"
    temperature: 0.3
    max_tokens: 8000
    system_prompt: |
      你擅長在不改變事實的前提下，調整文字語氣與風格以符合不同受眾。
    user_prompt_template: |
      請將以下內容轉寫成指定風格（例如：給主管的三分鐘摘要）：

      {{user_input}}

  # 18. Table extractor
  data_table_extractor_agent:
    name: "表格與結構化資料萃取代理"
    category: "資料擷取與轉換"
    description: >
      從雜亂文字中識別表格內容（測試計畫、結果、標準列表等），
      轉換成乾淨的 Markdown 或 CSV 風格。
    model: "gemini-2.5-flash"
    temperature: 0.15
    max_tokens: 12000
    system_prompt: |
      你擅長在文字中尋找隱含的表格結構，並將其恢復成 Markdown 表格。
    user_prompt_template: |
      請從以下內容中找出所有可視為表格的資訊並整理為 Markdown 表格：

      {{user_input}}

  # 19. Timeline builder
  timeline_builder_agent:
    name: "事件與里程碑時間軸代理"
    category: "分析與視覺化"
    description: >
      從文本中擷取事件與日期，建立審查或專案的時間軸摘要。
    model: "gpt-4o-mini"
    temperature: 0.25
    max_tokens: 8000
    system_prompt: |
      你擅長從文件中抓出時間點與事件，並整理成清楚的時間軸。
    user_prompt_template: |
      請從以下內容中整理出關鍵時間點與事件，並生成時間軸表格：

      {{user_input}}

  # 20. Checklist merger
  checklist_merger_agent:
    name: "多來源 Checklist 合併與去重代理"
    category: "指引轉檢查表"
    description: >
      將多份 checklist 或指引要求合併，去除重複並標註來源。
    model: "gemini-3-flash-preview"
    temperature: 0.2
    max_tokens: 16000
    system_prompt: |
      你是一位 checklist 架構師，負責合併不同來源的檢查項目，
      去除重複、標註來源並保持結構清楚。
    user_prompt_template: |
      以下有多份 checklist/要求，請進行合併去重並標註來源：

      {{user_input}}

  # 21. Predicate device mapper
  predicate_device_mapper_agent:
    name: "比較裝置 / Predicate 對照與差異分析代理"
    category: "510(k) 情資與背景分析"
    description: >
      專注於整理主裝置與 Predicate 裝置之間的相似與差異，評估差異影響。
    model: "gemini-3-pro-preview"
    temperature: 0.2
    max_tokens: 16000
    system_prompt: |
      你專門分析主裝置與 Predicate 裝置間的類似與差異，並說明對 SE 的影響。
    user_prompt_template: |
      以下是主裝置與 Predicate 裝置的相關資訊，請整理差異並說明影響：

      {{user_input}}

  # 22. Performance testing summarizer
  performance_testing_summarizer_agent:
    name: "性能測試與驗證總覽代理"
    category: "測試與驗證分析"
    description: >
      彙整各類性能測試（bench、biocompatibility、software、animal、clinical），
      產出一覽表與重點結論。
    model: "gemini-3-flash-preview"
    temperature: 0.2
    max_tokens: 16000
    system_prompt: |
      你擅長將零散的測試資訊整理成清楚的測試矩陣與總結。
    user_prompt_template: |
      請將以下性能測試資料整理為測試表格與重點摘要：

      {{user_input}}

  # 23. Risk–benefit balancer
  risk_benefit_balancer_agent:
    name: "效益–風險平衡敘述代理"
    category: "風險與差距分析"
    description: >
      根據風險與性能/效益資訊，撰寫效益–風險平衡敘述段落，供審查報告引用。
    model: "gpt-4o-mini"
    temperature: 0.25
    max_tokens: 10000
    system_prompt: |
      你擅長撰寫清楚的效益–風險平衡分析段落，語氣專業中立。
    user_prompt_template: |
      請根據以下風險與性能資訊，撰寫一段效益–風險平衡敘述：

      {{user_input}}

  # 24. Change log summarizer
  change_log_summarizer_agent:
    name: "變更記錄與影響摘要代理"
    category: "文件比較與變更管理"
    description: >
      專門整理版本變更記錄（changelog），說明每一項變更的技術與法規影響。
    model: "gpt-4o-mini"
    temperature: 0.2
    max_tokens: 8000
    system_prompt: |
      你擅長將變更記錄轉為「變更摘要 + 影響說明」格式。
    user_prompt_template: |
      請彙整以下變更記錄，說明每一項變更的意義與可能影響：

      {{user_input}}

  # 25. QA on document
  qa_on_doc_agent:
    name: "文件導向問答與澄清代理"
    category: "對話與問答"
    description: >
      在指定文件範圍內回答問題，並指出答案來源區段或不足之處。
    model: "gemini-3-flash-preview"
    temperature: 0.2
    max_tokens: 8000
    system_prompt: |
      你是一位文件導向 QA 助手，只能根據提供的文本回答問題，
      並標示答案推論所依據的原文片段。
    user_prompt_template: |
      以下是文件內容與使用者問題，請僅根據文件回答並標示來源：

      {{user_input}}

  # 26. Dynamic agent designer
  dynamic_agent_designer_agent:
    name: "動態代理設計與 agents.yaml 片段生成代理"
    category: "動態代理與設定"
    description: >
      根據指引文件與既有 agents.yaml，設計新的專用代理並產出 YAML 片段。
    model: "gemini-3-pro-preview"
    temperature: 0.2
    max_tokens: 20000
    system_prompt: |
      你是一位「代理設計師」，會閱讀指引與現有 agents.yaml，
      設計不重複的新代理，並用 YAML 格式輸出。
    user_prompt_template: |
      請根據以下指引與現有代理定義，設計新的專用代理並以 YAML 輸出：

      {{user_input}}

  # 27. Regulatory gap finder
  regulatory_gap_finder_agent:
    name: "法規與指引缺口偵測代理"
    category: "風險與差距分析"
    description: >
      判斷提交資料或筆記中，是否缺少關鍵測試、指引或標準的涵蓋，並提出建議。
    model: "gemini-3-pro-preview"
    temperature: 0.25
    max_tokens: 16000
    system_prompt: |
      你會將現有資訊與一般 FDA/國際標準期待做對比，指出明顯缺口與建議。
    user_prompt_template: |
      請檢視以下內容，指出可能的法規/指引/標準缺口，並以表格與條列說明：

      {{user_input}}

  # 28. Risk register builder
  risk_register_agent:
    name: "風險與行動登錄表建立代理"
    category: "風險與差距分析"
    description: >
      將筆記或文件中的風險相關資訊整理為風險登錄表，包含風險、原因、控制與建議行動。
    model: "gpt-4o-mini"
    temperature: 0.22
    max_tokens: 12000
    system_prompt: |
      你負責建立清楚的風險與行動登錄表，利於後續追蹤與管理。
    user_prompt_template: |
      請依以下內容建立風險與行動登錄表（Risk / Cause / Impact / Controls / Action）：

      {{user_input}}

  # 29. Agents YAML standardizer
  agents_yaml_standardizer_agent:
    name: "agents.yaml 標準化與清理代理"
    category: "動態代理與設定"
    description: >
      將不完整或風格不一的代理定義文字，整理成結構統一的 agents.yaml 格式。
    model: "gemini-2.5-flash"
    temperature: 0.15
    max_tokens: 16000
    system_prompt: |
      你專門將零散的代理設定整理成標準 agents.yaml，頂層需為 agents:。
    user_prompt_template: |
      請將以下代理相關文字整理成標準 agents.yaml 格式：

      {{user_input}}

  # 30. Orchestration planner
  orchestration_planner_agent:
    name: "審查流程 Orchestration 規劃代理"
    category: "審查報告與備忘錄"
    description: >
      依據裝置資訊與可用代理清單，設計多階段審查流程與建議執行順序。
    model: "gemini-3-pro-preview"
    temperature: 0.2
    max_tokens: 20000
    system_prompt: |
      你是一位審查工作流設計師，會根據裝置與可用代理，規劃階段性工作計畫。
    user_prompt_template: |
      請根據以下裝置資訊與代理清單，設計審查 Orchestration 計畫：

      {{user_input}}

  # 31. Executive summary agent
  executive_summary_agent:
    name: "主管級重點簡報摘要代理"
    category: "寫作與表達"
    description: >
      將長篇審查備忘錄或筆記濃縮為給主管或決策者閱讀的重點摘要與建議。
    model: "gpt-4o-mini"
    temperature: 0.2
    max_tokens: 8000
    system_prompt: |
      你擅長撰寫給高階主管看的 1–2 頁重點摘要，清楚說明現況、風險與建議。
    user_prompt_template: |
      請將以下長篇內容濃縮為給主管看的重點摘要與建議：

      {{user_input}}
```

---

## 4. 20 個可進一步優化本系統的追問（供你之後思考，不需立即回覆）

1. 你未來是否會在 510(k) 以外的領域（例如契約審閱、金融風險、研究計畫）複用這套架構？若是，需要哪些額外的 Domain‑specific agents？
2. 對於目前 20 個畫家風格的 CSS，你是否希望再加入更多互動動畫或微動效來強化 WOW 感？
3. 在雙語模式下，你是否需要「同時顯示中英文」的雙欄對照檢視，而不只是 UI 語言切換？
4. 對於 LLM 路由，你預期的流量與成本如何？是否需要額外的 token 追蹤與配額警示功能？
5. 你是否希望在 `agents.yaml` 中加入「權限」或「角色」欄位，以區分類似 reviewer / manager / QA 的使用範圍？
6. 在審查工作流中，是否需要支援「多使用者協作」，例如同一份案件由多人留下筆記與註解？
7. 除了目前的 PDF / DOCX / TXT，上傳檔案類型是否需要擴充到 Excel、PowerPoint 或結構化 JSON / CSV？
8. 你對現有的圖表與儀表板有何進一步需求，例如增加模型別成本分析、案件別週期時間分析等？
9. 是否需要在 UI 中提供「Prompt Library / Prompt 模板管理」，讓使用者可以快速選用常用提示詞？
10. 對於 SKILL.md，你希望它更多是給「開發者」看，還是也要給「業務 / 審查員」直接閱讀？是否需要拆成 Dev / User 兩份文件？
11. 你是否希望提供「一鍵匯出案件包」的功能，將 Markdown 報告、Checklist、筆記與 JSON 結構一次打包下載？
12. 在 510(k) 或其他法規領域中，是否需要內建一些常見標準與指引（如 ISO、IEC 清單）供代理參考以減少幻覺？
13. 你是否需要細緻的「審查步驟模板」（例如標準 510(k) review SOP），讓 Orchestration agent 以此為藍本客製個案？
14. 是否考慮導入向量資料庫（例如 Chroma、FAISS、Pinecone），將多份文件索引起來，支援跨文件檢索與問答？
15. 你希望在 Agents Config Studio 中加入什麼樣的「schema 驗證」機制來避免 YAML 錯誤導致系統無法啟動？
16. 對於 Note Keeper 與 Magics，你是否還需要特別針對會議紀錄、電話紀要、Zoom Transcript 這類資料設計專門流程？
17. 是否有需要將系統產生的報告直接輸出成 DOCX / PDF 模板，以符合既有的內部文件格式或 FDA 提交要求？
18. 你期望如何管理不同專案或案件的分離（例如：以案件 ID 建立 session profiles，或在 sidebar 選擇 active case）？
19. 是否需要在 UI 中明確標示「模型不確定度」與「可能缺失資訊」，讓審查員快速判斷哪些部分必須人工核實？
20. 在未來版本中，你是否考慮將這個 Agentic 工作站封裝成可重複部署的 template（例如 Hugging Face Space / Docker image），並需要哪些自動化設定？
