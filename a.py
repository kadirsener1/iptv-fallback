let CACHE = {};
let CACHE_TIME = 60; // saniye

async function ping(url) {
  try {
    let start = Date.now();
    let res = await fetch(url, { method: "HEAD" });
    if (res.ok) {
      return Date.now() - start;
    }
  } catch (e) {}
  return null;
}

async function getBestUrl(channel) {
  let now = Date.now();

  if (CACHE[channel] && (now - CACHE[channel].time < CACHE_TIME * 1000)) {
    return CACHE[channel].url;
  }

  // GitHub raw JSON çek
  let res = await fetch("https://raw.githubusercontent.com/kadirsener1/iptv-fallback/main/kanallar.json");
  let data = await res.json();

  if (!data[channel]) return null;

  let results = [];

  for (let url of data[channel]) {
    let t = await ping(url);
    if (t !== null) {
      results.push({ t, url });
    }
  }

  if (results.length === 0) return null;

  results.sort((a, b) => a.t - b.t);
  let best = results[0].url;

  CACHE[channel] = {
    url: best,
    time: now
  };

  return best;
}

export default {
  async fetch(request) {
    let url = new URL(request.url);

    // 🎬 STREAM
    if (url.pathname.startsWith("/stream/")) {
      let channel = url.pathname.split("/")[2];

      let best = await getBestUrl(channel);

      if (best) {
        return Response.redirect(best, 302);
      }

      return new Response("Yayın yok", { status: 404 });
    }

    // 📺 M3U
    if (url.pathname === "/playlist.m3u") {

      let res = await fetch("https://raw.githubusercontent.com/kadirsener1/iptv-fallback/main/kanallar.json");
      let data = await res.json();

      let m3u = "#EXTM3U\n";

      for (let ch in data) {
        m3u += `#EXTINF:-1 tvg-id="${ch}" group-title="TV",${ch}\n`;
        m3u += `https://34.magnitude.workers.dev/stream/${ch}\n`;
      }

      return new Response(m3u, {
        headers: { "Content-Type": "audio/x-mpegurl" }
      });
    }

    return new Response("OK");
  }
}
