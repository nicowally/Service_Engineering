<script>
  import { onMount } from 'svelte';
  import { page } from '$app/state';
  import { library, initializeLibrary, selectUser } from '#lib/state/library.svelte.js';
  import { demoMode } from '#lib/services/api.js';
  import Icon from '#lib/components/Icon.svelte';
  import '../app.css';
  let { children } = $props();
  onMount(() => {
    initializeLibrary();
  });
</script>

<svelte:head
  ><link rel="icon" href="/favicon.svg" type="image/svg+xml" /><meta
    name="theme-color"
    content="#f7f6f2"
  /></svelte:head
>
<a class="skip-link" href="#main">Skip to content</a>
<div class="app-shell">
  <header class="site-header">
    <a class="brand" href="/" aria-label="Side A home"
      ><span class="brand-icon"><span></span><span></span><span></span><span></span></span><span
        >side a<span class="brand-period">.</span></span
      ></a
    >
    <nav aria-label="Main navigation">
      <a
        class:current={page.url.pathname === '/' ||
          page.url.pathname === '/catalog' ||
          page.url.pathname.startsWith('/music/')}
        href="/catalog"
        aria-current={page.url.pathname === '/' || page.url.pathname === '/catalog'
          ? 'page'
          : undefined}>Discover</a
      ><a
        class:current={page.url.pathname === '/collection'}
        href="/collection"
        aria-current={page.url.pathname === '/collection' ? 'page' : undefined}
        >My collection<span class="nav-count">{library.collection.length}</span></a
      >
    </nav>
    <div class="header-tools">
      <span class="mode-badge"><span></span>{demoMode ? 'Sample library' : 'FastAPI mode'}</span
      ><label class="user-picker"
        ><span class="user-avatar">{library.user?.username?.slice(0, 1).toUpperCase() ?? '–'}</span
        ><span class="sr-only">Current user</span><select
          aria-label="Current user"
          value={library.user?.id ?? ''}
          onchange={(event) => selectUser(event.currentTarget.value)}
          disabled={library.loading || !!Object.keys(library.pending).length}
          >{#if !library.users.length}<option value="">Loading…</option
            >{/if}{#each library.users as user}<option value={user.id}
              >{user.username}{user.role === 'admin' ? ' (admin)' : ''}</option
            >{/each}</select
        ></label
      >
    </div>
  </header>
  {#if demoMode}<div class="demo-notice">
      <span>Make yourself at home.</span> This sample library works without a database. Collection changes
      stay in this browser.
    </div>{/if}
  <main id="main">
    {#if library.error}<div class="error-banner" role="alert">
        <span>{library.error}</span>{#if !library.ready}<button onclick={initializeLibrary}
            >Try again</button
          >{:else}<button onclick={() => (library.error = '')} aria-label="Dismiss error"
            ><Icon name="close" size={18} /></button
          >{/if}
      </div>{/if}{@render children()}
  </main>
  <footer class="site-footer">
    <a class="footer-brand" href="/">side a.</a><span>A little space for the music you love.</span
    ><span class="footer-label">MUSIC COLLECTION MANAGER</span>
  </footer>
</div>
