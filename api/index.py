# =========================================================
# 👑 Credit: SAMARTH • Max-Glow Core v3.0
# =========================================================
from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>NUMBER TO INFO INFO ENGINE</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');
        * { margin:0; padding:0; box-sizing:border-box; }
        body {
            background: #000; color: #00ffff; font-family: 'VT323', monospace;
            min-height: 100vh; overflow: hidden;
            background-image: linear-gradient(rgba(0,255,255,0.03) 1px, transparent 1px),
                              linear-gradient(90deg, rgba(0,255,255,0.03) 1px, transparent 1px);
            background-size: 25px 25px;
        }
        .splash, .main { max-width: 480px; margin: 0 auto; border: 4px solid #00ffff; box-shadow: 0 0 40px #00ffff; border-radius: 12px; overflow: hidden; background: #0a0a0a; }
        .splash { height: 100vh; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 20px; }
        .title { font-size: 1.8rem; text-shadow: 0 0 20px #00ffff; margin-bottom: 20px; }
        button { padding: 15px 40px; font-size: 1.4rem; background: #000; color: #00ff9f; border: 3px solid #00ff9f; cursor: pointer; box-shadow: 0 0 20px #00ff9f; margin-top: 30px; }
        .boot { display: none; padding: 20px; text-align: center; }
        .main { display: none; }
        .input-box, .log, .results { margin: 15px; }
        /* Rest of styles same as before */
        .input-box { background: #000; border: 3px solid #00ffff; border-radius: 8px; padding: 12px; display: flex; align-items: center; gap: 10px; }
        input { flex: 1; background: transparent; border: none; color: #00ffff; font-size: 1.4rem; outline: none; }
        .buttons { display: flex; gap: 12px; margin: 0 15px 15px; }
        button.execute { flex: 1; padding: 14px; font-size: 1.3rem; border: 3px solid #00ff9f; color: #00ff9f; }
        .log { background: #000; border: 3px solid #00ffff; padding: 15px; min-height: 90px; font-size: 1.25rem; line-height: 1.4; color: #00ff9f; }
        .data-box { background: #000; border: 2px solid #00ffff; padding: 12px; margin-bottom: 10px; border-radius: 6px; }
        .label { color: #00ff9f; } .value { color: #fff; word-break: break-all; }
    </style>
</head>
<body>
    <!-- WELCOME SPLASH -->
    <div class="splash" id="splash">
        <div class="title">WELCOME TO NUMBERS TO<br>INFO ENGINE</div>
        <div style="color:#00ff9f; font-size:1.4rem;">MADE BY SAMARTH</div>
        <button onclick="startBoot()">ENTER SYSTEM</button>
    </div>

    <!-- FAKE BOOT -->
    <div class="boot" id="boot">
        <div class="title">INITIALIZING MAX-GLOW CORE v3.0...</div>
        <div id="bootLog" style="margin:20px 0; text-align:left; font-size:1.2rem; line-height:1.6;">
            > Connecting to secure nodes...<br>
            > Bypassing firewall...<br>
            > Establishing encrypted tunnel...<br>
            > Syncing with calltracer mirror...
        </div>
        <div style="color:#00ff9f;">● BOOT SEQUENCE IN PROGRESS ●</div>
    </div>

    <!-- MAIN INTERFACE -->
    <div class="main" id="main">
        <header style="padding:15px; text-align:center; border-bottom:3px solid #00ffff;">
            <div class="title">NUMBER TO INFO INFO ENGINE</div>
            <div style="color:#00ff9f;">Developer: SAMARTH</div>
        </header>

        <div class="input-box">
            <span style="font-size:1.8rem">📞</span>
            <input type="text" id="phoneInput" placeholder="Enter phone number" maxlength="15">
        </div>

        <div class="buttons">
            <button class="execute" onclick="executeQuery()">EXECUTE QUERY</button>
            <button onclick="resetAll()">RESET</button>
        </div>

        <div class="log" id="log">[*] Core online. Awaiting input.</div>

        <div class="results" id="results" style="display:none;">
            <div style="text-align:center; color:#00ff9f; margin:10px;">EXTRACTION COMPLETE</div>
            <div id="dataContainer"></div>
        </div>

        <div style="margin:15px; padding:12px; border:3px dashed #ff0044; color:#ffcccc; font-size:1.1rem;">
            NOTE: Information is for educational use only. Your number is safe.
        </div>
    </div>

    <!-- PHONK MUSIC - Metamorphosis -->
    <audio id="phonk" loop autoplay>
        <source src="https://cdn.pixabay.com/audio/2023/03/24/audio_3b7f5c5e1f.mp3" type="audio/mpeg"> <!-- Replace with better link if needed -->
    </audio>

    <script>
        let music = document.getElementById('phonk');

        function startBoot() {
            document.getElementById('splash').style.display = 'none';
            const bootScreen = document.getElementById('boot');
            bootScreen.style.display = 'block';

            setTimeout(() => {
                bootScreen.style.display = 'none';
                document.getElementById('main').style.display = 'block';
                music.play().catch(() => {}); // Autoplay on user interaction
            }, 2800); // Fake boot time
        }

        async function executeQuery() {
            // Same as previous version - real scraping
            const input = document.getElementById('phoneInput').value.trim();
            const log = document.getElementById('log');
            if (!input) { log.innerHTML = "[!] ENTER A VALID NUMBER"; return; }
            log.innerHTML = `[*] Querying ${input}...`;
            // ... (keep the fetch logic from previous version)
            try {
                const res = await fetch('/lookup', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({number: input}) });
                const data = await res.json();
                if (data.error) { log.innerHTML += `<br>[!] ${data.error}`; return; }
                log.innerHTML += `<br>[+] Data retrieved.`;
                const container = document.getElementById('dataContainer');
                container.innerHTML = '';
                Object.keys(data).forEach(key => {
                    const box = document.createElement('div');
                    box.className = 'data-box';
                    box.innerHTML = `<div class="label">\( {key.toUpperCase()}</div><div class="value"> \){data[key]}</div>`;
                    container.appendChild(box);
                });
                document.getElementById('results').style.display = 'block';
            } catch(e) { log.innerHTML += `<br>[!] Network error.`; }
        }

        function resetAll() {
            document.getElementById('phoneInput').value = '';
            document.getElementById('log').innerHTML = '[*] Core online. Awaiting input.';
            document.getElementById('results').style.display = 'none';
        }
    </script>
</body>
</html>"""

# Keep the same lookup_phone_number function and routes as in previous messages
def lookup_phone_number(phone_number):
    # ... (paste the full scraper function from earlier)
    url = "https://calltracer.in"
    headers = {"Host": "calltracer.in", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Content-Type": "application/x-www-form-urlencoded"}
    payload = {"country": "IN", "q": phone_number}
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        def get_value(label):
            cell = soup.find(string=lambda t: t and label in t)
            if cell:
                tr = cell.find_parent("tr")
                if tr and tr.find_all("td"):
                    tds = tr.find_all("td")
                    if len(tds) > 1: return tds[1].get_text(strip=True)
            return "N/A"
        data = { /* same dict as before */ "Number": phone_number, "Complaints": get_value("Complaints"), /* ... all fields */ }
        if all(v == "N/A" for v in list(data.values())[1:]): return {"error": "No data found for this number."}
        return data
    except Exception as e:
        return {"error": f"Error: {str(e)}"}

@app.route('/')
def index():
    return HTML_TEMPLATE

@app.route('/lookup', methods=['POST'])
def lookup():
    data = request.get_json()
    number = data.get('number') if data else None
    if not number: return jsonify({"error": "Number required"})
    result = lookup_phone_number(number)
    return jsonify(result)

if __name__ == '__main__':
    app.run()
