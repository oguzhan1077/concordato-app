import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Railway production build config
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: process.env.PORT || 4173,
    strictPort: true
  },
  preview: {
    host: '0.0.0.0',
    port: process.env.PORT || 4173,
    strictPort: true
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    minify: 'terser'
  }
})

