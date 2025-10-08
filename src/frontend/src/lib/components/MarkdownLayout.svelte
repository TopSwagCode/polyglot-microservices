<script lang="ts">
  export let frontmatter: Record<string, any> = {};
</script>

<div class="markdown-container">
  {#if frontmatter.title}
    <h1 class="page-title hc">{frontmatter.title}</h1>
  {/if}
  <article class="prose">
    <slot />
  </article>
</div>

<style>
  .markdown-container { max-width: 900px; margin: 0 auto; padding: 2rem 1.25rem 3rem; }
  .page-title { margin:0 0 1.75rem; font-size:2.15rem; line-height:1.1; letter-spacing:-.02em; }
  .prose :global(p){ line-height:1.6; margin:0 0 1.05rem; color:var(--color-text); }
  .prose :global(h1){ font-size:2rem; margin:2.5rem 0 1rem; line-height:1.15; letter-spacing:-.02em; color:#f5f7fa; }
  .prose :global(h2){ font-size:1.45rem; margin:2rem 0 .9rem; line-height:1.2; letter-spacing:-.01em; color:#f2f5f9; }
  .prose :global(h3){ font-size:1.05rem; margin:1.5rem 0 .65rem; letter-spacing:.05em; text-transform:uppercase; opacity:.9; color:var(--color-text-dim); }
  .prose :global(code){ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, 'Courier New', monospace; font-size:.85em; background:rgba(255,255,255,.08); padding:.18rem .45rem; border-radius:.35rem; color:#f7f9fb; }
  .prose :global(pre){ background:#14181d; padding:1rem 1.1rem; border-radius:.8rem; overflow:auto; line-height:1.45; font-size:.8rem; box-shadow:0 4px 14px -4px rgba(0,0,0,.55); border:1px solid rgba(255,255,255,.09); }
  .prose :global(pre code){ background:transparent; padding:0; font-size:.8rem; color:#e9edf3; }
  .prose :global(a){ color:var(--color-accent); text-decoration:none; }
  .prose :global(a:hover){ text-decoration:underline; }
  .prose :global(ul), .prose :global(ol){ margin:0 0 1.15rem 1.4rem; padding:0; line-height:1.55; }
  .prose :global(li){ margin:.3rem 0; }
  .prose :global(blockquote){ margin:1.35rem 0; padding:.95rem 1.15rem; background:linear-gradient(135deg,rgba(255,255,255,.05),rgba(255,255,255,.02)); border-left:4px solid var(--color-accent); border-radius:.55rem; font-style:italic; color:var(--color-text); }
  .prose :global(hr){ border:none; height:1px; background:linear-gradient(to right, rgba(255,255,255,.18), rgba(255,255,255,.05)); margin:2.2rem 0; }
  .prose :global(table){ width:100%; border-collapse:collapse; font-size:.85rem; margin:1.35rem 0; }
  .prose :global(th), .prose :global(td){ border:1px solid rgba(255,255,255,.18); padding:.55rem .65rem; text-align:left; }
  .prose :global(th){ background:rgba(255,255,255,.08); font-weight:600; color:#f2f5f9; }
  .prose :global(img){ max-width:100%; border-radius:.6rem; box-shadow:0 6px 18px -6px rgba(0,0,0,.45); }
  .prose :global(strong){ font-weight:600; color:#f2f5f9; }
  .prose :global(em){ opacity:.92; }
  .prose :global(mark){ background:var(--color-accent); color:var(--color-bg); padding:.18rem .38rem; border-radius:.3rem; }
  .prose :global(details){ background:rgba(255,255,255,.06); padding:.8rem 1rem; border-radius:.65rem; border:1px solid rgba(255,255,255,.1); margin:1.1rem 0; }
  .prose :global(summary){ cursor:pointer; font-weight:600; }
  .prose :global(::selection){ background:var(--color-accent); color:var(--color-bg); }

  @media (max-width: 640px){
    .markdown-container { padding: 1.5rem 1rem 2.5rem; }
    .page-title { font-size:1.85rem; }
  }
</style>
