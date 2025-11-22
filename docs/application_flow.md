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

## 3️⃣ Solve Puzzle Flow (Full Solve)

**File:** `web/frontend/src/components/SolveForm.tsx`

```
User enters puzzle in editable grid
    ↓
User clicks "Solve Puzzle" button
    ↓
handleSubmit(e) function executes
    ↓
Validates puzzle input (non-empty)
    ↓
Sets loading state (button shows "Solving...")
    ↓
Calls solve({ grid, debug_level }) from api service
    ↓
Frontend: POST /api/solve
    Body: {"grid": number[][], "debug_level": number}
    ↓
[Vite Proxy (dev) or Nginx (prod)]
    ↓
Backend: POST /api/solve
    ↓
FastAPI processes request with SudokuSolver
    ↓
Returns: {
  "solution": number[][] | null,
  "success": boolean,
  "message": "string"
}
    ↓
Frontend receives response
    ↓
Updates state with solution/message
    ↓
UI displays result in ResultPanel
```

---

## 3️⃣b Stepwise Solving Flow (Experimental)

**File:** `web/frontend/src/components/SolveForm.tsx`

**Create Session:**
```
User enters puzzle in editable grid
    ↓
User clicks "Start Step Session" button
    ↓
handleStartStepSession() function executes
    ↓
Calls createSession({ grid, debug_level }) from api service
    ↓
Frontend: POST /api/sessions
    Body: {"grid": number[][], "debug_level": number}
    ↓
[Vite Proxy (dev) or Nginx (prod)]
    ↓
Backend: POST /api/sessions
    ↓
FastAPI generates session_id (UUID)
    ↓
Stores grid state in Redis (key: sudoku:session:{session_id})
    ↓
Returns: {"session_id": "string"}
    ↓
Frontend stores session_id in state
    ↓
UI enables "Next Step" and "End Session" buttons
```

**Apply Step:**
```
User clicks "Next Step" button
    ↓
handleNextStep() function executes
    ↓
Calls stepSession(sessionId) from api service
    ↓
Frontend: POST /api/sessions/{session_id}/step
    ↓
[Vite Proxy (dev) or Nginx (prod)]
    ↓
Backend: POST /api/sessions/{session_id}/step
    ↓
FastAPI retrieves grid from Redis
    ↓
Calls apply_one_step(grid) (stub for now)
    ↓
Updates grid in Redis with new state
    ↓
Returns: {
  "grid": number[][],
  "step": {"rule": string, "row": number, "col": number, "value": number},
  "done": boolean
}
    ↓
Frontend updates grid state with response.grid
    ↓
UI displays updated grid and step information
    ↓
If done=true, "Next Step" button is disabled
```

**End Session:**
```
User clicks "End Session" button
    ↓
handleEndSession() function executes
    ↓
Calls deleteSession(sessionId) from api service
    ↓
Frontend: DELETE /api/sessions/{session_id}
    ↓
[Vite Proxy (dev) or Nginx (prod)]
    ↓
Backend: DELETE /api/sessions/{session_id}
    ↓
FastAPI deletes session from Redis
    ↓
Returns: {"deleted": boolean}
    ↓
Frontend clears session state
    ↓
UI returns to initial state
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

// Solve Function (Full Solve)
export async function solve(request: SolveRequest): Promise<SolveResponse> {
  const response = await fetch(`${API_BASE}/solve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  return response.json();
}

// Session Functions (Stepwise Solving)
export async function createSession(grid: Grid, debug_level = 0): Promise<SessionCreateResponse> {
  const res = await fetch(`${API_BASE}/sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ grid, debug_level }),
  });
  return res.json();
}

export async function stepSession(sessionId: string): Promise<StepResponse> {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}/step`, {
    method: 'POST',
  });
  return res.json();
}

export async function deleteSession(sessionId: string): Promise<{ deleted: boolean }> {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}`, {
    method: 'DELETE',
  });
  return res.json();
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

### Solve Endpoint (Full Solve)

```python
@app.post("/api/solve", response_model=SolveResponse)
async def solve_sudoku(request: SolveRequest) -> SolveResponse:
    # Integrated with SudokuSolver engine
    solver = SudokuSolver(request.grid, debug_level=request.debug_level)
    ok = solver.solve()
    solution_grid = _to_int_grid(solver)
    return SolveResponse(
        solution=solution_grid,
        success=bool(ok),
        message="Solved" if ok else "Unsolved or invalid"
    )
```

**What happens:**
1. FastAPI receives HTTP request
2. Pydantic validates request body against `SolveRequest` model
3. Creates SudokuSolver instance with grid and debug level
4. Solves puzzle completely (all steps at once)
5. Extracts solution grid
6. Returns SolveResponse with solution, success status, and message

### Session Endpoints (Stepwise Solving)

**Create Session:**
```python
@app.post("/api/sessions")
async def create_session(payload: StepSessionCreate) -> Dict[str, str]:
    r = get_redis()
    session_id = uuid.uuid4().hex
    data = {"grid": payload.grid, "debug_level": payload.debug_level}
    r.set(f"sudoku:session:{session_id}", json.dumps(data))
    return {"session_id": session_id}
```

**Apply Step:**
```python
@app.post("/api/sessions/{session_id}/step", response_model=StepResponse)
async def step_session(session_id: str) -> StepResponse:
    r = get_redis()
    raw = r.get(f"sudoku:session:{session_id}")
    if raw is None:
        raise HTTPException(status_code=404, detail="Session not found")
    
    data = json.loads(raw)
    grid = data["grid"]
    new_grid, step_info_dict, done = apply_one_step(grid)
    
    data["grid"] = new_grid
    r.set(f"sudoku:session:{session_id}", json.dumps(data))
    
    return StepResponse(grid=new_grid, step=StepInfo(**step_info_dict), done=done)
```

**Delete Session:**
```python
@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str) -> Dict[str, bool]:
    r = get_redis()
    exists = r.delete(f"sudoku:session:{session_id}")
    return {"deleted": bool(exists)}
```

**What happens:**
1. FastAPI receives HTTP request
2. Pydantic validates request body/models
3. Redis client retrieves/updates session data
4. Step solver applies one solving step (stub currently)
5. Updated grid state persisted in Redis
6. FastAPI returns JSON response with updated state

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
| Solve Endpoint | `@app.post("/api/solve")` | Full puzzle solving endpoint |
| Session Endpoints | `@app.post("/api/sessions")`, `@app.post("/api/sessions/{id}/step")`, `@app.delete("/api/sessions/{id}")` | Stepwise solving endpoints |
| Step Solver | `web/backend/step_solver.py` | Step-wise solving logic (stub) |
| Redis Client | `get_redis()` in `app.py` | Session state storage |
| Pydantic Models | `SolveRequest`, `SolveResponse`, `StepSessionCreate`, `StepInfo`, `StepResponse` | Data validation models |

### Infrastructure

| Component | File | Purpose |
|-----------|------|---------|
| Vite Config | `vite.config.ts` | Dev server proxy configuration |
| Nginx Config | `web/nginx/nginx.conf` | Production reverse proxy |
| Docker Compose | `web/docker-compose.yml` | Container orchestration (includes Redis service) |
| Redis | Docker service | Session state storage backend |

---

## 🎯 Key Architectural Principles

1. **Separation of Concerns**: Frontend handles UI, backend handles logic
2. **Type Safety**: TypeScript on frontend, Pydantic on backend
3. **Environment-Aware**: Different routing for dev vs production
4. **Abstraction**: API service layer isolates components from HTTP details
5. **Validation**: Both frontend (TypeScript) and backend (Pydantic) validate data
6. **Proxy/Routing**: Vite (dev) or Nginx (prod) handles API routing
7. **Session State**: Redis-backed sessions for stepwise solving (experimental feature)

---

## 🚀 Future Integration Points

1. **Step Solver Integration**: Replace stub in `step_solver.py` with real one-step wrapper around `SudokuSolver`
2. **Add OCR Endpoint**: For image-based puzzle input
3. **Session Persistence**: Consider TTL for sessions to auto-cleanup
4. **Error Handling**: More detailed error responses for session endpoints
5. **Session History**: Track step-by-step history in Redis for undo/redo functionality

The current architecture supports both full solve and stepwise solving workflows!

---

## 📚 Related Documentation

- [Web README](../web/README.md) - General web application documentation
- [Deployment Guide](../web/README-deploy-images.md) - How to deploy to production
- [Frontend README](../web/frontend/README.md) - Frontend-specific documentation

---

**Last Updated:** 2025-01-XX (Added Redis-backed stepwise solving support)

