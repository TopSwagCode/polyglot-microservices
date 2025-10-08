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
		{#if $auth.user}
			<div class="welcome">Welcome {$auth.user.username ?? 'User'}</div>
		{/if}
		<div class="nav-actions">
			<button class="menu-btn" class:open={open} on:click={() => open = !open} aria-label={open ? 'Close menu' : 'Open menu'} aria-expanded={open}>
				<span class="bar top"></span>
				<span class="bar middle"></span>
				<span class="bar bottom"></span>
			</button>
			<ul class:open>
				{#if $auth.user}
					<li><a href="/dashboard">Dashboard</a></li>
					<li><a href="/analytics">Analytics</a></li>
					<li><a href="/" class="link" on:click|preventDefault={logout}>Logout</a></li>
				{:else}
					<li><a href="/login">Login</a></li>
					<li><a href="/register">Register</a></li>
				{/if}
				<li><a href="/devtools">Dev Tools</a></li>
			</ul>
		</div>
	</div>
</nav>

<style>
	.navbar { position:sticky; top:0; z-index:50; background:var(--color-bg); border-bottom:1px solid rgba(255,255,255,.06); backdrop-filter:blur(12px); -webkit-backdrop-filter:blur(12px); }
	.nav-inner { max-width:1100px; margin:0 auto; padding:.85rem 1.2rem; display:flex; align-items:center; gap:1.4rem; position:relative; }
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
	.welcome { position:absolute; left:50%; top:50%; transform:translate(-50%, -50%); font-size:.70rem; letter-spacing:.08em; text-transform:uppercase; color:var(--color-text-dim); pointer-events:none; white-space:nowrap; }
	.nav-actions { margin-left:auto; display:flex; align-items:center; gap:.75rem; }
	ul { list-style:none; margin:0; padding:0; display:flex; gap:.9rem; align-items:center; }
	ul a, .link { text-decoration:none; font-size:.75rem; letter-spacing:.05em; text-transform:uppercase; color:var(--color-text-dim); padding:.45rem .6rem; border-radius:.4rem; transition:background .2s, color .2s; background:none; border:none; cursor:pointer; }
	ul a:hover, .link:hover { background:rgba(255,255,255,.08); color:var(--color-text); }
	/* Hidden by default (desktop); enabled in mobile media query */
	.menu-btn { --bar-width:22px; --bar-height:2px; --bar-gap:5px; position:relative; display:none; background:linear-gradient(145deg,#171c22,#13171c); border:1px solid rgba(255,255,255,.12); padding:.55rem; border-radius:.65rem; cursor:pointer; width:42px; height:40px; box-sizing:border-box; flex-direction:column; justify-content:center; align-items:center; gap:var(--bar-gap); transition:background .35s ease, border-color .35s ease, box-shadow .35s ease, transform .4s ease; }
	.menu-btn .bar { display:block; width:var(--bar-width); height:var(--bar-height); background:linear-gradient(90deg,#6fb1ff,#8dd8ff); border-radius:2px; position:relative; transition:transform .5s cubic-bezier(.68,-0.55,.27,1.55), opacity .3s ease, width .4s ease, background .4s ease; }
	.menu-btn .bar:after { content:""; position:absolute; inset:0; background:inherit; filter:blur(4px) opacity(.6); border-radius:inherit; transition:opacity .4s ease; }
	.menu-btn:hover { border-color:rgba(255,255,255,.3); box-shadow:0 0 0 1px rgba(130,180,255,.15), 0 4px 18px -6px rgba(0,0,0,.6); }
	.menu-btn:active { transform:scale(.92); }
	.menu-btn:hover .bar { background:linear-gradient(90deg,#8dd8ff,#6fb1ff); }
	.menu-btn.open .top { transform:translateY(calc(var(--bar-gap) + var(--bar-height))) rotate(45deg); }
	.menu-btn.open .middle { opacity:0; transform:scaleX(.2); }
	.menu-btn.open .bottom { transform:translateY(calc(-1 * (var(--bar-gap) + var(--bar-height)))) rotate(-45deg); }
	.menu-btn.open .bar:after { opacity:.35; }
	.menu-btn:focus-visible { outline:none; box-shadow:0 0 0 3px rgba(120,180,255,.35); }
	@media (prefers-reduced-motion: reduce) { .menu-btn .bar { transition:none; } }
	@media (max-width: 920px){
		.menu-btn { display:flex; margin-left:auto; }
		.welcome { display:none; }
		ul { position:absolute; top:100%; right:0; min-width:60%; flex-direction:column; align-items:stretch; padding:.6rem 1rem 1rem; background:var(--color-bg); border-bottom:1px solid rgba(255,255,255,.07); display:none; left:auto; }
		ul.open { display:flex; }
		ul a, .link { font-size:.65rem; }
	}
</style>
