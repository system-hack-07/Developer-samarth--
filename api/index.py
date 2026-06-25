from flask import Flask, request, jsonify, send_from_directory
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

# ============================================================
# YOUR ORIGINAL LOOKUP FUNCTION - UNCHANGED
# ============================================================

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


# ============================================================
# ROUTE TO SERVE MP3 FILE FROM DOWNLOAD FOLDER
# ============================================================

@app.route('/download/<path:filename>')
def serve_audio(filename):
    return send_from_directory('download', filename)


# ============================================================
# PAGE 1: WELCOME TO SAMARTH WEBSITE (DARK BOLD)
# ============================================================

HOME_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Samarth Website</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #000000;
            font-family: 'Arial Black', 'Impact', sans-serif;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            max-width: 750px;
            width: 100%;
            padding: 60px 50px;
            background: #0a0a0a;
            border: 3px solid #1a1a1a;
            border-radius: 20px;
            text-align: center;
            box-shadow: 0 0 80px rgba(0,0,0,0.8);
        }
        .glow-text {
            font-size: 3.8rem;
            font-weight: 900;
            color: #ffffff;
            text-shadow: 
                0 0 10px rgba(255,255,255,0.3),
                0 0 20px rgba(255,255,255,0.1);
            letter-spacing: 4px;
            margin-bottom: 10px;
        }
        .sub-text {
            color: #888888;
            font-size: 1.1rem;
            font-weight: 700;
            letter-spacing: 6px;
            text-transform: uppercase;
            border-top: 2px solid #1a1a1a;
            border-bottom: 2px solid #1a1a1a;
            padding: 15px 0;
            margin-bottom: 30px;
        }
        .desc {
            color: #666666;
            font-size: 1rem;
            font-weight: 600;
            line-height: 1.8;
            margin-bottom: 35px;
        }
        .btn {
            display: inline-block;
            padding: 18px 60px;
            background: #1a1a1a;
            color: #ffffff;
            border: 2px solid #333333;
            border-radius: 50px;
            text-decoration: none;
            font-size: 1rem;
            font-weight: 900;
            letter-spacing: 3px;
            text-transform: uppercase;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        .btn:hover {
            background: #ffffff;
            color: #000000;
            border-color: #ffffff;
            box-shadow: 0 0 40px rgba(255,255,255,0.1);
        }
        .footer {
            position: fixed;
            bottom: 20px;
            color: #222222;
            font-size: 0.7rem;
            font-weight: 700;
            letter-spacing: 2px;
        }
        /* Audio player hidden */
        #bg-audio { display: none; }
    </style>
</head>
<body>
    <!-- HIDDEN AUDIO - AUTOPLAYS -->
    <audio id="bg-audio" autoplay loop>
        <source src="/download/neww.mp3" type="audio/mpeg">
    </audio>

    <div class="container">
        <div class="glow-text">WELCOME TO</div>
        <div class="glow-text" style="color:#ffffff; text-shadow:0 0 30px rgba(255,255,255,0.15);">SAMARTH</div>
        <div class="sub-text">Website</div>
        <p class="desc">
            Advanced Intelligence Platform<br>
            Secure &bull; Private &bull; Authorized Access
        </p>
        <a href="/boot" class="btn">Enter System</a>
    </div>
    <div class="footer">● SAMARTH INTELLIGENCE v2026</div>

    <script>
        // Force audio play on user interaction (browser policy)
        document.addEventListener('click', function() {
            var audio = document.getElementById('bg-audio');
            if (audio.paused) {
                audio.play().catch(function(e) {});
            }
        });
        // Try autoplay on load
        window.addEventListener('load', function() {
            var audio = document.getElementById('bg-audio');
            audio.play().catch(function(e) {});
        });
    </script>
</body>
</html>
'''


# ============================================================
# PAGE 2: BOOT SEQUENCE (DARK BOLD)
# ============================================================

BOOT_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Initializing</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #000000;
            font-family: 'Courier New', monospace;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .box {
            max-width: 650px;
            width: 100%;
            padding: 45px 40px;
            background: #0a0a0a;
            border: 2px solid #1a1a1a;
            border-radius: 16px;
        }
        .log {
            color: #555555;
            font-size: 0.9rem;
            padding: 5px 0;
            font-weight: 700;
        }
        .log.success { color: #00ff88; }
        .log.active { color: #ffffff; }
        .spinner {
            width: 40px;
            height: 40px;
            margin: 30px auto;
            border: 3px solid #1a1a1a;
            border-top: 3px solid #ffffff;
            border-radius: 50%;
            animation: spin 0.7s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        #status {
            color: #333333;
            font-size: 0.75rem;
            text-align: center;
            letter-spacing: 3px;
            font-weight: 700;
        }
    </style>
</head>
<body>
    <div class="box" id="bootlog">
        <div class="log">> Initializing Samarth core...</div>
        <div class="log">> Establishing secure tunnel...</div>
        <div class="log">> Authenticating session...</div>
        <div class="spinner"></div>
        <div id="status">CONNECTING TO NODES</div>
    </div>
    <script>
        const logDiv = document.getElementById('bootlog');
        const statusDiv = document.getElementById('status');
        const msgs = [
            { text: "> Loading modules...", cls: "log" },
            { text: "> Encryption handshake complete.", cls: "log" },
            { text: "> Database synchronization...", cls: "log" },
            { text: "> Connection established.", cls: "log success" },
            { text: "> System ready.", cls: "log success" }
        ];
        let idx = 0;
        function nextLog() {
            if (idx < msgs.length) {
                const d = document.createElement('div');
                d.className = msgs[idx].cls;
                d.textContent = msgs[idx].text;
                logDiv.insertBefore(d, statusDiv);
                idx++;
                setTimeout(nextLog, 550);
            } else {
                statusDiv.textContent = "● ONLINE — Redirecting";
                statusDiv.style.color = "#00ff88";
                setTimeout(() => { window.location.href = '/main'; }, 1200);
            }
        }
        setTimeout(nextLog, 400);
    </script>
</body>
</html>
'''


# ============================================================
# PAGE 3: SAMARTH NUMBER TO ADDRESS WEBSITE (DARK BOLD)
# ============================================================

MAIN_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Samarth Number to Address</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #000000;
            font-family: 'Arial Black', 'Impact', sans-serif;
            min-height: 100vh;
            padding: 30px 20px;
        }
        .wrap { max-width: 900px; margin: 0 auto; }
        .header {
            text-align: center;
            padding-bottom: 25px;
            border-bottom: 3px solid #1a1a1a;
            margin-bottom: 30px;
        }
        .header h1 {
            color: #ffffff;
            font-size: 2.4rem;
            font-weight: 900;
            letter-spacing: 4px;
            text-shadow: 0 0 30px rgba(255,255,255,0.05);
        }
        .header h1 span {
            color: #888888;
        }
        .header .sub {
            color: #444444;
            font-size: 0.8rem;
            font-weight: 700;
            letter-spacing: 4px;
            text-transform: uppercase;
            margin-top: 8px;
        }
        .card {
            background: #0a0a0a;
            border: 2px solid #1a1a1a;
            border-radius: 16px;
            padding: 35px 40px;
        }
        .card-label {
            color: #444444;
            font-size: 0.7rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 4px;
            margin-bottom: 18px;
        }
        .input-row {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }
        .input-row input {
            flex: 1;
            min-width: 200px;
            padding: 15px 18px;
            background: #111111;
            border: 2px solid #1a1a1a;
            border-radius: 10px;
            color: #ffffff;
            font-size: 1rem;
            font-weight: 700;
            transition: 0.3s;
            font-family: 'Arial Black', sans-serif;
        }
        .input-row input:focus {
            outline: none;
            border-color: #333333;
            background: #0d0d0d;
        }
        .input-row input::placeholder {
            color: #333333;
            font-weight: 700;
        }
        .btn {
            padding: 15px 35px;
            background: #1a1a1a;
            border: 2px solid #333333;
            border-radius: 10px;
            color: #ffffff;
            font-size: 0.8rem;
            font-weight: 900;
            letter-spacing: 3px;
            text-transform: uppercase;
            cursor: pointer;
            transition: 0.3s;
            font-family: 'Arial Black', sans-serif;
        }
        .btn:hover {
            background: #ffffff;
            color: #000000;
            border-color: #ffffff;
        }
        #result {
            margin-top: 30px;
            background: #080808;
            border-radius: 12px;
            padding: 25px;
            min-height: 120px;
            border: 2px solid #121212;
            color: #888888;
            font-size: 0.95rem;
            line-height: 2;
            font-weight: 700;
            white-space: pre-wrap;
            word-break: break-word;
            font-family: 'Courier New', monospace;
        }
        #result .key { color: #ffffff; }
        #result .val { color: #aaaaaa; }
        #result .err { color: #ff3333; }
        #result .ok { color: #00ff88; }
        .footer {
            text-align: center;
            margin-top: 35px;
            color: #1a1a1a;
            font-size: 0.65rem;
            font-weight: 700;
            letter-spacing: 3px;
        }
        /* Hidden audio */
        #bg-audio { display: none; }
        @media (max-width:600px) {
            body { padding: 15px 10px; }
            .card { padding: 20px; }
            .header h1 { font-size: 1.6rem; }
            .input-row input { min-width: 100%; }
            .btn { width: 100%; text-align: center; }
        }
    </style>
</head>
<body>
    <!-- HIDDEN AUDIO - AUTOPLAYS -->
    <audio id="bg-audio" autoplay loop>
        <source src="/download/neww.mp3" type="audio/mpeg">
    </audio>

    <div class="wrap">
        <div class="header">
            <h1>WELCOME TO <span>SAMARTH</span></h1>
            <div class="sub">Number to Address Website</div>
        </div>
        <div class="card">
            <div class="card-label">Enter Target Number</div>
            <form id="lookupForm">
                <div class="input-row">
                    <input type="text" id="phone" placeholder="+91XXXXXXXXXX" required>
                    <button type="submit" class="btn">Trace</button>
                </div>
            </form>
            <div id="result">Awaiting input...</div>
        </div>
        <div class="footer">● SAMARTH INTELLIGENCE v2026 ●</div>
    </div>

    <script>
        // Force audio play on user interaction
        document.addEventListener('click', function() {
            var audio = document.getElementById('bg-audio');
            if (audio.paused) {
                audio.play().catch(function(e) {});
            }
        });
        window.addEventListener('load', function() {
            var audio = document.getElementById('bg-audio');
            audio.play().catch(function(e) {});
        });

        // Lookup form handler
        document.getElementById('lookupForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const phone = document.getElementById('phone').value;
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = '<span style="color:#444444;">Processing request...</span>';
            try {
                const res = await fetch('/lookup', {
                    method:'POST',
                    headers:{'Content-Type':'application/x-www-form-urlencoded'},
                    body:'phone='+encodeURIComponent(phone)
                });
                const data = await res.json();
                if (data.error) {
                    resultDiv.innerHTML = `<span class="err">⚠ ${data.error}</span>`;
                } else {
                    let html = `<span class="ok">✓ Report Generated</span><br><br>`;
                    for (let [key, val] of Object.entries(data)) {
                        if (val && val !== 'N/A') {
                            html += `<span class="key">${key}:</span> <span class="val">${val}</span><br>`;
                        }
                    }
                    resultDiv.innerHTML = html;
                }
            } catch(err) {
                resultDiv.innerHTML = '<span class="err">⚠ Connection error. Retry.</span>';
            }
        });
    </script>
</body>
</html>
'''


# ============================================================
# FLASK ROUTES
# ============================================================

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


# ============================================================
# MAIN ENTRY POINT
# ============================================================

if __name__ == '__main__':
    print("""
    ╔════════════════════════════════════════════╗
    ║  SAMARTH INTELLIGENCE SYSTEM — ONLINE      ║
    ║  http://127.0.0.1:5000                     ║
    ╚════════════════════════════════════════════╝
    """)
    app.run(debug=True, host='0.0.0.0', port=5000)
