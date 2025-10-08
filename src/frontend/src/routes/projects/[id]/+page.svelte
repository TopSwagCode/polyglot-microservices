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
			// optimistic provisional
			const provisional: Task = { id: 'temp-' + Date.now(), title: newTask.trim(), status: 'open', project_id: projectId };
			tasks = [provisional, ...tasks];
			const enteredTitle = newTask.trim();
			newTask='';
			try {
				const created = await apiClient.post<Task>('/tasks', { title: enteredTitle, project_id: Number(projectId) }, { auth:true });
				// replace provisional (keep order at front)
				tasks = tasks.map(t => t.id === provisional.id ? created : t);
			} catch (e: any) {
				// rollback
				tasks = tasks.filter(t => t.id !== provisional.id);
				error = e.body?.message || e.message;
			}
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
	<div class="tasks-wrapper">
		<form class="add-task" onsubmit={(e)=>{e.preventDefault(); addTask();}} aria-label="Add task form">
			<input placeholder="New task..." bind:value={newTask} class="input" />
			<button class="btn" disabled={!newTask.trim()}>Add Task</button>
		</form>
		{#if tasks.length === 0}
			<p style="margin-top:1rem;">No tasks yet.</p>
		{:else}
			<div class="task-grid">
				{#each tasks as t (t.id)}
					<div class="task-card" data-status={t.status} data-temp={String(t.id).startsWith('temp-')}>
						<header class="task-head">
							<strong class="task-title">{t.title}</strong>
							<div class="task-meta">
								<span class="badge {t.status==='completed' ? 'success':'pending'}">{t.status}</span>
								<button class="btn outline sm" onclick={() => toggle(t)}>{t.status==='completed' ? 'Reopen' : 'Complete'}</button>
							</div>
						</header>
						{#if t.description}
							<p class="desc">{t.description}</p>
						{/if}
					</div>
				{/each}
			</div>
		{/if}
	</div>
{/if}

<style>
  .tasks-wrapper { max-width:1100px; margin:0 0 2rem; display:flex; flex-direction:column; gap:1.25rem; }
  .add-task { display:flex; gap:.75rem; flex-wrap:wrap; align-items:center; background:linear-gradient(145deg,#1b2128,#161c22); padding:.9rem 1rem; border:1px solid var(--color-border); border-radius:var(--radius-md); box-shadow:var(--shadow-sm); }
  .add-task .input { flex:1; min-width:240px; }
  .task-grid { --min:250px; display:grid; gap:1rem; grid-template-columns:repeat(auto-fill,minmax(var(--min),1fr)); }
  .task-card { position:relative; display:flex; flex-direction:column; gap:.45rem; padding:1rem .95rem 1rem; background:linear-gradient(155deg,#1c232b,#182026 70%); border:1px solid var(--color-border); border-radius:var(--radius-md); box-shadow:0 2px 6px -2px rgba(0,0,0,.55), inset 0 0 0 1px rgba(255,255,255,.02); opacity:0; transform:translateY(14px) scale(.96); animation:taskIn .75s cubic-bezier(.65,.05,.36,1) forwards; overflow:hidden; }
  /* Stagger entrance */
  .task-card:nth-child(1){ animation-delay:40ms; }
  .task-card:nth-child(2){ animation-delay:80ms; }
  .task-card:nth-child(3){ animation-delay:120ms; }
  .task-card:nth-child(4){ animation-delay:160ms; }
  .task-card:nth-child(5){ animation-delay:200ms; }
  .task-card[data-temp='true'] { animation:popIn .6s cubic-bezier(.55,1.4,.5,1) forwards, glow 2.2s ease 0.6s forwards; }
  .task-card[data-temp='true']::after { content:'Saving'; position:absolute; top:6px; right:8px; font-size:.55rem; letter-spacing:.07em; text-transform:uppercase; background:rgba(255,255,255,.06); padding:.25rem .4rem; border-radius:4px; }
  .task-card[data-status='completed'] { background:linear-gradient(170deg,#1d252b,#1a2425 60%, #1a261f); }
  .task-card[data-status='completed'] .task-title { text-decoration:line-through; opacity:.75; }
  .task-card:hover { border-color:var(--color-border-strong); background:linear-gradient(155deg,#222c35,#1c252c 70%); }
  .task-head { display:flex; justify-content:space-between; align-items:flex-start; gap:.75rem; }
  .task-title { font-size:.95rem; font-weight:600; letter-spacing:.01em; }
  .task-meta { display:flex; align-items:center; gap:.45rem; }
  .btn.sm { padding:.4rem .65rem; font-size:.6rem; line-height:1; }
  .desc { margin:.15rem 0 0; font-size:.7rem; color:var(--color-text-dim); line-height:1.35; }
  @keyframes taskIn { 0% { opacity:0; transform:translateY(14px) scale(.96);} 55% { opacity:1;} 100% { opacity:1; transform:translateY(0) scale(1);} }
  @keyframes popIn { 0% { opacity:0; transform:scale(.65) translateY(10px);} 60% { opacity:1; transform:scale(1.05) translateY(0);} 100% { opacity:1; transform:scale(1);} }
  @keyframes glow { 0% { box-shadow:0 0 0 0 rgba(120,180,255,.0);} 40% { box-shadow:0 0 0 4px rgba(120,180,255,.18);} 100% { box-shadow:0 0 0 0 rgba(120,180,255,0);} }
  @media (prefers-reduced-motion:reduce){
    .task-card { animation:none !important; opacity:1 !important; transform:none !important; }
    .task-card[data-temp='true'] { animation:none !important; }
  }
</style>
