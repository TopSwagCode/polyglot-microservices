<script lang="ts">
import { auth } from '$lib/stores/auth';
import { goto } from '$app/navigation';

let username = '';
let password = '';
let confirm = '';
let loading = false;
let error: string | null = null;
let success = false;

const API_BASE = (import.meta as any).env?.VITE_API_BASE || 'http://localhost:8080';

async function register() {
  error = null; success = false;
  if (!username || !password) { error = 'Username and password required'; return; }
  if (password.length < 8) { error = 'Password must be at least 8 characters'; return; }
  if (password !== confirm) { error = 'Passwords do not match'; return; }
  loading = true;
  try {
    const res = await fetch(API_BASE + '/auth/register', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ Username: username.trim(), Password: password }) });
    const body = await res.json().catch(()=>({}));
    if(!res.ok) throw new Error(body?.message || 'Registration failed');
    success = true;
    // auto-login convenience: attempt login then goto dashboard
    try {
      await auth.login(username.trim(), password);
      goto('/dashboard');
      return;
    } catch {
      // swallow; user can go to login manually
    }
  } catch (e:any) {
    error = e.message || 'Registration failed';
  } finally {
    loading = false;
  }
}
</script>

<svelte:head>
  <title>Register</title>
</svelte:head>

<div class="auth-wrapper center" style="min-height:60vh;">
  <form class="surface register-form" on:submit|preventDefault={register}>
    <h1 class="reg-title">Create Account</h1>
    <div class="field full">
      <label for="username">Username</label>
      <input id="username" name="username" bind:value={username} required class="input" autocomplete="username" />
    </div>
    <div class="field full">
      <label for="password">Password</label>
      <input id="password" type="password" name="password" bind:value={password} required class="input" autocomplete="new-password" />
      <small class="hint">Minimum 8 characters.</small>
    </div>
    <div class="field full">
      <label for="confirm">Confirm Password</label>
      <input id="confirm" type="password" name="confirm" bind:value={confirm} required class="input" autocomplete="new-password" />
    </div>
    {#if error}
      <div class="error-msg">{error}</div>
    {/if}
    {#if success}
      <div class="success-msg">Registration successful! Redirecting...</div>
    {/if}
    <button class="btn primary full" disabled={loading}>{loading ? 'Registering...' : 'Register'}</button>
    <p class="hint center-text">Already have an account? <a href="/login">Login</a></p>
  </form>
</div>

<style>
  .register-form { max-width:480px; width:100%; display:flex; flex-direction:column; gap:1rem; }
  .reg-title { margin:.25rem 0 .25rem; font-size:1.55rem; text-align:center; }
  .field { display:flex; flex-direction:column; gap:.4rem; }
  .full { width:100%; }
  .error-msg { color:var(--color-negative); font-size:.8rem; }
  .success-msg { color:var(--color-positive); font-size:.8rem; }
  .hint { font-size:.65rem; color:var(--color-text-dim); }
  .center-text { text-align:center; }
</style>
