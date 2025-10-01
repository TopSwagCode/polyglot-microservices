<script lang="ts">
	import { apiClient } from '$lib/api';
	import { auth } from '$lib/stores/auth';
	import { onMount, onDestroy } from 'svelte';

	interface DashboardAnalytics {
	  total_tasks: number;
	  completed_tasks: number;
	  active_projects: number;
	  completion_rate: number; // 0..1
	  recent_activity: Array<{ type:string; event:string; task_id:number; project_id:number; timestamp:string }>;
	}
	interface TaskSummary {
	  total_tasks: number;
	  completed_tasks: number;
	  pending_tasks: number;
	  completion_rate: number;
	  tasks_by_status: Record<string, number>;
	  recent_completions: Array<{ task_id:number; project_id:number; title:string; completed_at:string }>;
	}
	interface Productivity {
	  daily_completions: Record<string, number>;
	  weekly_summary: { total_completions:number; avg_daily_completions:number; most_productive_day:string };
	  productivity_score: number;
	  recommendations: string[];
	}

	let dashboard = $state<DashboardAnalytics | null>(null);
	let summary = $state<TaskSummary | null>(null);
	let productivity = $state<Productivity | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let lastRefreshed = $state<Date | null>(null);

	async function fetchAll() {
	  if (!auth.token) {
	    error = 'Not authenticated';
	    loading = false;
	    return;
	  }
	  loading = true;
	  error = null;
	  try {
	    const [d,s,p] = await Promise.all([
	      apiClient.get<DashboardAnalytics>('/analytics/dashboard'),
	      apiClient.get<TaskSummary>('/analytics/tasks/summary'),
	      apiClient.get<Productivity>('/analytics/productivity')
	    ]);
	    dashboard = d;
	    summary = s;
	    productivity = p;
	    lastRefreshed = new Date();
	  } catch (e:any) {
	    console.error(e);
	    error = e?.message || 'Failed to load analytics';
	  } finally {
	    loading = false;
	  }
	}

	function formatPercent(v:number|undefined) { return v == null ? '-' : (v*100).toFixed(0)+'%'; }
	function formatDate(ts:string) { return new Date(ts).toLocaleString(); }

	let started = false;
	let prevToken: string | null = null;
	let unsub: (() => void) | null = null;

	onMount(() => {
	  // subscribe to auth store token changes explicitly
	  unsub = auth.subscribe(s => {
	    const token = s.token;
	    if (token && token !== prevToken) {
	      prevToken = token;
	      fetchAll();
	    }
	  });
	  // if token already present at mount, trigger once
	  const initialToken = auth.token;
	  if (initialToken) {
	    prevToken = initialToken;
	    fetchAll();
	  } else {
	    loading = false; // avoid perpetual loading without token
	  }
	  started = true;
	});

	onDestroy(() => { if (unsub) unsub(); });

</script>

<svelte:head><title>Analytics</title></svelte:head>
<h1 style="margin:0 0 1.5rem; display:flex; gap:.75rem; align-items:center;">Analytics
  <button class="btn subtle" onclick={fetchAll} disabled={loading} style="margin-left:auto; display:flex; gap:.35rem; align-items:center;">
    {#if loading}<span class="spinner" style="width:.75rem; height:.75rem; border:2px solid var(--color-border); border-top-color:var(--color-accent); border-radius:50%; animation:spin .6s linear infinite;"></span>{/if}
    <span>{loading ? 'Loading':'Refresh'}</span>
  </button>
</h1>
{#if error}
  <div class="card" style="border:1px solid var(--color-danger); background:rgba(220,53,69,.08);">
    <strong style="color:var(--color-danger);">Error:</strong> {error}
  </div>
{:else if loading}
  <p>Loading analytics...</p>
{:else if !dashboard || !summary}
  <p class="muted-label">No analytics data available.</p>
{:else}
  <div class="grid" style="display:grid; gap:1rem; grid-template-columns:repeat(auto-fit,minmax(200px,1fr));">
    <div class="card">
      <span class="muted-label">Total Tasks</span>
      <strong class="big-number">{dashboard.total_tasks}</strong>
      <span class="badge pending">{summary.pending_tasks} pending</span>
    </div>
    <div class="card">
      <span class="muted-label">Completed Tasks</span>
      <strong class="big-number">{dashboard.completed_tasks}</strong>
      <span class="badge success">{formatPercent(summary.completion_rate)}</span>
    </div>
    <div class="card">
      <span class="muted-label">Active Projects</span>
      <strong class="big-number">{dashboard.active_projects}</strong>
      <span class="badge neutral">Projects</span>
    </div>
    <div class="card">
      <span class="muted-label">Productivity Score</span>
      <strong class="big-number">{productivity?.productivity_score?.toFixed(1) ?? '-'}</strong>
      <span class="badge success">Score</span>
    </div>
  </div>

  <hr class="divider" />
  <h2 style="margin:.5rem 0 1rem; font-size:1rem;">Recent Activity</h2>
  {#if dashboard.recent_activity.length === 0}
    <p class="muted-label">No recent activity</p>
  {:else}
  <div class="card" style="padding:0; overflow:hidden;">
    <table style="width:100%; border-collapse:collapse; font-size:.75rem;">
      <thead style="background:var(--color-surface-alt); text-align:left;">
        <tr>
          <th style="padding:.5rem .75rem; font-weight:500;">Event</th>
          <th style="padding:.5rem .75rem; font-weight:500;">Task</th>
          <th style="padding:.5rem .75rem; font-weight:500;">Project</th>
          <th style="padding:.5rem .75rem; font-weight:500;">Timestamp</th>
        </tr>
      </thead>
      <tbody>
        {#each dashboard.recent_activity as a}
        <tr>
          <td style="padding:.4rem .75rem;">{a.event}</td>
          <td style="padding:.4rem .75rem;">#{a.task_id}</td>
          <td style="padding:.4rem .75rem;">#{a.project_id}</td>
          <td style="padding:.4rem .75rem; white-space:nowrap;">{formatDate(a.timestamp)}</td>
        </tr>
        {/each}
      </tbody>
    </table>
  </div>
  {/if}

  <hr class="divider" />
  <h2 style="margin:.5rem 0 1rem; font-size:1rem;">Recent Completions</h2>
  {#if summary.recent_completions.length === 0}
    <p class="muted-label">None yet</p>
  {:else}
  <ul style="list-style:none; padding:0; margin:0; display:grid; gap:.5rem;">
    {#each summary.recent_completions as c}
      <li class="card" style="padding:.5rem .75rem; display:flex; gap:.5rem; align-items:center;">
        <span class="badge success" style="font-size:.55rem;">#{c.task_id}</span>
        <span style="font-weight:500;">{c.title}</span>
        <span class="muted-label" style="margin-left:auto; font-size:.6rem;">{new Date(c.completed_at).toLocaleTimeString()}</span>
      </li>
    {/each}
  </ul>
  {/if}

  <hr class="divider" />
  <h2 style="margin:.5rem 0 1rem; font-size:1rem;">Daily Completions</h2>
  {#if productivity}
    <div class="card" style="display:flex; flex-wrap:wrap; gap:.75rem;">
      {#each Object.entries(productivity.daily_completions) as [day,count]}
        <div style="display:flex; flex-direction:column; align-items:center; padding:.5rem .75rem; background:var(--color-surface-alt); border-radius:var(--radius-sm); min-width:70px;">
          <strong style="font-size:1.1rem;">{count}</strong>
          <span style="font-size:.6rem; letter-spacing:.05em; text-transform:uppercase;">{day.slice(5)}</span>
        </div>
      {/each}
    </div>
    <p class="muted-label" style="margin-top:.5rem; font-size:.65rem;">Most productive day: {productivity.weekly_summary.most_productive_day}</p>
  {/if}

  <hr class="divider" />
  <h2 style="margin:.5rem 0 1rem; font-size:1rem;">Recommendations</h2>
  {#if productivity && productivity.recommendations.length}
    <ul style="margin:0; padding-left:1.1rem; font-size:.75rem; display:grid; gap:.35rem;">
      {#each productivity.recommendations as r}
        <li>{r}</li>
      {/each}
    </ul>
  {:else}
    <p class="muted-label">No recommendations.</p>
  {/if}

  <hr class="divider" />
  <p class="muted-label" style="font-size:.6rem;">Last refreshed {lastRefreshed ? lastRefreshed.toLocaleTimeString() : 'just now'}</p>
{/if}

<style>
  .muted-label { color: var(--color-text-dim); font-size: .65rem; letter-spacing:.08em; text-transform:uppercase; }
  .big-number { font-size:1.7rem; letter-spacing:-.03em; font-weight:600; }
  .badge.neutral { background:var(--color-surface-alt); color:var(--color-text-dim); }
  @keyframes spin { to { transform: rotate(360deg); } }
</style>
