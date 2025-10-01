#!/usr/bin/env node
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import path from 'node:path';

async function main() {
  const root = path.resolve(process.cwd(), '..');
  const srcFile = path.join(root, 'DEVELOPER_TOOLS.md');
  const destDir = path.join(process.cwd(), 'src', 'routes', 'devtools');
  const destFile = path.join(destDir, '+page.md');

  try {
    const raw = await readFile(srcFile, 'utf-8');
    await mkdir(destDir, { recursive: true });
    const banner = `---\nlayout: ./src/lib/components/MarkdownLayout.svelte\ntitle: Developer Tools\n---\n`;
    await writeFile(destFile, banner + raw, 'utf-8');
    console.log('Synced devtools markdown to', destFile);
  } catch (err) {
    console.error('Failed to sync developer tools markdown:', err);
    process.exit(1);
  }
}

main();
