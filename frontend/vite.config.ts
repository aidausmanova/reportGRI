import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  css: {
    preprocessorOptions: {
      css: {
        // No special settings needed for Tailwind by default
      }
    }
  },
  server: {
    port: 5173,
    open: true,
  }
})
