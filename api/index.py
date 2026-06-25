from flask import Flask, request, jsonify, send_from_directory
import requests
from bs4 import BeautifulSoup
import os
import sqlite3
from datetime import datetime
import json
import base64
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import threading
import time

app = Flask(__name__)

# ============================================================
# DATABASE SETUP (Option 1)
# ============================================================

def init_db():
    """Initialize SQLite database for history"""
    conn = sqlite3.connect('lookups.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone TEXT NOT NULL,
        result TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        ip_address TEXT,
        screenshot TEXT
    )''')
    conn.commit()
    conn.close()
    print("✅ Database initialized: lookups.db")

def save_lookup(phone, result, ip_address=None, screenshot=None):
    """Save lookup result to database"""
    try:
        conn = sqlite3.connect('lookups.db')
        c = conn.cursor()
        c.execute('''INSERT INTO history 
                     (phone, result, timestamp, ip_address, screenshot) 
                     VALUES (?, ?, ?, ?, ?)''',
                  (phone, json.dumps(result), datetime.now().isoformat(), ip_address, screenshot))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def get_history(limit=50):
    """Get recent lookup history"""
    try:
        conn = sqlite3.connect('lookups.db')
        c = conn.cursor()
        c.execute('''SELECT id, phone, timestamp, result 
                     FROM history 
                     ORDER BY id DESC 
                     LIMIT ?''', (limit,))
        rows = c.fetchall()
        conn.close()
        
        history = []
        for row in rows:
            history.append({
                'id': row[0],
                'phone': row[1],
                'timestamp': row[2],
                'result': json.loads(row[3]) if row[3] else {}
            })
        return history
    except Exception as e:
        print(f"❌ History error: {e}")
        return []

def get_history_by_phone(phone):
    """Get history for a specific phone number"""
    try:
        conn = sqlite3.connect('lookups.db')
        c = conn.cursor()
        c.execute('''SELECT id, phone, timestamp, result, screenshot 
                     FROM history 
                     WHERE phone = ? 
                     ORDER BY id DESC''', (phone,))
        rows = c.fetchall()
        conn.close()
        
        history = []
        for row in rows:
            history.append({
                'id': row[0],
                'phone': row[1],
                'timestamp': row[2],
                'result': json.loads(row[3]) if row[3] else {},
                'screenshot': row[4] if row[4] else None
            })
        return history
    except Exception as e:
        print(f"❌ History error: {e}")
        return []

# ============================================================
# SCREENSHOT CAPTURE (Option 15)
# ============================================================

def capture_screenshot(url, phone_number):
    """Capture screenshot of lookup result page using Selenium"""
    try:
        # Chrome options for headless mode
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1200,800')
        chrome_options.add_argument('--disable-gpu')
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        
        # Wait for page to load
        time.sleep(2)
        
        # Take screenshot
        screenshot = driver.get_screenshot_as_base64()
        driver.quit()
        
        return screenshot
    except Exception as e:
        print(f"❌ Screenshot error: {e}")
        return None

def capture_screenshot_async(url, phone_number):
    """Capture screenshot in background thread"""
    def capture():
        screenshot = capture_screenshot(url, phone_number)
        if screenshot:
            # Save to database
            conn = sqlite3.connect('lookups.db')
            c = conn.cursor()
            c.execute('''UPDATE history 
                         SET screenshot = ? 
                         WHERE phone = ? AND screenshot IS NULL
                         ORDER BY id DESC LIMIT 1''', (screenshot, phone_number))
            conn.commit()
            conn.close()
            print(f"✅ Screenshot saved for {phone_number}")
    
    thread = threading.Thread(target=capture)
    thread.daemon = True
    thread.start()
    return thread

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
# ROUTE TO SERVE MP3 FILE FROM DOWNLOAD FOLDER
# ============================================================

@app.route('/download/<path:filename>')
def serve_audio(filename):
    return send_from_directory('download', filename)


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
# PAGE 3: MAIN DASHBOARD WITH HISTORY
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
        body.dark .history-table {
            border-color: #1a1a1a;
        }
        body.dark .history-table th {
            background: #0a0a0a;
            color: #888888;
            border-color: #1a1a1a;
        }
        body.dark .history-table td {
            border-color: #1a1a1a;
            color: #aaaaaa;
        }
        body.dark .history-table tr:hover {
            background: #0a0a0a;
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
        body.light .history-table {
            border-color: #dddddd;
        }
        body.light .history-table th {
            background: #f5f5f5;
            color: #555555;
            border-color: #dddddd;
        }
        body.light .history-table td {
            border-color: #dddddd;
            color: #555555;
        }
        body.light .history-table tr:hover {
            background: #f5f5f5;
        }
        
        body {
            font-family: 'Arial Black', 'Impact', sans-serif;
            min-height: 100vh;
            padding: 30px 20px;
            transition: all 0.3s ease;
        }
        .wrap { max-width: 950px; margin: 0 auto; }
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
            margin-bottom: 25px;
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
        
        /* History Table */
        .history-section {
            margin-top: 30px;
        }
        .history-section h2 {
            font-size: 1.2rem;
            font-weight: 700;
            letter-spacing: 2px;
            margin-bottom: 15px;
            color: #888888;
        }
        .history-table {
            width: 100%;
            border-collapse: collapse;
            border: 2px solid;
            font-family: 'Courier New', monospace;
            font-weight: 700;
            font-size: 0.8rem;
            transition: all 0.3s ease;
        }
        .history-table th {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 2px solid;
            letter-spacing: 1px;
            font-weight: 900;
            text-transform: uppercase;
            font-size: 0.65rem;
            transition: all 0.3s ease;
        }
        .history-table td {
            padding: 10px 15px;
            border-bottom: 1px solid;
            transition: all 0.3s ease;
        }
        .history-table tr:hover {
            transition: all 0.3s ease;
        }
        .history-table .view-btn {
            padding: 4px 12px;
            border-radius: 5px;
            font-size: 0.6rem;
            font-weight: 900;
            cursor: pointer;
            font-family: 'Arial Black', sans-serif;
            background: #1a1a1a;
            color: #ffffff;
            border: 1px solid #333333;
        }
        .history-table .view-btn:hover {
            background: #ffffff;
            color: #000000;
        }
        .screenshot-preview {
            max-width: 200px;
            max-height: 100px;
            border-radius: 5px;
            border: 1px solid #333333;
            cursor: pointer;
        }
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.9);
            justify-content: center;
            align-items: center;
        }
        .modal img {
            max-width: 90%;
            max-height: 90%;
            border-radius: 10px;
        }
        .modal-close {
            position: absolute;
            top: 20px;
            right: 30px;
            color: #ffffff;
            font-size: 2rem;
            cursor: pointer;
            font-weight: 900;
        }
        .no-data {
            color: #444444;
            text-align: center;
            padding: 20px;
            font-weight: 700;
            font-size: 0.9rem;
        }
        
        @media (max-width:600px) {
            body { padding: 15px 10px; }
            .card { padding: 20px; }
            .header h1 { font-size: 1.4rem; }
            .input-row input { min-width: 100%; }
            .btn { width: 100%; text-align: center; }
            .toggle-wrap { top: 10px; right: 10px; }
            .toggle-btn { padding: 6px 12px; font-size: 0.6rem; }
            .history-table { font-size: 0.6rem; }
            .history-table th, .history-table td { padding: 6px 8px; }
            .screenshot-preview { max-width: 80px; max-height: 50px; }
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

    <!-- Modal for screenshot -->
    <div class="modal" id="screenshotModal" onclick="closeModal()">
        <span class="modal-close">&times;</span>
        <img id="modalImage" src="" alt="Screenshot">
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
        </div>

        <!-- HISTORY SECTION -->
        <div class="card history-section">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
                <h2 style="font-weight:900; letter-spacing:2px; color:#888888; font-size:1rem;">📜 LOOKUP HISTORY</h2>
                <button class="btn" onclick="refreshHistory()" style="padding:8px 20px; font-size:0.6rem;">🔄 Refresh</button>
            </div>
            <div id="historyContainer">
                <div class="no-data">Loading history...</div>
            </div>
        </div>

        <div class="footer">● SAMARTH INTELLIGENCE v2026 ●</div>
    </div>

    <script>
        // Audio autoplay
        document.addEventListener('click', function() {
            var audio = document.getElementById('bg-audio');
            if (audio.paused) {
                audio.play().catch(function(e) {});
            }
        });
        window.addEventListener('load', function() {
            var audio = document.getElementById('bg-audio');
            audio.play().catch(function(e) {});
            loadHistory();
        });

        // Dark/Light toggle
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

        // Modal functions
        function openModal(imageSrc) {
            document.getElementById('modalImage').src = imageSrc;
            document.getElementById('screenshotModal').style.display = 'flex';
        }
        function closeModal() {
            document.getElementById('screenshotModal').style.display = 'none';
        }

        // Load history
        async function loadHistory() {
            try {
                const res = await fetch('/history');
                const data = await res.json();
                const container = document.getElementById('historyContainer');
                
                if (data.history && data.history.length > 0) {
                    let html = `<table class="history-table">
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Phone</th>
                                <th>Timestamp</th>
                                <th>Owner</th>
                                <th>Screenshot</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>`;
                    
                    data.history.forEach((item, index) => {
                        const result = item.result || {};
                        const owner = result['Owner Name'] || 'N/A';
                        const screenshot = item.screenshot ? 
                            `<img src="data:image/png;base64,${item.screenshot}" 
                                  class="screenshot-preview" 
                                  onclick="openModal('data:image/png;base64,${item.screenshot}')"
                                  alt="Screenshot">` : 
                            '<span style="color:#444444;">No SS</span>';
                        
                        html += `<tr>
                            <td>${index + 1}</td>
                            <td>${item.phone}</td>
                            <td style="font-size:0.7rem;">${item.timestamp.substring(0,16)}</td>
                            <td>${owner}</td>
                            <td>${screenshot}</td>
                            <td>
                                <button class="view-btn" onclick="viewHistory('${item.phone}')">View</button>
                            </td>
                        </tr>`;
                    });
                    
                    html += `</tbody></table>`;
                    container.innerHTML = html;
                } else {
                    container.innerHTML = '<div class="no-data">📭 No history yet. Start tracing numbers!</div>';
                }
            } catch(err) {
                document.getElementById('historyContainer').innerHTML = 
                    '<div class="no-data" style="color:#ff3333;">❌ Error loading history</div>';
            }
        }

        function refreshHistory() {
            loadHistory();
        }

        async function viewHistory(phone) {
            document.getElementById('phone').value = phone;
            document.getElementById('lookupForm').dispatchEvent(new Event('submit'));
        }

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
                    // Refresh history after lookup
                    setTimeout(loadHistory, 1000);
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
    
    # Get client IP
    ip_address = request.remote_addr
    
    # Perform lookup
    result = lookup_phone_number(phone)
    
    # Save to database
    save_lookup(phone, result, ip_address)
    
    # Capture screenshot asynchronously (Option 15)
    # This will save screenshot to database in background
    capture_screenshot_async(f"{request.host_url}main", phone)
    
    return jsonify(result)

@app.route('/history')
def history():
    """Get lookup history"""
    history_data = get_history(50)
    return jsonify({"history": history_data})

@app.route('/history/<phone>')
def history_by_phone(phone):
    """Get history for specific phone"""
    history_data = get_history_by_phone(phone)
    return jsonify({"history": history_data})


# ============================================================
# MAIN ENTRY POINT
# ============================================================

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║  SAMARTH INTELLIGENCE SYSTEM — ONLINE                    ║
    ║  http://127.0.0.1:5000                                   ║
    ║                                                          ║
    ║  ✅ Database History (Option 1)                         ║
    ║  ✅ Screenshot Capture (Option 15)                      ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    app.run(debug=True, host='0.0.0.0', port=5000)
