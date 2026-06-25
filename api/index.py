from flask import Flask, request, jsonify, render_template_string
import requests
from bs4 import BeautifulSoup
import time
import re

app = Flask(__name__)

# ============================================================
# CORE LOOKUP ENGINE
# ============================================================

def lookup_phone_number(phone_number):
    """Professional phone number intelligence lookup"""
    
    # Clean input
    phone_number = re.sub(r'\s+', '', phone_number.strip())
    if not phone_number.startswith('+'):
        phone_number = '+' + phone_number
    
    url = "https://calltracer.in"
    headers = {
        "Host": "calltracer.in",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://calltracer.in",
        "Referer": "https://calltracer.in/"
    }
    payload = {
        "country": "IN",
        "q": phone_number
    }

    try:
        response = requests.post(url, headers=headers, data=payload, timeout=20)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        def extract_value(label):
            """Extract value from table row containing label"""
            try:
                # Find element containing the label
                element = soup.find(string=lambda t: t and label in str(t))
                if element:
                    # Navigate to parent row
                    row = element.find_parent('tr')
                    if row:
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            value = cells[1].get_text(strip=True)
                            return value if value else "Not Available"
            except:
                pass
            return "Not Available"

        # Build comprehensive intelligence report
        report = {
            "phone_number": phone_number,
            "status": "verified",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "intelligence": {
                "owner_name": extract_value("Owner Name"),
                "sim_card": extract_value("SIM card"),
                "mobile_state": extract_value("Mobile State"),
                "connection_type": extract_value("Connection"),
                "language": extract_value("Language"),
                "country": extract_value("Country"),
                "hometown": extract_value("Hometown"),
                "reference_city": extract_value("Refrence City"),
                "owner_address": extract_value("Owner Address"),
                "owner_personality": extract_value("Owner Personality"),
                "tracking_history": extract_value("Tracking History"),
                "tower_locations": extract_value("Tower Locations"),
                "current_location": extract_value("Mobile Locations"),
                "ip_address": extract_value("IP address"),
                "imei": extract_value("IMEI number"),
                "mac_address": extract_value("MAC address"),
                "tracker_id": extract_value("Tracker Id"),
                "complaints": extract_value("Complaints")
            }
        }

        # Check if we got meaningful data
        has_data = any(v != "Not Available" for v in report["intelligence"].values())
        if not has_data:
            return {
                "status": "error",
                "message": "No intelligence data found. Please verify the number or try a different source."
            }

        return report

    except requests.exceptions.Timeout:
        return {"status": "error", "message": "Request timeout. Please try again."}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Network error: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": f"System error: {str(e)}"}


# ============================================================
# PROFESSIONAL UI - ENTERPRISE GRADE
# ============================================================

HOME_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Global Intelligence Systems</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: #0a0e17;
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            background-image: 
                radial-gradient(ellipse at 10% 20%, rgba(0, 200, 255, 0.05) 0%, transparent 50%),
                radial-gradient(ellipse at 90% 80%, rgba(0, 200, 255, 0.05) 0%, transparent 50%);
        }
        
        .security-badge {
            position: fixed;
            top: 20px;
            right: 30px;
            color: rgba(0, 200, 255, 0.3);
            font-size: 11px;
            letter-spacing: 2px;
            text-transform: uppercase;
            font-weight: 300;
        }
        
        .main-container {
            max-width: 750px;
            width: 90%;
            padding: 60px 50px;
            background: rgba(10, 14, 23, 0.85);
            border: 1px solid rgba(0, 200, 255, 0.15);
            border-radius: 16px;
            box-shadow: 
                0 0 80px rgba(0, 200, 255, 0.05),
                inset 0 0 80px rgba(0, 200, 255, 0.02);
            backdrop-filter: blur(10px);
            text-align: center;
        }
        
        .logo-icon {
            font-size: 3rem;
            margin-bottom: 10px;
            display: block;
            letter-spacing: 4px;
        }
        
        h1 {
            color: #e8f0fe;
            font-size: 2.8rem;
            font-weight: 200;
            letter-spacing: 6px;
            text-transform: uppercase;
            margin-bottom: 8px;
        }
        
        .subtitle {
            color: rgba(0, 200, 255, 0.6);
            font-size: 0.85rem;
            letter-spacing: 4px;
            text-transform: uppercase;
            font-weight: 300;
            margin-bottom: 35px;
            border-bottom: 1px solid rgba(0, 200, 255, 0.08);
            padding-bottom: 25px;
        }
        
        .tagline {
            color: rgba(255, 255, 255, 0.4);
            font-size: 1rem;
            font-weight: 300;
            margin-bottom: 40px;
            line-height: 1.7;
        }
        
        .enter-btn {
            display: inline-block;
            padding: 18px 65px;
            font-size: 1.1rem;
            font-weight: 400;
            letter-spacing: 3px;
            text-transform: uppercase;
            color: #00c8ff;
            background: transparent;
            border: 1px solid rgba(0, 200, 255, 0.3);
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
            text-decoration: none;
            position: relative;
            overflow: hidden;
        }
        
        .enter-btn:hover {
            background: rgba(0, 200, 255, 0.1);
            border-color: #00c8ff;
            box-shadow: 0 0 40px rgba(0, 200, 255, 0.1);
            transform: translateY(-2px);
        }
        
        .enter-btn:active {
            transform: scale(0.98);
        }
        
        .footer {
            position: fixed;
            bottom: 25px;
            width: 100%;
            text-align: center;
            color: rgba(255, 255, 255, 0.12);
            font-size: 0.7rem;
            letter-spacing: 2px;
            font-weight: 300;
        }
        
        .status-dot {
            display: inline-block;
            width: 6px;
            height: 6px;
            background: #00ff88;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.2; }
        }
        
        @media (max-width: 600px) {
            .main-container {
                padding: 40px 25px;
            }
            h1 {
                font-size: 2rem;
                letter-spacing: 3px;
            }
            .enter-btn {
                padding: 15px 40px;
                font-size: 0.95rem;
                width: 100%;
            }
            .security-badge {
                display: none;
            }
        }
    </style>
</head>
<body>
    <div class="security-badge">● Secure Connection • v4.2</div>
    <div class="main-container">
        <span class="logo-icon">◈</span>
        <h1>Global Intelligence</h1>
        <div class="subtitle">Advanced Number Intelligence Platform</div>
        <p class="tagline">
            Enterprise-grade phone number analytics &amp; intelligence gathering.
            <br>Secure • Private • Authorized Access Only
        </p>
        <a href="/boot" class="enter-btn">Access Platform</a>
    </div>
    <div class="footer">
        <span class="status-dot"></span> System Operational • v2026.06
    </div>
</body>
</html>
'''

BOOT_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>System Initialization</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #0a0e17;
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .terminal-box {
            max-width: 650px;
            width: 100%;
            padding: 45px 40px;
            background: rgba(10, 14, 23, 0.9);
            border: 1px solid rgba(0, 200, 255, 0.12);
            border-radius: 12px;
            box-shadow: 0 0 60px rgba(0, 200, 255, 0.03);
        }
        .log-line {
            color: rgba(255, 255, 255, 0.5);
            font-size: 0.9rem;
            padding: 4px 0;
            font-weight: 300;
            letter-spacing: 0.5px;
            font-family: 'Courier New', monospace;
        }
        .log-line.success { color: #00ff88; }
        .log-line.active { color: #00c8ff; }
        .loader {
            width: 40px;
            height: 40px;
            margin: 25px auto;
            border: 2px solid rgba(0, 200, 255, 0.1);
            border-top: 2px solid #00c8ff;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        #status {
            color: rgba(0, 200, 255, 0.5);
            font-size: 0.8rem;
            letter-spacing: 2px;
            text-align: center;
            margin-top: 15px;
            font-weight: 300;
        }
        @media (max-width: 600px) {
            .terminal-box { padding: 30px 20px; }
        }
    </style>
</head>
<body>
    <div class="terminal-box" id="bootlog">
        <div class="log-line">> Initializing intelligence engine...</div>
        <div class="log-line">> Establishing secure channels...</div>
        <div class="log-line">> Authenticating credentials...</div>
        <div class="loader"></div>
        <div id="status">CONNECTING TO SECURE NODES</div>
    </div>
    <script>
        const logDiv = document.getElementById('bootlog');
        const statusDiv = document.getElementById('status');
        const messages = [
            { text: "> Loading core modules...", cls: "log-line" },
            { text: "> Establishing encrypted tunnel...", cls: "log-line" },
            { text: "> Synchronizing with global databases...", cls: "log-line" },
            { text: "> Connection established.", cls: "log-line success" },
            { text: "> System ready.", cls: "log-line success" }
        ];
        let idx = 0;
        function nextLog() {
            if (idx < messages.length) {
                const div = document.createElement('div');
                div.className = messages[idx].cls;
                div.textContent = messages[idx].text;
                logDiv.insertBefore(div, statusDiv);
                idx++;
                setTimeout(nextLog, 600);
            } else {
                statusDiv.textContent = "● SYSTEM ONLINE — REDIRECTING";
                statusDiv.style.color = "#00ff88";
                setTimeout(() => { window.location.href = '/main'; }, 1200);
            }
        }
        setTimeout(nextLog, 500);
    </script>
</body>
</html>
'''

MAIN_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Intelligence Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #0a0e17;
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            min-height: 100vh;
            padding: 30px 20px;
        }
        .dashboard {
            max-width: 900px;
            margin: 0 auto;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 25px;
            border-bottom: 1px solid rgba(0, 200, 255, 0.08);
            margin-bottom: 30px;
        }
        .header h1 {
            color: #e8f0fe;
            font-size: 1.6rem;
            font-weight: 300;
            letter-spacing: 3px;
        }
        .header span {
            color: rgba(255, 255, 255, 0.15);
            font-size: 0.7rem;
            letter-spacing: 1px;
        }
        .card {
            background: rgba(10, 14, 23, 0.85);
            border: 1px solid rgba(0, 200, 255, 0.08);
            border-radius: 12px;
            padding: 35px 40px;
            box-shadow: 0 0 40px rgba(0, 0, 0, 0.3);
        }
        .card-title {
            color: rgba(255, 255, 255, 0.4);
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 3px;
            font-weight: 400;
            margin-bottom: 20px;
        }
        .input-group {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }
        .input-group input {
            flex: 1;
            min-width: 220px;
            padding: 14px 18px;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(0, 200, 255, 0.12);
            border-radius: 8px;
            color: #e8f0fe;
            font-size: 1rem;
            font-weight: 300;
            letter-spacing: 0.5px;
            transition: all 0.3s;
            font-family: 'Segoe UI', system-ui, sans-serif;
        }
        .input-group input:focus {
            outline: none;
            border-color: rgba(0, 200, 255, 0.3);
            background: rgba(255, 255, 255, 0.06);
        }
        .input-group input::placeholder {
            color: rgba(255, 255, 255, 0.2);
        }
        .btn {
            padding: 14px 35px;
            background: transparent;
            border: 1px solid rgba(0, 200, 255, 0.25);
            border-radius: 8px;
            color: #00c8ff;
            font-size: 0.85rem;
            font-weight: 400;
            letter-spacing: 2px;
            text-transform: uppercase;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn:hover {
            background: rgba(0, 200, 255, 0.08);
            border-color: #00c8ff;
        }
        .btn:active { transform: scale(0.98); }
        
        #result {
            margin-top: 30px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
            padding: 25px;
            min-height: 120px;
            border: 1px solid rgba(0, 200, 255, 0.05);
            color: rgba(255, 255, 255, 0.7);
            font-size: 0.95rem;
            line-height: 1.9;
            font-weight: 300;
            white-space: pre-wrap;
            word-break: break-word;
        }
        #result .key {
            color: rgba(0, 200, 255, 0.7);
            font-weight: 400;
        }
        #result .value {
            color: #e8f0fe;
        }
        #result .error {
            color: #ff6b6b;
        }
        #result .success {
            color: #00ff88;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            color: rgba(255, 255, 255, 0.06);
            font-size: 0.65rem;
            letter-spacing: 2px;
        }
        @media (max-width: 600px) {
            body { padding: 15px 10px; }
            .card { padding: 20px; }
            .header h1 { font-size: 1.2rem; }
            .header span { display: none; }
            .input-group input { min-width: 100%; }
            .btn { width: 100%; text-align: center; }
        }
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>◈ Number Intelligence</h1>
            <span>SECURE • v4.2</span>
        </div>
        <div class="card">
            <div class="card-title">Enter Target Number</div>
            <form id="lookupForm">
                <div class="input-group">
                    <input type="text" id="phone" placeholder="+91XXXXXXXXXX or 91XXXXXXXXXX" required>
                    <button type="submit" class="btn">Trace</button>
                </div>
            </form>
            <div id="result">Awaiting input...</div>
        </div>
        <div class="footer">System Intelligence • Authorized Use Only</div>
    </div>
    <script>
        document.getElementById('lookupForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const phone = document.getElementById('phone').value;
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = '<span style="color: rgba(0,200,255,0.5);">Processing intelligence request...</span>';
            try {
                const res = await fetch('/lookup', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: 'phone=' + encodeURIComponent(phone)
                });
                const data = await res.json();
                if (data.status === 'error') {
                    resultDiv.innerHTML = `<span class="error">⚠ ${data.message}</span>`;
                } else {
                    let html = `<span class="success">✓ Intelligence report generated</span><br><br>`;
                    html += `<span class="key">Phone:</span> <span class="value">${data.phone_number}</span><br>`;
                    html += `<span class="key">Timestamp:</span> <span class="value">${data.timestamp}</span><br><br>`;
                    for (let [key, val] of Object.entries(data.intelligence)) {
                        if (val && val !== 'Not Available') {
                            const label = key.replace(/_/g, ' ').toUpperCase();
                            html += `<span class="key">${label}:</span> <span class="value">${val}</span><br>`;
                        }
                    }
                    resultDiv.innerHTML = html;
                }
            } catch(err) {
                resultDiv.innerHTML = `<span class="error">⚠ Connection error. Please retry.</span>`;
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
        return jsonify({"status": "error", "message": "Phone number required"}), 400
    result = lookup_phone_number(phone)
    return jsonify(result)


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║  GLOBAL INTELLIGENCE SYSTEM — ONLINE                  ║
    ║  http://127.0.0.1:5000                               ║
    ╚═══════════════════════════════════════════════════════╝
    """)
    app.run(debug=True, host='0.0.0.0', port=5000)
