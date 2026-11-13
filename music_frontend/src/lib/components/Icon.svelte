<script>
  let { name, size = 20 } = $props();
  const paths = {
    search: 'M21 21l-5-5M18 10a8 8 0 1 1-16 0 8 8 0 0 1 16 0Z',
    plus: 'M12 5v14M5 12h14',
    check: 'm5 12 4 4L19 6',
    arrow: 'M5 12h14m-5-5 5 5-5 5',
    back: 'M19 12H5m5-5-5 5 5 5',
    heart:
      'M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1.1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21l8.8-8.6a5.5 5.5 0 0 0 0-7.8Z',
    music:
      'M9 18V5l12-2v13M9 8l12-2M9 18a3 3 0 1 1-3-3c1.7 0 3 1.3 3 3Zm12-2a3 3 0 1 1-3-3c1.7 0 3 1.3 3 3Z',
    close: 'm6 6 12 12M6 18 18 6',
    like: 'M7 10v11H3V10h4Zm0 1 5-9c3 0 2 5 1 7h6c2 0 2 2 1 5l-2 7H7',
    dislike: 'M7 14V3H3v11h4Zm0-1 5 9c3 0 2-5 1-7h6c2 0 2-2 1-5l-2-7H7'
  };
</script>

<svg
  width={size}
  height={size}
  viewBox="0 0 24 24"
  fill="none"
  stroke="currentColor"
  stroke-width="1.7"
  stroke-linecap="round"
  stroke-linejoin="round"
  aria-hidden="true"><path d={paths[name] ?? paths.music} /></svg
>
