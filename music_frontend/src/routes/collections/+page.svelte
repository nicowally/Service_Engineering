<script>
  import { library } from '#lib/state/library.svelte.js';
  import { getAllCollections } from '#lib/services/api.js';
  let collections = $state([]);
  let selected = $state('all');
  let loading = $state(false);
  let error = $state('');
  let retry = $state(0);
  let isAdmin = $derived(library.user?.role === 'admin');
  let visible = $derived(
    collections.filter((entry) => selected === 'all' || entry.user_id === selected)
  );
  $effect(() => {
    const user = library.user;
    void retry;
    let active = true;
    collections = [];
    selected = 'all';
    error = '';
    if (user?.role !== 'admin') return;
    loading = true;
    getAllCollections(user)
      .then((entries) => {
        if (active) collections = entries;
      })
      .catch((cause) => {
        if (active) error = cause.message;
      })
      .finally(() => {
        if (active) loading = false;
      });
    return () => {
      active = false;
    };
  });
</script>

<svelte:head><title>All collections · Side A</title></svelte:head>
<section class="page-heading">
  <p class="eyebrow">ADMIN OVERVIEW</p>
  <h1>Every <em>collection.</em></h1>
  <p>A look at what everyone is keeping on their shelf.</p>
</section>
{#if library.loading}<p role="status">Loading users…</p>
{:else if !isAdmin}<div class="empty-state">
    <h2>Admin access only.</h2>
    <p>Select an admin user to view all collections.</p>
    <a href="/collection" class="primary-button">My collection</a>
  </div>
{:else}
  {#if error}<div class="error-banner" role="alert">
      {error}<button onclick={() => (retry += 1)}>Try again</button>
    </div>{/if}
  <label class="overview-filter"
    >Show collection<select bind:value={selected}
      ><option value="all">All users</option>{#each collections as entry}<option
          value={entry.user_id}>{entry.username}</option
        >{/each}</select
    ></label
  >
  {#if loading}<p role="status">Loading collections…</p>
  {:else}
    {#each visible as entry (entry.user_id)}<section class="user-collection">
        <h2>{entry.username}<span class="item-count">{entry.items.length}</span></h2>
        {#if !entry.items.length}<p class="subtle">This collection is empty.</p>{/if}
        <ul class="overview-list">
          {#each entry.items as saved (saved.music_item.id)}<li>
              <a href={`/music/${saved.music_item.id}`}
                ><strong>{saved.music_item.title}</strong><small
                  >{saved.music_item.type} · {saved.music_item.artist ??
                    'Personal selection'}</small
                ></a
              ><span
                >{saved.is_favourite ? '♥ Favourite' : ''}{saved.is_favourite && saved.reaction
                  ? ' · '
                  : ''}{saved.reaction ?? ''}</span
              >
            </li>{/each}
        </ul>
      </section>{/each}
  {/if}
{/if}
