<script>
  import MusicCard from './MusicCard.svelte';
  import Cover from './Cover.svelte';
  import Icon from './Icon.svelte';
  import { library } from '#lib/state/library.svelte.js';
  import { demoMode } from '#lib/services/api.js';
  let { collectionOnly = false } = $props();
  let search = $state('');
  let type = $state('all');
  let sort = $state('title');
  let favourites = $state(false);
  const filters = [
    { id: 'all', label: 'All music' },
    { id: 'track', label: 'Tracks' },
    { id: 'album', label: 'Albums' },
    { id: 'playlist', label: 'Playlists' }
  ];
  let source = $derived(
    collectionOnly
      ? library.collection
          .filter((entry) => !favourites || entry.is_favourite)
          .map((entry) => entry.music_item)
      : library.items
  );
  let filtered = $derived.by(() => {
    const query = search.trim().toLowerCase();
    return source
      .filter(
        (item) =>
          (type === 'all' || item.type === type) &&
          `${item.title} ${item.artist ?? ''} ${item.album_name ?? ''}`
            .toLowerCase()
            .includes(query)
      )
      .toSorted((a, b) =>
        sort === 'year'
          ? (b.release_year ?? 0) - (a.release_year ?? 0) || a.title.localeCompare(b.title)
          : a.title.localeCompare(b.title)
      );
  });
  let featured = $derived(library.items.find((item) => item.type === 'album') ?? library.items[0]);
</script>

<svelte:head
  ><title>{collectionOnly ? 'My collection' : 'Discover your next favourite'} · Side A</title><meta
    name="description"
    content="A little space for the music you love. Browse tracks, albums and playlists, and build your own collection."
  /></svelte:head
>
{#if !collectionOnly}
  <section class="hero-section" aria-labelledby="hero-title">
    <div class="hero-copy">
      <p class="eyebrow"><span class="tiny-line"></span> YOUR MUSIC, WELL KEPT</p>
      <h1 id="hero-title">Good music.<br /><em>Great company.</em></h1>
      <p class="hero-description">
        The songs you come back to. The albums you know by heart.<br class="desktop-break" /> A little
        space for everything you love listening to.
      </p>
      <a class="primary-button" href="#library"
        >Explore the library <Icon name="arrow" size={18} /></a
      >
      <div class="hero-footnote">
        <span class="little-record"></span> Tracks, albums &amp; playlists. All in one place.
      </div>
    </div>
    {#if featured}<div class="hero-art">
        <div class="hero-record"></div>
        <div class="featured-cover"><Cover item={featured} hero /></div>
        <span class="hero-art-note">A GOOD PLACE TO START ↗</span>
      </div>{/if}
  </section>
{:else}<section class="collection-heading">
    <p class="eyebrow">YOUR PERSONAL ROTATION</p>
    <h1>My <em>collection.</em></h1>
    <p>The keepers, the classics, and everything in between.</p>
  </section>{/if}
<section class="library-section" id="library" aria-labelledby="library-title">
  <div class="section-heading">
    <div>
      <p class="eyebrow">
        {collectionOnly
          ? `${library.user?.username ?? 'Your'}'s shelf`
          : 'FIND SOMETHING THAT STAYS'}
      </p>
      <h2 id="library-title">
        {collectionOnly ? 'Made yours.' : 'The library.'}<span class="item-count"
          >{source.length}</span
        >
      </h2>
    </div>
    <span class="library-note"
      >{demoMode ? 'A small sample. A world of possibility.' : 'Your shared music catalog.'}</span
    >
  </div>
  <div class="filter-bar">
    <div class="search-field">
      <Icon name="search" size={18} /><input
        type="search"
        bind:value={search}
        placeholder="Search music or artists…"
        aria-label="Search music or artists"
      />
    </div>
    <label class="sort-field"
      >Sort by <select bind:value={sort}
        ><option value="title">Title A–Z</option><option value="year">Newest year</option></select
      ></label
    >
  </div>
  <div class="filter-row">
    <div class="type-tabs" aria-label="Filter music type">
      {#each filters as filter}<button
          class:active={type === filter.id}
          aria-pressed={type === filter.id}
          onclick={() => (type = filter.id)}
          >{filter.label}<span
            >{source.filter((item) => filter.id === 'all' || item.type === filter.id).length}</span
          ></button
        >{/each}
    </div>
    {#if collectionOnly}<label class="favourites-filter"
        ><input type="checkbox" bind:checked={favourites} /> Favourites only</label
      >{/if}<span class="results-count" aria-live="polite"
      >{filtered.length} {filtered.length === 1 ? 'item' : 'items'}</span
    >
  </div>
  {#if library.loading || (collectionOnly && library.collectionLoading)}<div
      class="empty-state"
      role="status"
    >
      <span class="loading-dot"></span>
      <h3>Finding your music…</h3>
    </div>
  {:else if !library.ready}<div class="empty-state">
      <Icon name="music" size={30} />
      <h3>The library is unavailable.</h3>
      <p>Check the message above and try again.</p>
    </div>
  {:else if filtered.length === 0}<div class="empty-state">
      <Icon name="music" size={30} />
      <h3>
        {search || type !== 'all' || favourites
          ? 'No matches just yet.'
          : 'Your next favourite is out there.'}
      </h3>
      <p>
        {search || type !== 'all' || favourites
          ? 'Try another search or change your filters.'
          : 'Explore the library and add some music to your collection.'}
      </p>
      {#if collectionOnly && !source.length}<a class="primary-button" href="/catalog"
          >Explore the library <Icon name="arrow" size={17} /></a
        >{/if}
    </div>
  {:else}<div class="music-grid">
      {#each filtered as item (item.id)}<MusicCard {item} showReactions={collectionOnly} />{/each}
    </div>{/if}
</section>
