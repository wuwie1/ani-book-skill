import { readFileSync } from 'node:fs';
import { defineConfig } from 'vite';
import { viteSingleFile } from 'vite-plugin-singlefile';

const notices = ['react', 'react-dom', 'scheduler', 'three', 'lucide-react'].map(name => {
  const license = readFileSync(new URL('./node_modules/' + name + '/LICENSE', import.meta.url), 'utf8');
  return name + '\n' + license.trim();
}).join('\n\n');

// Include the illustrated plates so the author can open the finished atlas from disk.
export default defineConfig({
  build: { outDir: '离线地图', emptyOutDir: false },
  plugins: [
    viteSingleFile(),
    {
      name: 'atlas-license-notices',
      transformIndexHtml: () => [{ tag: 'script', attrs: { type: 'text/plain', id: '开源组件许可' }, children: notices, injectTo: 'body' }]
    }
  ]
});
