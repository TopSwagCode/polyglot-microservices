<script lang="ts">
	import { auth } from '$lib/stores/auth';
	import { goto } from '$app/navigation';
	import { apiClient } from '$lib/api';
		interface Project { id:string|number; name:string; openTasks?:number; completed?:number; }
		let projects = $state<Project[]>([]);
		let loading = $state(true);
		let error = $state<string|null>(null);

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
</script>

<svelte:head><title>Dashboard</title></svelte:head>

<h1 style="margin:0 0 1.5rem;">Dashboard</h1>
{#if error}
  <p style="color:var(--color-negative);">{error}</p>
{/if}
{#if loading}
  <p>Loading projects...</p>
{:else if projects.length === 0}
  <p>No projects yet.</p>
{:else}
  <div class="grid" style="display:grid; gap:1rem; grid-template-columns:repeat(auto-fill,minmax(240px,1fr));">
    {#each projects as p}
      <a class="card interactive" href={`/projects/${p.id}`}>
        <strong style="font-size:1rem;">{p.name}</strong>
      </a>
    {/each}
  </div>
{/if}
