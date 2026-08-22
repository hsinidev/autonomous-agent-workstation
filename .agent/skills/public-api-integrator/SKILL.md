---
name: public-api-integrator
description: Query, discover, and integrate 1,695+ verified public APIs into applications. Use when the user requests external data, real-time widgets, open APIs, mock-free frontend prototyping, or live backend integrations without guessing endpoints.
---

# 🌐 Public API Integrator Skill

This skill equips the Antigravity Agent with direct, zero-friction access to **1,695+ curated, verified public APIs** across 51 categories (Anime, Finance, Weather, Sports, Geocoding, Cryptocurrency, Open Data, Development, Games, and more).

---

## ⚡ When to Trigger This Skill

Automatically invoke this skill whenever:
- User requests building a **data-driven frontend or fullstack feature** (charts, feeds, calculators, trackers, widgets).
- User wants **live prototyping without mock data** (e.g. real dogs/cats API, real weather, real stock prices, real dictionary/jokes/quotes).
- Identifying suitable third-party endpoints, free tiers, or authentication specifications.
- Replacing hardcoded mockup objects (`[{id: 1, name: 'dummy'}]`) with robust, typed real endpoints.

---

## 🔍 Step 1: CLI Discovery & Lookup

Use the local lookup tool to discover endpoints with zero latency and zero hallucinations:

```bash
# General search by keyword
python .agent/skills/public-api-integrator/api_lookup.py --query "weather"

# Filter by category and zero-auth requirement
python .agent/skills/public-api-integrator/api_lookup.py --category "Anime" --no-auth

# Instant frontend vibe-coding preset (Auth: No + CORS: Yes + HTTPS: True)
python .agent/skills/public-api-integrator/api_lookup.py --frontend-ready --category "Finance"

# Output raw JSON for programmatic consumption
python .agent/skills/public-api-integrator/api_lookup.py --query "crypto" --json --limit 5

# List all 51 available categories
python .agent/skills/public-api-integrator/api_lookup.py --categories
```

---

## 🧭 Step 2: Architecture Decision Matrix

When integrating an endpoint, follow this architectural hierarchy:

| Condition | Recommended Architecture | Implementation Strategy |
| :--- | :--- | :--- |
| **`auth: No` + `cors: yes` + `https: true`** | **Direct Client Fetch** | Pure frontend component / TanStack Query / SWR with zero proxy overhead. |
| **`cors: no` or `cors: unknown`** | **Backend Proxy Route** | Next.js Route Handler (`app/api/proxy/route.ts`) or Express/Hono backend route. |
| **`auth: apiKey`** | **Secure Server-Side Route** | Store key in `.env.local`, fetch strictly from backend/server action. Never leak keys in client bundle! |
| **`auth: OAuth`** | **OAuth 2.0 PKCE / Server Flow** | Use NextAuth / Lucia / custom OAuth route with encrypted session cookies. |

---

## 🛠️ Step 3: Production Code Patterns

### 1. Robust Typed TypeScript Client Fetch (Zero-Auth / CORS-Enabled)

```typescript
// services/publicApiService.ts

export interface EndpointResponse<T> {
  data: T | null;
  error: string | null;
  loading: boolean;
}

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
      throw new Error(`HTTP error! status: ${response.status} (${response.statusText})`);
    }

    const payload = await response.json();
    return payload as T;
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

### 2. Next.js App Router Backend Proxy (For `cors: no` or `auth: apiKey`)

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

    // Attach secret server-side API key if needed
    if (process.env.PUBLIC_API_SECRET_KEY) {
      headers['Authorization'] = `Bearer ${process.env.PUBLIC_API_SECRET_KEY}`;
    }

    const res = await fetch(targetEndpoint, {
      headers,
      next: { revalidate: 60 }, // Cache response for 60 seconds
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

### 3. React / TanStack Query Hook Template

```typescript
// hooks/usePublicData.ts
import { useQuery } from '@tanstack/react-query';
import { fetchPublicApi } from '@/services/publicApiService';

interface FactData {
  fact: string;
  length: number;
}

export function usePublicFact() {
  return useQuery<FactData, Error>({
    queryKey: ['catFact'],
    queryFn: () => fetchPublicApi<FactData>('https://catfact.ninja/fact'),
    staleTime: 1000 * 60 * 5, // 5 minutes
    retry: 2,
  });
}
```

---

## 🔒 Step 4: Strict Quality & Safety Guidelines

1. **Never Assume Schema Shapes**: Always generate defensive TypeScript interfaces or Zod schemas matching real payload responses.
2. **Handle Offline & Rate Limits**: Implement graceful UI fallbacks (skeleton loaders, error retry buttons, cached local storage data).
3. **No Key Leaks**: For `apiKey` / `OAuth` services, enforce environment variable masking (`.env.local`) and server-side relay.
