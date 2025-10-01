<script lang="ts">
	interface Metric { label:string; value:number; trend:number; }
	let metrics: Metric[] = [];
	let loading = true;
	async function load() {
		loading = true;
		await new Promise(r => setTimeout(r, 350));
		metrics = [
			{ label:'Total Tasks', value: 42, trend: 6 },
			{ label:'Completed Tasks', value: 27, trend: 3 },
			{ label:'Active Users', value: 5, trend: -1 },
			{ label:'Events / min', value: 128, trend: 14 }
		];
		loading = false;
	}
	load();
</script>

<svelte:head><title>Analytics</title></svelte:head>
<h1 style="margin:0 0 1.5rem;">Analytics</h1>
{#if loading}
	<p>Loading metrics...</p>
{:else}
	<div class="grid" style="display:grid; gap:1rem; grid-template-columns:repeat(auto-fit,minmax(200px,1fr));">
		{#each metrics as m}
			<div class="card" style="gap:.25rem;">
				<span style="font-size:.65rem; letter-spacing:.08em; text-transform:uppercase; color:var(--color-text-dim);">{m.label}</span>
				<strong style="font-size:1.7rem; letter-spacing:-.03em;">{m.value}</strong>
				<span class="badge {m.trend>=0 ? 'success':'pending'}" style="align-self:start;">{m.trend>=0 ? '+'+m.trend : m.trend}</span>
			</div>
		{/each}
	</div>
	<hr class="divider" />
	<p style="font-size:.8rem; color:var(--color-text-dim);">Metrics are mocked; wire up real analytics service calls later.</p>
{/if}
