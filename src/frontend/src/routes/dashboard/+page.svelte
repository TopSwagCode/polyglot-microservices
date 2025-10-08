<script lang="ts">
	import { auth } from '$lib/stores/auth';
	import { goto } from '$app/navigation';
	import { apiClient } from '$lib/api';
		interface Project { id:string|number; name:string; openTasks?:number; completed?:number; }
		let projects = $state<Project[]>([]);
		let loading = $state(true);
		let error = $state<string|null>(null);
			let creating = $state(false);
			let newProjectName = $state('');

		async function load() {
			if (!$auth.token) { goto('/login'); return; }
			loading = true; error = null;
			try {
				const data = await apiClient.get<Project[]>('/projects', { auth: true });
				projects = data;
			} catch (e: any) {
				error = e.body?.message || e.message;
			} finally {
				loading = false;
			}
		}
			let _loaded = false;
			$effect(() => {
				if (!_loaded) { _loaded = true; load(); }
			});

			async function createProject() {
				if (!newProjectName.trim() || creating) return;
				creating = true; error = null;
				const provisional: Project = { id: 'temp-' + Date.now(), name: newProjectName.trim() };
				projects = [provisional, ...projects]; // optimistic
				try {
					const created = await apiClient.post<Project>('/projects', { name: newProjectName.trim() }, { auth:true });
					// replace provisional
					projects = projects.map(p => p.id === provisional.id ? created : p);
					newProjectName = '';
				} catch (e: any) {
					// rollback
					projects = projects.filter(p => p.id !== provisional.id);
					error = e.body?.message || e.message;
				} finally { creating = false; }
			}
</script>

<svelte:head><title>Dashboard</title></svelte:head>

<h1 style="margin:0 0 1.5rem;">Dashboard</h1>
<form onsubmit={(e)=>{e.preventDefault(); createProject();}} class="row" style="gap:.75rem; margin:0 0 1.25rem; flex-wrap:wrap;">
	<input placeholder="New project name" bind:value={newProjectName} class="input" style="flex:1; min-width:220px;" />
	<button class="btn" disabled={!newProjectName.trim() || creating}>{creating ? 'Creating...' : 'Add Project'}</button>
</form>
{#if error}
  <p style="color:var(--color-negative);">{error}</p>
{/if}
{#if loading}
  <p>Loading projects...</p>
{:else if projects.length === 0}
  <p>No projects yet.</p>
{:else}
	<div class="grid project-grid">
		{#each projects as p (p.id)}
			<a class="card interactive project-card" data-temp={String(p.id).startsWith('temp-')} href={`/projects/${p.id}`}>
				<strong style="font-size:1rem;">{p.name}</strong>
			</a>
		{/each}
	</div>
{/if}

<style>
	.project-grid { display:grid; gap:1rem; grid-template-columns:repeat(auto-fill,minmax(240px,1fr)); position:relative; }
	.project-card { --delay:0ms; opacity:0; transform:translateY(14px) scale(.96); animation:cardIn .75s cubic-bezier(.65,.05,.36,1) forwards; background:linear-gradient(155deg,#1b222a,#181e25); overflow:hidden; }
	/* Stagger existing on initial load */
	.project-card:nth-child(1){ animation-delay:40ms; }
	.project-card:nth-child(2){ animation-delay:80ms; }
	.project-card:nth-child(3){ animation-delay:120ms; }
	.project-card:nth-child(4){ animation-delay:160ms; }
	.project-card:nth-child(5){ animation-delay:200ms; }
	.project-card:nth-child(6){ animation-delay:240ms; }
	/* Provisional (optimistic) project pops with pulse */
	.project-card[data-temp='true'] { animation:popIn .6s cubic-bezier(.55,1.4,.5,1) forwards, glow 2.2s ease 0.6s forwards; position:relative; }
	.project-card[data-temp='true']:after { content:"Creating..."; position:absolute; top:6px; right:8px; font-size:.55rem; letter-spacing:.08em; text-transform:uppercase; background:rgba(255,255,255,.06); padding:.25rem .4rem; border-radius:4px; }
	.project-card:hover { background:linear-gradient(155deg,#202a34,#1d242c); }
	.project-card:focus-visible { outline:2px solid var(--color-accent); outline-offset:2px; }
	@keyframes cardIn { 0% { opacity:0; transform:translateY(14px) scale(.96); } 55% { opacity:1; } 100% { opacity:1; transform:translateY(0) scale(1); } }
	@keyframes popIn { 0% { opacity:0; transform:scale(.65) translateY(10px); } 60% { opacity:1; transform:scale(1.04) translateY(0); } 100% { opacity:1; transform:scale(1); } }
	@keyframes glow { 0% { box-shadow:0 0 0 0 rgba(120,180,255,.0); } 40% { box-shadow:0 0 0 4px rgba(120,180,255,.15); } 100% { box-shadow:0 0 0 0 rgba(120,180,255,0); } }
	@media (prefers-reduced-motion:reduce){
		.project-card, .project-card[data-temp='true'] { animation:none !important; opacity:1 !important; transform:none !important; }
		.project-card[data-temp='true']:after { content:"Creating"; }
	}
</style>
