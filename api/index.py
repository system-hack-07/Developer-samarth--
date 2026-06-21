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
            background: #000;
            color: #00ffff;
            font-family: 'VT323', monospace;
            min-height: 100vh;
            padding: 10px;
            background-image: 
                linear-gradient(rgba(0,255,255,0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0,255,255,0.03) 1px, transparent 1px);
            background-size: 25px 25px;
        }
        .main {
            max-width: 480px;
            margin: 0 auto;
            border: 4px solid #00ffff;
            box-shadow: 0 0 40px #00ffff, inset 0 0 30px rgba(0,255,255,0.2);
            border-radius: 12px;
            overflow: hidden;
            background: #0a0a0a;
        }
        header {
            background: #000;
            padding: 20px 15px;
            text-align: center;
            border-bottom: 3px solid #00ffff;
        }
        .title { font-size: 1.65rem; line-height: 1.1; text-transform: uppercase; text-shadow: 0 0 15px #00ffff; }
        .dev { color: #00ff9f; margin-top: 8px; font-size: 1.3rem; }
        .isolated {
            display: inline-block; background: #000; border: 2px solid #00ff9f; color: #00ff9f;
            padding: 8px 25px; border-radius: 30px; margin: 15px 0; font-size: 1.1rem;
            box-shadow: 0 0 20px #00ff9f;
        }
        .status-bar {
            display: flex; justify-content: space-around; background: #000; padding: 12px;
            border-bottom: 2px solid #00ffff;
        }
        .input-box {
            margin: 15px; background: #000; border: 3px solid #00ffff; border-radius: 8px;
            padding: 12px; display: flex; align-items: center; gap: 10px;
        }
        input { flex: 1; background: transparent; border: none; color: #00ffff; font-size: 1.4rem; outline: none; }
        .buttons { display: flex; gap: 12px; margin: 0 15px 15px; }
        button {
            flex: 1; padding: 14px; font-size: 1.3rem; border: 3px solid #00ffff;
            background: #000; color: #00ffff; cursor: pointer; border-radius: 6px;
            box-shadow: 0 0 15px #00ffff;
        }
        .execute { border-color: #00ff9f; color: #00ff9f; }
        .log {
            margin: 15px; background: #000; border: 3px solid #00ffff; padding: 15px;
            min-height: 90px; font-size: 1.25rem; line-height: 1.4; color: #00ff9f;
        }
        .results {
            margin: 15px; display: none;
        }
        .data-box {
            background: #000; border: 2px solid #00ffff; padding: 12px; margin-bottom: 10px;
            border-radius: 6px; box-shadow: 0 0 10px #00ffff;
        }
        .label { color: #00ff9f; font-size: 1.2rem; }
        .value { color: #ffffff; font-size: 1.35rem; word-break: break-all; }
        .note {
            margin: 15px; border: 3px dashed #ff0044; padding: 12px; color: #ffcccc; font-size: 1.15rem;
        }
        footer {
            padding: 15px; text-align: center; font-size: 1.1rem; border-top: 2px solid #00ffff;
        }
        .glow { text-shadow: 0 0 20px currentColor; }
    </style>
</head>
<body>
    <div class="main">
        <header>
            <div class="title glow">WELCOME TO NUMBER TO INFO<br>INFO ENGINE</div>
            <div class="dev">Developer is SAMARTH</div>
            <div class="isolated">● LINK ISOLATED</div>
        </header>

        <div class="status-bar">
            <div>LATENCY: <span style="color:#00ff9f">23ms</span></div>
            <div>NODE CORE: <span style="color:#00ff9f">READY</span></div>
        </div>

        <div class="input-box">
            <span style="font-size:1.8rem">📞</span>
            <input type="text" id="phoneInput" placeholder="Enter phone number" maxlength="15">
        </div>

        <div class="buttons">
            <button class="execute" onclick="executeQuery()">EXECUTE QUERY</button>
            <button onclick="resetAll()">RESET</button>
        </div>

        <div class="log" id="log">
            [*] Core interface deployed.<br>
            Listening for validated string configurations.
        </div>

        <div class="results" id="results">
            <div style="text-align:center; color:#00ff9f; margin:10px 0;">EXTRACTION COMPLETE</div>
            <div id="dataContainer"></div>
        </div>

        <div class="note">
            <strong>NOTE</strong><br>
            Those Informations are not coming [There data is not leaked in any database] [your number is safe]
        </div>

        <footer>
            Disclaimer: This application environment is engineered strictly for educational purpose processing. External framework exploitation is prohibited.<br><br>
            <strong>Max-Glow Core v3.0</strong>  @Samarth
        </footer>
    </div>

    <script>
        async function executeQuery() {
            const input = document.getElementById('phoneInput').value.trim();
            const log = document.getElementById('log');
            const resultsDiv = document.getElementById('results');
            const container = document.getElementById('dataContainer');
            
            if (!input) {
                log.innerHTML = "[!] ERROR: Enter a valid number";
                return;
            }
            
            log.innerHTML = `[*] Querying ${input}...<br>[+] Connecting to secure nodes...`;
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
                    log.innerHTML += `<br>[!] ERROR: ${data.error}`;
                    return;
                }
                
                log.innerHTML += `<br>[+] Data retrieved successfully.`;
                
                // Build beautiful result boxes
                Object.keys(data).forEach(key => {
                    const box = document.createElement('div');
                    box.className = 'data-box';
                    box.innerHTML = `
                        <div class="label">${key.toUpperCase()}</div>
                        <div class="value">${data[key] || 'N/A'}</div>
                    `;
                    container.appendChild(box);
                });
                
                resultsDiv.style.display = 'block';
            } catch(e) {
                log.innerHTML += `<br>[!] Network error. Try again.`;
            }
        }

        function resetAll() {
            document.getElementById('phoneInput').value = '';
            document.getElementById('log').innerHTML = '[*] Core interface deployed.<br>Listening for validated string configurations.';
            document.getElementById('results').style.display = 'none';
        }
    </script>
</body>
</html>"""

def lookup_phone_number(phone_number):
    url = "https://calltracer.in"
    headers = {
        "Host": "calltracer.in",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Content-Type": "application/x-www-form-urlencoded"
    }
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

        if all(v == "N/A" for v in list(data.values())[1:]):
            return {"error": "No data found for this number."}
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
    if not number:
        return jsonify({"error": "Number required"})
    result = lookup_phone_number(number)
    return jsonify(result)

if __name__ == '__main__':
    app.run()
