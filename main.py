import os
import subprocess
import glob
import sys
from flask import Flask, render_template_string, request, jsonify, send_file

app = Flask(__name__)

TMP_DIR = os.path.join(os.getcwd(), "downloads_temp")
os.makedirs(TMP_DIR, exist_ok=True)

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
        <input type="text" id="url" placeholder="YouTube, Spotify, Suno vb. link yapıştırın..." autocomplete="off">
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
        status.innerText = "⏳ Bulut sunucusu YouTube engelini aşıyor... (30 sn sürebilir)";

        fetch('/process', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url, mode: mode })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw new Error(err.error || "İndirme hatası"); });
            }
            return response.blob().then(blob => ({ blob }));
        })
        .then(({ blob }) => {
            status.style.color = "#34d399";
            status.innerText = "✅ İşlem tamam! İndirme başladı.";
            btn.disabled = false;
            
            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = mode === 'mp3' ? 'download.mp3' : 'download.mp4';
            document.body.appendChild(a);
            a.click();
            a.remove();
        })
        .catch(err => {
            status.style.color = "#ef4444";
            status.innerText = "❌ Hata: " + err.message;
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

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    url = data.get('url')
    mode = data.get('mode')
    
    if not url:
        return jsonify({"error": "Link bos olamaz"}), 400

    out_template = os.path.join(TMP_DIR, "file_%(id)s.%(ext)s")
    
    # YouTube bot duvarını aşmak için iOS/Safari taklidi ve gelişmiş extractor parametreleri ekliyoruz
    base_args = [
        "yt-dlp",
        "--extractor-args", "youtube:player-client=ios,web_safari",
        "--user-agent", "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
        "--add-header", "Accept-Language:tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        "--no-check-certificates",
        "-o", out_template,
        url
    ]
    
    # Komut dizilimini Flask'ın hata vermeyeceği şekilde birleştiriyoruz
    if mode == 'mp3':
        cmd = [base_args[0]] + base_args[1:5] + ["-f", "ba", "-x", "--audio-format", "mp3"] + base_args[5:]
    else:
        cmd = [base_args[0]] + base_args[1:5] + ["-f", "mp4"] + base_args[5:]
        
    try:
        for f in glob.glob(os.path.join(TMP_DIR, "file_*")):
            try: os.remove(f)
            except: pass
            
        print(f"Komut calistiriliyor: {' '.join(cmd)}", flush=True)
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=90)
        
        print(f"STDOUT: {result.stdout}", flush=True)
        print(f"STDERR: {result.stderr}", flush=True)
        
        if result.returncode == 0:
            downloaded_files = glob.glob(os.path.join(TMP_DIR, "file_*"))
            if downloaded_files:
                return send_file(downloaded_files[0], as_attachment=True)
            else:
                return jsonify({"error": "Dosya sunucuda olusturulamadi."}), 500
        else:
            lines = [line.strip() for line in result.stderr.split('\n') if line.strip()]
            clean_error = lines[-1] if lines else "Bilinmeyen hata"
            if "sign in to confirm" in result.stderr.lower() or "bot" in result.stderr.lower():
                clean_error = "YouTube bot duvarı hala aktif. Başka platform linki (Suno/SoundCloud vb.) deneyebilir veya kodu lokal pydroid'de çalıştırabilirsin."
            return jsonify({"error": f"yt-dlp hatasi: {clean_error}"}), 400
            
    except Exception as e:
        return jsonify({"error": f"Sistem hatası: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
