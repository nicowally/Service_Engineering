import * as api from '#lib/services/api.js';

// Shared reactive state. Components render it; services handle data access.
export const library = $state({
  items: [],
  users: [],
  user: null,
  collection: [],
  loading: true,
  collectionLoading: false,
  error: '',
  pending: {},
  ready: false
});
let initialization;
async function refreshCollection(user) {
  library.collectionLoading = true;
  library.collection = [];
  try {
    const entries = await api.getCollection(user);
    if (library.user?.id === user.id) library.collection = entries;
  } finally {
    if (library.user?.id === user.id) library.collectionLoading = false;
  }
}
export function initializeLibrary() {
  if (initialization) return initialization;
  initialization = (async () => {
    library.loading = true;
    library.error = '';
    try {
      [library.items, library.users] = await Promise.all([api.listMusic(), api.listUsers()]);
      let savedUser;
      try {
        savedUser = localStorage.getItem('side-a-selected-user');
      } catch {
        /* Optional preference. */
      }
      library.user =
        library.users.find((user) => user.id === savedUser) ??
        library.users.find((user) => user.username === 'anna') ??
        library.users[0] ??
        null;
      if (library.user) await refreshCollection(library.user);
      library.ready = true;
    } catch (error) {
      library.error = error.message;
      initialization = null;
    } finally {
      library.loading = false;
    }
  })();
  return initialization;
}
export async function selectUser(userId) {
  const user = library.users.find((entry) => entry.id === userId);
  if (!user) return;
  library.user = user;
  library.error = '';
  try {
    try {
      localStorage.setItem('side-a-selected-user', user.id);
    } catch {
      /* Optional preference. */
    }
    await refreshCollection(user);
  } catch (error) {
    if (library.user?.id === user.id) library.error = error.message;
  }
}
export function entryFor(itemId) {
  return library.collection.find((entry) => entry.music_item.id === itemId);
}
export async function changeCollection(itemId, action, changes = {}) {
  const user = library.user;
  if (!user || library.collectionLoading || library.pending[itemId]) return;
  library.pending[itemId] = true;
  library.error = '';
  try {
    if (action === 'toggle') {
      if (entryFor(itemId)) await api.removeFromCollection(user, itemId);
      else await api.addToCollection(user, itemId);
    } else {
      await api.markCollectionItem(user, itemId, changes);
    }
    const entries = await api.getCollection(user);
    if (library.user?.id === user.id) library.collection = entries;
  } catch (error) {
    if (library.user?.id === user.id) library.error = error.message;
  } finally {
    delete library.pending[itemId];
  }
}
