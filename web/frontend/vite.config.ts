import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // Base path for production builds (e.g., '/sudokusolver/')
  // Defaults to '/' for development
  base: process.env.VITE_BASE_PATH || '/',
  server: {
    proxy: {
      // Proxy API requests to the backend server
      // In dev mode: localhost:5173/api/* -> localhost:8000/api/*
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      }
    }
  }
})
