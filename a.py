from flask import Flask, redirect, jsonify
import requests, time, json

app = Flask(__name__)

CACHE = {}
CACHE_TIME = 60  # saniye

def load_channels():
    with open("kanallar.json", "r") as f:
        return json.load(f)

def ping(url):
    try:
        start = time.time()
        r = requests.head(url, timeout=2)
        if r.status_code == 200:
            return time.time() - start
    except:
        return None
    return None

def get_best_url(channel):
    now = time.time()

    # cache varsa kullan
    if channel in CACHE:
        if now - CACHE[channel]["time"] < CACHE_TIME:
            return CACHE[channel]["url"]

    channels = load_channels()

    if channel not in channels:
        return None

    results = []

    for url in channels[channel]:
        t = ping(url)
        if t is not None:
            results.append((t, url))

    if not results:
        return None

    # en hızlı link
    best = sorted(results)[0][1]

    # cache kaydet
    CACHE[channel] = {
        "url": best,
        "time": now
    }

    return best

@app.route("/stream/<channel>")
def stream(channel):
    best_url = get_best_url(channel)

    if best_url:
        return redirect(best_url)

    return "Yayın yok", 404


# 📺 M3U üretici
@app.route("/playlist.m3u")
def playlist():
    channels = load_channels()

    m3u = "#EXTM3U\n"

    for ch in channels:
        m3u += f'#EXTINF:-1 tvg-id="{ch}" group-title="TV",{ch}\n'
        m3u += f"https://senin-domain.com/stream/{ch}\n"

    return m3u, 200, {"Content-Type": "audio/x-mpegurl"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
