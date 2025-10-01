<script lang="ts">
	import { page } from '$app/state';
	interface Task { id:string; title:string; completed:boolean; }
	let tasks: Task[] = [];
	let newTask = '';
	let loading = true;
	const projectId = $derived(page.params.id);

	async function load() {
		loading = true;
		await new Promise(r => setTimeout(r, 200));
		tasks = [
			{ id:'1', title:'Provision infrastructure', completed:true },
			{ id:'2', title:'Implement API endpoints', completed:false },
			{ id:'3', title:'Wire analytics events', completed:false }
		];
		loading = false;
	}
	load();

	function toggle(t: Task) { t.completed = !t.completed; tasks = [...tasks]; }
	function addTask() { if(!newTask.trim()) return; tasks = [...tasks, { id:crypto.randomUUID(), title:newTask.trim(), completed:false }]; newTask=''; }
</script>

<svelte:head><title>Project {projectId}</title></svelte:head>

<a href="/dashboard" class="btn ghost" style="margin-bottom:1rem;">← Back</a>
<h1 style="margin:0 0 1.25rem;">Project {projectId}</h1>
{#if loading}
	<p>Loading tasks...</p>
{:else}
	<div class="stack" style="max-width:640px;">
		<ul class="list-reset stack" style="gap:.4rem;">
			{#each tasks as t}
				<li class="card row" style="align-items:center; justify-content:space-between;">
					<button on:click={() => toggle(t)} class="btn outline" style="padding:.4rem .7rem; font-size:.65rem; min-width:84px;">{t.completed ? 'Completed' : 'Pending'}</button>
					<div style="flex:1; margin:0 .9rem; text-decoration:{t.completed ? 'line-through' : 'none'}; color:{t.completed? 'var(--color-text-dim)':'var(--color-text)'};">{t.title}</div>
					<input type="checkbox" checked={t.completed} on:change={() => toggle(t)} aria-label="mark complete" />
				</li>
			{/each}
		</ul>
		<form on:submit|preventDefault={addTask} class="row" style="gap:.75rem;">
			<input placeholder="New task..." bind:value={newTask} />
			<button class="btn" disabled={!newTask.trim()}>Add</button>
		</form>
	</div>
{/if}
