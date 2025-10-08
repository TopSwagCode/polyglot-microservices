<script lang="ts">
	import { auth } from '$lib/stores/auth';
	import { goto } from '$app/navigation';
	let open = false;

	function logout() {
		auth.logout();
		goto('/');
	}
</script>

<nav class="navbar">
	<div class="nav-inner">
		<a class="brand" href="/">polyglot-microservices</a>
		<button class="menu-btn" on:click={() => open = !open} aria-label="Menu" aria-expanded={open}>☰</button>
		<ul class:open>
			{#if $auth.user}
                <li class="user">Welcome {$auth.user.username ?? 'User'}</li>
				<li><a href="/dashboard">Dashboard</a></li>
				<li><a href="/analytics">Analytics</a></li>
				
				<li><button class="link" on:click={logout}>Logout</button></li>
			{:else}
				<li><a href="/login">Login</a></li>
				<li><a href="/register">Register</a></li>
			{/if}
            <li><a href="/devtools">Dev Tools</a></li>
		</ul>
	</div>
</nav>

<style>
	.navbar { position:sticky; top:0; z-index:50; background:var(--color-bg); border-bottom:1px solid rgba(255,255,255,.06); backdrop-filter:blur(12px); -webkit-backdrop-filter:blur(12px); }
	.nav-inner { max-width:1100px; margin:0 auto; padding:.85rem 1.2rem; display:flex; align-items:center; gap:1.4rem; }
	.brand { font-family:var(--font-tech); font-weight:600; letter-spacing:.08em; text-decoration:none; font-size:1.05rem; position:relative; display:inline-flex; align-items:center; text-transform:lowercase; line-height:1; padding-bottom:2px; }
	/* Fallback solid color for environments without background-clip */
	.brand { color:#a9cfff; }
	/* Gradient text where supported */
	@supports (-webkit-background-clip:text) or (background-clip:text) {
		.brand { background:linear-gradient(90deg,#6fb1ff,#8dd8ff 40%,#9fa9ff 70%,#a7b7ff); -webkit-background-clip:text; background-clip:text; color:transparent; -webkit-text-fill-color:transparent; }
	}
	.brand:after { content:""; position:absolute; left:0; bottom:0; height:2px; width:0; background:linear-gradient(90deg,#6fb1ff,#8dd8ff); transition:width .35s ease; border-radius:2px; }
	.brand:hover:after, .brand:focus-visible:after { width:100%; }
	.brand:hover { text-shadow:0 0 4px rgba(140,190,255,.25); filter:none; }
	ul { list-style:none; margin:0; padding:0; display:flex; gap:.9rem; align-items:center; }
	ul a, .link { text-decoration:none; font-size:.75rem; letter-spacing:.05em; text-transform:uppercase; color:var(--color-text-dim); padding:.45rem .6rem; border-radius:.4rem; transition:background .2s, color .2s; background:none; border:none; cursor:pointer; }
	ul a:hover, .link:hover { background:rgba(255,255,255,.08); color:var(--color-text); }
	.user { font-size:.7rem; opacity:.85; padding:.2rem .4rem; }
	.menu-btn { display:none; background:none; border:1px solid rgba(255,255,255,.15); color:var(--color-text-dim); font-size:1rem; padding:.35rem .55rem; border-radius:.35rem; cursor:pointer; }
	.menu-btn:hover { color:var(--color-text); border-color:rgba(255,255,255,.3); }
	@media (max-width: 720px){
		.menu-btn { display:inline-block; margin-left:auto; }
		ul { position:absolute; top:100%; left:0; right:0; flex-direction:column; align-items:stretch; padding:.6rem 1rem 1rem; background:var(--color-bg); border-bottom:1px solid rgba(255,255,255,.07); display:none; }
		ul.open { display:flex; }
		ul a, .link { font-size:.65rem; }
	}
</style>
