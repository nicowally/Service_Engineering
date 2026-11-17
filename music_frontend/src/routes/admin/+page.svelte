<script>
  import { library, refreshLibrary } from '#lib/state/library.svelte.js';
  import { getMusic, saveMusic, deleteMusic } from '#lib/services/api.js';
  const blank = () => ({
    type: 'track',
    title: '',
    artist: '',
    genre: '',
    release_year: '',
    album_name: '',
    duration_seconds: '',
    description: '',
    external_url: ''
  });
  let form = $state(blank());
  let editingId = $state(null);
  let trackIds = $state([]);
  let trackToAdd = $state('');
  let busy = $state(false);
  let error = $state('');
  let notice = $state('');
  let deleteId = $state(null);
  let search = $state('');
  let isAdmin = $derived(library.user?.role === 'admin');
  let tracks = $derived(library.items.filter((item) => item.type === 'track'));
  let availableTracks = $derived(tracks.filter((item) => !trackIds.includes(item.id)));
  let items = $derived(
    library.items
      .filter((item) =>
        `${item.title} ${item.artist ?? ''}`.toLowerCase().includes(search.trim().toLowerCase())
      )
      .toSorted((a, b) => a.title.localeCompare(b.title))
  );
  $effect(() => {
    const id = library.user?.id;
    resetForm();
    error = '';
    notice = '';
    deleteId = null;
  });
  function resetForm() {
    form = blank();
    editingId = null;
    trackIds = [];
    trackToAdd = '';
  }
  async function edit(itemId) {
    busy = true;
    error = '';
    notice = '';
    try {
      const item = await getMusic(itemId);
      form = Object.fromEntries(Object.keys(blank()).map((key) => [key, item[key] ?? '']));
      editingId = item.id;
      trackIds = item.tracks.map((track) => track.id);
      trackToAdd = '';
      document
        .getElementById('editor-title')
        ?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      document.getElementById('music-title')?.focus({ preventScroll: true });
    } catch (cause) {
      error = cause.message;
    } finally {
      busy = false;
    }
  }
  function moveTrack(index, direction) {
    const reordered = [...trackIds];
    [reordered[index], reordered[index + direction]] = [
      reordered[index + direction],
      reordered[index]
    ];
    trackIds = reordered;
  }
  function addTrack() {
    if (trackToAdd && !trackIds.includes(trackToAdd)) trackIds = [...trackIds, trackToAdd];
    trackToAdd = '';
  }
  const nullableNumber = (value) => (value === '' || value == null ? null : Number(value));
  async function save(event) {
    event.preventDefault();
    if (!isAdmin || busy) return;
    error = '';
    notice = '';
    if (!form.title.trim()) {
      error = 'Please enter a title.';
      return;
    }
    if (!editingId && form.type !== 'track' && !trackIds.length) {
      error = 'Add at least one existing track to the album or playlist.';
      return;
    }
    busy = true;
    const body = {
      title: form.title.trim(),
      artist: form.artist.trim() || null,
      genre: form.genre.trim() || null,
      release_year: nullableNumber(form.release_year),
      description: form.description.trim() || null,
      external_url: form.external_url.trim() || null,
      ...(editingId ? {} : { type: form.type }),
      ...(form.type === 'track'
        ? {
            album_name: form.album_name.trim() || null,
            duration_seconds: nullableNumber(form.duration_seconds)
          }
        : { track_ids: [...trackIds] })
    };
    try {
      await saveMusic(library.user, body, editingId);
      await refreshLibrary();
      resetForm();
      notice = 'Music saved to the catalog.';
    } catch (cause) {
      error = cause.message;
    } finally {
      busy = false;
    }
  }
  async function remove(itemId) {
    if (!isAdmin || busy) return;
    busy = true;
    error = '';
    notice = '';
    try {
      await deleteMusic(library.user, itemId);
      await refreshLibrary();
      if (editingId === itemId) resetForm();
      deleteId = null;
      notice = 'Music deleted from the catalog and collections.';
    } catch (cause) {
      error = cause.message;
    } finally {
      busy = false;
    }
  }
</script>

<svelte:head><title>Catalog editor · Side A</title></svelte:head>
<section class="page-heading">
  <p class="eyebrow">ADMIN TOOLS</p>
  <h1>The catalog <em>editor.</em></h1>
  <p>Add music, organise tracklists, and keep the library in order.</p>
</section>
{#if library.loading}<p role="status">Loading…</p>
{:else if !isAdmin}<div class="empty-state">
    <h2>Admin access only.</h2>
    <p>Select an admin user to manage the shared catalog.</p>
    <a href="/catalog" class="primary-button">Back to the library</a>
  </div>
{:else}
  {#if error}<div class="error-banner" role="alert">{error}</div>{/if}
  {#if notice}<p class="success-message" role="status">{notice}</p>{/if}
  <section class="editor-section" aria-labelledby="editor-title">
    <div class="section-heading">
      <h2 id="editor-title">{editingId ? 'Edit music' : 'Add something good'}</h2>
      {#if editingId}<button class="text-button" onclick={resetForm} disabled={busy}
          >Cancel edit</button
        >{/if}
    </div>
    <form onsubmit={save} class="editor-form">
      <div class="form-grid">
        <label
          >Format<select bind:value={form.type} disabled={!!editingId || busy}
            ><option value="track">Track</option><option value="album">Album</option><option
              value="playlist">Playlist</option
            ></select
          ></label
        >
        <label
          >Title <span class="subtle">(required)</span><input
            id="music-title"
            bind:value={form.title}
            required
            maxlength="255"
            disabled={busy}
          /></label
        >
        <label>Artist<input bind:value={form.artist} maxlength="255" disabled={busy} /></label>
        <label>Genre<input bind:value={form.genre} maxlength="100" disabled={busy} /></label>
        <label
          >Release year<input
            type="number"
            min="1000"
            max="9999"
            step="1"
            bind:value={form.release_year}
            disabled={busy}
          /></label
        >
        {#if form.type === 'track'}<label
            >Duration in seconds<input
              type="number"
              min="0"
              step="1"
              bind:value={form.duration_seconds}
              disabled={busy}
            /></label
          >{/if}
      </div>
      {#if form.type !== 'track'}
        <fieldset class="track-editor">
          <legend>Tracks in order</legend>
          <p class="subtle">Create tracks first, then add them here. Each track can appear once.</p>
          <div class="track-picker">
            <label class="grow"
              >Choose a track<select bind:value={trackToAdd} disabled={busy}
                ><option value="">Select existing track…</option
                >{#each availableTracks as track}<option value={track.id}
                    >{track.title} — {track.artist ?? 'Unknown artist'}</option
                  >{/each}</select
              ></label
            ><button
              type="button"
              class="secondary-button"
              onclick={addTrack}
              disabled={!trackToAdd || busy}>Add track</button
            >
          </div>
          {#if !trackIds.length}<p class="subtle">No tracks selected.</p>{/if}
          <ol class="ordered-tracks">
            {#each trackIds as id, index (id)}<li>
                <span>{tracks.find((track) => track.id === id)?.title ?? 'Unavailable track'}</span>
                <div>
                  <button
                    type="button"
                    class="text-button"
                    disabled={index === 0 || busy}
                    aria-label={`Move track ${index + 1} up`}
                    onclick={() => moveTrack(index, -1)}>↑</button
                  ><button
                    type="button"
                    class="text-button"
                    disabled={index === trackIds.length - 1 || busy}
                    aria-label={`Move track ${index + 1} down`}
                    onclick={() => moveTrack(index, 1)}>↓</button
                  ><button
                    type="button"
                    class="text-button"
                    disabled={busy}
                    onclick={() => (trackIds = trackIds.filter((entry) => entry !== id))}
                    >Remove</button
                  >
                </div>
              </li>{/each}
          </ol>
        </fieldset>
      {/if}
      <details class="more-details">
        <summary>More details</summary>
        <div class="form-grid">
          {#if form.type === 'track'}<label
              >Album name<input
                bind:value={form.album_name}
                maxlength="255"
                disabled={busy}
              /></label
            >{/if}
          <label
            >External link<input
              type="url"
              pattern="https?://.*"
              title="Use an http:// or https:// link"
              bind:value={form.external_url}
              maxlength="1024"
              disabled={busy}
              placeholder="https://…"
            /></label
          >
          <label class="full-width"
            >Description<textarea bind:value={form.description} rows="3" disabled={busy}
            ></textarea></label
          >
        </div>
      </details>
      <button class="primary-button" disabled={busy}
        >{busy ? 'Working…' : editingId ? 'Save changes' : 'Create music item'}</button
      >
    </form>
  </section>
  <section class="manage-section" aria-labelledby="manage-title">
    <h2 id="manage-title">In the catalog</h2>
    <label class="manage-search"
      >Find music<input type="search" bind:value={search} placeholder="Title or artist…" /></label
    >
    {#if !items.length}<p class="subtle">No items match your search.</p>{/if}
    <ul class="manage-list">
      {#each items as item (item.id)}<li>
          <div>
            <a href={`/music/${item.id}`}><strong>{item.title}</strong></a>
            <p class="subtle">{item.type} · {item.artist ?? 'Personal selection'}</p>
          </div>
          {#if deleteId === item.id}<div
              class="delete-confirm"
              role="group"
              aria-label="Confirm deletion"
            >
              <p>
                Delete permanently? This also removes it from collections and deletes its comments
                and ratings.
              </p>
              <button class="danger-button" disabled={busy} onclick={() => remove(item.id)}
                >Delete permanently</button
              ><button class="text-button" disabled={busy} onclick={() => (deleteId = null)}
                >Cancel</button
              >
            </div>
          {:else}<div class="row-actions">
              <button class="secondary-button" disabled={busy} onclick={() => edit(item.id)}
                >Edit</button
              ><button
                class="text-button danger-text"
                disabled={busy}
                onclick={() => (deleteId = item.id)}>Delete</button
              >
            </div>{/if}
        </li>{/each}
    </ul>
  </section>
{/if}
