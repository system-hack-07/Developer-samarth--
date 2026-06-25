from flask import Flask, request, jsonify, send_from_directory, send_file
import requests
from bs4 import BeautifulSoup
import os
import time
import json
from datetime import datetime
import base64
from io import BytesIO

# ============================================================
# SELENIUM FOR SCREENSHOTS
# ============================================================

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

# Create screenshot folder
SCREENSHOT_FOLDER = 'screenshots'
if not os.path.exists(SCREENSHOT_FOLDER):
    os.makedirs(SCREENSHOT_FOLDER)

# ============================================================
# SCREENSHOT FUNCTION
# ============================================================

def take_screenshot(phone_number, data):
    """Take screenshot of lookup results"""
    try:
        # Setup headless Chrome
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=800,600")
        
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        # Create HTML page with results
        html_content = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ 
                    background: #0a0e17; 
                    color: #e8f0fe; 
                    font-family: 'Segoe UI', Arial, sans-serif;
                    padding: 30px;
                    max-width: 800px;
                    margin: 0 auto;
                }}
                h1 {{ 
                    color: #00c8ff;
                    font-size: 24px;
                    border-bottom: 2px solid #00c8ff;
                    padding-bottom: 10px;
                }}
                .result {{
                    background: rgba(255,255,255,0.05);
                    padding: 20px;
                    border-radius: 8px;
                    margin-top: 20px;
                }}
                .row {{
                    display: flex;
                    padding: 8px 0;
                    border-bottom: 1px solid rgba(255,255,255,0.05);
                }}
                .key {{
                    color: #00c8ff;
                    font-weight: bold;
                    width: 180px;
                    flex-shrink: 0;
                }}
                .value {{
                    color: #e8f0fe;
                }}
                .footer {{
                    margin-top: 30px;
                    color: rgba(255,255,255,0.2);
                    font-size: 12px;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <h1>📱 SAMARTH INTELLIGENCE REPORT</h1>
            <div class="result">
                <div class="row"><span class="key">Phone Number:</span><span class="value">{phone_number}</span></div>
                <div class="row"><span class="key">Timestamp:</span><span class="value">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span></div>
        '''
        
        for key, val in data.items():
            if val and val != 'N/A' and key != 'Number':
                html_content += f'<div class="row"><span class="key">{key}:</span><span class="value">{val}</span></div>'
        
        html_content += '''
            </div>
            <div class="footer">● SAMARTH INTELLIGENCE v2026 ●</div>
        </body>
        </html>
        '''
        
        # Save HTML to temp file
        temp_html = os.path.join(SCREENSHOT_FOLDER, f'temp_{phone_number}.html')
        with open(temp_html, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Load HTML in headless browser
        driver.get(f'file://{os.path.abspath(temp_html)}')
        time.sleep(1)  # Wait for render
        
        # Take screenshot
        screenshot_path = os.path.join(SCREENSHOT_FOLDER, f'screenshot_{phone_number}_{int(time.time())}.png')
        driver.save_screenshot(screenshot_path)
        
        driver.quit()
        os.remove(temp_html)  # Cleanup temp HTML
        
        return screenshot_path
        
    except Exception as e:
        print(f"Screenshot error: {str(e)}")
        return None


# ============================================================
# YOUR ORIGINAL LOOKUP FUNCTION
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
# ROUTE TO SERVE MP3 FILE
# ============================================================

@app.route('/download/<path:filename>')
def serve_audio(filename):
    return send_from_directory('download', filename)


# ============================================================
# ROUTE TO SERVE SCREENSHOTS
# ============================================================

@app.route('/screenshots/<path:filename>')
def serve_screenshot(filename):
    return send_from_directory(SCREENSHOT_FOLDER, filename)


# ============================================================
# PAGE 1: WELCOME TO SAMARTH WEBSITE
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
        
        body.dark {
            background: #000000;
            color: #ffffff;
        }
        body.dark .container {
            background: #0a0a0a;
            border: 3px solid #1a1a1a;
        }
        body.dark .glow-text { color: #ffffff; }
        body.dark .sub-text { color: #888888; border-color: #1a1a1a; }
        body.dark .desc { color: #666666; }
        body.dark .btn {
            background: #1a1a1a;
            color: #ffffff;
            border: 2px solid #333333;
        }
        body.dark .btn:hover {
            background: #ffffff;
            color: #000000;
        }
        body.dark .footer { color: #222222; }
        body.dark .toggle-btn {
            background: #1a1a1a;
            color: #ffffff;
            border: 2px solid #333333;
        }
        
        body.light {
            background: #f5f5f5;
            color: #000000;
        }
        body.light .container {
            background: #ffffff;
            border: 3px solid #dddddd;
            box-shadow: 0 0 40px rgba(0,0,0,0.05);
        }
        body.light .glow-text { color: #000000; text-shadow: none; }
        body.light .sub-text { color: #555555; border-color: #dddddd; }
        body.light .desc { color: #777777; }
        body.light .btn {
            background: #eeeeee;
            color: #000000;
            border: 2px solid #cccccc;
        }
        body.light .btn:hover {
            background: #000000;
            color: #ffffff;
            border-color: #000000;
        }
        body.light .footer { color: #cccccc; }
        body.light .toggle-btn {
            background: #eeeeee;
            color: #000000;
            border: 2px solid #cccccc;
        }
        body.light .toggle-btn:hover {
            background: #000000;
            color: #ffffff;
        }
        
        body {
            font-family: 'Arial Black', 'Impact', sans-serif;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 20px;
            transition: all 0.3s ease;
        }
        .container {
            max-width: 650px;
            width: 100%;
            padding: 50px 45px;
            border-radius: 20px;
            text-align: center;
            transition: all 0.3s ease;
            position: relative;
        }
        .glow-text {
            font-size: 2.2rem;
            font-weight: 900;
            letter-spacing: 3px;
            margin-bottom: 5px;
            transition: all 0.3s ease;
        }
        .glow-text.name {
            font-size: 2.6rem;
            letter-spacing: 5px;
        }
        .sub-text {
            font-size: 0.9rem;
            font-weight: 700;
            letter-spacing: 5px;
            text-transform: uppercase;
            padding: 12px 0;
            margin-bottom: 25px;
            transition: all 0.3s ease;
        }
        .desc {
            font-size: 0.9rem;
            font-weight: 600;
            line-height: 1.8;
            margin-bottom: 30px;
            transition: all 0.3s ease;
        }
        .btn {
            display: inline-block;
            padding: 15px 50px;
            border-radius: 50px;
            text-decoration: none;
            font-size: 0.9rem;
            font-weight: 900;
            letter-spacing: 3px;
            text-transform: uppercase;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        .footer {
            position: fixed;
            bottom: 20px;
            font-size: 0.6rem;
            font-weight: 700;
            letter-spacing: 2px;
            transition: all 0.3s ease;
        }
        #bg-audio { display: none; }
        
        .toggle-wrap {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 100;
        }
        .toggle-btn {
            padding: 10px 18px;
            border-radius: 30px;
            font-size: 0.7rem;
            font-weight: 900;
            letter-spacing: 2px;
            text-transform: uppercase;
            cursor: pointer;
            transition: all 0.3s ease;
            font-family: 'Arial Black', sans-serif;
        }
        
        @media (max-width:600px) {
            .container { padding: 30px 20px; }
            .glow-text { font-size: 1.6rem; }
            .glow-text.name { font-size: 2rem; }
            .btn { width: 100%; text-align: center; padding: 14px; }
            .toggle-wrap { top: 10px; right: 10px; }
            .toggle-btn { padding: 6px 12px; font-size: 0.6rem; }
        }
    </style>
</head>
<body class="dark">
    <audio id="bg-audio" autoplay loop>
        <source src="/download/neww.mp3" type="audio/mpeg">
    </audio>

    <div class="toggle-wrap">
        <button class="toggle-btn" onclick="toggleMode()">🌓 Toggle</button>
    </div>

    <div class="container">
        <div class="glow-text">WELCOME TO</div>
        <div class="glow-text name">SAMARTH</div>
        <div class="sub-text">Website</div>
        <p class="desc">
            Advanced Intelligence Platform<br>
            Secure &bull; Private &bull; Authorized Access
        </p>
        <a href="/boot" class="btn">Enter System</a>
    </div>
    <div class="footer">● SAMARTH INTELLIGENCE v2026 ●</div>

    <script>
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

        function toggleMode() {
            const body = document.body;
            if (body.classList.contains('dark')) {
                body.classList.remove('dark');
                body.classList.add('light');
                localStorage.setItem('theme', 'light');
            } else {
                body.classList.remove('light');
                body.classList.add('dark');
                localStorage.setItem('theme', 'dark');
            }
        }
        window.addEventListener('load', function() {
            const saved = localStorage.getItem('theme');
            if (saved === 'light') {
                document.body.classList.remove('dark');
                document.body.classList.add('light');
            }
        });
    </script>
</body>
</html>
'''


# ============================================================
# PAGE 2: BOOT SEQUENCE
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
        
        body.dark {
            background: #000000;
            color: #ffffff;
        }
        body.dark .box {
            background: #0a0a0a;
            border: 2px solid #1a1a1a;
        }
        body.dark .log { color: #555555; }
        body.dark .log.success { color: #00ff88; }
        body.dark .log.active { color: #ffffff; }
        body.dark .spinner { border: 3px solid #1a1a1a; border-top: 3px solid #ffffff; }
        body.dark #status { color: #333333; }
        body.dark .toggle-btn {
            background: #1a1a1a;
            color: #ffffff;
            border: 2px solid #333333;
        }
        
        body.light {
            background: #f5f5f5;
            color: #000000;
        }
        body.light .box {
            background: #ffffff;
            border: 2px solid #dddddd;
        }
        body.light .log { color: #888888; }
        body.light .log.success { color: #00aa55; }
        body.light .log.active { color: #000000; }
        body.light .spinner { border: 3px solid #dddddd; border-top: 3px solid #000000; }
        body.light #status { color: #aaaaaa; }
        body.light .toggle-btn {
            background: #eeeeee;
            color: #000000;
            border: 2px solid #cccccc;
        }
        body.light .toggle-btn:hover {
            background: #000000;
            color: #ffffff;
        }
        
        body {
            font-family: 'Courier New', monospace;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
            transition: all 0.3s ease;
        }
        .box {
            max-width: 650px;
            width: 100%;
            padding: 45px 40px;
            border-radius: 16px;
            transition: all 0.3s ease;
        }
        .log {
            font-size: 0.9rem;
            padding: 5px 0;
            font-weight: 700;
            transition: all 0.3s ease;
        }
        .spinner {
            width: 40px;
            height: 40px;
            margin: 30px auto;
            border-radius: 50%;
            animation: spin 0.7s linear infinite;
            transition: all 0.3s ease;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        #status {
            font-size: 0.75rem;
            text-align: center;
            letter-spacing: 3px;
            font-weight: 700;
            transition: all 0.3s ease;
        }
        .toggle-wrap {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 100;
        }
        .toggle-btn {
            padding: 10px 18px;
            border-radius: 30px;
            font-size: 0.7rem;
            font-weight: 900;
            letter-spacing: 2px;
            text-transform: uppercase;
            cursor: pointer;
            transition: all 0.3s ease;
            font-family: 'Arial Black', sans-serif;
        }
        @media (max-width:600px) {
            .box { padding: 30px 20px; }
            .toggle-wrap { top: 10px; right: 10px; }
            .toggle-btn { padding: 6px 12px; font-size: 0.6rem; }
        }
    </style>
</head>
<body class="dark">
    <div class="toggle-wrap">
        <button class="toggle-btn" onclick="toggleMode()">🌓 Toggle</button>
    </div>
    
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
        
        function toggleMode() {
            const body = document.body;
            if (body.classList.contains('dark')) {
                body.classList.remove('dark');
                body.classList.add('light');
                localStorage.setItem('theme', 'light');
            } else {
                body.classList.remove('light');
                body.classList.add('dark');
                localStorage.setItem('theme', 'dark');
            }
        }
        window.addEventListener('load', function() {
            const saved = localStorage.getItem('theme');
            if (saved === 'light') {
                document.body.classList.remove('dark');
                document.body.classList.add('light');
            }
        });
    </script>
</body>
</html>
'''


# ============================================================
# PAGE 3: SAMARTH NUMBER TO ADDRESS (WITH SCREENSHOT BUTTON)
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
        
        body.dark {
            background: #000000;
            color: #ffffff;
        }
        body.dark .header { border-bottom: 3px solid #1a1a1a; }
        body.dark .header h1 { color: #ffffff; }
        body.dark .header h1 span { color: #888888; }
        body.dark .header .sub { color: #444444; }
        body.dark .card {
            background: #0a0a0a;
            border: 2px solid #1a1a1a;
        }
        body.dark .card-label { color: #444444; }
        body.dark .input-row input {
            background: #111111;
            border: 2px solid #1a1a1a;
            color: #ffffff;
        }
        body.dark .input-row input:focus { border-color: #333333; background: #0d0d0d; }
        body.dark .input-row input::placeholder { color: #333333; }
        body.dark .btn {
            background: #1a1a1a;
            border: 2px solid #333333;
            color: #ffffff;
        }
        body.dark .btn:hover {
            background: #ffffff;
            color: #000000;
            border-color: #ffffff;
        }
        body.dark #result {
            background: #080808;
            border: 2px solid #121212;
            color: #888888;
        }
        body.dark #result .key { color: #ffffff; }
        body.dark #result .val { color: #aaaaaa; }
        body.dark #result .err { color: #ff3333; }
        body.dark #result .ok { color: #00ff88; }
        body.dark .footer { color: #1a1a1a; }
        body.dark .toggle-btn {
            background: #1a1a1a;
            color: #ffffff;
            border: 2px solid #333333;
        }
        body.dark .screenshot-btn {
            background: #1a1a1a;
            color: #00ff88;
            border: 2px solid #00ff88;
        }
        body.dark .screenshot-btn:hover {
            background: #00ff88;
            color: #000000;
        }
        
        body.light {
            background: #f5f5f5;
            color: #000000;
        }
        body.light .header { border-bottom: 3px solid #dddddd; }
        body.light .header h1 { color: #000000; }
        body.light .header h1 span { color: #555555; }
        body.light .header .sub { color: #888888; }
        body.light .card {
            background: #ffffff;
            border: 2px solid #dddddd;
        }
        body.light .card-label { color: #888888; }
        body.light .input-row input {
            background: #f9f9f9;
            border: 2px solid #dddddd;
            color: #000000;
        }
        body.light .input-row input:focus { border-color: #aaaaaa; background: #f5f5f5; }
        body.light .input-row input::placeholder { color: #bbbbbb; }
        body.light .btn {
            background: #eeeeee;
            border: 2px solid #cccccc;
            color: #000000;
        }
        body.light .btn:hover {
            background: #000000;
            color: #ffffff;
            border-color: #000000;
        }
        body.light #result {
            background: #f9f9f9;
            border: 2px solid #e0e0e0;
            color: #888888;
        }
        body.light #result .key { color: #000000; }
        body.light #result .val { color: #555555; }
        body.light #result .err { color: #cc0000; }
        body.light #result .ok { color: #008844; }
        body.light .footer { color: #cccccc; }
        body.light .toggle-btn {
            background: #eeeeee;
            color: #000000;
            border: 2px solid #cccccc;
        }
        body.light .toggle-btn:hover {
            background: #000000;
            color: #ffffff;
        }
        body.light .screenshot-btn {
            background: #eeeeee;
            color: #008844;
            border: 2px solid #008844;
        }
        body.light .screenshot-btn:hover {
            background: #008844;
            color: #ffffff;
        }
        
        body {
            font-family: 'Arial Black', 'Impact', sans-serif;
            min-height: 100vh;
            padding: 30px 20px;
            transition: all 0.3s ease;
        }
        .wrap { max-width: 850px; margin: 0 auto; }
        .header {
            text-align: center;
            padding-bottom: 20px;
            margin-bottom: 30px;
            transition: all 0.3s ease;
        }
        .header h1 {
            font-size: 2rem;
            font-weight: 900;
            letter-spacing: 3px;
            transition: all 0.3s ease;
        }
        .header h1 span {
            transition: all 0.3s ease;
        }
        .header .sub {
            font-size: 0.8rem;
            font-weight: 700;
            letter-spacing: 4px;
            text-transform: uppercase;
            margin-top: 6px;
            transition: all 0.3s ease;
        }
        .card {
            border-radius: 16px;
            padding: 30px 35px;
            transition: all 0.3s ease;
        }
        .card-label {
            font-size: 0.7rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 4px;
            margin-bottom: 18px;
            transition: all 0.3s ease;
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
            border-radius: 10px;
            font-size: 1rem;
            font-weight: 700;
            transition: all 0.3s ease;
            font-family: 'Arial Black', sans-serif;
        }
        .input-row input:focus { outline: none; }
        .btn {
            padding: 15px 35px;
            border-radius: 10px;
            font-size: 0.8rem;
            font-weight: 900;
            letter-spacing: 3px;
            text-transform: uppercase;
            cursor: pointer;
            transition: all 0.3s ease;
            font-family: 'Arial Black', sans-serif;
        }
        .btn-group {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-top: 10px;
        }
        .screenshot-btn {
            padding: 12px 25px;
            border-radius: 10px;
            font-size: 0.7rem;
            font-weight: 900;
            letter-spacing: 2px;
            text-transform: uppercase;
            cursor: pointer;
            transition: all 0.3s ease;
            font-family: 'Arial Black', sans-serif;
            background: transparent;
        }
        #result {
            margin-top: 30px;
            border-radius: 12px;
            padding: 25px;
            min-height: 100px;
            font-size: 0.9rem;
            line-height: 2;
            font-weight: 700;
            white-space: pre-wrap;
            word-break: break-word;
            font-family: 'Courier New', monospace;
            transition: all 0.3s ease;
        }
        .footer {
            text-align: center;
            margin-top: 35px;
            font-size: 0.65rem;
            font-weight: 700;
            letter-spacing: 3px;
            transition: all 0.3s ease;
        }
        #bg-audio { display: none; }
        
        .toggle-wrap {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 100;
        }
        .toggle-btn {
            padding: 10px 18px;
            border-radius: 30px;
            font-size: 0.7rem;
            font-weight: 900;
            letter-spacing: 2px;
            text-transform: uppercase;
            cursor: pointer;
            transition: all 0.3s ease;
            font-family: 'Arial Black', sans-serif;
        }
        
        .screenshot-preview {
            margin-top: 20px;
            max-width: 100%;
            border-radius: 8px;
            border: 2px solid #1a1a1a;
        }
        
        @media (max-width:600px) {
            body { padding: 15px 10px; }
            .card { padding: 20px; }
            .header h1 { font-size: 1.4rem; }
            .input-row input { min-width: 100%; }
            .btn { width: 100%; text-align: center; }
            .toggle-wrap { top: 10px; right: 10px; }
            .toggle-btn { padding: 6px 12px; font-size: 0.6rem; }
            .btn-group { flex-direction: column; }
            .screenshot-btn { width: 100%; text-align: center; }
        }
    </style>
</head>
<body class="dark">
    <audio id="bg-audio" autoplay loop>
        <source src="/download/neww.mp3" type="audio/mpeg">
    </audio>

    <div class="toggle-wrap">
        <button class="toggle-btn" onclick="toggleMode()">🌓 Toggle</button>
    </div>

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
            <div id="screenshotArea"></div>
        </div>
        <div class="footer">● SAMARTH INTELLIGENCE v2026 ●</div>
    </div>

    <script>
        let lastData = null;
        let lastPhone = null;

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

        function toggleMode() {
            const body = document.body;
            if (body.classList.contains('dark')) {
                body.classList.remove('dark');
                body.classList.add('light');
                localStorage.setItem('theme', 'light');
            } else {
                body.classList.remove('light');
                body.classList.add('dark');
                localStorage.setItem('theme', 'dark');
            }
        }
        window.addEventListener('load', function() {
            const saved = localStorage.getItem('theme');
            if (saved === 'light') {
                document.body.classList.remove('dark');
                document.body.classList.add('light');
            }
        });

        // Take Screenshot
        async function takeScreenshot() {
            if (!lastPhone || !lastData) {
                alert('Please trace a number first!');
                return;
            }
            
            const area = document.getElementById('screenshotArea');
            area.innerHTML = '<span style="color:#444444;">📸 Capturing screenshot... Please wait.</span>';
            
            try {
                const res = await fetch('/screenshot', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ phone: lastPhone, data: lastData })
                });
                const result = await res.json();
                
                if (result.success) {
                    area.innerHTML = `
                        <div style="margin-top:15px; padding:15px; background:rgba(0,255,136,0.05); border:1px solid #00ff88; border-radius:8px;">
                            <span style="color:#00ff88;">✅ Screenshot captured!</span>
                            <br><br>
                            <a href="${result.url}" download target="_blank" style="color:#00c8ff; text-decoration:underline;">📥 Download Screenshot</a>
                            <br><br>
                            <img src="${result.url}" class="screenshot-preview" style="max-width:100%; max-height:400px; border:2px solid #1a1a1a; border-radius:8px;">
                        </div>
                    `;
                } else {
                    area.innerHTML = `<span style="color:#ff3333;">❌ Screenshot failed: ${result.message}</span>`;
                }
            } catch(err) {
                area.innerHTML = `<span style="color:#ff3333;">❌ Error: ${err.message}</span>`;
            }
        }

        // Lookup form handler
        document.getElementById('lookupForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const phone = document.getElementById('phone').value;
            const resultDiv = document.getElementById('result');
            const screenshotArea = document.getElementById('screenshotArea');
            screenshotArea.innerHTML = '';
            
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
                    
                    // Store for screenshot
                    lastPhone = phone;
                    lastData = data;
                    
                    // Show screenshot button
                    resultDiv.innerHTML += `<br><button class="screenshot-btn" onclick="takeScreenshot()">📸 Take Screenshot</button>`;
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
# SCREENSHOT API ROUTE
# ============================================================

@app.route('/screenshot', methods=['POST'])
def screenshot_api():
    try:
        data = request.get_json()
        phone = data.get('phone')
        result_data = data.get('data')
        
        if not phone or not result_data:
            return jsonify({"success": False, "message": "Missing data"}), 400
        
        # Take screenshot
        screenshot_path = take_screenshot(phone, result_data)
        
        if screenshot_path and os.path.exists(screenshot_path):
            filename = os.path.basename(screenshot_path)
            url = f"/screenshots/{filename}"
            return jsonify({
                "success": True,
                "url": url,
                "filename": filename,
                "message": "Screenshot captured successfully"
            })
        else:
            return jsonify({"success": False, "message": "Screenshot capture failed"}), 500
            
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


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
    ╔═══════════════════════════════════════════════════════════╗
    ║  SAMARTH INTELLIGENCE SYSTEM — ONLINE                     ║
    ║  http://127.0.0.1:5000                                   ║
    ║                                                          ║
    ║  📸 Screenshot Feature: Captures results as PNG          ║
    ║  📁 Saved in: /screenshots/                             ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    app.run(debug=True, host='0.0.0.0', port=5000)
