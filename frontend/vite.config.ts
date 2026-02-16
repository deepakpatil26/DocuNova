/// <reference types="vitest" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (!id.includes('node_modules')) return;

          if (id.includes('firebase')) return 'firebase';
          if (
            id.includes('react-markdown') ||
            id.includes('remark-gfm') ||
            id.includes('react-syntax-highlighter')
          ) {
            return 'markdown';
          }
          if (id.includes('@tanstack/react-query')) return 'react-query';
          if (id.includes('framer-motion')) return 'motion';

          return undefined;
        },
      },
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
  },
});
