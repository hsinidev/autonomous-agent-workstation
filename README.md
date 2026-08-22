# ⚡ Autonomous Agent Workstation — Public APIs Engine

> **A local-first, zero-hallucination public API registry and autonomous agent skill providing direct access to 1,695+ verified endpoints across 51 categories.**

---

## 🎯 Overview

Modern AI coding agents frequently struggle with hallucinated API endpoints, outdated URLs, or resorting to mock data (`[{ id: 1, name: "dummy" }]`) when prototyping applications.

The **Public APIs Engine** integrates a normalized, indexed database of **1,695+ live public APIs** directly into your autonomous agent's memory and skill workflow. It allows AI agents to instantly search, filter, and wire real endpoints for pure frontend vibe-coding, live dashboard widgets, and robust full-stack applications.

---

## 📊 Dataset Metrics & Statistics

| Metric | Value | Details |
| :--- | :--- | :--- |
| **Total Public APIs** | **1,695** | Fully normalized records with verified URLs & metadata |
| **Categories** | **51** | Development, Finance, Weather, Animals, Anime, Crypto, Games, etc. |
| **Zero-Auth Endpoints** | **796** | Instant client access without API keys or OAuth setup |
| **API Key Required** | **749** | Free/freemium API keys for secure server-side integration |
| **OAuth Services** | **150** | Production OAuth 2.0 services |
| **CORS-Enabled** | **562** | Ready for pure browser/client-side vibe-coding |

### Top Categories

```
• Development:          150 APIs    • Cryptocurrency:       77 APIs
• Government:           103 APIs    • Transportation:       77 APIs
• Games & Comics:       101 APIs    • Finance:              60 APIs
• Geocoding:             95 APIs    • Open Data:            52 APIs
```

---

## 📁 Repository Structure

```
autonomous-agent-workstation/
├── data/
│   └── public_apis_index.json       # 1,695+ normalized API records (JSON)
├── scripts/
│   ├── api_lookup.py                # High-speed CLI search & filtering tool
│   └── index_public_apis.py         # Markdown-to-JSON database indexer
├── skills/
│   └── public-api-integrator/
│       ├── SKILL.md                 # Agent skill definition and prompt rules
│       ├── api_lookup.py            # Embedded CLI utility
│       └── public_apis_index.json   # Embedded registry
├── .agent/                          # IDE agent configuration root
│   ├── brain/
│   │   └── public_apis_index.json
│   └── skills/
│       └── public-api-integrator/
└── README.md                        # Documentation & agent integration guide
```

---

## 🚀 CLI Search & Query Tool (`api_lookup.py`)

The CLI utility provides fast query capabilities with human-readable table views and raw JSON output for agent automation.

### Quick Commands

```bash
# 1. Search by keyword
python scripts/api_lookup.py --query "weather"

# 2. Vibe-coding filter: Free + CORS Yes + HTTPS True
python scripts/api_lookup.py --frontend-ready --limit 10

# 3. Filter by category and zero authentication
python scripts/api_lookup.py --category "Anime" --no-auth

# 4. Filter by CORS support and API key requirement
python scripts/api_lookup.py --auth apiKey --cors yes --limit 15

# 5. Output raw JSON for programmatic use
python scripts/api_lookup.py --category "Finance" --json --limit 5

# 6. Pick 3 random APIs for inspiration
python scripts/api_lookup.py --frontend-ready --random 3

# 7. List all 51 available categories
python scripts/api_lookup.py --categories
```

### CLI Parameters Reference

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `-q, --query` | `string` | Search query across name, category, and description |
| `-c, --category` | `string` | Filter by category name (e.g. `Animals`, `Cryptocurrency`) |
| `-a, --auth` | `string` | Filter by auth type (`No`, `apiKey`, `OAuth`) |
| `--no-auth` | `flag` | Filter for zero-auth public endpoints |
| `--cors` | `string` | Filter by CORS status (`yes`, `no`, `unknown`) |
| `--https` | `flag` | Require HTTPS endpoints |
| `--frontend-ready` | `flag` | Preset for `Auth: No` + `CORS: Yes` + `HTTPS: True` |
| `-l, --limit` | `int` | Maximum items to return (default: `30`) |
| `-r, --random` | `int` | Pick N random matching items |
| `--json` | `flag` | Output raw JSON instead of table |
| `--categories` | `flag` | List all categories with item counts |

---

## 🤖 How to Use in Your AI Agent (Antigravity / Claude Code / Cursor)

### 1. Register the Agent Skill
Place the `skills/public-api-integrator/` folder inside your agent's skills directory:
- **Global:** `~/.gemini/config/skills/public-api-integrator/` or `.claude/skills/`
- **Workspace:** `.agent/skills/public-api-integrator/`

### 2. Configure Agent Instruction Rule
Add the following rule to your agent system prompt or `.agent/rules/public-apis-integration.md`:

```markdown
# 🌐 Zero-Mock Public API Standard
- Whenever building data-driven features, live widgets, dashboards, or prototypes, the agent MUST query the local Public API index (`scripts/api_lookup.py` or `.agent/brain/public_apis_index.json`) before resorting to mock data.
- For client-side React/Vue/Svelte apps, prioritize `auth: No` + `cors: yes` + `https: true` endpoints.
- For APIs requiring keys or lacking CORS, wrap requests in server-side proxy routes with strict `.env` secret isolation.
- Generate accurate TypeScript interfaces directly against real schema examples.
```

---

## 💻 Production Integration Patterns

### 1. Robust TypeScript Client Fetch (Zero-Auth / CORS-Enabled)

```typescript
// services/publicApiService.ts

export async function fetchPublicApi<T>(
  url: string,
  options: { timeoutMs?: number; headers?: Record<string, string> } = {}
): Promise<T> {
  const { timeoutMs = 8000, headers = {} } = options;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      signal: controller.signal,
      headers: {
        'Accept': 'application/json',
        ...headers,
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return (await response.json()) as T;
  } catch (err: unknown) {
    if (err instanceof DOMException && err.name === 'AbortError') {
      throw new Error(`Request timed out after ${timeoutMs}ms`);
    }
    throw err instanceof Error ? err : new Error(String(err));
  } finally {
    clearTimeout(timeoutId);
  }
}
```

### 2. Next.js App Router Proxy (CORS Bypass & API Key Security)

```typescript
// app/api/public-proxy/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const targetEndpoint = searchParams.get('endpoint');

  if (!targetEndpoint) {
    return NextResponse.json({ error: 'Missing endpoint parameter' }, { status: 400 });
  }

  try {
    const headers: Record<string, string> = {
      'Accept': 'application/json',
    };

    if (process.env.PUBLIC_API_SECRET_KEY) {
      headers['Authorization'] = `Bearer ${process.env.PUBLIC_API_SECRET_KEY}`;
    }

    const res = await fetch(targetEndpoint, {
      headers,
      next: { revalidate: 60 },
    });

    if (!res.ok) {
      return NextResponse.json(
        { error: `Upstream error: ${res.statusText}` },
        { status: res.status }
      );
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || 'Internal proxy error' },
      { status: 500 }
    );
  }
}
```

---

## 🔄 Re-indexing the Database

To refresh or update the dataset with new entries:

```bash
# Parse and update the local database from a raw markdown list
python scripts/index_public_apis.py path/to/README.md
```

---

## 📜 License & Acknowledgments

- Data sourced from the [public-apis/public-apis](https://github.com/public-apis/public-apis) community initiative under the MIT License.
- Autonomous Agent Workstation integration by [hsinidev](https://github.com/hsinidev).
