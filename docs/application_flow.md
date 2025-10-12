# Application Flow: Frontend → Backend

This document explains the complete application flow from the frontend UI to the backend API in the SudokuSolver web application.

## 🔄 Overview

The SudokuSolver web application follows a typical client-server architecture with React frontend and FastAPI backend, communicating via REST API endpoints.

## 1️⃣ User Interface Layer

**File:** `web/frontend/src/App.tsx`

```
User opens browser → http://localhost:5173 (dev) or http://localhost (production)
                   ↓
                App Component Renders
                   ↓
         ┌─────────┴─────────┐
         ↓                   ↓
    HealthCheck         SolveForm
    Component           Component
```

**What happens:**
- React renders the main `App` component
- Two child components are mounted:
  - `HealthCheck`: Automatically checks API status on mount
  - `SolveForm`: Provides the puzzle input interface

---

## 2️⃣ Health Check Flow

**File:** `web/frontend/src/components/HealthCheck.tsx`

```tsx
Component mounts
    ↓
useEffect hook triggers
    ↓
Calls getHealth() from api service
    ↓
Frontend: GET /api/healthz
    ↓
[Vite Proxy (dev) or Nginx (prod)]
    ↓
Backend: GET /api/healthz
    ↓
Returns: {"status": "ok"}
    ↓
Component displays: "API: ✓ ok" (green badge)
```

**Network flow:**
```
Browser → http://localhost:5173/api/healthz (dev mode)
       → Vite proxy forwards to → http://localhost:8000/api/healthz
       → FastAPI handles request
       → Returns JSON response
       → React updates UI
```

---

## 3️⃣ Solve Puzzle Flow

**File:** `web/frontend/src/components/SolveForm.tsx`

```
User enters puzzle text in textarea
    ↓
User clicks "Solve Puzzle" button
    ↓
handleSubmit(e) function executes
    ↓
Validates puzzle input (non-empty)
    ↓
Sets loading state (button shows "Solving...")
    ↓
Calls solve({ puzzle }) from api service
    ↓
Frontend: POST /api/solve
    Body: {"puzzle": "...user input..."}
    ↓
[Vite Proxy (dev) or Nginx (prod)]
    ↓
Backend: POST /api/solve
    ↓
FastAPI processes request
    ↓
Returns: {
  "solution": "...",
  "success": true,
  "message": "Puzzle received successfully"
}
    ↓
Frontend receives response
    ↓
Updates state with solution/message
    ↓
UI displays result in green box
```

---

## 4️⃣ API Service Layer

**File:** `web/frontend/src/services/api.ts`

This is the **abstraction layer** between React components and the backend:

```typescript
// Health Check Function
export async function getHealth(): Promise<Healthz> {
  const response = await fetch(`${API_BASE}/healthz`);
  return response.json();
}

// Solve Function
export async function solve(request: SolveRequest): Promise<SolveResponse> {
  const response = await fetch(`${API_BASE}/solve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  return response.json();
}
```

**What it does:**
- Uses native `fetch()` API to make HTTP requests
- Handles JSON serialization/deserialization
- Provides type-safe interfaces (TypeScript)
- Uses `API_BASE` from config (currently `/api`)

---

## 5️⃣ Configuration Layer

**File:** `web/frontend/src/config.ts`

```typescript
export const API_BASE = import.meta.env.VITE_API_BASE ?? '/api';
```

**Environment-specific values:**
- **Development**: `/api` → proxied by Vite to `http://localhost:8000/api`
- **Production**: `/api` → routed by Nginx to backend container

**Files:**
- `.env.development`: `VITE_API_BASE=/api`
- `.env.production`: `VITE_API_BASE=/api`

---

## 6️⃣ Network Routing Layer

### Development Mode (Vite Proxy)

**File:** `web/frontend/vite.config.ts`

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      secure: false,
    }
  }
}
```

**Flow:**
```
Browser: http://localhost:5173/api/healthz
    ↓
Vite Dev Server intercepts /api/* requests
    ↓
Proxies to: http://localhost:8000/api/healthz
    ↓
Backend responds
    ↓
Vite forwards response to browser
```

### Production Mode (Nginx)

**File:** `web/nginx/nginx.conf`

```nginx
location /api/ {
    proxy_pass http://backend:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    # ... other headers
}
```

**Flow:**
```
Browser: http://your-server.com/api/healthz
    ↓
Nginx receives request
    ↓
Proxies to: http://backend:8000/api/healthz
    ↓
Backend container responds
    ↓
Nginx forwards response to browser
```

---

## 7️⃣ Backend API Layer

**File:** `web/backend/app.py`

### Health Check Endpoint

```python
@app.get("/api/healthz")
async def health_check() -> Dict[str, str]:
    return {"status": "ok"}
```

### Solve Endpoint

```python
@app.post("/api/solve", response_model=SolveResponse)
async def solve_sudoku(request: SolveRequest) -> SolveResponse:
    # TODO: Integrate with actual SudokuSolver backend
    return SolveResponse(
        solution=request.puzzle,  # Echo for now
        success=True,
        message="Puzzle received successfully"
    )
```

**What happens:**
1. FastAPI receives HTTP request
2. Pydantic validates request body against `SolveRequest` model
3. Function processes request (currently just echoes)
4. Pydantic serializes response using `SolveResponse` model
5. FastAPI returns JSON response with proper status codes

---

## 8️⃣ Type Safety Layer

**File:** `web/frontend/src/types/api.ts`

Defines TypeScript interfaces that mirror the backend Pydantic models:

```typescript
// Matches backend SolveRequest
export interface SolveRequest {
  puzzle: string;
}

// Matches backend SolveResponse
export interface SolveResponse {
  solution: string;
  success: boolean;
  message: string;
}

// Matches backend health check response
export interface Healthz {
  status: 'ok';
}
```

**Benefits:**
- Compile-time type checking
- IDE autocomplete
- Catches type mismatches before runtime

---

## 📊 Complete Request Flow Diagrams

### Development Mode

```
┌─────────────────────────────────────────────────────────────────┐
│ Browser (http://localhost:5173)                                 │
│   ↓ User clicks "Solve"                                         │
│ React Component (SolveForm)                                     │
│   ↓ calls solve({ puzzle })                                     │
│ API Service (src/services/api.ts)                               │
│   ↓ fetch('/api/solve', { method: 'POST', body: {...} })       │
│ Vite Dev Server (port 5173)                                     │
│   ↓ proxies /api/* → http://localhost:8000                      │
├─────────────────────────────────────────────────────────────────┤
│ FastAPI Backend (port 8000)                                     │
│   ↓ @app.post("/api/solve")                                     │
│ Pydantic Validation                                             │
│   ↓ SolveRequest model                                          │
│ solve_sudoku() function                                         │
│   ↓ Process puzzle (currently echo)                             │
│ Pydantic Serialization                                          │
│   ↓ SolveResponse model                                         │
│ JSON Response                                                   │
├─────────────────────────────────────────────────────────────────┤
│   ↑ Response flows back up                                      │
│ React Component updates state                                   │
│   ↑ Displays solution in UI                                     │
└─────────────────────────────────────────────────────────────────┘
```

### Production Mode (Docker)

```
┌─────────────────────────────────────────────────────────────────┐
│ Browser (http://your-server.com)                                │
│   ↓ GET /api/healthz                                            │
│ Nginx Container (port 80)                                       │
│   ↓ location /api/ → proxy_pass http://backend:8000            │
│ Docker Network                                                  │
│   ↓ Routes to backend container                                 │
│ FastAPI Backend Container (port 8000)                           │
│   ↓ Processes request                                           │
│   ↑ Returns JSON response                                       │
│ Nginx Container                                                 │
│   ↑ Forwards response                                           │
│ Browser                                                         │
│   ↑ Updates UI                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔑 Key Components Summary

### Frontend Components

| Component | File | Purpose |
|-----------|------|---------|
| App | `src/App.tsx` | Main application container |
| HealthCheck | `src/components/HealthCheck.tsx` | Displays API status badge |
| SolveForm | `src/components/SolveForm.tsx` | Puzzle input and solve UI |
| API Service | `src/services/api.ts` | HTTP request abstraction |
| Config | `src/config.ts` | Environment configuration |
| Types | `src/types/api.ts` | TypeScript type definitions |

### Backend Components

| Component | File | Purpose |
|-----------|------|---------|
| FastAPI App | `web/backend/app.py` | Main API application |
| Health Endpoint | `@app.get("/api/healthz")` | Health check endpoint |
| Solve Endpoint | `@app.post("/api/solve")` | Puzzle solving endpoint |
| Pydantic Models | `SolveRequest`, `SolveResponse` | Data validation models |

### Infrastructure

| Component | File | Purpose |
|-----------|------|---------|
| Vite Config | `vite.config.ts` | Dev server proxy configuration |
| Nginx Config | `web/nginx/nginx.conf` | Production reverse proxy |
| Docker Compose | `web/docker-compose.yml` | Container orchestration |

---

## 🎯 Key Architectural Principles

1. **Separation of Concerns**: Frontend handles UI, backend handles logic
2. **Type Safety**: TypeScript on frontend, Pydantic on backend
3. **Environment-Aware**: Different routing for dev vs production
4. **Abstraction**: API service layer isolates components from HTTP details
5. **Validation**: Both frontend (TypeScript) and backend (Pydantic) validate data
6. **Proxy/Routing**: Vite (dev) or Nginx (prod) handles API routing
7. **Stateless**: Each request is independent (no session state yet)

---

## 🚀 Future Integration Points

When integrating the actual SudokuSolver logic, you'll need to:

1. **Update Backend**: Replace echo logic in `solve_sudoku()` with actual solver
2. **No Frontend Changes**: Frontend API contract remains the same
3. **Add OCR Endpoint**: For image-based puzzle input
4. **Session Management**: If puzzle history is needed
5. **Error Handling**: More detailed error responses

The current architecture makes it easy to integrate the actual SudokuSolver logic in the backend without changing the frontend!

---

## 📚 Related Documentation

- [Web README](../web/README.md) - General web application documentation
- [Deployment Guide](../web/README-deploy-images.md) - How to deploy to production
- [Frontend README](../web/frontend/README.md) - Frontend-specific documentation

---

**Last Updated:** 2025-10-08

