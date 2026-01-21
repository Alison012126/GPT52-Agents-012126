Below is a complete Next.js 15 + TypeScript implementation of **Artistic Intelligence Workspace v2.0** with:

- WOW UI (light/dark, EN/TC, 20 painter styles + Jackpot).
- WOW status indicators + interactive dashboard (Recharts).
- API key handling (use env key if present; input only if missing).
- Agent Studio with:
  - Prompt / maxTokens / model selection.
  - Run agents one-by-one.
  - Output editable and can be sent back to input (chaining).
  - Text / Markdown view toggle.
- agents.yaml + SKILL.md:
  - View, edit, upload, download.
  - Non-standard agents YAML auto-normalized.
  - AI repair of YAML via Genkit flow.
- Document Intelligence: paste/upload, summarize via Genkit.
- i18n (English / Traditional Chinese).
- Painter styles applied via CSS variables + Tailwind.

You can copy these files into a fresh Next.js App Router project.

---

## 1. `package.json`

```jsonc
{
  "name": "artistic-intelligence-workspace-v2",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "@genkit-ai/google-genai": "^1.20.0",
    "@genkit-ai/next": "^1.20.0",
    "@google/generative-ai": "^0.16.0",
    "@radix-ui/react-accordion": "^1.2.3",
    "@radix-ui/react-select": "^2.0.0",
    "@radix-ui/react-switch": "^1.0.0",
    "@radix-ui/react-tabs": "^1.0.0",
    "@radix-ui/react-toast": "^1.1.4",
    "class-variance-authority": "^0.7.1",
    "clsx": "^2.1.1",
    "genkit": "^1.20.0",
    "js-yaml": "4.1.0",
    "lucide-react": "^0.475.0",
    "next": "15.5.9",
    "react": "^19.2.1",
    "react-dom": "^19.2.1",
    "recharts": "^2.15.1",
    "tailwind-merge": "^3.0.1",
    "tailwindcss-animate": "^1.0.7",
    "react-markdown": "^9.0.1",
    "zod": "^3.24.2"
  },
  "devDependencies": {
    "@types/node": "22.10.2",
    "@types/react": "19.0.8",
    "@types/react-dom": "19.0.3",
    "autoprefixer": "10.4.20",
    "postcss": "8.5.1",
    "tailwindcss": "3.4.17",
    "typescript": "5.7.3"
  }
}
```

---

## 2. Tailwind & Global Styles

### `tailwind.config.ts`

```ts
import type { Config } from "tailwindcss";
import { fontFamily } from "tailwindcss/defaultTheme";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./src/app/**/*.{ts,tsx}",
    "./src/components/**/*.{ts,tsx}",
    "./src/hooks/**/*.{ts,tsx}",
    "./src/lib/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--wow-font-body)", ...fontFamily.sans],
        display: ["var(--wow-font-headline)", ...fontFamily.sans]
      },
      colors: {
        bg: "var(--wow-bg)",
        fg: "var(--wow-fg)",
        accent: "var(--wow-accent)",
        "accent-soft": "var(--wow-accent-soft)",
        border: "var(--wow-border)",
        card: "var(--wow-card-bg)"
      },
      borderRadius: {
        xl: "1.1rem",
        "2xl": "1.5rem"
      },
      boxShadow: {
        "wow-soft": "0 18px 40px rgba(0,0,0,0.25)"
      }
    }
  },
  plugins: [require("tailwindcss-animate")]
};
export default config;
```

### `src/app/globals.css`

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Base painter variables – overridden dynamically */
:root {
  --wow-bg: radial-gradient(circle at top left, #121826, #050816 55%, #02010a 100%);
  --wow-fg: #f9fafb;
  --wow-accent: #f97316;
  --wow-accent-soft: rgba(249, 115, 22, 0.18);
  --wow-border: rgba(148, 163, 184, 0.4);
  --wow-card-bg: rgba(15, 23, 42, 0.7);
  --wow-font-headline: system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Display",
    "Segoe UI", sans-serif;
  --wow-font-body: system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text",
    "Segoe UI", sans-serif;
}

html.light {
  color-scheme: light;
}
html.dark {
  color-scheme: dark;
}

body {
  @apply min-h-screen bg-black text-slate-100 antialiased;
  background: var(--wow-bg);
  color: var(--wow-fg);
}

/* WOW glass panels */
.glass-panel {
  @apply rounded-2xl border border-border shadow-wow-soft;
  background-color: color-mix(in srgb, var(--wow-card-bg) 80%, transparent);
  backdrop-filter: blur(24px) saturate(160%);
}

/* Headline / body fonts */
.font-headline {
  font-family: var(--wow-font-headline);
}
.font-body {
  font-family: var(--wow-font-body);
}

/* Simple scrollbar */
*::-webkit-scrollbar {
  width: 8px;
}
*::-webkit-scrollbar-thumb {
  background: rgba(148, 163, 184, 0.6);
  border-radius: 999px;
}
```

---

## 3. Lib: Types, Constants, Utils

### `src/lib/types.ts`

```ts
export type Theme = "light" | "dark";
export type Language = "en" | "tc";

export const VIEW_TYPES = ["dashboard", "agent-studio", "doc-intelligence"] as const;
export type ViewType = (typeof VIEW_TYPES)[number];

export type PainterStyle =
  | "van_gogh"
  | "monet"
  | "picasso"
  | "dali"
  | "kahlo"
  | "hokusai"
  | "turner"
  | "pollock"
  | "klimt"
  | "matisse"
  | "chagall"
  | "cezanne"
  | "rembrandt"
  | "vermeer"
  | "warhol"
  | "banksy"
  | "miro"
  | "basquiat"
  | "rothko";

export interface AppSettings {
  theme: Theme;
  language: Language;
  painterStyle: PainterStyle;
}

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

export interface AppMetrics {
  totalRuns: number;
  activeAgents: number;
  avgLatencyMs: number;
}

export type ApiStatus = "operational" | "key-missing";

export interface PainterCssVariables {
  [cssVar: string]: string;
}
```

### `src/lib/constants.ts`

```ts
import { AppMetrics, PainterCssVariables, PainterStyle, Agent } from "./types";

export const PAINTER_STYLES: PainterStyle[] = [
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
  "rothko"
];

export const PAINTER_CSS: Record<PainterStyle, PainterCssVariables> = {
  van_gogh: {
    "--wow-bg":
      "radial-gradient(circle at 0% 0%, #0f172a 0%, #020617 55%, #02010a 100%)",
    "--wow-fg": "#fefce8",
    "--wow-accent": "#facc15",
    "--wow-accent-soft": "rgba(250, 204, 21, 0.2)",
    "--wow-border": "rgba(148, 163, 184, 0.5)",
    "--wow-card-bg": "rgba(15, 23, 42, 0.85)",
    "--wow-font-headline": '"Playfair Display", system-ui, serif',
    "--wow-font-body": '"Inter", system-ui, sans-serif'
  },
  monet: {
    "--wow-bg":
      "radial-gradient(circle at 10% 0%, #0f172a 0%, #1d3557 35%, #020617 100%)",
    "--wow-fg": "#f9fafb",
    "--wow-accent": "#38bdf8",
    "--wow-accent-soft": "rgba(56, 189, 248, 0.22)",
    "--wow-border": "rgba(148, 163, 184, 0.5)",
    "--wow-card-bg": "rgba(15, 23, 42, 0.84)",
    "--wow-font-headline": '"DM Serif Display", system-ui, serif',
    "--wow-font-body": '"Inter", system-ui, sans-serif'
  },
  picasso: {
    "--wow-bg":
      "radial-gradient(circle at 0 0, #020617 0%, #0b1120 30%, #1e293b 80%)",
    "--wow-fg": "#e5e7eb",
    "--wow-accent": "#fb7185",
    "--wow-accent-soft": "rgba(251, 113, 133, 0.22)",
    "--wow-border": "rgba(148, 163, 184, 0.55)",
    "--wow-card-bg": "rgba(15, 23, 42, 0.9)",
    "--wow-font-headline": '"Space Grotesk", system-ui, sans-serif',
    "--wow-font-body": '"Inter", system-ui, sans-serif'
  },
  dali: {
    "--wow-bg":
      "radial-gradient(circle at 100% 0%, #020617 0%, #0f172a 35%, #581c87 100%)",
    "--wow-fg": "#f9fafb",
    "--wow-accent": "#a855f7",
    "--wow-accent-soft": "rgba(168, 85, 247, 0.2)",
    "--wow-border": "rgba(148, 163, 184, 0.55)",
    "--wow-card-bg": "rgba(15, 23, 42, 0.88)",
    "--wow-font-headline": '"DM Sans", system-ui, sans-serif',
    "--wow-font-body": '"Inter", system-ui, sans-serif'
  },
  kahlo: {
    "--wow-bg":
      "radial-gradient(circle at 0% 0%, #020617 0%, #14532d 40%, #020617 100%)",
    "--wow-fg": "#ecfdf3",
    "--wow-accent": "#22c55e",
    "--wow-accent-soft": "rgba(34, 197, 94, 0.23)",
    "--wow-border": "rgba(74, 222, 128, 0.5)",
    "--wow-card-bg": "rgba(5, 46, 22, 0.9)",
    "--wow-font-headline": '"Playfair Display", system-ui, serif',
    "--wow-font-body": '"Inter", system-ui, sans-serif'
  },
  hokusai: {
    "--wow-bg":
      "radial-gradient(circle at 10% 0%, #0b1120 0%, #075985 40%, #020617 100%)",
    "--wow-fg": "#e5f2ff",
    "--wow-accent": "#38bdf8",
    "--wow-accent-soft": "rgba(56, 189, 248, 0.26)",
    "--wow-border": "rgba(125, 211, 252, 0.6)",
    "--wow-card-bg": "rgba(15, 23, 42, 0.9)",
    "--wow-font-headline": '"Noto Serif JP", system-ui, serif',
    "--wow-font-body": '"Noto Sans JP", system-ui, sans-serif'
  },
  turner: {
    "--wow-bg":
      "radial-gradient(circle at 0% 100%, #0f172a 0%, #ca8a04 40%, #020617 100%)",
    "--wow-fg": "#fef9c3",
    "--wow-accent": "#facc15",
    "--wow-accent-soft": "rgba(250, 204, 21, 0.26)",
    "--wow-border": "rgba(250, 204, 21, 0.5)",
    "--wow-card-bg": "rgba(15, 23, 42, 0.9)",
    "--wow-font-headline": '"DM Serif Display", system-ui, serif',
    "--wow-font-body": '"Inter", system-ui, sans-serif'
  },
  pollock: {
    "--wow-bg":
      "radial-gradient(circle at 50% 0%, #020617 0%, #111827 45%, #000000 100%)",
    "--wow-fg": "#f9fafb",
    "--wow-accent": "#f97316",
    "--wow-accent-soft": "rgba(249, 115, 22, 0.3)",
    "--wow-border": "rgba(148, 163, 184, 0.6)",
    "--wow-card-bg": "rgba(15, 23, 42, 0.95)",
    "--wow-font-headline": '"Space Grotesk", system-ui, sans-serif',
    "--wow-font-body": '"Inter", system-ui, sans-serif'
  },
  klimt: {
    "--wow-bg":
      "radial-gradient(circle at 0% 0%, #0f172a 0%, #92400e 50%, #020617 100%)",
    "--wow-fg": "#fefce8",
    "--wow-accent": "#facc15",
    "--wow-accent-soft": "rgba(250, 204, 21, 0.28)",
    "--wow-border": "rgba(253, 224, 71, 0.6)",
    "--wow-card-bg": "rgba(24, 16, 7, 0.9)",
    "--wow-font-headline": '"Playfair Display", system-ui, serif',
    "--wow-font-body": '"Inter", system-ui, sans-serif'
  },
  matisse: {
    "--wow-bg":
      "radial-gradient(circle at 100% 0%, #0f172a 0%, #1d4ed8 40%, #020617 100%)",
    "--wow-fg": "#eff6ff",
    "--wow-accent": "#fb7185",
    "--wow-accent-soft": "rgba(251, 113, 133, 0.25)",
    "--wow-border": "rgba(191, 219, 254, 0.7)",
    "--wow-card-bg": "rgba(15, 23, 42, 0.9)",
    "--wow-font-headline": '"DM Sans", system-ui, sans-serif',
    "--wow-font-body": '"Inter", system-ui, sans-serif'
  },
  chagall: {
    "--wow-bg":
      "radial-gradient(circle at 0% 0%, #020617 0%, #1d4ed8 35%, #4c1d95 100%)",
    "--wow-fg": "#e5e7eb",
    "--wow-accent": "#a855f7",
    "--wow-accent-soft": "rgba(168, 85, 247, 0.25)",
    "--wow-border": "rgba(191, 219, 254, 0.6)",
    "--wow-card-bg": "rgba(15, 23, 42, 0.92)",
    "--wow-font-headline": '"DM Serif Display", system-ui, serif',
    "--wow-font-body": '"Inter", system-ui, sans-serif'
  },
  cezanne: {
    "--wow-bg":
      "radial-gradient(circle at 0% 0%, #0f172a 0%, #0369a1 35%, #0f172a 100%)",
    "--wow-fg": "#e5f2ff",
    "--wow-accent": "#22c55e",
    "--wow-accent-soft": "rgba(34, 197, 94, 0.23)",
    "--wow-border": "rgba(125, 211, 252, 0.6)",
    "--wow-card-bg": "rgba(15, 23, 42, 0.9)",
    "--wow-font-headline": '"DM Sans", system-ui, sans-serif',
    "--wow-font-body": '"Inter", system-ui, sans-serif'
  },
  rembrandt: {
    "--wow-bg":
      "radial-gradient(circle at 0% 100%, #020617 0%, #1f2937 40%, #000000 100%)",
    "--wow-fg": "#f9fafb",
    "--wow-accent": "#f97316",
    "--wow-accent-soft": "rgba(249, 115, 22, 0.2)",
    "--wow-border": "rgba(156, 163, 175, 0.6)",
    "--wow-card-bg": "rgba(15, 23, 42, 0.95)",
    "--wow-font-headline": '"Playfair Display", system-ui, serif',
    "--wow-font-body": '"Inter", system-ui, sans-serif'
  },
  vermeer: {
    "--wow-bg":
      "radial-gradient(circle at 100% 0%, #020617 0%, #0ea5e9 40%, #050816 100%)",
    "--wow-fg": "#f9fafb",
    "--wow-accent": "#facc15",
    "--wow-accent-soft": "rgba(250, 204, 21, 0.22)",
    "--wow-border": "rgba(125, 211, 252, 0.6)",
    "--wow-card-bg": "rgba(15, 23, 42, 0.92)",
    "--wow-font-headline": '"DM Serif Display", system-ui, serif',
    "--wow-font-body": '"Inter", system-ui, sans-serif'
  },
  warhol: {
    "--wow-bg":
      "radial-gradient(circle at 0% 0%, #0f172a 0%, #e11d48 35%, #4f46e5 100%)",
    "--wow-fg": "#fdf2f8",
    "--wow-accent": "#22c55e",
    "--wow-accent-soft": "rgba(34, 197, 94, 0.25)",
    "--wow-border": "rgba(248, 250, 252, 0.7)",
    "--wow-card-bg": "rgba(15, 23, 42, 0.9)",
    "--wow-font-headline": '"Space Grotesk", system-ui, sans-serif',
    "--wow-font-body": '"Inter", system-ui, sans-serif'
  },
  banksy: {
    "--wow-bg":
      "radial-gradient(circle at 0% 0%, #020617 0%, #111827 40%, #000000 100%)",
    "--wow-fg": "#f9fafb",
    "--wow-accent": "#ef4444",
    "--wow-accent-soft": "rgba(239, 68, 68, 0.3)",
    "--wow-border": "rgba(156, 163, 175, 0.7)",
    "--wow-card-bg": "rgba(15, 23, 42, 0.95)",
    "--wow-font-headline": '"Space Grotesk", system-ui, sans-serif',
    "--wow-font-body": '"Inter", system-ui, sans-serif'
  },
  miro: {
    "--wow-bg":
      "radial-gradient(circle at 100% 0%, #0f172a 0%, #1d4ed8 40%, #6d28d9 100%)",
    "--wow-fg": "#eff6ff",
    "--wow-accent": "#f97316",
    "--wow-accent-soft": "rgba(249, 115, 22, 0.24)",
    "--wow-border": "rgba(191, 219, 254, 0.7)",
    "--wow-card-bg": "rgba(15, 23, 42, 0.9)",
    "--wow-font-headline": '"DM Sans", system-ui, sans-serif',
    "--wow-font-body": '"Inter", system-ui, sans-serif'
  },
  basquiat: {
    "--wow-bg":
      "radial-gradient(circle at 0% 0%, #020617 0%, #1f2937 35%, #111827 100%)",
    "--wow-fg": "#f9fafb",
    "--wow-accent": "#facc15",
    "--wow-accent-soft": "rgba(250, 204, 21, 0.28)",
    "--wow-border": "rgba(148, 163, 184, 0.7)",
    "--wow-card-bg": "rgba(15, 23, 42, 0.95)",
    "--wow-font-headline": '"Space Grotesk", system-ui, sans-serif',
    "--wow-font-body": '"Inter", system-ui, sans-serif'
  },
  rothko: {
    "--wow-bg":
      "radial-gradient(circle at 50% 0%, #0f172a 0%, #7c2d12 35%, #111827 100%)",
    "--wow-fg": "#fef9c3",
    "--wow-accent": "#f97316",
    "--wow-accent-soft": "rgba(249, 115, 22, 0.3)",
    "--wow-border": "rgba(253, 224, 71, 0.7)",
    "--wow-card-bg": "rgba(24, 16, 7, 0.92)",
    "--wow-font-headline": '"DM Serif Display", system-ui, serif',
    "--wow-font-body": '"Inter", system-ui, sans-serif'
  }
};

/** UI Labels (EN + Traditional Chinese) */
export const LABELS = {
  en: {
    appTitle: "Artistic Intelligence Workspace v2.0",
    sidebar: {
      dashboard: "Dashboard",
      agentStudio: "Agent Studio",
      docIntelligence: "Document Intelligence",
      apiKeyLabel: "Gemini API Key",
      apiStatusOperational: "Operational",
      apiStatusMissing: "Key Missing",
      appearance: "Appearance",
      painterStyle: "Painter Style",
      jackpot: "Jackpot!",
      theme: "Theme",
      light: "Light",
      dark: "Dark",
      language: "Language",
      en: "EN",
      tc: "TC"
    },
    dashboard: {
      title: "Control Center",
      totalRuns: "Total Runs",
      activeAgents: "Active Agents",
      avgLatency: "Avg. Latency",
      tokenTrends: "Token Usage Trends",
      modelDistribution: "Model Distribution",
      apiStatus: "API Status"
    },
    agentStudio: {
      title: "Agent Studio",
      runTab: "Run",
      manageTab: "Manage",
      selectAgent: "Select Agent",
      overrideModel: "Override model (optional)",
      modelSelectPlaceholder: "Select model",
      maxTokens: "Max tokens",
      promptPlaceholder: "Type your prompt...",
      runAgent: "Run Agent",
      running: "Running...",
      copy: "Copy",
      copied: "Copied",
      outputPlaceholder: "Agent output will appear here.",
      useAsInput: "Use as next input",
      viewModeText: "Text view",
      viewModeMarkdown: "Markdown view",
      manageYamlTitle: "Agents.yaml",
      manageSkillTitle: "SKILL.md",
      uploadYaml: "Upload YAML",
      downloadYaml: "Download YAML",
      aiRepair: "AI Repair",
      uploadSkill: "Upload SKILL.md",
      downloadSkill: "Download SKILL.md"
    },
    docIntelligence: {
      title: "Document Intelligence",
      pasteTab: "Paste Text",
      uploadTab: "Upload File",
      pastePlaceholder: "Paste or type your document content here...",
      dropPrompt: "Click or drop a document (txt, md, pdf, png, jpg)",
      outputTitle: "AI Summary",
      process: "Process Document",
      downloadMd: "Download .md",
      downloadTxt: "Download .txt",
      fontSize: "Font size"
    },
    toasts: {
      yamlLoadError: "Failed to load agents.yaml. Using defaults.",
      yamlParseError: "Invalid YAML. Please repair or use AI Repair.",
      yamlRepaired: "YAML repaired successfully.",
      yamlDownloaded: "agents.yaml downloaded.",
      skillDownloaded: "SKILL.md downloaded."
    }
  },
  tc: {
    appTitle: "藝術智慧工作室 v2.0",
    sidebar: {
      dashboard: "總覽儀表板",
      agentStudio: "代理工作室",
      docIntelligence: "文件智慧",
      apiKeyLabel: "Gemini API 金鑰",
      apiStatusOperational: "運作中",
      apiStatusMissing: "尚未設定金鑰",
      appearance: "外觀設定",
      painterStyle: "畫家風格主題",
      jackpot: "隨機驚喜！",
      theme: "主題模式",
      light: "亮色",
      dark: "深色",
      language: "語言",
      en: "英",
      tc: "繁"
    },
    dashboard: {
      title: "控制中心",
      totalRuns: "總執行次數",
      activeAgents: "啟用代理數",
      avgLatency: "平均延遲",
      tokenTrends: "Token 使用趨勢",
      modelDistribution: "模型使用分佈",
      apiStatus: "API 狀態"
    },
    agentStudio: {
      title: "代理工作室",
      runTab: "執行",
      manageTab: "管理",
      selectAgent: "選擇代理",
      overrideModel: "覆寫模型（選填）",
      modelSelectPlaceholder: "選擇模型",
      maxTokens: "最大 Token 數",
      promptPlaceholder: "在此輸入提示...",
      runAgent: "執行代理",
      running: "執行中...",
      copy: "複製",
      copied: "已複製",
      outputPlaceholder: "代理輸出將顯示於此。",
      useAsInput: "作為下一個輸入",
      viewModeText: "文字檢視",
      viewModeMarkdown: "Markdown 檢視",
      manageYamlTitle: "Agents.yaml",
      manageSkillTitle: "SKILL.md",
      uploadYaml: "上傳 YAML",
      downloadYaml: "下載 YAML",
      aiRepair: "AI 修復",
      uploadSkill: "上傳 SKILL.md",
      downloadSkill: "下載 SKILL.md"
    },
    docIntelligence: {
      title: "文件智慧",
      pasteTab: "貼上文字",
      uploadTab: "上傳檔案",
      pastePlaceholder: "在此貼上或輸入文件內容...",
      dropPrompt: "點擊或拖曳文件（txt, md, pdf, png, jpg）",
      outputTitle: "AI 摘要",
      process: "處理文件",
      downloadMd: "下載 .md",
      downloadTxt: "下載 .txt",
      fontSize: "字體大小"
    },
    toasts: {
      yamlLoadError: "讀取 agents.yaml 失敗，已載入預設設定。",
      yamlParseError: "YAML 格式錯誤，請修正或使用 AI 修復。",
      yamlRepaired: "YAML 修復成功。",
      yamlDownloaded: "agents.yaml 已下載。",
      skillDownloaded: "SKILL.md 已下載。"
    }
  }
};

/** Mock metrics & chart data */
export const MOCK_METRICS: AppMetrics = {
  totalRuns: 1289,
  activeAgents: 7,
  avgLatencyMs: 1432
};

export const MOCK_CHART_DATA = {
  tokenTrends: [
    { day: "Mon", tokens: 12000 },
    { day: "Tue", tokens: 18500 },
    { day: "Wed", tokens: 16200 },
    { day: "Thu", tokens: 23400 },
    { day: "Fri", tokens: 29120 },
    { day: "Sat", tokens: 15210 },
    { day: "Sun", tokens: 19875 }
  ],
  modelDistribution: [
    { model: "gemini-2.5-flash", runs: 420 },
    { model: "gemini-3-pro-preview", runs: 180 },
    { model: "gpt-4o-mini", runs: 230 },
    { model: "gpt-4.1-mini", runs: 145 },
    { model: "anthropic", runs: 110 },
    { model: "grok", runs: 75 }
  ]
};

/** Default advanced agents – used if /agents.yaml fails to load */
export const DEFAULT_AGENTS: Agent[] = [
  {
    id: "creative-writer",
    name: "Creative Writer",
    description: "Long-form creative writing with painterly metaphors.",
    model: "gemini-2.5-flash",
    maxTokens: 8000,
    temperature: 0.9,
    systemPrompt:
      "You are a world-class creative writer who uses imagery inspired by classic painters, while remaining precise and concise on request."
  },
  {
    id: "yaml-architect",
    name: "YAML Architect",
    description: "Designs and validates complex agents.yaml configurations.",
    model: "gemini-2.5-flash",
    maxTokens: 6000,
    temperature: 0.4,
    systemPrompt:
      "You are an expert in YAML schemas for multi-agent systems. Produce strictly valid, standardized agents.yaml structures."
  },
  {
    id: "doc-summarizer",
    name: "Document Summarizer",
    description: "Summarizes long documents into concise briefs.",
    model: "gemini-2.5-flash",
    maxTokens: 4000,
    temperature: 0.3,
    systemPrompt:
      "You create faithful, structured summaries (overview, key points, risks, next steps)."
  },
  {
    id: "code-assistant",
    name: "Code Assistant",
    description: "Multi-language code assistant focused on safety and clarity.",
    model: "gemini-2.5-flash",
    maxTokens: 12000,
    temperature: 0.45,
    systemPrompt:
      "You are a senior software engineer. Prefer step-by-step reasoning, explicit tradeoffs, and production-ready examples."
  }
];
```

### `src/lib/utils.ts`

```ts
import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function fileToDataUri(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = (e) => reject(e);
    reader.readAsDataURL(file);
  });
}
```

---

## 4. Hooks

### `src/hooks/use-mobile.tsx`

```tsx
"use client";

import { useEffect, useState } from "react";

export function useIsMobile(breakpoint = 768) {
  const [isMobile, setIsMobile] = useState(false);
  useEffect(() => {
    const update = () => setIsMobile(window.innerWidth < breakpoint);
    update();
    window.addEventListener("resize", update);
    return () => window.removeEventListener("resize", update);
  }, [breakpoint]);
  return isMobile;
}
```

### `src/hooks/use-toast.ts`

(ShadCN-style lightweight toast implementation)

```tsx
"use client";

import * as React from "react";
import * as ToastPrimitive from "@radix-ui/react-toast";
import { cn } from "@/lib/utils";

type ToastVariant = "default" | "destructive" | "success";

export interface Toast {
  id: string;
  title?: string;
  description?: string;
  variant?: ToastVariant;
}

type ToastContextValue = {
  toast: (t: Omit<Toast, "id">) => void;
};

const ToastContext = React.createContext<ToastContextValue | undefined>(
  undefined
);

export const useToast = () => {
  const ctx = React.useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used within ToastProvider");
  return ctx;
};

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = React.useState<Toast[]>([]);

  const toast = React.useCallback((t: Omit<Toast, "id">) => {
    const id = crypto.randomUUID();
    setToasts((current) => [...current, { id, ...t }]);
  }, []);

  return (
    <ToastContext.Provider value={{ toast }}>
      <ToastPrimitive.Provider>
        {children}
        <div className="fixed inset-x-0 bottom-0 z-50 flex flex-col items-center gap-2 pb-6">
          {toasts.map((t) => (
            <ToastPrimitive.Root
              key={t.id}
              duration={3500}
              className={cn(
                "glass-panel flex min-w-[260px] items-start gap-3 px-4 py-3 text-sm",
                t.variant === "destructive" && "border-red-500/60 text-red-100",
                t.variant === "success" && "border-emerald-500/60 text-emerald-50"
              )}
              onOpenChange={(open) => {
                if (!open) {
                  setToasts((prev) => prev.filter((x) => x.id !== t.id));
                }
              }}
            >
              <div className="flex flex-1 flex-col">
                {t.title && (
                  <ToastPrimitive.Title className="font-medium">
                    {t.title}
                  </ToastPrimitive.Title>
                )}
                {t.description && (
                  <ToastPrimitive.Description className="text-xs text-slate-200/80">
                    {t.description}
                  </ToastPrimitive.Description>
                )}
              </div>
            </ToastPrimitive.Root>
          ))}
        </div>
      </ToastPrimitive.Provider>
    </ToastContext.Provider>
  );
}
```

---

## 5. UI Primitives (ShadCN-style)

### `src/components/ui/button.tsx`

```tsx
"use client";

import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-xl px-4 py-2 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-60 ring-offset-slate-950",
  {
    variants: {
      variant: {
        default:
          "bg-accent text-slate-950 hover:bg-amber-400 focus-visible:ring-accent",
        outline:
          "border border-border/70 bg-card/40 text-fg hover:bg-accent-soft/30",
        ghost: "text-fg/80 hover:bg-accent-soft/20",
        subtle: "bg-accent-soft/30 text-fg hover:bg-accent-soft/60"
      },
      size: {
        default: "h-9 px-4 py-2",
        sm: "h-8 rounded-lg px-3 text-xs",
        lg: "h-11 rounded-xl px-5 text-base",
        icon: "h-9 w-9"
      }
    },
    defaultVariants: {
      variant: "default",
      size: "default"
    }
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";
```

### `src/components/ui/card.tsx`

```tsx
"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

export function Card({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("glass-panel p-4", className)} {...props} />;
}
```

### `src/components/ui/input.tsx`

```tsx
"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, ...props }, ref) => (
    <input
      ref={ref}
      className={cn(
        "flex h-9 w-full rounded-xl border border-border/80 bg-slate-900/50 px-3 text-sm text-fg shadow-sm outline-none placeholder:text-slate-400 focus-visible:ring-2 focus-visible:ring-accent",
        className
      )}
      {...props}
    />
  )
);
Input.displayName = "Input";
```

### `src/components/ui/textarea.tsx`

```tsx
"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

export interface TextareaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {}

export const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, ...props }, ref) => (
    <textarea
      ref={ref}
      className={cn(
        "flex min-h-[120px] w-full rounded-xl border border-border/80 bg-slate-900/40 px-3 py-2 text-sm text-fg shadow-sm outline-none placeholder:text-slate-400 focus-visible:ring-2 focus-visible:ring-accent",
        className
      )}
      {...props}
    />
  )
);
Textarea.displayName = "Textarea";
```

### `src/components/ui/select.tsx`

```tsx
"use client";

import * as React from "react";
import * as RadixSelect from "@radix-ui/react-select";
import { ChevronDown, Check } from "lucide-react";
import { cn } from "@/lib/utils";

export const Select = RadixSelect.Root;
export const SelectValue = RadixSelect.Value;

export function SelectTrigger({
  className,
  children,
  ...props
}: React.ComponentPropsWithoutRef<typeof RadixSelect.Trigger>) {
  return (
    <RadixSelect.Trigger
      className={cn(
        "flex h-9 w-full items-center justify-between rounded-xl border border-border/80 bg-slate-900/50 px-3 text-sm text-fg shadow-sm outline-none focus-visible:ring-2 focus-visible:ring-accent",
        className
      )}
      {...props}
    >
      {children}
      <RadixSelect.Icon>
        <ChevronDown className="h-4 w-4 opacity-70" />
      </RadixSelect.Icon>
    </RadixSelect.Trigger>
  );
}

export function SelectContent({
  className,
  ...props
}: React.ComponentPropsWithoutRef<typeof RadixSelect.Content>) {
  return (
    <RadixSelect.Portal>
      <RadixSelect.Content
        className={cn(
          "z-50 overflow-hidden rounded-xl border border-border/70 bg-slate-900/95 text-xs shadow-lg",
          className
        )}
        {...props}
      >
        <RadixSelect.Viewport className="p-1">
          {props.children}
        </RadixSelect.Viewport>
      </RadixSelect.Content>
    </RadixSelect.Portal>
  );
}

export function SelectItem({
  className,
  children,
  ...props
}: React.ComponentPropsWithoutRef<typeof RadixSelect.Item>) {
  return (
    <RadixSelect.Item
      className={cn(
        "relative flex cursor-pointer select-none items-center rounded-lg px-2 py-1.5 text-xs text-slate-100 outline-none data-[highlighted]:bg-accent-soft/60",
        className
      )}
      {...props}
    >
      <RadixSelect.ItemText>{children}</RadixSelect.ItemText>
      <RadixSelect.ItemIndicator className="absolute right-2">
        <Check className="h-3 w-3" />
      </RadixSelect.ItemIndicator>
    </RadixSelect.Item>
  );
}
```

### `src/components/ui/tabs.tsx`

```tsx
"use client";

import * as TabsPrimitive from "@radix-ui/react-tabs";
import { cn } from "@/lib/utils";

export const Tabs = TabsPrimitive.Root;

export function TabsList({
  className,
  ...props
}: React.ComponentPropsWithoutRef<typeof TabsPrimitive.List>) {
  return (
    <TabsPrimitive.List
      className={cn(
        "inline-flex h-9 items-center justify-center gap-1 rounded-full bg-slate-900/60 p-1 text-xs",
        className
      )}
      {...props}
    />
  );
}

export function TabsTrigger({
  className,
  ...props
}: React.ComponentPropsWithoutRef<typeof TabsPrimitive.Trigger>) {
  return (
    <TabsPrimitive.Trigger
      className={cn(
        "inline-flex min-w-[80px] items-center justify-center rounded-full px-3 py-1 text-xs font-medium text-slate-300 ring-offset-slate-950 transition-colors data-[state=active]:bg-accent data-[state=active]:text-slate-950",
        className
      )}
      {...props}
    />
  );
}

export function TabsContent({
  className,
  ...props
}: React.ComponentPropsWithoutRef<typeof TabsPrimitive.Content>) {
  return (
    <TabsPrimitive.Content
      className={cn("mt-3 focus-visible:outline-none", className)}
      {...props}
    />
  );
}
```

### `src/components/ui/switch.tsx`

```tsx
"use client";

import * as React from "react";
import * as SwitchPrimitives from "@radix-ui/react-switch";
import { cn } from "@/lib/utils";

export const Switch = React.forwardRef<
  React.ElementRef<typeof SwitchPrimitives.Root>,
  React.ComponentPropsWithoutRef<typeof SwitchPrimitives.Root>
>(({ className, ...props }, ref) => (
  <SwitchPrimitives.Root
    ref={ref}
    className={cn(
      "peer inline-flex h-5 w-9 items-center rounded-full border border-border/80 bg-slate-900/80 transition-colors data-[state=checked]:bg-accent",
      className
    )}
    {...props}
  >
    <SwitchPrimitives.Thumb
      className={cn(
        "block h-4 w-4 translate-x-0 rounded-full bg-slate-300 shadow-lg transition-transform data-[state=checked]:translate-x-4 data-[state=checked]:bg-slate-950"
      )}
    />
  </SwitchPrimitives.Root>
));
Switch.displayName = "Switch";
```

### `src/components/ui/badge.tsx`

```tsx
"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

export function Badge({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "inline-flex items-center gap-1 rounded-full bg-slate-900/70 px-2.5 py-0.5 text-xs font-medium",
        className
      )}
      {...props}
    />
  );
}
```

### `src/components/ui/slider.tsx`

```tsx
"use client";

import * as SliderPrimitive from "@radix-ui/react-slider";
import { cn } from "@/lib/utils";

export function Slider({
  className,
  ...props
}: SliderPrimitive.SliderProps) {
  return (
    <SliderPrimitive.Root
      className={cn(
        "relative flex w-full touch-none select-none items-center",
        className
      )}
      {...props}
    >
      <SliderPrimitive.Track className="relative h-1 flex-1 rounded-full bg-slate-700">
        <SliderPrimitive.Range className="absolute h-full rounded-full bg-accent" />
      </SliderPrimitive.Track>
      <SliderPrimitive.Thumb className="block h-4 w-4 rounded-full border border-slate-900 bg-slate-100 shadow" />
    </SliderPrimitive.Root>
  );
}
```

### `src/components/ui/chart-container.tsx`

```tsx
"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

export function ChartContainer({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "glass-panel flex h-[260px] flex-col overflow-hidden p-4",
        className
      )}
      {...props}
    />
  );
}
```

---

## 6. Sidebar / App Shell / Views

### `src/components/main-sidebar.tsx`

```tsx
"use client";

import { useState } from "react";
import {
  LayoutDashboard,
  Bot,
  FileText,
  Eye,
  EyeOff,
  Sun,
  Moon,
  Dices
} from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Badge } from "./ui/badge";
import { Switch } from "./ui/switch";
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from "./ui/select";
import { AppSettings, ViewType } from "@/lib/types";
import { LABELS, PAINTER_STYLES } from "@/lib/constants";

interface MainSidebarProps {
  currentView: ViewType;
  onChangeView: (view: ViewType) => void;
  apiKey: string;
  setApiKey: (key: string) => void;
  settings: AppSettings;
  setSettings: (settings: AppSettings) => void;
  hasServerApiKey: boolean;
  language: "en" | "tc";
}

export function MainSidebar({
  currentView,
  onChangeView,
  apiKey,
  setApiKey,
  settings,
  setSettings,
  hasServerApiKey,
  language
}: MainSidebarProps) {
  const [showKey, setShowKey] = useState(false);
  const labels = LABELS[language];

  const apiOperational = hasServerApiKey || !!apiKey;

  function randomPainter() {
    const idx = Math.floor(Math.random() * PAINTER_STYLES.length);
    setSettings({ ...settings, painterStyle: PAINTER_STYLES[idx] });
  }

  return (
    <aside className="flex h-full w-[280px] flex-col border-r border-border/60 bg-slate-950/80 px-3 py-4">
      <div className="flex items-center justify-between px-1 pb-4">
        <div className="flex flex-col">
          <span className="font-headline text-sm font-semibold tracking-tight">
            {labels.appTitle}
          </span>
          <span className="text-[10px] text-slate-400">
            Artistic Intelligence Workspace
          </span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="mb-4 flex flex-col gap-1">
        <SidebarNavItem
          label={labels.sidebar.dashboard}
          icon={<LayoutDashboard className="h-4 w-4" />}
          active={currentView === "dashboard"}
          onClick={() => onChangeView("dashboard")}
        />
        <SidebarNavItem
          label={labels.sidebar.agentStudio}
          icon={<Bot className="h-4 w-4" />}
          active={currentView === "agent-studio"}
          onClick={() => onChangeView("agent-studio")}
        />
        <SidebarNavItem
          label={labels.sidebar.docIntelligence}
          icon={<FileText className="h-4 w-4" />}
          active={currentView === "doc-intelligence"}
          onClick={() => onChangeView("doc-intelligence")}
        />
      </nav>

      {/* API key */}
      <div className="mb-4 space-y-1">
        <div className="flex items-center justify-between text-[11px] text-slate-400">
          <span>{labels.sidebar.apiKeyLabel}</span>
          {hasServerApiKey && (
            <span className="text-emerald-400/90">env</span>
          )}
        </div>

        <div className="flex items-center gap-1">
          <Input
            disabled={hasServerApiKey}
            type={showKey ? "text" : "password"}
            placeholder={
              hasServerApiKey ? "Using server API key" : "Paste Gemini API key"
            }
            value={hasServerApiKey ? "••••••••••••••" : apiKey}
            onChange={(e) => !hasServerApiKey && setApiKey(e.target.value)}
          />
          {!hasServerApiKey && (
            <Button
              type="button"
              variant="ghost"
              size="icon"
              onClick={() => setShowKey((v) => !v)}
            >
              {showKey ? (
                <EyeOff className="h-4 w-4" />
              ) : (
                <Eye className="h-4 w-4" />
              )}
            </Button>
          )}
        </div>

        <Badge
          className={
            apiOperational
              ? "bg-emerald-500/15 text-emerald-300"
              : "bg-red-500/10 text-red-300"
          }
        >
          <span
            className={`inline-block h-1.5 w-1.5 rounded-full ${
              apiOperational ? "bg-emerald-400" : "bg-red-400"
            } animate-pulse`}
          />
          <span className="text-[10px] uppercase tracking-wide">
            {apiOperational
              ? labels.sidebar.apiStatusOperational
              : labels.sidebar.apiStatusMissing}
          </span>
        </Badge>
      </div>

      {/* Appearance */}
      <div className="flex-1 space-y-3 border-t border-border/60 pt-3 text-[11px] text-slate-300">
        <div className="font-medium tracking-wide">
          {labels.sidebar.appearance}
        </div>

        {/* Painter Style */}
        <div className="space-y-1">
          <div className="flex items-center justify-between">
            <span>{labels.sidebar.painterStyle}</span>
            <Button
              size="sm"
              variant="ghost"
              className="h-7 px-2 text-[10px]"
              onClick={randomPainter}
            >
              <Dices className="mr-1 h-3 w-3" />
              {labels.sidebar.jackpot}
            </Button>
          </div>
          <Select
            value={settings.painterStyle}
            onValueChange={(val) =>
              setSettings({ ...settings, painterStyle: val as any })
            }
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {PAINTER_STYLES.map((style) => (
                <SelectItem key={style} value={style}>
                  {style.replace("_", " ")}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Theme */}
        <div className="flex items-center justify-between pt-1">
          <div className="flex items-center gap-1">
            {settings.theme === "dark" ? (
              <Moon className="h-3.5 w-3.5 text-slate-200" />
            ) : (
              <Sun className="h-3.5 w-3.5 text-amber-300" />
            )}
            <span>{labels.sidebar.theme}</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-[10px] text-slate-400">
              {settings.theme === "light"
                ? labels.sidebar.light
                : labels.sidebar.dark}
            </span>
            <Switch
              checked={settings.theme === "dark"}
              onCheckedChange={(checked) =>
                setSettings({ ...settings, theme: checked ? "dark" : "light" })
              }
            />
          </div>
        </div>

        {/* Language */}
        <div className="flex items-center justify-between pt-1">
          <span>{labels.sidebar.language}</span>
          <div className="flex items-center gap-1">
            <span className="text-[10px] text-slate-400">
              {settings.language === "en"
                ? labels.sidebar.en
                : labels.sidebar.tc}
            </span>
            <Switch
              checked={settings.language === "tc"}
              onCheckedChange={(checked) =>
                setSettings({ ...settings, language: checked ? "tc" : "en" })
              }
            />
          </div>
        </div>
      </div>
    </aside>
  );
}

function SidebarNavItem({
  label,
  icon,
  active,
  onClick
}: {
  label: string;
  icon: React.ReactNode;
  active?: boolean;
  onClick?: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={
        "flex items-center gap-2 rounded-xl px-2.5 py-1.5 text-xs font-medium transition-colors " +
        (active
          ? "bg-accent text-slate-950"
          : "text-slate-300 hover:bg-accent-soft/40")
      }
    >
      <span className="flex h-6 w-6 items-center justify-center rounded-lg bg-slate-900/60">
        {icon}
      </span>
      <span>{label}</span>
    </button>
  );
}
```

### `src/components/dashboard.tsx`

```tsx
"use client";

import { Card } from "./ui/card";
import { ChartContainer } from "./ui/chart-container";
import { LABELS, MOCK_CHART_DATA, MOCK_METRICS } from "@/lib/constants";
import { Language, ApiStatus } from "@/lib/types";
import {
  Activity,
  Gauge,
  Timer,
  CheckCircle2,
  AlertTriangle
} from "lucide-react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar
} from "recharts";

interface DashboardProps {
  language: Language;
  apiStatus: ApiStatus;
}

export function Dashboard({ language, apiStatus }: DashboardProps) {
  const labels = LABELS[language];
  const { tokenTrends, modelDistribution } = MOCK_CHART_DATA;

  return (
    <div className="flex h-full flex-col gap-4">
      {/* Header + API status */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="font-headline text-xl font-semibold">
            {labels.dashboard.title}
          </h1>
          <p className="text-xs text-slate-300/80">
            Real-time overview of your artistic AI workspace.
          </p>
        </div>
        <Card className="flex items-center gap-2 px-3 py-2 text-xs">
          <span className="text-slate-300/90">{labels.dashboard.apiStatus}</span>
          <span
            className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 ${
              apiStatus === "operational"
                ? "bg-emerald-500/15 text-emerald-300"
                : "bg-red-500/10 text-red-300"
            }`}
          >
            <span
              className={`h-1.5 w-1.5 rounded-full ${
                apiStatus === "operational" ? "bg-emerald-400" : "bg-red-400"
              } animate-pulse`}
            />
            {apiStatus === "operational" ? (
              <>
                <CheckCircle2 className="h-3 w-3" />
                <span className="uppercase tracking-wide">OK</span>
              </>
            ) : (
              <>
                <AlertTriangle className="h-3 w-3" />
                <span className="uppercase tracking-wide">Missing Key</span>
              </>
            )}
          </span>
        </Card>
      </div>

      {/* Metrics row */}
      <div className="grid gap-3 md:grid-cols-3">
        <MetricCard
          title={labels.dashboard.totalRuns}
          value={MOCK_METRICS.totalRuns.toLocaleString()}
          icon={<Activity className="h-4 w-4 text-emerald-300" />}
          trend="+18% this week"
        />
        <MetricCard
          title={labels.dashboard.activeAgents}
          value={MOCK_METRICS.activeAgents.toString()}
          icon={<Gauge className="h-4 w-4 text-sky-300" />}
          trend="4 high-priority"
        />
        <MetricCard
          title={labels.dashboard.avgLatency}
          value={`${MOCK_METRICS.avgLatencyMs} ms`}
          icon={<Timer className="h-4 w-4 text-amber-300" />}
          trend="-7% vs last week"
        />
      </div>

      {/* Charts */}
      <div className="grid flex-1 gap-3 md:grid-cols-2">
        <ChartContainer>
          <div className="mb-2 flex items-center justify-between text-xs">
            <span className="font-medium">{labels.dashboard.tokenTrends}</span>
          </div>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={tokenTrends}>
              <XAxis dataKey="day" stroke="#94a3b8" fontSize={10} />
              <YAxis stroke="#94a3b8" fontSize={10} />
              <Tooltip
                contentStyle={{
                  background: "#020617",
                  border: "1px solid rgba(148,163,184,0.6)",
                  borderRadius: 12,
                  fontSize: 11
                }}
              />
              <Line
                type="monotone"
                dataKey="tokens"
                stroke="#f97316"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </ChartContainer>

        <ChartContainer>
          <div className="mb-2 flex items-center justify-between text-xs">
            <span className="font-medium">
              {labels.dashboard.modelDistribution}
            </span>
          </div>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={modelDistribution}>
              <XAxis dataKey="model" stroke="#94a3b8" fontSize={9} />
              <YAxis stroke="#94a3b8" fontSize={10} />
              <Tooltip
                contentStyle={{
                  background: "#020617",
                  border: "1px solid rgba(148,163,184,0.6)",
                  borderRadius: 12,
                  fontSize: 11
                }}
              />
              <Bar dataKey="runs" fill="#38bdf8" radius={8} />
            </BarChart>
          </ResponsiveContainer>
        </ChartContainer>
      </div>
    </div>
  );
}

function MetricCard({
  title,
  value,
  icon,
  trend
}: {
  title: string;
  value: string;
  trend: string;
  icon: React.ReactNode;
}) {
  return (
    <Card className="flex flex-col gap-2">
      <div className="flex items-center justify-between text-xs text-slate-300">
        <span>{title}</span>
        <span className="flex h-6 w-6 items-center justify-center rounded-lg bg-slate-900/70">
          {icon}
        </span>
      </div>
      <div className="text-lg font-semibold">{value}</div>
      <div className="text-[11px] text-emerald-300/90">{trend}</div>
    </Card>
  );
}
```

### `src/components/agent-studio.tsx`

```tsx
"use client";

import { useEffect, useRef, useState } from "react";
import { Agent, Language } from "@/lib/types";
import { LABELS } from "@/lib/constants";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "./ui/tabs";
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from "./ui/select";
import { Input } from "./ui/input";
import { Textarea } from "./ui/textarea";
import { Button } from "./ui/button";
import { Card } from "./ui/card";
import { Badge } from "./ui/badge";
import { Loader2, Copy, Wand2, Upload, Download } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import yaml from "js-yaml";
import ReactMarkdown from "react-markdown";
import {
  generateContentAction,
  repairYamlAction
} from "@/app/actions";

const MODEL_OPTIONS = [
  "gpt-4o-mini",
  "gpt-4.1-mini",
  "gemini-2.5-flash",
  "gemini-2.5-flash-lite",
  "gemini-3-pro-preview",
  "anthropic",
  "grok-4-fast-reasoning",
  "grok-3-mini"
];

interface AgentStudioProps {
  agents: Agent[];
  onUpdateAgents: (agents: Agent[]) => void;
  language: Language;
  apiKey: string;
  hasServerApiKey: boolean;
  skillText: string;
  setSkillText: (txt: string) => void;
}

export function AgentStudio({
  agents,
  onUpdateAgents,
  language,
  apiKey,
  hasServerApiKey,
  skillText,
  setSkillText
}: AgentStudioProps) {
  const labels = LABELS[language];
  const { toast } = useToast();

  const [selectedAgentId, setSelectedAgentId] = useState(agents[0]?.id ?? "");
  const [overrideModel, setOverrideModel] = useState("");
  const [modelChoice, setModelChoice] = useState<string>("gemini-2.5-flash");
  const [maxTokens, setMaxTokens] = useState<number>(12000);
  const [prompt, setPrompt] = useState("");
  const [output, setOutput] = useState("");
  const [viewMode, setViewMode] = useState<"text" | "markdown">("text");
  const [running, setRunning] = useState(false);

  const [yamlText, setYamlText] = useState("");
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const skillInputRef = useRef<HTMLInputElement | null>(null);

  // Sync YAML text from agents
  useEffect(() => {
    setYamlText(
      yaml.dump({ agents }, { noRefs: true, lineWidth: 100 }) as string
    );
  }, [agents]);

  async function handleRunAgent() {
    const agent = agents.find((a) => a.id === selectedAgentId);
    if (!agent) return;

    setRunning(true);
    try {
      const usedModel = overrideModel || modelChoice || agent.model;
      const result = await generateContentAction({
        apiKey,
        prompt,
        systemPrompt: agent.systemPrompt,
        model: usedModel,
        maxTokens: maxTokens || agent.maxTokens || 12000
      });
      setOutput(result.text);
    } catch (err: any) {
      setOutput(`Error: ${err?.message ?? String(err)}`);
    } finally {
      setRunning(false);
    }
  }

  function handleCopy() {
    navigator.clipboard.writeText(output || "");
  }

  async function handleUploadYaml(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    const text = await file.text();
    setYamlText(text);
    try {
      const parsed = yaml.load(text);
      let normalizedAgents: Agent[] = [];
      if (Array.isArray(parsed)) {
        normalizedAgents = parsed as Agent[];
      } else if (parsed && typeof parsed === "object") {
        const obj = parsed as any;
        if (Array.isArray(obj.agents)) {
          normalizedAgents = obj.agents;
        } else {
          normalizedAgents = Object.values(obj) as Agent[];
        }
      }
      onUpdateAgents(normalizedAgents);
      setYamlText(
        yaml.dump({ agents: normalizedAgents }, { noRefs: true }) as string
      );
    } catch {
      toast({
        title: "YAML parse error",
        description: LABELS[language].toasts.yamlParseError,
        variant: "destructive"
      });
    } finally {
      e.target.value = "";
    }
  }

  function handleDownloadYaml() {
    const blob = new Blob([yamlText], { type: "text/yaml" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "agents.yaml";
    a.click();
    URL.revokeObjectURL(url);
  }

  async function handleRepairYaml() {
    try {
      const result = await repairYamlAction(yamlText);
      setYamlText(result.repairedYaml);
      const parsed = yaml.load(result.repairedYaml) as any;
      const normalizedAgents = Array.isArray(parsed?.agents)
        ? (parsed.agents as Agent[])
        : (parsed as Agent[]);
      onUpdateAgents(normalizedAgents);
      toast({
        title: "YAML repaired",
        description: LABELS[language].toasts.yamlRepaired,
        variant: "success"
      });
    } catch (e: any) {
      toast({
        title: "AI repair failed",
        description: e?.message ?? "Unknown error",
        variant: "destructive"
      });
    }
  }

  function handleUploadSkill(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    file.text().then((txt) => setSkillText(txt));
    e.target.value = "";
  }

  function handleDownloadSkill() {
    const blob = new Blob([skillText], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "SKILL.md";
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="flex h-full flex-col gap-3">
      <div className="flex items-center justify-between">
        <h1 className="font-headline text-xl font-semibold">
          {labels.agentStudio.title}
        </h1>
        <Badge className="bg-slate-900/70 text-[10px] uppercase tracking-wide text-slate-300">
          Agent Orchestration
        </Badge>
      </div>

      <Tabs defaultValue="run" className="flex h-full flex-col">
        <TabsList>
          <TabsTrigger value="run">{labels.agentStudio.runTab}</TabsTrigger>
          <TabsTrigger value="manage">{labels.agentStudio.manageTab}</TabsTrigger>
        </TabsList>

        {/* Run Tab */}
        <TabsContent value="run" className="flex-1">
          <div className="grid gap-3 md:grid-cols-[minmax(0,260px)_minmax(0,1fr)]">
            {/* Sidebar controls */}
            <Card className="flex flex-col gap-3">
              <div className="space-y-1 text-xs">
                <div className="text-slate-300">
                  {labels.agentStudio.selectAgent}
                </div>
                <Select
                  value={selectedAgentId}
                  onValueChange={(val) => setSelectedAgentId(val)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {agents.map((a) => (
                      <SelectItem key={a.id} value={a.id}>
                        {a.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-1 text-xs">
                <div className="text-slate-300">
                  {labels.agentStudio.modelSelectPlaceholder}
                </div>
                <Select
                  value={modelChoice}
                  onValueChange={(val) => setModelChoice(val)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {MODEL_OPTIONS.map((m) => (
                      <SelectItem key={m} value={m}>
                        {m}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-1 text-xs">
                <div className="text-slate-300">
                  {labels.agentStudio.overrideModel}
                </div>
                <Input
                  value={overrideModel}
                  onChange={(e) => setOverrideModel(e.target.value)}
                  placeholder="e.g. gemini-2.5-flash"
                />
              </div>

              <div className="space-y-1 text-xs">
                <div className="text-slate-300">
                  {labels.agentStudio.maxTokens}
                </div>
                <Input
                  type="number"
                  value={maxTokens}
                  onChange={(e) => setMaxTokens(Number(e.target.value) || 0)}
                />
              </div>

              <div className="flex items-center justify-between pt-1 text-[11px]">
                <span className="text-slate-400">
                  {viewMode === "text"
                    ? labels.agentStudio.viewModeText
                    : labels.agentStudio.viewModeMarkdown}
                </span>
                <div className="flex gap-1">
                  <Button
                    size="sm"
                    variant={viewMode === "text" ? "default" : "ghost"}
                    className="h-7 px-2 text-[10px]"
                    onClick={() => setViewMode("text")}
                  >
                    TXT
                  </Button>
                  <Button
                    size="sm"
                    variant={viewMode === "markdown" ? "default" : "ghost"}
                    className="h-7 px-2 text-[10px]"
                    onClick={() => setViewMode("markdown")}
                  >
                    MD
                  </Button>
                </div>
              </div>
            </Card>

            {/* Main I/O */}
            <div className="flex flex-col gap-3">
              <div className="grid flex-1 gap-3 md:grid-cols-2">
                <Card className="flex flex-col gap-2">
                  <div className="text-xs text-slate-300">
                    {labels.agentStudio.promptPlaceholder}
                  </div>
                  <Textarea
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    className="flex-1 text-xs"
                  />
                </Card>

                <Card className="flex flex-col gap-2">
                  <div className="flex items-center justify-between text-xs text-slate-300">
                    <span>Output</span>
                    <div className="flex gap-1">
                      <Button
                        size="sm"
                        variant="ghost"
                        className="h-7 px-2 text-[10px]"
                        onClick={handleCopy}
                        disabled={!output}
                      >
                        <Copy className="mr-1 h-3 w-3" />
                        {labels.agentStudio.copy}
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        className="h-7 px-2 text-[10px]"
                        onClick={() => setPrompt(output)}
                        disabled={!output}
                      >
                        {labels.agentStudio.useAsInput}
                      </Button>
                    </div>
                  </div>
                  <div className="relative flex-1 overflow-auto rounded-xl border border-border/70 bg-slate-950/50 p-2 text-xs">
                    {!output && !running && (
                      <span className="text-slate-500">
                        {labels.agentStudio.outputPlaceholder}
                      </span>
                    )}
                    {running && (
                      <div className="flex items-center gap-2 text-slate-300">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span>{labels.agentStudio.running}</span>
                      </div>
                    )}
                    {!running && output && (
                      <div className="prose prose-invert max-w-none text-xs">
                        {viewMode === "markdown" ? (
                          <ReactMarkdown>{output}</ReactMarkdown>
                        ) : (
                          <pre className="whitespace-pre-wrap break-words text-xs">
                            {output}
                          </pre>
                        )}
                      </div>
                    )}
                  </div>
                </Card>
              </div>

              <div className="flex justify-end">
                <Button onClick={handleRunAgent} disabled={running || (!apiKey && !hasServerApiKey)}>
                  {running && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  {labels.agentStudio.runAgent}
                </Button>
              </div>
            </div>
          </div>
        </TabsContent>

        {/* Manage Tab: agents.yaml + SKILL.md */}
        <TabsContent value="manage" className="flex-1">
          <div className="grid gap-3 md:grid-cols-2">
            {/* Agents.yaml */}
            <Card className="flex flex-1 flex-col gap-2">
              <div className="flex items-center justify-between text-xs text-slate-300">
                <span>{labels.agentStudio.manageYamlTitle}</span>
                <Badge className="bg-slate-900/70 text-[10px] text-slate-300">
                  YAML
                </Badge>
              </div>
              <Textarea
                className="min-h-[260px] flex-1 font-mono text-[11px]"
                value={yamlText}
                onChange={(e) => setYamlText(e.target.value)}
              />
              <div className="flex flex-wrap justify-between gap-2 pt-1 text-xs">
                <div className="flex gap-2">
                  <input
                    type="file"
                    accept=".yml,.yaml"
                    ref={fileInputRef}
                    className="hidden"
                    onChange={handleUploadYaml}
                  />
                  <Button
                    size="sm"
                    variant="outline"
                    className="h-8 px-2"
                    onClick={() => fileInputRef.current?.click()}
                  >
                    <Upload className="mr-1 h-3 w-3" />
                    {labels.agentStudio.uploadYaml}
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    className="h-8 px-2"
                    onClick={handleDownloadYaml}
                  >
                    <Download className="mr-1 h-3 w-3" />
                    {labels.agentStudio.downloadYaml}
                  </Button>
                </div>
                <Button
                  size="sm"
                  variant="subtle"
                  className="h-8 px-2"
                  onClick={handleRepairYaml}
                >
                  <Wand2 className="mr-1 h-3 w-3" />
                  {labels.agentStudio.aiRepair}
                </Button>
              </div>
            </Card>

            {/* SKILL.md */}
            <Card className="flex flex-1 flex-col gap-2">
              <div className="flex items-center justify-between text-xs text-slate-300">
                <span>{labels.agentStudio.manageSkillTitle}</span>
                <Badge className="bg-slate-900/70 text-[10px] text-slate-300">
                  Markdown
                </Badge>
              </div>
              <Textarea
                className="min-h-[260px] flex-1 font-mono text-[11px]"
                value={skillText}
                onChange={(e) => setSkillText(e.target.value)}
              />
              <div className="flex flex-wrap justify-between gap-2 pt-1 text-xs">
                <div className="flex gap-2">
                  <input
                    type="file"
                    accept=".md,.markdown,.txt"
                    ref={skillInputRef}
                    className="hidden"
                    onChange={handleUploadSkill}
                  />
                  <Button
                    size="sm"
                    variant="outline"
                    className="h-8 px-2"
                    onClick={() => skillInputRef.current?.click()}
                  >
                    <Upload className="mr-1 h-3 w-3" />
                    {labels.agentStudio.uploadSkill}
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    className="h-8 px-2"
                    onClick={handleDownloadSkill}
                  >
                    <Download className="mr-1 h-3 w-3" />
                    {labels.agentStudio.downloadSkill}
                  </Button>
                </div>
              </div>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
```

### `src/components/doc-intelligence.tsx`

```tsx
"use client";

import { useState } from "react";
import { Language } from "@/lib/types";
import { LABELS } from "@/lib/constants";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "./ui/tabs";
import { Textarea } from "./ui/textarea";
import { Card } from "./ui/card";
import { Button } from "./ui/button";
import { Slider } from "./ui/slider";
import { fileToDataUri } from "@/lib/utils";
import { summarizeDocumentAction } from "@/app/actions";
import { FileText, Image as ImageIcon, Upload, Download, Loader2 } from "lucide-react";

interface DocIntelligenceProps {
  language: Language;
}

export function DocumentIntelligence({ language }: DocIntelligenceProps) {
  const labels = LABELS[language];

  const [mode, setMode] = useState<"paste" | "upload">("paste");
  const [text, setText] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [previewDataUri, setPreviewDataUri] = useState<string | null>(null);
  const [output, setOutput] = useState("");
  const [fontSize, setFontSize] = useState(13);
  const [loading, setLoading] = useState(false);

  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const selected = e.target.files?.[0] ?? null;
    setFile(selected);
    if (selected) {
      const uri = await fileToDataUri(selected);
      setPreviewDataUri(uri);
    } else {
      setPreviewDataUri(null);
    }
  }

  async function handleProcess() {
    setLoading(true);
    try {
      let dataUri: string;
      if (mode === "paste") {
        const blob = new Blob([text], { type: "text/plain" });
        dataUri = await fileToDataUri(
          new File([blob], "pasted.txt", { type: "text/plain" })
        );
      } else if (file) {
        dataUri = previewDataUri ?? (await fileToDataUri(file));
      } else {
        return;
      }

      const res = await summarizeDocumentAction({ documentDataUri: dataUri });
      setOutput(res.summary);
    } finally {
      setLoading(false);
    }
  }

  function downloadAs(ext: "md" | "txt") {
    const blob = new Blob([output], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `summary.${ext}`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="flex h-full flex-col gap-3">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-headline text-xl font-semibold">
            {labels.docIntelligence.title}
          </h1>
          <p className="text-xs text-slate-300/80">
            Summarize, distill, and reinterpret your documents with AI.
          </p>
        </div>
      </div>

      <div className="grid flex-1 gap-3 md:grid-cols-[minmax(0,1.1fr)_minmax(0,1fr)]">
        {/* Input side */}
        <Card className="flex flex-col">
          <Tabs
            value={mode}
            onValueChange={(v) => setMode(v as "paste" | "upload")}
          >
            <TabsList>
              <TabsTrigger value="paste">
                {labels.docIntelligence.pasteTab}
              </TabsTrigger>
              <TabsTrigger value="upload">
                {labels.docIntelligence.uploadTab}
              </TabsTrigger>
            </TabsList>

            <TabsContent value="paste" className="mt-3">
              <Textarea
                className="min-h-[260px] text-xs"
                placeholder={labels.docIntelligence.pastePlaceholder}
                value={text}
                onChange={(e) => setText(e.target.value)}
              />
            </TabsContent>

            <TabsContent value="upload" className="mt-3">
              <label className="flex min-h-[220px] cursor-pointer flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-border/70 bg-slate-950/50 text-xs text-slate-300 hover:border-accent/70 hover:bg-slate-900/40">
                <Upload className="h-5 w-5 text-accent" />
                <div>{labels.docIntelligence.dropPrompt}</div>
                <input
                  type="file"
                  accept=".txt,.md,.pdf,.png,.jpg,.jpeg"
                  className="hidden"
                  onChange={handleFileChange}
                />
                {file && (
                  <div className="mt-3 flex items-center gap-2 text-[11px] text-slate-200/90">
                    {file.type.startsWith("image/") ? (
                      <ImageIcon className="h-4 w-4" />
                    ) : (
                      <FileText className="h-4 w-4" />
                    )}
                    <span>
                      {file.name} · {(file.size / 1024).toFixed(1)} KB
                    </span>
                  </div>
                )}
              </label>
            </TabsContent>
          </Tabs>

          <div className="mt-3 flex justify-end">
            <Button
              onClick={handleProcess}
              disabled={loading || (mode === "paste" ? !text : !file)}
            >
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {labels.docIntelligence.process}
            </Button>
          </div>
        </Card>

        {/* Output side */}
        <Card className="flex flex-col gap-2">
          <div className="flex items-center justify-between text-xs text-slate-300">
            <span>{labels.docIntelligence.outputTitle}</span>
            <div className="flex items-center gap-2">
              <span className="text-[10px] text-slate-400">
                {labels.docIntelligence.fontSize}
              </span>
              <div className="w-24">
                <Slider
                  min={11}
                  max={18}
                  step={1}
                  value={[fontSize]}
                  onValueChange={([v]) => setFontSize(v)}
                />
              </div>
            </div>
          </div>
          <Textarea
            className="min-h-[260px] flex-1 text-xs"
            style={{ fontSize }}
            value={output}
            onChange={(e) => setOutput(e.target.value)}
          />
          <div className="mt-1 flex flex-wrap justify-end gap-2 text-xs">
            <Button
              size="sm"
              variant="outline"
              className="h-8 px-2"
              disabled={!output}
              onClick={() => downloadAs("md")}
            >
              <Download className="mr-1 h-3 w-3" />
              {labels.docIntelligence.downloadMd}
            </Button>
            <Button
              size="sm"
              variant="outline"
              className="h-8 px-2"
              disabled={!output}
              onClick={() => downloadAs("txt")}
            >
              <Download className="mr-1 h-3 w-3" />
              {labels.docIntelligence.downloadTxt}
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
}
```

### `src/components/app-shell.tsx`

```tsx
"use client";

import { useEffect } from "react";
import { AppSettings, ViewType, Agent, ApiStatus, Language } from "@/lib/types";
import { Dashboard } from "./dashboard";
import { MainSidebar } from "./main-sidebar";
import { AgentStudio } from "./agent-studio";
import { DocumentIntelligence } from "./doc-intelligence";
import { PAINTER_CSS } from "@/lib/constants";
import { cn } from "@/lib/utils";

interface AppShellProps {
  currentView: ViewType;
  onChangeView: (view: ViewType) => void;
  apiKey: string;
  setApiKey: (key: string) => void;
  agents: Agent[];
  setAgents: (agents: Agent[]) => void;
  settings: AppSettings;
  setSettings: (s: AppSettings) => void;
  hasServerApiKey: boolean;
  skillText: string;
  setSkillText: (txt: string) => void;
}

export function AppShell({
  currentView,
  onChangeView,
  apiKey,
  setApiKey,
  agents,
  setAgents,
  settings,
  setSettings,
  hasServerApiKey,
  skillText,
  setSkillText
}: AppShellProps) {
  // Theme class
  useEffect(() => {
    const html = document.documentElement;
    html.classList.remove("light", "dark");
    html.classList.add(settings.theme);
  }, [settings.theme]);

  // Painter variables
  useEffect(() => {
    const style = PAINTER_CSS[settings.painterStyle];
    Object.entries(style ?? {}).forEach(([key, val]) => {
      document.documentElement.style.setProperty(key, val);
    });
  }, [settings.painterStyle]);

  const apiStatus: ApiStatus =
    hasServerApiKey || apiKey ? "operational" : "key-missing";

  const language: Language = settings.language;

  return (
    <div className={cn("flex h-screen w-screen bg-black/90 text-fg")}>
      <MainSidebar
        currentView={currentView}
        onChangeView={onChangeView}
        apiKey={apiKey}
        setApiKey={setApiKey}
        settings={settings}
        setSettings={setSettings}
        hasServerApiKey={hasServerApiKey}
        language={language}
      />

      <main className="flex-1 overflow-hidden px-4 py-4">
        <div className="glass-panel h-full overflow-hidden p-4">
          <div className="flex h-full flex-col">
            <div className="flex-1 overflow-auto">
              {currentView === "dashboard" && (
                <Dashboard language={language} apiStatus={apiStatus} />
              )}
              {currentView === "agent-studio" && (
                <AgentStudio
                  language={language}
                  agents={agents}
                  onUpdateAgents={setAgents}
                  apiKey={apiKey}
                  hasServerApiKey={hasServerApiKey}
                  skillText={skillText}
                  setSkillText={setSkillText}
                />
              )}
              {currentView === "doc-intelligence" && (
                <DocumentIntelligence language={language} />
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
```

---

## 7. AI / Server Actions

### `src/ai/genkit.ts`

```ts
import { genkit } from "genkit";
import { googleAI } from "@genkit-ai/google-genai";
import { nextPlugin } from "@genkit-ai/next";

export const ai = genkit({
  plugins: [
    googleAI({
      apiKey: process.env.GOOGLE_API_KEY
    }),
    nextPlugin()
  ],
  defaultModel: "gemini-2.5-flash"
});
```

### `src/ai/flows/repair-invalid-yaml.ts`

```ts
import { ai } from "../genkit";
import { z } from "zod";

const RepairInvalidYamlInputSchema = z.object({
  rawText: z.string()
});

const RepairInvalidYamlOutputSchema = z.object({
  repairedYaml: z.string()
});

const repairAgentYamlPrompt = `
You are a world-class YAML engineer.

Task:
- Take the user-provided text that *should* be an agents.yaml configuration.
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
`;

export const repairInvalidYamlFlow = ai.defineFlow(
  {
    name: "repair-invalid-yaml",
    inputSchema: RepairInvalidYamlInputSchema,
    outputSchema: RepairInvalidYamlOutputSchema
  },
  async (input) => {
    const { rawText } = input;

    const res = await ai.generate({
      model: "gemini-2.5-flash",
      input: [
        {
          role: "system",
          content: repairAgentYamlPrompt
        },
        {
          role: "user",
          content: `Here is the possibly invalid YAML:\n\n${rawText}`
        }
      ]
    });

    const text = res.outputText();
    return { repairedYaml: text.trim() };
  }
);

export async function repairInvalidYaml(rawText: string) {
  return repairInvalidYamlFlow({ rawText });
}
```

### `src/ai/flows/summarize-document-intelligence.ts`

```ts
import { ai } from "../genkit";
import { z } from "zod";

const SummarizeDocumentIntelligenceInputSchema = z.object({
  documentDataUri: z.string()
});

const SummarizeDocumentIntelligenceOutputSchema = z.object({
  summary: z.string()
});

const summarizePrompt = `
You are a precise summarization engine for arbitrary documents.

The document will be provided as a media attachment.
Produce a concise, structured summary with:

- Overview (2–3 sentences)
- Key points (bullet list)
- Risks or caveats (if any)
- Suggested next steps

Write clearly and avoid hallucinations.
`;

export const summarizeDocumentIntelligenceFlow = ai.defineFlow(
  {
    name: "summarize-document-intelligence",
    inputSchema: SummarizeDocumentIntelligenceInputSchema,
    outputSchema: SummarizeDocumentIntelligenceOutputSchema
  },
  async (input) => {
    const { documentDataUri } = input;

    const res = await ai.generate({
      model: "gemini-2.5-flash",
      input: [
        {
          role: "system",
          content: summarizePrompt
        },
        {
          role: "user",
          content: `{{media url=${documentDataUri}}}`
        }
      ]
    });

    return { summary: res.outputText().trim() };
  }
);

export async function summarizeDocumentIntelligence(documentDataUri: string) {
  return summarizeDocumentIntelligenceFlow({ documentDataUri });
}
```

### `src/ai/dev.ts` (optional for Genkit dev server)

```ts
import { dev } from "genkit/dev";
import "./genkit";
import "./flows/repair-invalid-yaml";
import "./flows/summarize-document-intelligence";

dev();
```

### `src/app/actions.ts`

```ts
"use server";

import { GoogleGenerativeAI } from "@google/generative-ai";
import { repairInvalidYaml } from "@/ai/flows/repair-invalid-yaml";
import { summarizeDocumentIntelligence } from "@/ai/flows/summarize-document-intelligence";

export async function generateContentAction(params: {
  apiKey?: string;
  prompt: string;
  systemPrompt?: string;
  model: string;
  maxTokens: number;
}) {
  const { apiKey, prompt, systemPrompt, model, maxTokens } = params;

  const key = apiKey || process.env.GOOGLE_API_KEY;
  if (!key) {
    throw new Error("No API key provided and GOOGLE_API_KEY not set.");
  }

  const genAI = new GoogleGenerativeAI(key);
  const usedModel = model || "gemini-2.5-flash";

  const gm = genAI.getGenerativeModel({ model: usedModel });
  const finalPrompt = systemPrompt
    ? `${systemPrompt.trim()}\n\nUser:\n${prompt}`
    : prompt;

  try {
    const result = await gm.generateContent({
      contents: [
        {
          role: "user",
          parts: [{ text: finalPrompt }]
        }
      ],
      generationConfig: { maxOutputTokens: maxTokens || 12000 }
    });

    const text = result.response.text();
    return { text };
  } catch (err: any) {
    throw new Error(
      err?.message ?? "Failed to generate content from Gemini model."
    );
  }
}

export async function repairYamlAction(rawText: string) {
  return repairInvalidYaml(rawText);
}

export async function summarizeDocumentAction(input: {
  documentDataUri: string;
}) {
  return summarizeDocumentIntelligence(input.documentDataUri);
}

/** Helper to indicate if server API key exists, for UI (do not expose actual key) */
export async function hasServerApiKeyAction() {
  return { hasServerKey: Boolean(process.env.GOOGLE_API_KEY) };
}
```

---

## 8. App Layout & Root Page

### `src/app/layout.tsx`

```tsx
import "./globals.css";
import type { Metadata } from "next";
import { ToastProvider } from "@/hooks/use-toast";

export const metadata: Metadata = {
  title: "Artistic Intelligence Workspace v2.0",
  description: "WOW UI multi-agent AI studio with painter-style theming."
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ToastProvider>{children}</ToastProvider>
      </body>
    </html>
  );
}
```

### `src/app/page.tsx`

```tsx
"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/app-shell";
import { AppSettings, ViewType, Agent } from "@/lib/types";
import { DEFAULT_AGENTS } from "@/lib/constants";
import { useToast } from "@/hooks/use-toast";
import yaml from "js-yaml";
import { hasServerApiKeyAction } from "./actions";

export default function Home() {
  const { toast } = useToast();

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

  /** Load agents.yaml & SKILL.md from public on first mount */
  useEffect(() => {
    async function loadConfigs() {
      try {
        const agentsRes = await fetch("/agents.yaml");
        if (agentsRes.ok) {
          const text = await agentsRes.text();
          const parsed = yaml.load(text) as any;
          const loadedAgents = Array.isArray(parsed?.agents)
            ? (parsed.agents as Agent[])
            : (parsed as Agent[]);
          setAgents(loadedAgents);
        } else {
          throw new Error("Failed to fetch agents.yaml");
        }
      } catch {
        toast({
          title: "agents.yaml",
          description: "Using built-in default agents.",
          variant: "default"
        });
        setAgents(DEFAULT_AGENTS);
      }

      try {
        const skillRes = await fetch("/SKILL.md");
        if (skillRes.ok) {
          const txt = await skillRes.text();
          setSkillText(txt);
        }
      } catch {
        // Ignore, keep default SKILL.md
      }
    }

    loadConfigs();
  }, [toast]);

  /** Check if server-side env API key exists */
  useEffect(() => {
    hasServerApiKeyAction().then((res) => {
      setHasServerApiKey(res.hasServerKey);
    });
  }, []);

  return (
    <AppShell
      currentView={currentView}
      onChangeView={setCurrentView}
      apiKey={apiKey}
      setApiKey={setApiKey}
      agents={agents}
      setAgents={setAgents}
      settings={settings}
      setSettings={setSettings}
      hasServerApiKey={hasServerApiKey}
      skillText={skillText}
      setSkillText={setSkillText}
    />
  );
}

/** Default SKILL.md used if /SKILL.md cannot be loaded */
const DEFAULT_SKILL_MD = `# Artistic Intelligence Workspace Skills

This file describes reusable skills and patterns for agents defined in \`agents.yaml\`.

---

## 1. Creative Writing Patterns

- \`creative-writer\` focuses on:
  - Gentle, painterly metaphors.
  - Clear narrative arcs.
  - Respecting requested length and tone.

**Usage Hints**

- Ask for "3 variants" when exploring style.
- Prompt with explicit audience, domain, and output format.

---

## 2. YAML Architecture Guidelines

The \`yaml-architect\` agent:

- Normalizes all agents into the structure:

\`\`\`yaml
agents:
  - id: string
    name: string
    description: string
    model: string
    maxTokens: number
    temperature: number
    systemPrompt: string
    tags: [string, ...]
\`\`\`

- Emphasizes:
  - Consistent IDs (kebab-case).
  - Concise but precise descriptions.
  - Clear separation between systemPrompt and user prompt.

---

## 3. Document Intelligence

The \`doc-summarizer\` agent is optimized for:

- Long-form documents (reports, research, PDFs).
- Producing structured summaries:

  1. Overview
  2. Key insights
  3. Risks / caveats
  4. Recommended next steps

---

## 4. Chaining Agents

Recommended patterns:

1. Use \`doc-summarizer\` to create a compact brief.
2. Feed that brief into \`creative-writer\` for narrative synthesis.
3. Optionally, call \`yaml-architect\` to define specialized agents for follow-up tasks.

You can implement these chains manually in the Agent Studio by:

- Running one agent.
- Editing its output.
- Sending it as input to the next agent via "Use as next input".
`;
```

---

## 9. Public Config Files

### `public/agents.yaml`

```yaml
agents:
  - id: creative-writer
    name: Creative Writer
    description: Long-form creative writing with painterly metaphors.
    model: gemini-2.5-flash
    maxTokens: 8000
    temperature: 0.9
    systemPrompt: >
      You are a world-class creative writer who uses imagery inspired by classic
      painters (Van Gogh, Monet, Kahlo, Hokusai) while remaining precise and
      concise on request. You adapt your voice to the user's needs.
    tags:
      - writing
      - creativity
      - narrative

  - id: yaml-architect
    name: YAML Architect
    description: Designs, validates, and normalizes complex agents.yaml files.
    model: gemini-2.5-flash
    maxTokens: 6000
    temperature: 0.4
    systemPrompt: >
      You are an expert in YAML schemas for multi-agent orchestration. 
      You always output strictly valid, standardized agents.yaml structures.
      Normalize configurations into:
      agents:
        - id: string
          name: string
          description: string
          model: string
          maxTokens: number
          temperature: number
          systemPrompt: string
          tags: [string, ...]
    tags:
      - yaml
      - config
      - tooling

  - id: doc-summarizer
    name: Document Summarizer
    description: Produces structured summaries for long documents.
    model: gemini-2.5-flash
    maxTokens: 4000
    temperature: 0.3
    systemPrompt: >
      You create faithful, structured summaries with Overview, Key Points,
      Risks, and Recommended Next Steps. Avoid hallucinations and
      clearly mark uncertainties.
    tags:
      - summarization
      - documents
      - analysis

  - id: code-assistant
    name: Code Assistant
    description: Multi-language code assistant focused on safety and clarity.
    model: gemini-2.5-flash
    maxTokens: 12000
    temperature: 0.45
    systemPrompt: >
      You are a senior software engineer. Prefer step-by-step reasoning,
      explicit tradeoffs, and production-ready examples. Highlight edge
      cases and common pitfalls. Where relevant, propose tests.
    tags:
      - coding
      - engineering
      - debugging
```

### `public/SKILL.md`

```md
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
```

---

## 10. Notes on WOW Features

- **Light/Dark themes**: Toggled via `settings.theme`, applied on `<html>` class (`light` / `dark`), with CSS variables still handling most color.
- **Painter Styles (20)**: `PAINTER_STYLES` + `PAINTER_CSS` fully implemented; changed via sidebar; Jackpot button chooses a random style.
- **i18n (EN/TC)**: All major strings pulled from `LABELS`; toggled via sidebar language switch.
- **WOW Status Indicators**:
  - Sidebar badge shows API key operational / missing.
  - Dashboard header shows API status with animated pulse.
- **API key handling**:
  - Server uses `params.apiKey || process.env.GOOGLE_API_KEY`.
  - Client calls `hasServerApiKeyAction` to know if env key exists.
  - If env key exists, input is disabled and masked; key is never exposed.
- **Agent chaining**:
  - `Use as next input` button in Agent Studio copies output into prompt.
- **Model selection / maxTokens / prompt**:
  - Full UI controls before running the agent.
  - Non-Gemini model names are accepted in UI but routed through `GoogleGenerativeAI` (you can later extend to other providers).
- **agents.yaml & SKILL.md**:
  - Edit, upload, download in Agent Studio Manage tab.
  - Non-standard agents YAML normalized on upload.
  - AI Repair using Genkit flow.

---

## 11. Twenty Follow-up Questions

1. Do you want the non-Gemini model names (e.g., `gpt-4o-mini`, Anthropic, Grok) to be wired to their real APIs with separate keys and routing logic, or is the current Google-only implementation acceptable for now?  
2. Should the model selector include a separate “provider” field (Google, OpenAI, Anthropic, Grok) and handle provider-specific options (like temperature, top_p) per provider?  
3. Would you like an explicit “Agent chain designer” UI (drag-and-drop agent pipeline graph) instead of manual chaining via “Use as next input”?  
4. Should the dashboard metrics be persisted (e.g., using a lightweight database) to show real historical usage instead of static mock data?  
5. Do you want per-agent runtime controls (temperature, top_p, etc.) exposed in the Run tab, or should those stay fixed in `agents.yaml` by default?  
6. For SKILL.md, would you like an AI helper similar to YAML Repair (e.g., “Refine Skills with AI” using a dedicated Genkit flow)?  
7. Should the Document Intelligence view support multi-document batches and comparative summaries (e.g., “compare document A vs B”)?  
8. Are there specific file types (like DOCX, PPTX, HTML) that you want to support in Document Intelligence beyond txt/md/pdf/images?  
9. Would you like a per-session history panel that shows previous runs, their prompts, and outputs for quick re-use?  
10. Should there be user profiles with saved preferences (theme, language, favorite painter styles, default agents) persisted per browser or via auth?  
11. Do you want a “live status” widget on the dashboard that pings each configured provider (Gemini, OpenAI, Anthropic, Grok) and shows latency/health?  
12. Should the WOW painter themes also influence chart colors, or do you prefer the current relatively neutral chart palette for clarity?  
13. Would you like keyboard shortcuts (e.g., `Ctrl+Enter` to run agent, `Ctrl+1/2/3` to switch views, `J` to trigger Jackpot) for power users?  
14. Should we add a compact mode for mobile where the sidebar collapses into an icon-only bottom bar to maximize content area?  
15. Do you want validation and schema hints in the YAML editor (e.g., inline warnings for missing `id` or `model` fields)?  
16. Would you like to visualize agents from `agents.yaml` as a grid of cards with tags and quick actions, in addition to the dropdown selector?  
17. Should there be a built-in “template gallery” of common `agents.yaml` and `SKILL.md` combinations that users can load as starting points?  
18. Do you want telemetry hooks (events) added so you can track usage analytics (view switches, runs per agent, document types processed)?  
19. Should the system support exporting/importing the entire workspace configuration (agents + skills + UI settings) as a single bundle file?  
20. Are there any specific painter styles or additional visual effects (e.g., subtle animated gradients, particle backgrounds) you’d like to add to make the WOW UI even more immersive?
