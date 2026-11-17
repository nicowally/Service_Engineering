<script>
  import { library } from '#lib/state/library.svelte.js';
  import { getComments, addComment, getRating, setRating } from '#lib/services/api.js';
  let { itemId } = $props();
  let comments = $state([]);
  let rating = $state(null);
  let text = $state('');
  let stars = $state(0);
  let loading = $state(true);
  let posting = $state(false);
  let savingRating = $state(false);
  let error = $state('');
  let notice = $state('');
  let retry = $state(0);
  $effect(() => {
    const id = itemId;
    const username = library.user?.username;
    void retry;
    let active = true;
    loading = true;
    error = '';
    notice = '';
    text = '';
    Promise.all([getComments(id), getRating(id)])
      .then(([entries, summary]) => {
        if (!active) return;
        comments = entries;
        rating = summary;
        stars = summary.ratings[username] ?? 0;
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
  async function postComment(event) {
    event.preventDefault();
    const user = library.user;
    const id = itemId;
    const message = text.trim();
    if (!user || !message || posting) return;
    posting = true;
    error = '';
    notice = '';
    try {
      const entry = await addComment(user, id, message);
      if (itemId === id && library.user?.id === user.id) {
        comments = [...comments, entry];
        text = '';
        notice = 'Your comment was added.';
      }
    } catch (cause) {
      error = cause.message;
    } finally {
      posting = false;
    }
  }
  async function rate(event) {
    event.preventDefault();
    const user = library.user;
    const id = itemId;
    if (!user || !stars || savingRating) return;
    savingRating = true;
    error = '';
    notice = '';
    try {
      const summary = await setRating(user, id, Number(stars));
      if (itemId === id && library.user?.id === user.id) {
        rating = summary;
        notice = 'Your rating was saved.';
      }
    } catch (cause) {
      error = cause.message;
    } finally {
      savingRating = false;
    }
  }
</script>

<section class="feedback-section" aria-labelledby="feedback-title">
  <p class="eyebrow">WHAT DO YOU THINK?</p>
  <h2 id="feedback-title">Notes &amp; stars.</h2>
  {#if error}<div class="error-banner" role="alert">
      {error}<button onclick={() => (retry += 1)}>Reload feedback</button>
    </div>{/if}
  {#if notice}<p class="success-message" role="status">{notice}</p>{/if}
  {#if loading}<p class="subtle" role="status">Loading comments and ratings…</p>
  {:else}
    <div class="feedback-grid">
      <div>
        <h3>Ratings</h3>
        <p class="rating-summary">
          {rating?.average == null ? 'No ratings yet' : `${rating.average} / 5`}
          <span class="subtle"
            >({rating?.count ?? 0} {rating?.count === 1 ? 'rating' : 'ratings'})</span
          >
        </p>
        <form onsubmit={rate} class="rating-form">
          <label
            >Your rating
            <select bind:value={stars} required disabled={!library.user || savingRating}>
              <option value={0} disabled>Choose stars</option>
              {#each [1, 2, 3, 4, 5] as number}<option value={number}
                  >{'★'.repeat(number)} — {number} / 5</option
                >{/each}
            </select>
          </label>
          <button class="primary-button" disabled={!library.user || !stars || savingRating}
            >{savingRating ? 'Saving…' : 'Save rating'}</button
          >
        </form>
        <p class="subtle">One rating per user. Saving again updates your rating.</p>
      </div>
      <div>
        <h3>Comments <span class="subtle">({comments.length})</span></h3>
        {#if !comments.length}<p class="subtle">Be the first to leave a note.</p>{/if}
        <ul class="comment-list">
          {#each comments as comment (comment.id)}<li>
              <div>
                <strong>{comment.username}</strong><time datetime={comment.created_at}
                  >{new Date(comment.created_at).toLocaleDateString()}</time
                >
              </div>
              <p>{comment.text}</p>
            </li>{/each}
        </ul>
        <form onsubmit={postComment} class="comment-form">
          <label
            >Your comment<textarea
              bind:value={text}
              required
              maxlength="2000"
              rows="3"
              placeholder="What makes this one worth keeping?"
              disabled={!library.user || posting}></textarea></label
          >
          <button class="primary-button" disabled={!library.user || !text.trim() || posting}
            >{posting ? 'Posting…' : 'Add comment'}</button
          >
        </form>
      </div>
    </div>
  {/if}
</section>
