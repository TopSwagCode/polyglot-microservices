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
	<form class="surface login-form" on:submit|preventDefault={submit}>
		<h1 class="login-title">Login</h1>
		<div class="field full">
			<label for="username">Username</label>
			<input id="username" name="username" autocomplete="username" bind:value={username} required class="full light-input" />
		</div>
		<div class="field full">
			<label for="password">Password</label>
			<div class="password-wrapper">
				<input id="password" type={showPwd ? 'text':'password'} name="password" autocomplete="current-password" bind:value={password} required class="full light-input" />
				<button type="button" class="btn ghost toggle-btn" on:click={() => showPwd = !showPwd}>{showPwd ? 'Hide':'Show'}</button>
			</div>
		</div>
		{#if localError || $auth.error}
			<div class="error-msg">{localError || $auth.error}</div>
		{/if}
		<button class="btn primary full" disabled={$auth.loading}>{$auth.loading ? 'Signing in...' : 'Login'}</button>
		
	</form>
</div>

<style>
	.login-form { max-width:420px; width:100%; display:flex; flex-direction:column; gap:1rem; }
	.login-title { margin:.25rem 0 0; font-size:1.6rem; text-align:center; }
	.field { display:flex; flex-direction:column; gap:.4rem; }
	.full { width:100%; }
	.password-wrapper { position:relative; }
	.toggle-btn { position:absolute; top:4px; right:4px; padding:.4rem .6rem; font-size:.6rem; }
	.error-msg { color:var(--color-negative); font-size:.8rem; }
	.hint { margin-top:.25rem; font-size:.7rem; text-align:center; color:var(--color-text-dim); }
</style>
