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
	</footer>
	<div class="social-fabs">
		<a href="https://github.com/TopSwagCode/polyglot-microservices" class="icon-link" aria-label="GitHub repository" rel="noopener" target="_blank">
			<svg viewBox="0 0 16 16" width="24" height="24" role="img" aria-hidden="true">
				<path fill="currentColor" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8Z" />
			</svg>
		</a>
		<a href="https://linkedin.com/in/joshua-ryder-4996b33b" class="icon-link" aria-label="LinkedIn profile" rel="noopener" target="_blank">
			<svg viewBox="0 0 16 16" width="24" height="24" role="img" aria-hidden="true">
				<path fill="currentColor" d="M0 1.146C0 .513.526 0 1.175 0h13.65C15.474 0 16 .513 16 1.146v13.708c0 .633-.526 1.146-1.175 1.146H1.175C.526 16 0 15.487 0 14.854V1.146zm4.943 12.248V6.169H2.542v7.225h2.401zm-1.2-8.212c.837 0 1.358-.554 1.358-1.248-.015-.709-.52-1.248-1.342-1.248-.822 0-1.359.54-1.359 1.248 0 .694.521 1.248 1.327 1.248h.016zM13.458 13.394V9.359c0-2.162-1.153-3.169-2.695-3.169-1.24 0-1.796.681-2.105 1.16V6.169H6.257c.03.678 0 7.225 0 7.225h2.401v-4.035c0-.216.016-.432.08-.586.173-.431.568-.878 1.232-.878.869 0 1.216.663 1.216 1.635v3.864h2.272z" />
			</svg>
		</a>
	</div>

</div>

<style>
	.layout-root { min-height:100vh; display:flex; flex-direction:column; }
	main { flex:1; padding:2.2rem 0 3rem; }
	.footer { font-size:.7rem; letter-spacing:.05em; text-transform:uppercase; opacity:.4; padding:1rem 0 2rem; }
	.social-fabs { position:fixed; bottom:1.1rem; right:1.1rem; display:flex; flex-direction:column; gap:.7rem; z-index:1000; }
	.social-fabs .icon-link { width:3.1rem; height:3.1rem; display:inline-flex; align-items:center; justify-content:center; border-radius:.9rem; background:rgba(30,30,35,.55); backdrop-filter:blur(8px); -webkit-backdrop-filter:blur(8px); color:var(--color-accent); box-shadow:0 4px 18px -4px rgba(0,0,0,.55); outline:1px solid rgba(255,255,255,.04); transition:background .25s, transform .25s, box-shadow .25s; }
	.social-fabs .icon-link svg { opacity:.9; transition:opacity .25s; }
	.social-fabs .icon-link:hover { background:var(--color-accent); color:var(--color-bg); transform:translateY(-3px); box-shadow:0 8px 26px -6px rgba(0,0,0,.65); }
	.social-fabs .icon-link:hover svg { opacity:1; }
	@media (max-width: 640px){
		.social-fabs { bottom:.85rem; right:.85rem; gap:.55rem; }
		.social-fabs .icon-link { width:2.7rem; height:2.7rem; border-radius:.75rem; }
	}
	@media (prefers-reduced-motion: reduce){
		.social-fabs .icon-link { transition:none; }
		.social-fabs .icon-link:hover { transform:none; }
	}
</style>
