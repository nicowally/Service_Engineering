<script>
  let { item, hero = false } = $props();
  const palettes = [
    ['#d1e3d5', '#2c604d', '#f3e6bd'],
    ['#f0bc9e', '#a83f36', '#f9dcc0'],
    ['#c5cbe6', '#434b85', '#e5d9ed'],
    ['#ebce89', '#8d4a32', '#f7e7c5'],
    ['#c9dddd', '#256568', '#e8d6b6'],
    ['#dbb6c4', '#764465', '#f0d9cc']
  ];
  let palette = $derived(
    palettes[[...item.title].reduce((sum, char) => sum + char.charCodeAt(0), 0) % palettes.length]
  );
</script>

<div
  class="cover"
  class:hero
  class:playlist={item.type === 'playlist'}
  style={`--cover-bg:${palette[0]};--cover-ink:${palette[1]};--cover-paper:${palette[2]}`}
  aria-hidden="true"
>
  <div class="cover-top">
    <span>SIDE A / LIBRARY</span><span>{item.release_year ?? 'MIX'}</span>
  </div>
  <div class="cover-art">
    <div class="arch"></div>
    <div class="disc"><div class="disc-label"><span>sa</span></div></div>
    <div class="stripe"></div>
  </div>
  <div class="cover-title">{item.title}</div>
  <div class="cover-bottom">
    <span>{item.artist ?? 'A PERSONAL SELECTION'}</span><span>{item.type.toUpperCase()}</span>
  </div>
</div>

<style>
  .cover {
    aspect-ratio: 1.14;
    background: var(--cover-bg);
    color: var(--cover-ink);
    position: relative;
    overflow: hidden;
    padding: 19px;
    display: flex;
    flex-direction: column;
  }
  .cover-top,
  .cover-bottom {
    display: flex;
    justify-content: space-between;
    font-size: 8px;
    font-weight: 700;
    letter-spacing: 1.1px;
    z-index: 1;
    gap: 10px;
  }
  .cover-bottom {
    margin-top: 10px;
    font-size: 8px;
    letter-spacing: 0.5px;
  }
  .cover-art {
    position: absolute;
    inset: 35px 0 34px;
    overflow: hidden;
  }
  .arch {
    width: 56%;
    height: 112%;
    border-radius: 50% 50% 0 0;
    background: var(--cover-ink);
    position: absolute;
    top: 8%;
    right: 7%;
    transform: rotate(23deg);
    opacity: 0.22;
  }
  .disc {
    position: absolute;
    width: 56%;
    aspect-ratio: 1;
    left: 7%;
    top: 3%;
    border-radius: 50%;
    background: repeating-radial-gradient(
      circle,
      var(--cover-ink) 0,
      var(--cover-ink) 2px,
      transparent 3px,
      transparent 5px
    );
    display: grid;
    place-items: center;
    transform: rotate(-16deg);
  }
  .disc-label {
    width: 38%;
    aspect-ratio: 1;
    border-radius: 50%;
    background: var(--cover-paper);
    display: grid;
    place-items: center;
    font-family: Georgia, serif;
    font-size: 27px;
    font-style: italic;
  }
  .disc-label:after {
    content: '';
    position: absolute;
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background: var(--cover-ink);
    bottom: 41%;
  }
  .cover-title {
    position: relative;
    font-family: Georgia, serif;
    font-size: clamp(25px, 2.8vw, 39px);
    line-height: 0.98;
    font-weight: 700;
    max-width: 88%;
    margin-top: auto;
    padding-top: 115px;
    letter-spacing: -1.2px;
    text-wrap: balance;
  }
  .stripe {
    position: absolute;
    right: -15%;
    top: 51%;
    height: 22px;
    width: 75%;
    background: var(--cover-paper);
    transform: rotate(-35deg);
    opacity: 0.65;
  }
  .playlist .disc {
    left: 28%;
    top: -8%;
    width: 64%;
  }
  .playlist .arch {
    left: -3%;
    right: auto;
    transform: rotate(-25deg);
  }
  .hero {
    aspect-ratio: 1;
    padding: 23px;
    box-shadow: 0 18px 30px #233d2022;
  }
  .hero .cover-title {
    font-size: 45px;
    padding-top: 120px;
  }
  @media (max-width: 600px) {
    .cover-title {
      font-size: 32px;
    }
    .hero .cover-title {
      font-size: 34px;
    }
    .cover {
      aspect-ratio: 1.1;
    }
  }
</style>
