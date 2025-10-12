/**
 * API Service
 * 
 * Functions for communicating with the FastAPI backend.
 * All API calls are typed using the interfaces from types/api.ts
 */

import { API_BASE } from '../config';
import type { SolveRequest, SolveResponse, Healthz } from '../types/api';

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

