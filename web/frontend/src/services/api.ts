/**
 * API Service
 * 
 * Functions for communicating with the FastAPI backend.
 * All API calls are typed using the interfaces from types/api.ts
 */

import { API_BASE } from '../config';
import type { SolveRequest, SolveResponse, Healthz, Grid, StepResponse, SessionCreateResponse } from '../types/api';

/**
 * Check backend health status
 * 
 * @returns Promise resolving to health status
 * @throws Error if the request fails
 */
export async function getHealth(): Promise<Healthz> {
  const response = await fetch(`${API_BASE}/healthz`);
  
  if (!response.ok) {
    throw new Error(`Health check failed: ${response.statusText}`);
  }
  
  return response.json();
}

/**
 * Solve a sudoku puzzle
 * 
 * @param request - Solve request containing 9x9 grid and optional debug_level
 * @returns Promise resolving to solve response with solution grid
 * @throws Error if the request fails
 */
export async function solve(request: SolveRequest): Promise<SolveResponse> {
  const response = await fetch(`${API_BASE}/solve`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });
  
  if (!response.ok) {
    throw new Error(`Solve request failed: ${response.statusText}`);
  }
  
  return response.json();
}

/**
 * Create a new step-wise solving session
 * 
 * @param grid - 9x9 grid to start solving
 * @param debug_level - Optional debug level (default: 0)
 * @returns Promise resolving to session creation response with session_id
 * @throws Error if the request fails
 */
export async function createSession(grid: Grid, debug_level = 0): Promise<SessionCreateResponse> {
  const res = await fetch(`${API_BASE}/sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ grid, debug_level }),
  });
  if (!res.ok) {
    throw new Error(await res.text());
  }
  return res.json();
}

/**
 * Apply one step to a solving session
 * 
 * @param sessionId - Session identifier
 * @returns Promise resolving to step response with updated grid and step info
 * @throws Error if the request fails
 */
export async function stepSession(sessionId: string): Promise<StepResponse> {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}/step`, {
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error(await res.text());
  }
  return res.json();
}

/**
 * Delete a solving session
 * 
 * @param sessionId - Session identifier
 * @returns Promise resolving to deletion status
 * @throws Error if the request fails
 */
export async function deleteSession(sessionId: string): Promise<{ deleted: boolean }> {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}`, {
    method: 'DELETE',
  });
  if (!res.ok) {
    throw new Error(await res.text());
  }
  return res.json();
}

