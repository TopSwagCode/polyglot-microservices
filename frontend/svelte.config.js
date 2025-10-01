import adapter from '@sveltejs/adapter-node';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';
import { mdsvex } from 'mdsvex';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	// Enable both standard Svelte preprocessing and MDX/Markdown via mdsvex
	preprocess: [vitePreprocess(), mdsvex({
		extensions: ['.md', '.svx', '.mdx'],
		layout: {
			_: './src/lib/components/MarkdownLayout.svelte'
		}
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
