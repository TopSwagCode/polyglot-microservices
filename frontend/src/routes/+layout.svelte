<script lang="ts">
	import '../app.css';
	import Navbar from '$lib/components/Navbar.svelte';
	let { children } = $props();
</script>

<div class="layout-root">
	<Navbar />
	<main class="container fade-in">
		{@render children()}
	</main>
	<footer class="footer container">
		<div class="meta">Polyglot Microservices Demo · <a href="https://github.com/TopSwagCode" rel="noopener" target="_blank">GitHub</a></div>
	</footer>
</div>

<style>
	.layout-root { min-height:100vh; display:flex; flex-direction:column; }
	main { flex:1; padding:2.2rem 0 3rem; }
	.footer { font-size:.7rem; letter-spacing:.05em; text-transform:uppercase; opacity:.55; padding:2rem 0 3rem; }
	.footer a { color:var(--color-text-dim); }
	.footer a:hover { color:var(--color-text); }
</style>
