# Artistic Intelligence Workspace v2.0  
**Comprehensive Technical Specification**

## 1. Overview

Artistic Intelligence Workspace v2.0 is a browser-based AI studio providing:

- A **WOW UI** with:
  - Light/Dark themes
  - Dual language support: English (EN) and Traditional Chinese (TC)
  - 20 “painter style” visual themes with a Jackpot/randomizer
- Three primary functional views:
  1. **Dashboard** – metrics and charts
  2. **Agent Studio** – run and manage agents, edit `agents.yaml`, and `SKILL.md`
  3. **Document Intelligence** – summarize and analyze documents

The system is built as a **Next.js 15+ App Router** application with a strongly typed **TypeScript** codebase. Styling is driven by **Tailwind CSS** and dynamically applied **CSS variables** for painter themes. **ShadCN UI**-style components provide consistent and composable UI primitives. 

AI functionality is implemented using **Genkit** (`@genkit-ai/next`, `@genkit-ai/google-genai`) and the **Google Generative AI SDK** (`@google/generative-ai`). The system is designed so that additional providers (OpenAI, Anthropic, Grok, etc.) can be added later without breaking the existing architecture.

---

## 2. Architecture Overview

### 2.1 High-Level Components

- **Next.js App (Frontend + Server Actions)**
  - Routes:
    - `src/app/layout.tsx` – global shell and providers
    - `src/app/page.tsx` – main UI and top-level state
  - Server actions:
    - `generateContentAction` – calls Gemini models
    - `repairYamlAction` – invokes Genkit YAML repair flow
    - `summarizeDocumentAction` – invokes Genkit document summarization flow
    - `hasServerApiKeyAction` – reports presence of server-side API key

- **Genkit AI Flows (`src/ai/`)**
  - `genkit.ts` – Genkit instance with `googleAI` and `next` plugins
  - `flows/repair-invalid-yaml.ts` – schema-bound YAML repair flow
  - `flows/summarize-document-intelligence.ts` – schema-bound summarization flow
  - `dev.ts` – optional runtime for Genkit development

- **UI Component Layer (`src/components/`)**
  - Layout & Shell:
    - `app-shell.tsx`
    - `main-sidebar.tsx`
  - Views:
    - `dashboard.tsx`
    - `agent-studio.tsx`
    - `doc-intelligence.tsx`
  - UI Primitives (`src/components/ui/`):
    - Button, Card, Input, Textarea, Select, Tabs, Switch, Badge, Slider, ChartContainer

- **Shared Utilities & Definitions (`src/lib/`)**
  - `types.ts` – core types and data models
  - `constants.ts` – painter styles, labels (i18n), default agents, mock metrics
  - `utils.ts` – generic helpers (class names, file → data URI)

- **Hooks**
  - `use-toast.ts` – lightweight toast system
  - `use-mobile.tsx` – responsive helper (currently optional)

- **Static Workspace Files (`public/`)**
  - `agents.yaml` – default agent definitions
  - `SKILL.md` – default shared skill library

---

## 3. Technology Stack

### 3.1 Core Framework & Language

- **Framework**: Next.js 15+ (App Router)
- **Language**: TypeScript (strict typing recommended)

### 3.2 UI & Styling

- **UI Components**: ShadCN-style components, locally implemented
- **Styling**: Tailwind CSS + CSS variables
- **Icons**: `lucide-react`
- **Charts**: `recharts` wrapped by a `ChartContainer` ShadCN-style component

### 3.3 AI & Backend

- **Genkit**:
  - `genkit`
  - `@genkit-ai/next`
  - `@genkit-ai/google-genai`
- **Google Gemini SDK**:
  - `@google/generative-ai`

### 3.4 Data & Utilities

- **YAML**: `js-yaml`
- **Validation**: `zod`
- **Classnames**:
  - `class-variance-authority`
  - `clsx`
  - `tailwind-merge`

---

## 4. Data Models & Configurations

### 4.1 Agent Schema

Defined in `src/lib/types.ts`:

```ts
export interface Agent {
  id: string;
  name: string;
  description?: string;
  model: string;
  maxTokens?: number;
  temperature?: number;
  systemPrompt?: string;
  tags?: string[];
}
id: stable, unique identifier (e.g., creative-writer).
name: human-readable label used in the UI.
description: short explanation of behavior/purpose.
model: default model identifier (gemini-2.5-flash, gpt-4o-mini, etc.).
maxTokens: default max output tokens (overridden in UI if needed).
temperature: standard model temperature (not yet surfaced in UI but may be used in future).
systemPrompt: system-level instruction string.
tags: optional classification tags.
4.2 App Settings & View Types
export type Theme = "light" | "dark";
export type Language = "en" | "tc";

export const VIEW_TYPES = ["dashboard", "agent-studio", "doc-intelligence"] as const;
export type ViewType = (typeof VIEW_TYPES)[number];

export interface AppSettings {
  theme: Theme;
  language: Language;
  painterStyle: PainterStyle;
}
4.3 Painter Styles
Enum: 20 PainterStyle keys (e.g., van_gogh, monet, picasso, etc.).
CSS Mapping: PAINTER_CSS is a Record<PainterStyle, PainterCssVariables> dict mapping each painter to:
--wow-bg
--wow-fg
--wow-accent
--wow-accent-soft
--wow-border
--wow-card-bg
--wow-font-headline
--wow-font-body
These variables are applied on <html> using document.documentElement.style.setProperty(key, value) in AppShell.

4.4 Internationalization Labels
LABELS in src/lib/constants.ts holds UI text for EN/TC:

LABELS.en and LABELS.tc each contain keys for:
appTitle
sidebar (navigation, API status, appearance controls)
dashboard (metric titles, chart labels)
agentStudio (Run/Manage tab labels, prompts, buttons)
docIntelligence (tab labels, prompts, button texts)
toasts (standard messages for error/success notifications)
All components that display text consume these labels via the language prop and do not hardcode strings.

4.5 Static Workspace Files
public/agents.yaml
Defines default agents array using the same Agent structure.
On initial load, page.tsx fetches this file, parses via js-yaml, and populates the top-level agents state.
public/SKILL.md
Defines shared patterns and instructions across agents (e.g., painterly metaphors, YAML normalization rules, summarization formats).
Loaded at startup; editable and downloadable from Agent Studio.
5. State Management
All top-level state is centralized in src/app/page.tsx:

const [currentView, setCurrentView] = useState<ViewType>("dashboard");
const [apiKey, setApiKey] = useState("");
const [agents, setAgents] = useState<Agent[]>(DEFAULT_AGENTS);
const [settings, setSettings] = useState<AppSettings>({
  theme: "dark",
  language: "en",
  painterStyle: "van_gogh"
});
const [hasServerApiKey, setHasServerApiKey] = useState(false);
const [skillText, setSkillText] = useState<string>(DEFAULT_SKILL_MD);
currentView: Determines which main view is displayed (Dashboard, Agent Studio, Document Intelligence).
apiKey:
In-memory only (never persisted to localStorage/cookies).
Override for Gemini API key when a server-side key is not available.
agents:
Initially loaded from public/agents.yaml.
Editable via Agent Studio Manage tab.
settings:
theme: applied as html.light / html.dark.
language: passed to all components to load appropriate labels.
painterStyle: drives dynamic CSS variables for WOW UI.
hasServerApiKey:
Determined by calling hasServerApiKeyAction() at runtime.
If true, UI shows that an environment key is in use and disables the plain-text API key input.
skillText:
Workspace-wide SKILL document loaded from public/SKILL.md or default.
These state values are passed down into AppShell, which further propagates them to child components as props.

6. UI & Theming
6.1 Global Layout
RootLayout (src/app/layout.tsx) provides:
HTML skeleton with lang="en".
<body> containing <ToastProvider> and the page content.
AppShell wraps the primary layout:
Left sidebar: MainSidebar
Main content: top-level container with glass background and inner content view.
6.2 Sidebar
MainSidebar responsibilities:

Navigation

Buttons for:
Dashboard (LayoutDashboard icon)
Agent Studio (Bot icon)
Document Intelligence (FileText icon)
Active view is highlighted with accent color.
API Key Input

Label: localized via LABELS.
If hasServerApiKey === true:
Input is disabled.
Placeholder shows “Using server API key”.
Text is masked as bullets.
If no server key:
User can input Gemini API key.
Eye/EyeOff button toggles visibility.
Status badge:
“Operational” (green) if env key or user key exists.
“Key Missing” (red) otherwise.
Pulsing dot indicates status.
Appearance Settings

Painter Style Select
ShadCN Select with all 20 painter styles.
“Jackpot!” button with a Dices icon selects a random style.
Theme Switch
Toggle between Light (Sun icon) and Dark (Moon icon).
Changes settings.theme and updates <html> class.
Language Switch
Toggle between EN and TC.
Changes settings.language and all labels.
6.3 WOW Theming
CSS variables defined in globals.css and overridden via PAINTER_CSS.
Body and components use the variables:
Backgrounds, foreground colors, accent colors, border color, card backgrounds.
Tailwind config uses:
fontFamily.sans → --wow-font-body
fontFamily.display → --wow-font-headline
Animated/visual polish:

.glass-panel class provides:
Border radius
Blur via backdrop-filter
Semi-transparent backgrounds
Soft drop shadow (shadow-wow-soft)
Custom scrollbars for consistent visuals.
7. Views
7.1 Dashboard
Implemented in src/components/dashboard.tsx.

Key features:

Header with API Status

Title, subtitle.
API status card with OK / Missing Key indicator.
Metrics Cards

“Total Runs”, “Active Agents”, “Avg. Latency”.
Icons from lucide-react.
Data from MOCK_METRICS.
Charts

Token Usage Trends:
LineChart (Recharts) with day vs tokens.
Wrapped in ChartContainer.
Model Distribution:
BarChart with model vs run count.
Data from MOCK_CHART_DATA.
All display-only; values are mock but the structure can be later wired to real logs.

7.2 Agent Studio
Implemented in src/components/agent-studio.tsx.
Two tabs using Tabs:

7.2.1 Run Tab
Components:

Agent Selector

Select agent by id from agents array.
UI uses localized labels.
Model Selection & Overrides

modelChoice: user chooses from a fixed set of model names (Gemini, GPT, Anthropic, Grok placeholders).
overrideModel: optional free-text input. If provided, it takes precedence.
maxTokens: numeric input (default 12000; can be adjusted per run).
Prompt / Output Panels

Left: Input Textarea for user prompt.
Right: Output card showing:
Placeholder when empty.
Loading spinner (Loader2) while waiting for response.
Output in:
Text mode (<pre>).
Markdown mode (ReactMarkdown), toggle via TXT/MD buttons.
Toolbar:
Copy output to clipboard.
“Use as next input” to set output as prompt for chaining.
Run Button

Calls generateContentAction with:
API key (from state or env)
Prompt and optional system prompt from agent
Chosen model
Max tokens
Disabled when no key is available or while request is in progress.
7.2.2 Manage Tab
Provides management for agents.yaml and SKILL.md.

Agents.yaml Panel

Editable Textarea (pre-populated via yaml.dump({ agents })).
Upload YAML:
Accepts .yml/.yaml.
Parses via js-yaml.
Normalizes to standard structure:
If root is array → treat as agents.
If root has agents array → use it.
Else treat object values as agent list.
Updates app’s agents state and UI.
If parsing fails → toast with localized message.
Download YAML:
Serializes yamlText to Blob → agents.yaml.
AI Repair:
Uses repairYamlAction, which calls Genkit repairInvalidYamlFlow.
Expects valid YAML structure in response.
Updates yamlText and app’s agents state.
SKILL.md Panel

Editable Textarea for SKILL content.
Upload SKILL:
Accepts markdown/text files.
Reads file text into skillText.
Download SKILL:
Saves current skillText as SKILL.md.
7.3 Document Intelligence
Implemented in src/components/doc-intelligence.tsx.

Modes (Tabs):

Paste Text

Textarea for arbitrary document content.
When processed, text is wrapped into a temporary .txt file and converted to a data URI.
Upload File

Card-shaped drop area:
Accepts .txt, .md, .pdf, .png, .jpg, .jpeg.
Shows Upload icon and localized prompt.
Displays file name and size once selected.
Images show image icon; others show text file icon.
File converted to data URI.
Processing Logic:

Button “Process Document”:
if mode=Paste: convert text to .txt file → data URI.
if mode=Upload: use selected file’s data URI.
Call summarizeDocumentAction with { documentDataUri }.
Output Area:

Card with:
Top toolbar:
“AI Summary” label.
Font size slider (Slider component, 11–18 px).
Textarea for output (editable).
Download buttons:
.md and .txt formats.
8. AI & Backend Logic
8.1 Genkit Configuration
src/ai/genkit.ts:

Initializes ai instance with:
googleAI({ apiKey: process.env.GOOGLE_API_KEY })
nextPlugin()
Sets defaultModel: "gemini-2.5-flash".
8.2 YAML Repair Flow
src/ai/flows/repair-invalid-yaml.ts:

Schemas using zod:
Input: { rawText: string }
Output: { repairedYaml: string }
Prompt:
Instructs the model to:
Fix invalid YAML.
Normalize to a standard agents array structure.
Return strictly valid YAML with no fences or code blocks.
Flow:
ai.defineFlow with name "repair-invalid-yaml".
Uses ai.generate with:
System message: YAML repair instructions.
User message: original text.
Returns trimmed YAML string.
8.3 Document Summarization Flow
src/ai/flows/summarize-document-intelligence.ts:

Schemas:
Input: { documentDataUri: string }
Output: { summary: string }
Prompt:
Summarize arbitrary documents into:
Overview
Key points
Risks/caveats
Suggested next steps
Flow:
ai.defineFlow with name "summarize-document-intelligence".
Uses {{media url=documentDataUri}} in the user message as Genkit/Handlebars media helper.
Returns structured summary text.
8.4 Server Actions
src/app/actions.ts contains:

generateContentAction

Parameters:
apiKey?: string
prompt: string
systemPrompt?: string
model: string
maxTokens: number
Logic:
Determine API key: params.apiKey or process.env.GOOGLE_API_KEY.
If none → error.
Create GoogleGenerativeAI client.
getGenerativeModel({ model }).
Combine systemPrompt and user prompt if both exist.
Call generateContent() with maxOutputTokens.
Return text result.
repairYamlAction

Lightweight wrapper over repairInvalidYaml(rawText) Genkit flow.
summarizeDocumentAction

Lightweight wrapper over summarizeDocumentIntelligence(documentDataUri) flow.
hasServerApiKeyAction

Returns { hasServerKey: Boolean(process.env.GOOGLE_API_KEY) }.
Used only to inform UI, never reveals key.
9. Security & Privacy
API keys

Environment variable: GOOGLE_API_KEY.
User-provided key:
Held only in React state.
Not serialized to disk, localStorage, or cookies.
Masked in input by default; Eye/EyeOff toggles visibility.
The presence of a server-side key is reported only as a boolean, never the value.
Document data

Files are read in-browser as data URIs and sent only to server actions as needed for summarization.
No persistent storage by default.
YAML & SKILL content

Kept in memory on client.
Optionally downloaded by user.
Uploaded files are parsed or read but not stored server-side.
10. Error Handling & UX
Toast notifications (via useToast) used for:
YAML load failures (fallback to defaults).
YAML parse errors.
AI repair success/failure.
Download confirmation (optional).
Loading states:
“Run Agent” button disabled when running.
Spinners displayed for AI requests in Agent Studio and Document Intelligence.
Graceful fallback:
If /agents.yaml fails to load, DEFAULT_AGENTS is used.
If /SKILL.md fails, built-in DEFAULT_SKILL_MD is used.
11. Extensibility & Future Enhancements
The system is designed with extensibility in mind:

Multi-provider support:

Currently, only the Gemini SDK is wired for actual inference.
UI already supports a set of model names across providers.
Future work:
Add OpenAI, Anthropic, Grok SDKs and route model names by prefix.
Extend Agent and UI to specify provider explicitly.
Advanced agent orchestration:

Presently, chaining is manual (use output as next input).
Future:
Visual workflow builder for multi-step pipelines.
Genkit workflows for complex orchestration.
Persistent metrics and logs:

Dashboard uses mock data now.
Future:
Instrument server actions to log usage metrics.
Back them with a database or telemetry system.
Schema-aware YAML editor:

Additional validation (e.g., with zod or JSON Schema) could provide inline errors.
User profiles and persistence:

Save settings (theme, language, painter style) per user or per browser.
Optionally sync agents.yaml and SKILL.md via remote storage.
12. Deployment Considerations
Runtime: Node.js (required for Next.js App Router and server actions).
Environment Variables:
GOOGLE_API_KEY: required for Genkit and Gemini SDK.
Static assets:
public/agents.yaml and public/SKILL.md must be deployed with the app.
Routes:
Single page routed via / (App Router), all functionality handled client-side and via server actions.
13. Summary
Artistic Intelligence Workspace v2.0 is a modular, theme-rich AI studio that:

Offers a visually distinctive, painter-inspired user experience.
Provides a multilingual interface with EN/TC switching.
Centralizes AI interaction through:
Agent Studio (run + manage agents and skills).
Document Intelligence (summarization).
Dashboard (metrics and health indicators).
Ensures security by never exposing environment API keys and avoiding client-side persistence of keys and documents.
Uses Genkit to enable structured AI flows, making it straightforward to extend capabilities and maintain consistent prompts.
This specification documents the core implementation and provides a strong foundation for extending to additional AI providers, richer orchestration, and persistent analytics.
