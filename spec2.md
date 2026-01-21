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
