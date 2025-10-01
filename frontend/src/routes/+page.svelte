<script lang="ts">
	import { auth } from '$lib/stores/auth';
	import { goto } from '$app/navigation';

	// Redirect authenticated users to dashboard
	$effect(() => {
		if ($auth.user) {
			goto('/dashboard');
		}
	});
</script>

<svelte:head>
	<title>Polyglot Microservices Platform</title>
	<meta name="description" content="Polyglot microservices demo platform across .NET, Go, Python." />
</svelte:head>

{#if !$auth.user}
<div class="hero stack-lg">
	<div class="stack" style="max-width:780px; margin-inline:auto; text-align:center;">
		<h1 style="margin:0;">Ship faster with a polyglot microservices stack</h1>
		<p style="margin:0; font-size:1.05rem; color:var(--color-text-dim);">Explore a modern demo platform combining <strong>.NET</strong>, <strong>Go</strong> and <strong>Python</strong> services behind a unified API gateway. Events & analytics—simplified.</p>
		<div class="row center" style="gap:1rem; margin-top:.5rem;">
			<a href="/login" class="btn">Login</a>
			<a href="/register" class="btn outline">Register User</a>
		</div>
	</div>
	<hr class="divider" />
	<div class="grid" style="display:grid; gap:1.25rem; grid-template-columns:repeat(auto-fit,minmax(240px,1fr));">
		<div class="card">
			<h3 style="margin:.2rem 0 .4rem; font-size:.95rem; letter-spacing:.05em; text-transform:uppercase; color:var(--color-text-dim);">Gateway</h3>
			<p style="margin:0; font-size:.9rem; color:var(--color-text-dim);">Single entrypoint with future YARP reverse proxy routing to language-specific services.</p>
		</div>
		<div class="card">
			<h3 style="margin:.2rem 0 .4rem; font-size:.95rem; letter-spacing:.05em; text-transform:uppercase; color:var(--color-text-dim);">Task Service</h3>
			<p style="margin:0; font-size:.9rem; color:var(--color-text-dim);">Go service emitting events and managing project tasks.</p>
		</div>
		<div class="card">
			<h3 style="margin:.2rem 0 .4rem; font-size:.95rem; letter-spacing:.05em; text-transform:uppercase; color:var(--color-text-dim);">Auth & Identity</h3>
			<p style="margin:0; font-size:.9rem; color:var(--color-text-dim);">.NET based token issuance with JWT placeholder for local demo.</p>
		</div>
		<div class="card">
			<h3 style="margin:.2rem 0 .4rem; font-size:.95rem; letter-spacing:.05em; text-transform:uppercase; color:var(--color-text-dim);">Analytics</h3>
			<p style="margin:0; font-size:.9rem; color:var(--color-text-dim);">Python FastAPI service aggregating events for dashboards.</p>
		</div>
	</div>
</div>
{/if}

<style>
	.hero { padding:2rem 0 3rem; }
</style>
