import os
import requests
import re
from flask import Flask, render_template_string, request, jsonify, Response

app = Flask(__name__)

# RapidAPI'den aldığın güncel anahtarını buraya sabitledim kanka:
RAPIDAPI_KEY = "20119f7480msh39541b239b12360p16c4acjsn913a16243db6"

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
        .status-box { margin-top: 25px; background-color: #05070c; border-radius: 8px; padding: 15px; font-family: monospace; font-size: 13px; color: #34d399; text-align: center; border: 1px solid rgba(52, 211, 153, 0.2); }
    </style>
</head>
<body>
<div class="container">
    <h1>🌍 Kuresel Medya Indirici</h1>
    <p class="subtitle">Herhangi bir cihazdan link girin, saniyeler icinde indirin.</p>
    
    <div class="input-group">
        <label for="url">Medya Linki (URL)</label>
        <input type="text" id="url" placeholder="YouTube linki yapıştırın..." autocomplete="off">
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
    function processDownload() {
        const url = document.getElementById('url').value.trim();
        const mode = document.getElementById('mp3').checked ? 'mp3' : 'mp4';
        const btn = document.getElementById('downloadBtn');
        const status = document.getElementById('statusText');

        if (!url) { alert("Lütfen link girin!"); return; }

        btn.disabled = true;
        status.style.color = "#34d399";
        status.innerText = "⏳ Medya işleniyor, lütfen sayfayı kapatmayın...";

        fetch('/process', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url, mode: mode })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success && data.download_route) {
                status.style.color = "#34d399";
                status.innerText = "✅ İşlem tamam! İndirme doğrudan sitenizden başlıyor.";
                btn.disabled = false;
                
                const a = document.createElement('a');
                a.href = data.download_route;
                document.body.appendChild(a);
                a.click();
                a.remove();
            } else {
                throw new Error(data.error || "İndirme bağlantısı oluşturulamadı.");
            }
        })
        .catch(err => {
            status.style.color = "#ef4444";
            status.innerText = "❌ Hata: Medya şu an işlenemedi. Lütfen az sonra tekrar deneyin.";
            btn.disabled = false;
        });
    }
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

def get_youtube_id(url):
    pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/|youtube\.com\/shorts\/)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else None

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    url = data.get('url')
    mode = data.get('mode')
    
    video_id = get_youtube_id(url)
    if not video_id:
        return jsonify({"success": False, "error": "Geçersiz YouTube linki"}), 400

    return jsonify({
        "success": True, 
        "download_route": f"/stream_file?id={video_id}&mode={mode}"
    })

@app.route('/stream_file')
def stream_file():
    video_id = request.args.get('id')
    mode = request.args.get('mode')
    
    file_url = None

    if mode == 'mp3':
        # ---- MP3 İÇİN SENİN RAPIDAPI MOTORUN (YOUTUBE MP3) ----
        url = "https://youtube-mp36.p.rapidapi.com/dl"
        headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": "youtube-mp36.p.rapidapi.com"
        }
        try:
            res = requests.get(url, headers=headers, params={"id": video_id}, timeout=12)
            if res.status_code == 200:
                file_url = res.json().get("link")
        except Exception as e:
            print(f"MP3 API Hatasi: {e}", flush=True)
    else:
        # ---- MP4 (VIDEO) İÇİN ÇOKLU ALTYAPI GEÇİŞ SİSTEMİ ----
        # 1. Havuz: Cobalt Engine Tüneli
        try:
            video_res = requests.post("https://api.cobalt.tools/api/json", json={
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "isAudioOnly": False,
                "vQuality": "720"
            }, headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"}, timeout=10)
            if video_res.status_code == 200:
                file_url = video_res.json().get("url")
        except:
            pass

        # 2. Havuz (Yedek): Devesed Video Tüneli
        if not file_url:
            try:
                alt_res = requests.get(f"https://api.devesed.com/yt/{video_id}", timeout=10)
                if alt_res.status_code == 200:
                    file_url = alt_res.json().get('mp4')
            except:
                pass

    if not file_url or not file_url.startswith("http"):
        return "Medya sunucusu şu an yanıt vermiyor veya API limiti tükendi. Lütfen birazdan tekrar deneyin.", 503

    # Gerçek medyayı (mp3/mp4) Render sunucusu üzerinden gizli akış (stream) olarak aktarıyoruz
    try:
        file_res = requests.get(file_url, stream=True, timeout=45)
        ext = "mp3" if mode == 'mp3' else "mp4"
        filename = f"media_{video_id}.{ext}"
        
        response_headers = {
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": "audio/mpeg" if mode == 'mp3' else "video/mp4"
        }
        
        def generate():
            for chunk in file_res.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk
                    
        return Response(generate(), headers=response_headers)
    except:
        return "Medya aktarılırken bir senkronizasyon hatası oluştu.", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
