<script>
  import { page } from '$app/state';
  import { getMusic } from '#lib/services/api.js';
  import { library, entryFor, changeCollection } from '#lib/state/library.svelte.js';
  import Cover from '#lib/components/Cover.svelte';
  import Icon from '#lib/components/Icon.svelte';
  import Feedback from '#lib/components/Feedback.svelte';
  let item = $state(null);
  let loading = $state(true);
  let error = $state('');
  let retry = $state(0);
  let entry = $derived(item ? entryFor(item.id) : null);
  let disabled = $derived(
    !library.user || library.collectionLoading || !!library.pending[item?.id]
  );
  function duration(seconds) {
    return seconds == null
      ? '—'
      : `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`;
  }
  $effect(() => {
    const id = page.params.id;
    void retry;
    let active = true;
    loading = true;
    error = '';
    getMusic(id)
      .then((result) => {
        if (active) item = result;
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

<svelte:head><title>{item?.title ?? 'Music detail'} · Side A</title></svelte:head>
<a class="back-link" href="/catalog"><Icon name="back" size={17} /> Back to the library</a>
{#if loading}<div class="empty-state" role="status"><h2>Finding your music…</h2></div>
{:else if error}<div class="empty-state" role="alert">
    <h2>We couldn’t find that item.</h2>
    <p>{error}</p>
    <button class="primary-button" onclick={() => (retry += 1)}>Try again</button>
  </div>
{:else if item}
  <section class="detail-section">
    <div class="detail-cover"><Cover {item} hero /></div>
    <div class="detail-copy">
      <p class="eyebrow">{item.type} {item.genre ? ` / ${item.genre}` : ''}</p>
      <h1>{item.title}</h1>
      <p class="detail-artist">
        {item.artist ?? 'A personal selection'}{item.release_year ? ` · ${item.release_year}` : ''}
      </p>
      <p class="detail-description">
        {item.description ??
          (item.album_name
            ? `From ${item.album_name}.`
            : 'A little something for your personal rotation.')}
      </p>
      <div class="detail-actions">
        <button
          class="primary-button"
          {disabled}
          onclick={() => changeCollection(item.id, 'toggle')}
          ><Icon name={entry ? 'check' : 'plus'} size={18} />{library.pending[item.id]
            ? 'Updating…'
            : entry
              ? 'Remove from collection'
              : 'Add to collection'}</button
        >{#if entry}<button
            class="icon-button favourite"
            class:active={entry.is_favourite}
            {disabled}
            aria-label="Favourite item"
            aria-pressed={entry.is_favourite}
            onclick={() => changeCollection(item.id, 'mark', { is_favourite: !entry.is_favourite })}
            ><Icon name="heart" /></button
          >{/if}
      </div>
      <div class="detail-facts">
        <span><small>FORMAT</small>{item.type}</span>{#if item.duration_seconds != null}<span
            ><small>DURATION</small>{duration(item.duration_seconds)}</span
          >{/if}{#if item.tracks?.length}<span><small>TRACKS</small>{item.tracks.length}</span>{/if}
      </div>
    </div>
  </section>
  {#if item.tracks?.length}<section class="track-section">
      <p class="eyebrow">IN THIS {item.type.toUpperCase()}</p>
      <h2>The tracklist.</h2>
      <ol class="tracklist">
        {#each item.tracks as track}<li>
            <a href={`/music/${track.id}`}
              ><span>{track.title}<small>{track.artist ?? 'Unknown artist'}</small></span><span
                >{duration(track.duration_seconds)} <Icon name="arrow" size={17} /></span
              ></a
            >
          </li>{/each}
      </ol>
    </section>{/if}
  {#key item.id}<Feedback itemId={item.id} />{/key}
{/if}
