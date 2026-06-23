from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def lookup_phone_number(phone_number):
    url = "https://calltracer.in"
    headers = {
        "Host": "calltracer.in",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {
        "country": "IN",
        "q": phone_number
    }

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
                    if len(tds) > 1:
                        return tds[1].get_text(strip=True)
            return "N/A"

        data = {
            "Number": phone_number,
            "Complaints": get_value("Complaints"),
            "Owner Name": get_value("Owner Name"),
            "SIM Card": get_value("SIM card"),
            "Mobile State": get_value("Mobile State"),
            "IMEI Number": get_value("IMEI number"),
            "MAC Address": get_value("MAC address"),
            "Connection": get_value("Connection"),
            "IP Address": get_value("IP address"),
            "Owner Address": get_value("Owner Address"),
            "Hometown": get_value("Hometown"),
            "Reference City": get_value("Refrence City"),
            "Owner Personality": get_value("Owner Personality"),
            "Language": get_value("Language"),
            "Mobile Locations": get_value("Mobile Locations"),
            "Country": get_value("Country"),
            "Tracking History": get_value("Tracking History"),
            "Tracker ID": get_value("Tracker Id"),
            "Tower Locations": get_value("Tower Locations"),
        }

        if all(v == "N/A" for v in data.values() if v != phone_number):
            return {"error": "No data found for this number. Try another or use residential proxies."}

        return data

    except Exception as e:
        return {"error": f"Lookup failed: {str(e)}. Real ops rotate proxies + headers."}

# === PAGE 1: NEON WELCOME ===
HOME_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SAMARTH HACKER</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');
        body { margin:0; padding:0; background:#000; color:#00ffff; font-family:'VT323',monospace; overflow:hidden; }
        .scanlines { position:fixed; top:0; left:0; width:100%; height:100%; background:repeating-linear-gradient(transparent 0px,transparent 2px,rgba(0,255,255,0.1) 2px,rgba(0,255,255,0.1) 4px); pointer-events:none; z-index:10; }
        .glitch { position:relative; font-size:4rem; text-align:center; margin-top:20vh; text-shadow:0 0 10px #00ffff,0 0 20px #00ffff; animation:glitch 1s infinite; }
        @keyframes glitch { 0%{transform:translate(0);} 20%{transform:translate(-2px,2px);} 40%{transform:translate(-2px,-2px);} 60%{transform:translate(2px,2px);} 80%{transform:translate(2px,-2px);} 100%{transform:translate(0);} }
        .enter-btn { display:block; margin:50px auto; padding:20px 60px; font-size:2rem; background:transparent; color:#00ffff; border:4px solid #00ffff; box-shadow:0 0 30px #00ffff; cursor:pointer; transition:all 0.3s; }
        .enter-btn:hover { background:#00ffff; color:#000; box-shadow:0 0 50px #00ffff; }
        footer { position:fixed; bottom:10px; width:100%; text-align:center; font-size:1.2rem; }
    </style>
</head>
<body>
    <div class="scanlines"></div>
    <div class="glitch">WELCOME TO SAMARTH HACKER WEBSITE</div>
    <button class="enter-btn" onclick="window.location.href='/boot'">ENTER SYSTEM</button>
    <footer>Made by Samarth © 2026 | @Toxicadminn</footer>
</body>
</html>'''

# === PAGE 2: FAKE BOOT WITH ANIMATION ===
BOOT_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BOOT SEQUENCE</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');
        body { margin:0; padding:0; background:#000; color:#00ffff; font-family:'VT323',monospace; overflow:hidden; }
        .terminal { padding:20px; max-width:800px; margin:40px auto; border:2px solid #00ffff; box-shadow:0 0 40px #00ffff; animation:flicker 0.1s infinite alternate; }
        @keyframes flicker { 0%{opacity:0.95;} 100%{opacity:1;} }
        .loader { width:80px; height:80px; border:8px solid #333; border-top:8px solid #00ffff; border-radius:50%; animation:spin 1s linear infinite; margin:30px auto; }
        @keyframes spin { to { transform:rotate(360deg); } }
        .log { margin:5px 0; }
        footer { position:fixed; bottom:10px; width:100%; text-align:center; }
    </style>
</head>
<body>
    <div class="terminal" id="bootlog">
        <div class="log">[SYSTEM] Initializing Samarth Hacker Kernel v9.6.6...</div>
        <div class="log">[NETWORK] Connecting to darknet nodes...</div>
        <div class="log">[AUTH] Verifying Developer Samarth clearance...</div>
        <div class="loader"></div>
        <div class="log" id="status">ESTABLISHING SECURE TUNNEL...</div>
    </div>
    <footer>Made by Samarth © 2026 | @Toxicadminn</footer>
    <script>
        let logs = ["[CORE] Loading neon matrix...","[TRACE] Zooming into target grid...","[SPIN] Connecting to Developer Samarth...","[SUCCESS] Boot complete. Redirecting..."];
        let i = 0;
        const logDiv = document.getElementById('bootlog');
        const status = document.getElementById('status');
        function typeLog() {
            if (i < logs.length) {
                let newLog = document.createElement('div'); newLog.className='log'; newLog.textContent=logs[i]; logDiv.appendChild(newLog); logDiv.scrollTop=logDiv.scrollHeight; i++; setTimeout(typeLog,800);
            } else { status.textContent="CONNECTION ESTABLISHED"; setTimeout(()=>{window.location.href='/main';},1500); }
        }
        setTimeout(typeLog,600);
    </script>
</body>
</html>'''

# === PAGE 3: MAIN TRACKER ===
MAIN_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PHONE TRACKER v2026</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');
        body { margin:0; padding:0; background:#000; color:#00ffff; font-family:'VT323',monospace; overflow:hidden; }
        .scanlines { position:fixed; top:0; left:0; width:100%; height:100%; background:repeating-linear-gradient(transparent 0px,transparent 2px,rgba(0,255,255,0.08) 2px,rgba(0,255,255,0.08) 4px); pointer-events:none; z-index:10; }
        .container { max-width:900px; margin:40px auto; padding:20px; border:3px solid #00ffff; box-shadow:0 0 50px #00ffff; }
        input, button { font-family:'VT323',monospace; font-size:1.5rem; padding:15px; margin:10px; background:#111; color:#00ffff; border:2px solid #00ffff; }
        button { cursor:pointer; box-shadow:0 0 20px #00ffff; }
        button:hover { background:#00ffff; color:#000; }
        #result { margin-top:30px; white-space:pre-wrap; background:#111; padding:20px; border:2px solid #00ffff; min-height:300px; }
        footer { position:fixed; bottom:10px; width:100%; text-align:center; }
    </style>
</head>
<body>
    <div class="scanlines"></div>
    <div class="container">
        <h1 style="text-align:center; text-shadow:0 0 20px #00ffff;">WELCOME TO PHONE NUMBER TO ADDRESS WEBSITE</h1>
        <p style="text-align:center;">Enter number below and EXECUTE</p>
        <form id="lookupForm">
            <input type="text" id="phone" placeholder="+91XXXXXXXXXX" required>
            <button type="submit">EXECUTE TRACE</button>
        </form>
        <div id="result"></div>
    </div>
    <footer>Made by Samarth © 2026 | @Toxicadminn</footer>
    <script>
        document.getElementById('lookupForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const phone = document.getElementById('phone').value;
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = '<div style="color:#0f0;">[EXECUTING] Tracing number... Please wait.</div>';
            try {
                const res = await fetch('/lookup', { method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded'}, body:'phone=' + encodeURIComponent(phone) });
                const data = await res.json();
                if (data.error) {
                    resultDiv.innerHTML = `<div style="color:#f00;">[ERROR] ${data.error}</div>`;
                } else {
                    let html = '<div style="color:#0f0;">[SUCCESS] Result completed successfully</div><br>';
                    for (let key in data) { html += `<strong>${key}:</strong> ${data[key]}<br>`; }
                    resultDiv.innerHTML = html;
                }
            } catch(err) {
                resultDiv.innerHTML = '<div style="color:#f00;">[FAIL] Connection lost. Use VPN.</div>';
            }
        });
    </script>
</body>
</html>'''

@app.route('/')
def home():
    return HOME_HTML

@app.route('/boot')
def boot():
    return BOOT_HTML

@app.route('/main')
def main_page():
    return MAIN_HTML

@app.route('/lookup', methods=['POST'])
def lookup():
    phone = request.form.get('phone')
    if not phone:
        return jsonify({"error": "Phone number required"}), 400
    result = lookup_phone_number(phone)
    return jsonify(result)

if __name__ == '__main__':
    print("🚀 Samarth Hacker Tracker LIVE → http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
