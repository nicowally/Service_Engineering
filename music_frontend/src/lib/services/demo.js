// Matches the backend seed music. This data source never contacts Supabase.
export const demoUsers = [
  { id: 'demo-admin', username: 'admin', role: 'admin' },
  { id: 'demo-anna', username: 'anna', role: 'user' },
  { id: 'demo-ben', username: 'ben', role: 'user' }
];
const track = (id, title, artist, genre, release_year, duration_seconds, album_name = null) => ({
  id,
  type: 'track',
  title,
  artist,
  genre,
  release_year,
  duration_seconds,
  album_name,
  description: null,
  external_url: null,
  tracks: []
});
export const demoItems = [
  track(
    'bohemian-rhapsody',
    'Bohemian Rhapsody',
    'Queen',
    'Rock',
    1975,
    354,
    'A Night at the Opera'
  ),
  track('love-of-my-life', 'Love of My Life', 'Queen', 'Rock', 1975, 219, 'A Night at the Opera'),
  track('blinding-lights', 'Blinding Lights', 'The Weeknd', 'Synth-Pop', 2019, 200),
  track('levitating', 'Levitating', 'Dua Lipa', 'Pop', 2020, 203)
];
demoItems.push(
  {
    id: 'a-night-at-the-opera',
    type: 'album',
    title: 'A Night at the Opera',
    artist: 'Queen',
    genre: 'Rock',
    release_year: 1975,
    album_name: null,
    duration_seconds: null,
    description:
      'The Queen album featured in our sample library. These two tracks are included in the backend demo.',
    external_url: null,
    tracks: [demoItems[0], demoItems[1]]
  },
  {
    id: 'annas-lernmusik',
    type: 'playlist',
    title: 'Annas Lernmusik',
    artist: null,
    genre: null,
    release_year: null,
    album_name: null,
    duration_seconds: null,
    description: 'A little focus, a little pop. A study playlist from the sample collection.',
    external_url: null,
    tracks: [demoItems[2], demoItems[0], demoItems[3]]
  }
);
const storageKey = 'side-a-demo-collections-v1';
const initial = {
  'demo-anna': [
    { itemId: 'annas-lernmusik', reaction: null, is_favourite: true },
    { itemId: 'blinding-lights', reaction: 'like', is_favourite: false },
    { itemId: 'a-night-at-the-opera', reaction: 'like', is_favourite: true }
  ],
  'demo-ben': [
    { itemId: 'levitating', reaction: 'like', is_favourite: false },
    { itemId: 'blinding-lights', reaction: 'dislike', is_favourite: false }
  ],
  'demo-admin': []
};
let collections;
function readCollections() {
  if (collections) return collections;
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey));
    const valid =
      saved &&
      demoUsers.every(
        (user) =>
          Array.isArray(saved[user.id]) &&
          saved[user.id].every(
            (entry) =>
              entry &&
              demoItems.some((item) => item.id === entry.itemId) &&
              typeof entry.is_favourite === 'boolean' &&
              [null, 'like', 'dislike'].includes(entry.reaction)
          )
      );
    collections = valid ? saved : structuredClone(initial);
  } catch {
    collections = structuredClone(initial);
  }
  return collections;
}
export function getDemoCollection(userId) {
  getDemoItems();
  return (readCollections()[userId] ?? [])
    .filter((entry) => demoItems.some((item) => item.id === entry.itemId))
    .map(({ itemId, ...entry }) => ({
      ...entry,
      music_item: demoItems.find((item) => item.id === itemId),
      added_at: '2026-11-10T12:00:00Z'
    }));
}

let catalogLoaded = false;
const catalogKey = 'side-a-demo-catalog-v1';
function persist(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {
    /* Memory fallback. */
  }
}
export function getDemoItems() {
  if (!catalogLoaded) {
    catalogLoaded = true;
    try {
      const saved = JSON.parse(localStorage.getItem(catalogKey));
      if (
        Array.isArray(saved) &&
        saved.every(
          (item) =>
            item &&
            typeof item.id === 'string' &&
            typeof item.title === 'string' &&
            ['track', 'album', 'playlist'].includes(item.type) &&
            Array.isArray(item.tracks)
        )
      ) {
        demoItems.splice(0, demoItems.length, ...saved);
      }
    } catch {
      /* Keep seed data if storage is unavailable or invalid. */
    }
  }
  for (const item of demoItems) {
    if (item.type !== 'track')
      item.tracks = (item.tracks ?? [])
        .map((track) => demoItems.find((entry) => entry.id === track.id && entry.type === 'track'))
        .filter(Boolean);
  }
  return demoItems;
}
function requireDemoAdmin(user) {
  if (user?.role !== 'admin') throw new Error('Only admins can change the catalog.');
}
export function saveDemoItem(user, body, itemId = null) {
  requireDemoAdmin(user);
  getDemoItems();
  const existing = itemId ? demoItems.find((item) => item.id === itemId) : null;
  if (itemId && !existing) throw new Error('Music item not found.');
  const type = existing?.type ?? body.type;
  if (!['track', 'album', 'playlist'].includes(type)) throw new Error('Choose a music type.');
  if (typeof body.title !== 'string' || !body.title.trim() || body.title.length > 255)
    throw new Error('A title of 1–255 characters is required.');
  const { track_ids, ...fields } = body;
  let tracks = existing?.tracks ?? [];
  if (type !== 'track' && track_ids !== undefined) {
    if (new Set(track_ids).size !== track_ids.length)
      throw new Error('Each track can appear only once.');
    tracks = track_ids.map((id) => {
      const track = demoItems.find((item) => item.id === id && item.type === 'track');
      if (!track) throw new Error('Select existing tracks only.');
      return track;
    });
  }
  if (!existing && type !== 'track' && !tracks.length)
    throw new Error('Select at least one track.');
  const item = existing ?? {
    id: crypto.randomUUID(),
    artist: null,
    genre: null,
    album_name: null,
    release_year: null,
    duration_seconds: null,
    description: null,
    external_url: null
  };
  Object.assign(item, fields, { type, tracks });
  if (!existing) demoItems.push(item);
  persist(catalogKey, demoItems);
  return structuredClone(item);
}
export function deleteDemoItem(user, itemId) {
  requireDemoAdmin(user);
  getDemoItems();
  const index = demoItems.findIndex((item) => item.id === itemId);
  if (index < 0) throw new Error('Music item not found.');
  demoItems.splice(index, 1);
  getDemoItems();
  const all = readCollections();
  for (const userId of Object.keys(all))
    all[userId] = all[userId].filter((entry) => entry.itemId !== itemId);
  persist(storageKey, all);
  persist(catalogKey, demoItems);
  const data = readFeedback();
  delete data.comments[itemId];
  delete data.ratings[itemId];
  persist(feedbackKey, data);
}
const feedbackKey = 'side-a-demo-feedback-v1';
let feedback;
function readFeedback() {
  if (feedback) return feedback;
  try {
    const saved = JSON.parse(localStorage.getItem(feedbackKey));
    if (
      saved &&
      typeof saved.comments === 'object' &&
      saved.comments &&
      typeof saved.ratings === 'object' &&
      saved.ratings
    )
      feedback = saved;
  } catch {
    /* Fall back to sample feedback. */
  }
  feedback ??= {
    comments: {
      'a-night-at-the-opera': [
        {
          id: 'demo-comment',
          username: 'anna',
          text: 'An absolute classic!',
          created_at: '2026-11-10T12:00:00Z'
        }
      ]
    },
    ratings: { 'a-night-at-the-opera': { anna: 5, ben: 4 } }
  };
  return feedback;
}
function requireDemoItem(itemId) {
  if (!getDemoItems().some((item) => item.id === itemId)) throw new Error('Music item not found.');
}
export function getDemoComments(itemId) {
  requireDemoItem(itemId);
  const comments = readFeedback().comments[itemId];
  return structuredClone(Array.isArray(comments) ? comments : []);
}
export function addDemoComment(user, itemId, text) {
  requireDemoItem(itemId);
  if (!user || !text.trim() || text.length > 2000)
    throw new Error('Write a comment of 1–2000 characters.');
  const data = readFeedback();
  const entry = {
    id: crypto.randomUUID(),
    username: user.username,
    text: text.trim(),
    created_at: new Date().toISOString()
  };
  data.comments[itemId] = [...getDemoComments(itemId), entry];
  persist(feedbackKey, data);
  return entry;
}
export function getDemoRating(itemId) {
  requireDemoItem(itemId);
  const ratings = readFeedback().ratings[itemId] ?? {};
  const values = Object.values(ratings).filter(
    (value) => Number.isInteger(value) && value >= 1 && value <= 5
  );
  return {
    music_item_id: itemId,
    ratings: { ...ratings },
    count: values.length,
    average: values.length
      ? Math.round((values.reduce((sum, value) => sum + value, 0) / values.length) * 100) / 100
      : null
  };
}
export function setDemoRating(user, itemId, stars) {
  requireDemoItem(itemId);
  if (!user || !Number.isInteger(stars) || stars < 1 || stars > 5)
    throw new Error('Choose 1–5 stars.');
  const data = readFeedback();
  data.ratings[itemId] = { ...data.ratings[itemId], [user.username]: stars };
  persist(feedbackKey, data);
  return getDemoRating(itemId);
}
export function changeDemoCollection(userId, itemId, action, changes = {}) {
  const all = readCollections();
  const entries = all[userId] ?? [];
  if (action === 'add' && !entries.some((entry) => entry.itemId === itemId)) {
    entries.push({ itemId, reaction: null, is_favourite: false });
  } else if (action === 'remove') {
    all[userId] = entries.filter((entry) => entry.itemId !== itemId);
  } else if (action === 'mark') {
    const entry = entries.find((entry) => entry.itemId === itemId);
    if (entry) Object.assign(entry, changes);
  }
  try {
    localStorage.setItem(storageKey, JSON.stringify(all));
  } catch {
    /* Memory still works. */
  }
}
