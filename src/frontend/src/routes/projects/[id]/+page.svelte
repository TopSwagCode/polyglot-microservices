<script lang="ts">
	import { page } from '$app/state';
	import { apiClient } from '$lib/api';
	import { auth } from '$lib/stores/auth';
		interface Task { id:number|string; title:string; status:string; description?:string; project_id:number|string; priority?:string; }
		let tasks = $state<Task[]>([]);
		let newTask = $state('');
		let loading = $state(true);
		let error = $state<string|null>(null);
		const projectId = $derived(page.params.id);

			async function load() {
				loading = true; error = null;
		try {
				// Prefer /projects/{id} if it returns tasks array, else fallback to /tasks?project_id
				try {
					const proj: any = await apiClient.get(`/projects/${projectId}`, { auth:true });
					if (Array.isArray(proj)) {
						tasks = proj as Task[];
					} else if (Array.isArray(proj?.tasks)) {
						tasks = proj.tasks as Task[];
					} else {
						// fallback
						const data = await apiClient.get<Task[]>(`/tasks?project_id=${projectId}`, { auth: true });
						tasks = data;
					}
				} catch (inner) {
					const data = await apiClient.get<Task[]>(`/tasks?project_id=${projectId}`, { auth: true });
					tasks = data;
				}
		} catch (e: any) { error = e.body?.message || e.message; }
			loading = false;
	}
			let _loaded = false;
			$effect(() => { if (!_loaded) { _loaded = true; load(); } });

		async function toggle(t: Task) {
			try {
				const current = t.status?.toLowerCase();
				const newStatus = current === 'completed' ? 'open' : 'completed';
				const updated = await apiClient.put<Task>(`/tasks/${t.id}`, { status: newStatus }, { auth:true });
				tasks = tasks.map(x => x.id === t.id ? updated : x);
			} catch (e: any) { error = e.body?.message || e.message; }
		}
		async function addTask() {
			if(!newTask.trim()) return; error=null;
			try {
				const created = await apiClient.post<Task>('/tasks', { title: newTask.trim(), project_id: Number(projectId) }, { auth:true });
				tasks = [...tasks, created]; newTask='';
			} catch (e: any) { error = e.body?.message || e.message; }
		}
</script>

<svelte:head><title>Project {projectId}</title></svelte:head>

<a href="/dashboard" class="btn ghost" style="margin-bottom:1rem;">← Back</a>
<h1 style="margin:0 0 1.25rem;">Project {projectId}</h1>
{#if error}
	<p style="color:var(--color-negative);">{error}</p>
{/if}
{#if loading}
	<p>Loading tasks...</p>
{:else}
	<div class="stack" style="max-width:640px;">
			<ul class="list-reset stack" style="gap:.4rem;">
						{#each tasks as t}
							<li class="card" style="gap:.55rem;">
								<div class="row" style="justify-content:space-between; align-items:center;">
									<strong style="font-size:.95rem;">{t.title}</strong>
									<div class="row" style="gap:.4rem;">
										<span class="badge {t.status==='completed' ? 'success':'pending'}">{t.status}</span>
										<button class="btn outline" style="padding:.35rem .6rem; font-size:.6rem;" onclick={() => toggle(t)}>{t.status==='completed' ? 'Reopen' : 'Complete'}</button>
									</div>
								</div>
								{#if t.description}
									<p style="margin:.1rem 0 0; font-size:.75rem; color:var(--color-text-dim);">{t.description}</p>
								{/if}
							</li>
						{/each}
			</ul>
				<form class="row" style="gap:.5rem;" onsubmit={(e)=>{e.preventDefault(); addTask();}}>
					<input placeholder="New task..." bind:value={newTask} class="input" />
					<button class="btn" disabled={!newTask.trim()}>Add</button>
				</form>
	</div>
{/if}
