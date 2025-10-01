<script lang="ts">
	import { auth } from '$lib/stores/auth';
	import { goto } from '$app/navigation';
	interface Project { id:string; name:string; openTasks:number; completed:number; }
	let projects: Project[] = [];
	let loading = true;

	async function load() {
		loading = true;
		await new Promise(r => setTimeout(r, 300));
		// Placeholder; replace with /tasks/projects endpoint
		projects = [
			{ id:'a', name:'Project A', openTasks:3, completed:5 },
			{ id:'b', name:'Project B', openTasks:1, completed:9 },
			{ id:'c', name:'Project C', openTasks:0, completed:4 }
		];
		loading = false;
	}
	load();

	$effect(() => { if (!$auth.user) { /* allow guest view but could redirect */ } });
</script>

<svelte:head><title>Dashboard</title></svelte:head>

<h1 style="margin:0 0 1.5rem;">Dashboard</h1>
{#if loading}
	<p>Loading projects...</p>
{:else}
	{#if projects.length === 0}
		<p>No projects yet.</p>
	{:else}
		<div class="grid" style="display:grid; gap:1rem; grid-template-columns:repeat(auto-fill,minmax(240px,1fr));">
			{#each projects as p}
				<a class="card interactive" href={`/projects/${p.id}`}> 
					<strong style="font-size:1rem;">{p.name}</strong>
					<div class="row" style="justify-content:space-between; margin-top:.25rem;">
						<span class="badge pending">{p.openTasks} open</span>
						<span class="badge success">{p.completed} done</span>
					</div>
				</a>
			{/each}
		</div>
	{/if}
{/if}
