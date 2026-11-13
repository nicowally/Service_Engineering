import test from 'node:test';
import assert from 'node:assert/strict';

function storage() {
  const values = new Map();
  return {
    getItem: (key) => values.get(key) ?? null,
    setItem: (key, value) => values.set(key, value)
  };
}
let version = 0;
async function freshDemo() {
  return import(`../src/lib/services/demo.js?test=${version++}`);
}

test('sample albums and playlists reference existing tracks in their intended order', async () => {
  const { demoItems } = await freshDemo();
  const album = demoItems.find((item) => item.type === 'album');
  const playlist = demoItems.find((item) => item.type === 'playlist');
  assert.deepEqual(
    album.tracks.map((item) => item.title),
    ['Bohemian Rhapsody', 'Love of My Life']
  );
  assert.deepEqual(
    playlist.tracks.map((item) => item.title),
    ['Blinding Lights', 'Bohemian Rhapsody', 'Levitating']
  );
  for (const container of [album, playlist]) {
    for (const track of container.tracks) {
      assert.ok(demoItems.some((item) => item.id === track.id && item.type === 'track'));
    }
  }
});

test('collection writes are isolated by user, avoid duplicates and survive reloading', async () => {
  globalThis.localStorage = storage();
  const demo = await freshDemo();
  const benBefore = structuredClone(demo.getDemoCollection('demo-ben'));
  demo.changeDemoCollection('demo-anna', 'levitating', 'add');
  demo.changeDemoCollection('demo-anna', 'levitating', 'add');
  demo.changeDemoCollection('demo-anna', 'levitating', 'mark', {
    is_favourite: true,
    reaction: 'like'
  });
  assert.deepEqual(demo.getDemoCollection('demo-ben'), benBefore);
  const reloaded = await freshDemo();
  const added = reloaded
    .getDemoCollection('demo-anna')
    .filter((entry) => entry.music_item.id === 'levitating');
  assert.equal(added.length, 1);
  assert.equal(added[0].is_favourite, true);
  assert.equal(added[0].reaction, 'like');
  reloaded.changeDemoCollection('demo-anna', 'levitating', 'mark', { reaction: null });
  assert.equal(
    reloaded.getDemoCollection('demo-anna').find((entry) => entry.music_item.id === 'levitating')
      .reaction,
    null
  );
  reloaded.changeDemoCollection('demo-anna', 'levitating', 'remove');
  assert.ok(
    !reloaded.getDemoCollection('demo-anna').some((entry) => entry.music_item.id === 'levitating')
  );
  assert.deepEqual(reloaded.getDemoCollection('demo-ben'), benBefore);
});

test('corrupt or incompatible saved collections fall back to safe sample data', async () => {
  for (const value of [
    'broken json',
    '{"demo-anna":[null]}',
    '{"demo-anna":[],"demo-admin":[],"demo-ben":[{"itemId":"unknown"}]}'
  ]) {
    globalThis.localStorage = storage();
    localStorage.setItem('side-a-demo-collections-v1', value);
    const demo = await freshDemo();
    assert.equal(demo.getDemoCollection('demo-anna').length, 3);
    assert.equal(demo.getDemoCollection('demo-ben').length, 2);
  }
});

test('sample mode remains usable when browser storage is blocked', async () => {
  globalThis.localStorage = {
    getItem() {
      throw new Error('blocked');
    },
    setItem() {
      throw new Error('blocked');
    }
  };
  const demo = await freshDemo();
  assert.equal(demo.getDemoCollection('demo-admin').length, 0);
  demo.changeDemoCollection('demo-admin', 'levitating', 'add');
  assert.equal(demo.getDemoCollection('demo-admin')[0].music_item.title, 'Levitating');
});
