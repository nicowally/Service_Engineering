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
  return (readCollections()[userId] ?? []).map(({ itemId, ...entry }) => ({
    ...entry,
    music_item: demoItems.find((item) => item.id === itemId),
    added_at: '2026-11-10T12:00:00Z'
  }));
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
