import {
  demoUsers,
  getDemoItems,
  getDemoCollection,
  changeDemoCollection,
  saveDemoItem,
  deleteDemoItem,
  getDemoComments,
  addDemoComment,
  getDemoRating,
  setDemoRating
} from './demo.js';

// These variables are public. Database credentials belong in FastAPI only.
export const demoMode = import.meta.env.VITE_USE_DEMO_DATA !== 'false';
const baseUrl = (import.meta.env.VITE_API_BASE_URL || '/api').replace(/\/$/, '');
async function request(path, { method = 'GET', body, user } = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 10000);
  try {
    const response = await fetch(`${baseUrl}${path}`, {
      method,
      signal: controller.signal,
      headers: {
        ...(body ? { 'Content-Type': 'application/json' } : {}),
        ...(user ? { 'X-Username': user.username } : {})
      },
      ...(body ? { body: JSON.stringify(body) } : {})
    });
    if (response.status === 204) return null;
    const data = await response.json().catch(() => null);
    if (!response.ok) {
      const detail = data?.detail;
      const message = Array.isArray(detail)
        ? detail.map((error) => error.msg).join('. ')
        : typeof detail === 'string'
          ? detail
          : detail?.message;
      throw new Error(message || `The API returned an error (${response.status}).`);
    }
    return data;
  } catch (error) {
    if (error.name === 'AbortError')
      throw new Error('The API took too long to respond. Please try again.');
    if (error instanceof TypeError)
      throw new Error('Cannot reach FastAPI. Check that the backend is running.');
    throw error;
  } finally {
    clearTimeout(timer);
  }
}
export async function listMusic() {
  return demoMode ? structuredClone(getDemoItems()) : request('/music-items');
}
export async function listUsers() {
  return demoMode ? structuredClone(demoUsers) : request('/users');
}
export async function getMusic(id) {
  if (!demoMode) return request(`/music-items/${encodeURIComponent(id)}`);
  const item = getDemoItems().find((entry) => entry.id === id);
  if (!item) throw new Error('This music item could not be found.');
  return structuredClone(item);
}
export async function getCollection(user) {
  return demoMode ? getDemoCollection(user.id) : request(`/users/${user.id}/collection`);
}
export async function addToCollection(user, itemId) {
  if (demoMode) return changeDemoCollection(user.id, itemId, 'add');
  return request(`/users/${user.id}/collection`, {
    method: 'POST',
    body: { music_item_id: itemId },
    user
  });
}
export async function removeFromCollection(user, itemId) {
  if (demoMode) return changeDemoCollection(user.id, itemId, 'remove');
  return request(`/users/${user.id}/collection/${itemId}`, { method: 'DELETE', user });
}
export async function markCollectionItem(user, itemId, changes) {
  if (demoMode) return changeDemoCollection(user.id, itemId, 'mark', changes);
  return request(`/users/${user.id}/collection/${itemId}`, {
    method: 'PATCH',
    body: changes,
    user
  });
}

export async function saveMusic(user, body, itemId = null) {
  if (demoMode) return saveDemoItem(user, body, itemId);
  if (itemId) return request(`/music-items/${itemId}`, { method: 'PATCH', body, user });
  return request(body.type === 'track' ? '/music-items/tracks' : '/music-items/albums', {
    method: 'POST',
    body:
      body.type === 'track'
        ? Object.fromEntries(Object.entries(body).filter(([key]) => key !== 'type'))
        : body,
    user
  });
}
export async function deleteMusic(user, itemId) {
  if (demoMode) return deleteDemoItem(user, itemId);
  return request(`/music-items/${itemId}`, { method: 'DELETE', user });
}
export async function getAllCollections(user) {
  if (!demoMode) return request('/collections', { user });
  if (user?.role !== 'admin') throw new Error('Only admins can view all collections.');
  return demoUsers.map((entry) => ({
    user_id: entry.id,
    username: entry.username,
    items: getDemoCollection(entry.id)
  }));
}
export async function getComments(itemId) {
  return demoMode ? getDemoComments(itemId) : request(`/music-items/${itemId}/comments`);
}
export async function addComment(user, itemId, text) {
  if (demoMode) return addDemoComment(user, itemId, text);
  return request(`/music-items/${itemId}/comments?user_id=${encodeURIComponent(user.id)}`, {
    method: 'POST',
    body: { text }
  });
}
export async function getRating(itemId) {
  return demoMode ? getDemoRating(itemId) : request(`/music-items/${itemId}/rating`);
}
export async function setRating(user, itemId, stars) {
  if (demoMode) return setDemoRating(user, itemId, stars);
  return request(`/music-items/${itemId}/rating?user_id=${encodeURIComponent(user.id)}`, {
    method: 'PUT',
    body: { stars }
  });
}
