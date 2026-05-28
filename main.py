import os
from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pro Media Downloader</title>
    <style>
        :root { --bg: #0b0f19; --card: #111827; --accent: #10b981; --text: #f3f4f6; }
        body { background: var(--bg); color: var(--text); font-family: system-ui; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
        .card { background: var(--card); padding: 30px; border-radius: 16px; width: 90%; max-width: 500px; box-shadow: 0 10px 25px rgba(0,0,0,0.3); }
        input, select, button { width: 100%; padding: 15px; margin-bottom: 15px; border-radius: 8px; border: 1px solid #374151; background: #05070c; color: white; }
        button { background: var(--accent); color: black; font-weight: bold; border: none; cursor: pointer; }
        #progress-container { display: none; margin-top: 20px; }
        #progress-bar { width: 0%; height: 8px; background: var(--accent); border-radius: 4px; transition: width 0.3s; }
        #download-ready { display: none; background: #3b82f6; }
    </style>
</head>
<body>
<div class="card">
    <h2 style="text-align:center; color:var(--accent)">🚀 Pro Medya İndirici</h2>
    <input type="text" id="url" placeholder="YouTube Linki...">
    <select id="format"><option value="mp3">MP3 (Ses)</option><option value="mp4">MP4 (Video)</option></select>
    <select id="quality"><option value="1080">1080p</option><option value="720">720p</option></select>
    
    <button id="btn" onclick="startProcess()">Medya Hazırla</button>
    <button id="download-ready" onclick="downloadFile()">✅ Dosya Hazır! İndir</button>

    <div id="progress-container">
        <div id="progress-bar"></div>
        <p id="status" style="text-align:center; font-size:12px; margin-top:5px;"></p>
    </div>
</div>

<script>
    let finalUrl = "";

    async function startProcess() {
        const url = document.getElementById('url').value;
        const format = document.getElementById('format').value;
        const quality = document.getElementById('quality').value;
        const btn = document.getElementById('btn');
        const progress = document.getElementById('progress-container');
        const bar = document.getElementById('progress-bar');
        const status = document.getElementById('status');
        const dlBtn = document.getElementById('download-ready');

        if(!url) return alert("Link gir!");
        
        btn.disabled = true;
        progress.style.display = 'block';
        bar.style.width = '30%';
        status.innerText = "Sunucuya bağlanılıyor...";

        const res = await fetch("https://api.cobalt.tools/api/json", {
            method: "POST",
            headers: { "Accept": "application/json", "Content-Type": "application/json" },
            body: JSON.stringify({ 
                url: url, 
                vQuality: quality, 
                isAudioOnly: (format === 'mp3'),
                filenamePattern: "classic" 
            })
        });
        
        const data = await res.json();
        
        if (data.url) {
            bar.style.width = '100%';
            status.innerText = "İşlem Tamamlandı!";
            finalUrl = data.url;
            dlBtn.style.display = 'block';
            btn.style.display = 'none';
        } else {
            status.innerText = "❌ Hata: " + (data.text || "Bir şeyler ters gitti");
            btn.disabled = false;
        }
    }

    function downloadFile() { window.location.href = finalUrl; }
</script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
