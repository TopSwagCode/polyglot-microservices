<script lang="ts">
	import { auth } from '$lib/stores/auth';
	import { goto } from '$app/navigation';
	let username = '';
	let password = '';
	let showPwd = false;
	let localError: string | null = null;

	async function submit() {
		localError = null;
		try {
			await auth.login(username.trim(), password);
			goto('/dashboard');
		} catch (e: any) {
			localError = e.message || 'Login failed';
		}
	}
</script>

<svelte:head>
	<title>Login</title>
</svelte:head>

<div class="auth-wrapper center" style="min-height:60vh;">
	<form class="surface" style="max-width:420px; width:100%;" on:submit|preventDefault={submit}>
		<h1 style="margin:.25rem 0 1.25rem; font-size:1.6rem; text-align:center;">Login</h1>
		<div class="field">
			<label for="username">Username</label>
			<input id="username" name="username" autocomplete="username" bind:value={username} required />
		</div>
		<div class="field">
			<label for="password">Password</label>
			<div style="position:relative;">
				<input id="password" type={showPwd ? 'text':'password'} name="password" autocomplete="current-password" bind:value={password} required />
				<button type="button" class="btn ghost" style="position:absolute; top:4px; right:4px; padding:.4rem .6rem; font-size:.6rem;" on:click={() => showPwd = !showPwd}>{showPwd ? 'Hide':'Show'}</button>
			</div>
		</div>
		{#if localError || $auth.error}
			<div style="color:var(--color-negative); font-size:.8rem; margin-bottom:1rem;">{localError || $auth.error}</div>
		{/if}
		<button class="btn" style="width:100%;" disabled={$auth.loading}>{$auth.loading ? 'Signing in...' : 'Login'}</button>
		<p style="margin-top:1rem; font-size:.7rem; text-align:center; color:var(--color-text-dim);">Demo login accepts any credentials.</p>
	</form>
</div>
