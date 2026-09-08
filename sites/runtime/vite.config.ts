import { defineConfig } from 'vite';
import { sites } from '@openai/sites-vite-plugin';
export default defineConfig({
  plugins: [sites()],
  build: { ssr: 'worker.ts', outDir: 'dist', emptyOutDir: false,
    rollupOptions: { output: { entryFileNames: 'server/index.js' } } },
});
