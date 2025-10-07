import adapter from '@sveltejs/adapter-node';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';
import { mdsvex } from 'mdsvex';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const markdownLayoutPath = resolve(__dirname, 'src/lib/components/MarkdownLayout.svelte');

/** @type {import('@sveltejs/kit').Config} */
const config = {
	// Enable both standard Svelte preprocessing and MDX/Markdown via mdsvex
	preprocess: [vitePreprocess(), mdsvex({
		extensions: ['.md', '.svx', '.mdx'],
		layout: { _: markdownLayoutPath }
	})],
	kit: {
		// adapter-auto only supports some environments, see https://svelte.dev/docs/kit/adapter-auto for a list.
		// If your environment is not supported, or you settled on a specific environment, switch out the adapter.
		// See https://svelte.dev/docs/kit/adapters for more information about adapters.
        adapter: adapter({ out: 'build' })
	},
	extensions: ['.svelte', '.md', '.svx', '.mdx']
};

export default config;
