import os
from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Global Media Downloader</title>
    <style>
        :root {
            --bg-color: #0b0f19;
            --container-bg: #111827;
            --accent-color: #10b981;
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
            --border-color: #374151;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', system-ui, sans-serif; }
        body { background-color: var(--bg-color); color: var(--text-main); display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; }
        .container { background-color: var(--container-bg); border: 1px solid var(--border-color); border-radius: 16px; padding: 40px; width: 100%; max-width: 600px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.5); }
        h1 { font-size: 24px; margin-bottom: 6px; color: var(--accent-color); font-weight: 700; text-align: center; }
        .subtitle { font-size: 14px; color: var(--text-muted); margin-bottom: 30px; text-align: center; }
        .input-group { margin-bottom: 25px; }
        label { display: block; font-size: 11px; text-transform: uppercase; margin-bottom: 10px; color: var(--text-muted); font-weight: 700; }
        input[type="text"] { width: 100%; padding: 14px; background-color: var(--bg-color); border: 1px solid var(--border-color); border-radius: 8px; color: var(--text-main); font-size: 15px; }
        input[type="text"]:focus { outline: none; border-color: var(--accent-color); }
        .radio-group { display: flex; gap: 20px; margin-bottom: 30px; }
        .radio-btn { flex: 1; position: relative; }
        .radio-btn input[type="radio"] { position: absolute; opacity: 0; }
        .radio-label { display: block; padding: 16px; text-align: center; background-color: var(--bg-color); border: 1px solid var(--border-color); border-radius: 8px; cursor: pointer; font-size: 15px; font-weight: 600; }
        .radio-btn input[type="radio"]:checked + .radio-label { border-color: var(--accent-color); background-color: rgba(16, 185, 129, 0.08); color: var(--accent-color); }
        button { width: 100%; padding: 16px; background-color: var(--accent-color); border: none; border-radius: 8px; color: #000; font-size: 16px; font-weight: 700; cursor: pointer; transition: background 0.2s; }
        button:disabled { background-color: var(--border-color); color: var(--text-muted); cursor: not-allowed; }
        .status-box { margin-top: 25px; background-color: #05070c; border-radius: 8px; padding: 15px; font-family: monospace; font-size: 13px; color: #34d399; text-align: center; border: 1px solid rgba(52, 211, 153, 0.2); white-space: pre-wrap; word-break: break-all; }
    </style>
</head>
<body>
<div class="container">
    <h1>🌍 Kuresel Medya Indirici</h1>
    <p class="subtitle">YouTube ve Shorts videolarını anında MP3 veya MP4 olarak indirin.</p>
    
    <div class="input-group">
        <label for="url">Medya Linki (URL)</label>
        <input type="text" id="url" placeholder="YouTube veya Shorts linki yapıştırın..." autocomplete="off">
    </div>

    <label>Format</label>
    <div class="radio-group">
        <div class="radio-btn">
            <input type="radio" id="mp3" name="format" value="mp3" checked>
            <label for="mp3" class="radio-label">🎵 MP3 (Ses)</label>
        </div>
        <div class="radio-btn">
            <input type="radio" id="mp4" name="format" value="mp4">
            <label for="mp4" class="radio-label">🎥 MP4 (Video)</label>
        </div>
    </div>

    <button id="downloadBtn" onclick="processDownload()">Medyayı Hazırla ve İndir</button>
    <div class="status-box" id="statusText">Link girilmesi bekleniyor...</div>
</div>

<script>
    const RAPIDAPI_KEY = "20119f7480msh39541b239b12360p16c4acjsn913a16243db6";

    function extractVideoId(url) {
        const pattern = /(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\\/\\n\\s]+\\/\\S+\\/|(?:v|e(?:mbed)?)\\/|\\S*?[?&]v=)|youtu\.be\\/|youtube\.com\\/shorts\\/)([a-zA-Z0-9_-]{11})/;
        const match = url.match(pattern);
        return (match && match[1]) ? match[1] : null;
    }

    function processDownload() {
        const urlInput = document.getElementById('url').value.trim();
        const mode = document.getElementById('mp3').checked ? 'mp3' : 'mp4';
        const btn = document.getElementById('downloadBtn');
        const status = document.getElementById('statusText');

        if (!urlInput) { alert("Lütfen bir link girin!"); return; }

        const videoId = extractVideoId(urlInput);
        if (!videoId) {
            alert("Geçerli bir YouTube veya Shorts linki bulunamadı!");
            return;
        }

        btn.disabled = true;
        status.style.color = "#34d399";
        status.innerText = "⏳ Medya formatı hazırlanıyor, lütfen bekleyin...";

        if (mode === 'mp3') {
            const apiUrl = `https://youtube-mp36.p.rapidapi.com/dl?id=${videoId}`;
            
            fetch(apiUrl, {
                method: "GET",
                headers: {
                    "x-rapidapi-key": RAPIDAPI_KEY,
                    "x-rapidapi-host": "youtube-mp36.p.rapidapi.com"
                }
            })
            .then(response => {
                if (!response.ok) throw new Error("RapidAPI bağlantı hatası: " + response.status);
                return response.json();
            })
            .then(data => {
                if (data && data.status === "processing") {
                    status.innerText = "⏳ Ses dosyası dönüştürülüyor, 3 saniye içinde otomatik tekrar denenecek...";
                    setTimeout(processDownload, 3000);
                    return;
                }
                if (data && data.status === "ok" && data.link) {
                    triggerDownload(data.link, status, btn);
                } else {
                    throw new Error(data.msg || "MP3 indirme bağlantısı alınamadı.");
                }
            })
            .catch(err => showHata(err.message, status, btn));
        } 
        else {
            fetch("https://cobalt.api.unblockit.pro/api/json", {
                method: "POST",
                headers: {
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    url: "https://www.youtube.com/watch?v=" + videoId,
                    isAudioOnly: false,
                    vQuality: "720",
                    filenamePattern: "basic"
                })
            })
            .then(response => {
                if (!response.ok) throw new Error("Video tünel sunucusu meşgul, durum kodu: " + response.status);
                return response.json();
            })
            .then(data => {
                if (data && data.url) {
                    triggerDownload(data.url, status, btn);
                } else if (data && data.text) {
                    throw new Error(data.text);
                } else {
                    throw new Error("Video tünelinden geçerli veri alınamadı.");
                }
            })
            .catch(err => showHata(err.message, status, btn));
        }
    }

    function triggerDownload(downloadUrl, status, btn) {
        status.style.color = "#34d399";
        status.innerText = "✅ İşlem tamam! İndirme tarayıcınızda başlatıldı.";
        btn.disabled = false;
        window.location.href = downloadUrl;
    }

    function showHata(message, status, btn) {
        status.style.color = "#ef4444";
        status.innerText = "Hata Detayı: " + message;
        btn.disabled = false;
    }
</script>
</body>
</html>
"""

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
