<script>
  import Cover from './Cover.svelte';
  import Icon from './Icon.svelte';
  import { library, entryFor, changeCollection } from '#lib/state/library.svelte.js';
  let { item, showReactions = false } = $props();
  let entry = $derived(entryFor(item.id));
  let disabled = $derived(!library.user || library.collectionLoading || !!library.pending[item.id]);
</script>

<article class="music-card">
  <a class="cover-link" href={`/music/${item.id}`} aria-label={`View ${item.title}`}
    ><Cover {item} /></a
  >
  <div class="card-body">
    <div class="card-meta">
      <span>{item.type}</span><span
        >{item.genre ?? 'Personal mix'}{item.release_year ? ` / ${item.release_year}` : ''}</span
      >
    </div>
    <h3><a href={`/music/${item.id}`}>{item.title}</a></h3>
    <p>{item.artist ?? 'Personal selection'}</p>
    <div class="card-actions">
      <button
        class="save-button"
        class:saved={!!entry}
        {disabled}
        onclick={() => changeCollection(item.id, 'toggle')}
        aria-label={`${entry ? 'Remove' : 'Save'} ${item.title}${entry ? ' from' : ' to'} collection`}
        ><Icon name={entry ? 'check' : 'plus'} size={16} />{library.pending[item.id]
          ? 'Updating…'
          : entry
            ? 'In collection'
            : 'Add to collection'}</button
      >
      {#if entry}<button
          class="icon-button favourite"
          class:active={entry.is_favourite}
          {disabled}
          aria-label={`${entry.is_favourite ? 'Unfavourite' : 'Favourite'} ${item.title}`}
          aria-pressed={entry.is_favourite}
          onclick={() => changeCollection(item.id, 'mark', { is_favourite: !entry.is_favourite })}
          ><Icon name="heart" size={18} /></button
        >{/if}
    </div>
    {#if showReactions && entry}<div class="reaction-actions">
        {#each ['like', 'dislike'] as reaction}<button
            class:active={entry.reaction === reaction}
            {disabled}
            aria-pressed={entry.reaction === reaction}
            onclick={() =>
              changeCollection(item.id, 'mark', {
                reaction: entry.reaction === reaction ? null : reaction
              })}
            ><Icon name={reaction} size={15} />{reaction === 'like' ? 'Like' : 'Dislike'}</button
          >{/each}
      </div>{/if}
  </div>
</article>
