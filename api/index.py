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
        body { background:#000; color:#00ffff; font-family:'VT323', monospace; min-height:100vh; padding:10px;
               background-image: linear-gradient(rgba(0,255,255,0.03)1px,transparent 1px),linear-gradient(90deg,rgba(0,255,255,0.03)1px,transparent 1px); background-size:25px 25px; }
        .splash, .boot, .main { max-width:480px; margin:0 auto; border:4px solid #00ffff; box-shadow:0 0 40px #00ffff; border-radius:12px; overflow:hidden; background:#0a0a0a; }
        .splash { height:100vh; display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center; padding:20px; }
        .title { font-size:1.8rem; text-shadow:0 0 20px #00ffff; margin-bottom:20px; }
        button { padding:15px 40px; font-size:1.4rem; background:#000; color:#00ff9f; border:3px solid #00ff9f; cursor:pointer; box-shadow:0 0 20px #00ff9f; margin-top:30px; }
        .boot { padding:30px 20px; text-align:center; display:none; }
        .main { display:none; }
        .input-box { margin:15px; background:#000; border:3px solid #00ffff; border-radius:8px; padding:12px; display:flex; align-items:center; gap:10px; }
        input { flex:1; background:transparent; border:none; color:#00ffff; font-size:1.4rem; outline:none; }
        .buttons { display:flex; gap:12px; margin:0 15px 15px; }
        button.execute { flex:1; padding:14px; font-size:1.3rem; border:3px solid #00ff9f; color:#00ff9f; }
        .log, .results { margin:15px; }
        .log { background:#000; border:3px solid #00ffff; padding:15px; min-height:90px; font-size:1.25rem; line-height:1.4; color:#00ff9f; }
        .data-box { background:#000; border:2px solid #00ffff; padding:12px; margin-bottom:10px; border-radius:6px; }
        .label { color:#00ff9f; } .value { color:#fff; word-break:break-all; }
    </style>
</head>
<body>

    <!-- WELCOME -->
    <div class="splash" id="splash">
        <div class="title">WELCOME TO NUMBERS TO<br>INFO ENGINE</div>
        <div style="color:#00ff9f;font-size:1.5rem;margin-bottom:30px;">MADE BY SAMARTH</div>
        <button onclick="startBoot()">ENTER SYSTEM</button>
    </div>

    <!-- BOOT -->
    <div class="boot" id="boot">
        <div class="title">INITIALIZING MAX-GLOW CORE v3.0...</div>
        <div id="bootLog" style="text-align:left;margin:25px 0;font-size:1.3rem;line-height:1.8;color:#00ff9f;"></div>
    </div>

    <!-- MAIN -->
    <div class="main" id="main">
        <header style="padding:15px;text-align:center;border-bottom:3px solid #00ffff;">
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

        <div class="log" id="log">[*] Core online. Ready for query.</div>

        <div class="results" id="results" style="display:none;">
            <div style="text-align:center;color:#00ff9f;margin:10px 0;">EXTRACTION COMPLETE</div>
            <div id="dataContainer"></div>
        </div>

        <div style="margin:15px;padding:12px;border:3px dashed #ff0044;color:#ffcccc;">
            NOTE: Those Informations are not coming [There data is not leaked in any database] [your number is safe]
        </div>
    </div>

    <!-- PHONK -->
    <audio id="phonk" loop>
        <source src="https://files.catbox.moe/0v4p2k.mp3" type="audio/mpeg">
    </audio>

    <script>
        const music = document.getElementById('phonk');
        const bootLines = ["> Connecting to secure nodes...", "> Bypassing tracer protection...", "> Establishing encrypted tunnel...", "> Syncing with calltracer.in mirror...", "> Data channels open.", "> System ready."];

        function startBoot() {
            document.getElementById('splash').style.display = 'none';
            const bootScreen = document.getElementById('boot');
            const bootLog = document.getElementById('bootLog');
            bootScreen.style.display = 'block';
            bootLog.innerHTML = '';

            let i = 0;
            const interval = setInterval(() => {
                if (i < bootLines.length) {
                    bootLog.innerHTML += bootLines[i] + '<br>';
                    i++;
                } else {
                    clearInterval(interval);
                    setTimeout(() => {
                        bootScreen.style.display = 'none';
                        document.getElementById('main').style.display = 'block';
                        music.play().catch(() => {});
                    }, 800);
                }
            }, 650);
        }

        async function executeQuery() {
            const input = document.getElementById('phoneInput').value.trim();
            const log = document.getElementById('log');
            if (!input) { log.innerHTML = "[!] ENTER VALID NUMBER"; return; }
            log.innerHTML = `[*] Querying ${input}...`;
            const resultsDiv = document.getElementById('results');
            const container = document.getElementById('dataContainer');
            container.innerHTML = '';
            resultsDiv.style.display = 'none';

            try {
                const res = await fetch('/lookup', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({number: input})
                });
                const data = await res.json();
                
                if (data.error) {
                    log.innerHTML += `<br>[!] ${data.error}`;
                    return;
                }
                
                log.innerHTML += `<br>[+] Data retrieved successfully.`;
                
                Object.keys(data).forEach(key => {
                    const box = document.createElement('div');
                    box.className = 'data-box';
                    box.innerHTML = `<div class="label">\( {key.toUpperCase()}</div><div class="value"> \){data[key] || 'N/A'}</div>`;
                    container.appendChild(box);
                });
                
                resultsDiv.style.display = 'block';
            } catch(e) {
                log.innerHTML += `<br>[!] Network error.`;
            }
        }

        function resetAll() {
            document.getElementById('phoneInput').value = '';
            document.getElementById('log').innerHTML = '[*] Core online. Ready for query.';
            document.getElementById('results').style.display = 'none';
        }
    </script>
</body>
</html>"""

def lookup_phone_number(phone_number):
    url = "https://calltracer.in"
    headers = {"Host": "calltracer.in","User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Content-Type": "application/x-www-form-urlencoded"}
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

        data = {"Number": phone_number,"Complaints": get_value("Complaints"),"Owner Name": get_value("Owner Name"),"SIM Card": get_value("SIM card"),"Mobile State": get_value("Mobile State"),"IMEI Number": get_value("IMEI number"),"MAC Address": get_value("MAC address"),"Connection": get_value("Connection"),"IP Address": get_value("IP address"),"Owner Address": get_value("Owner Address"),"Hometown": get_value("Hometown"),"Reference City": get_value("Refrence City"),"Owner Personality": get_value("Owner Personality"),"Language": get_value("Language"),"Mobile Locations": get_value("Mobile Locations"),"Country": get_value("Country"),"Tracking History": get_value("Tracking History"),"Tracker ID": get_value("Tracker Id"),"Tower Locations": get_value("Tower Locations")}

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
    app.run(host='0.0.0.0', port=5000, debug=True)
