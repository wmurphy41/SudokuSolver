/**
 * Application configuration
 * 
 * Environment variables are read at BUILD TIME by Vite (not runtime).
 * Any changes to .env files require a rebuild or dev server restart.
 * 
 * Vite exposes env variables prefixed with VITE_ via import.meta.env
 */

// API base URL - defaults to '/api' if not set in environment
export const API_BASE = import.meta.env.VITE_API_BASE ?? '/api';

