# ============================================================
# SAMARTH PHONE TRACKER PRO - VERCEL DEPLOYMENT READY
# ============================================================
# 📱 Complete single file for Vercel deployment
# - Welcome page with animations
# - Fake booting sequence with background music
# - Pro-level main interface
# - Real phone number lookup API (NO MOCK DATA)
# - Ready for Vercel serverless deployment
# ============================================================

from flask import Flask, request, jsonify, render_template_string
import requests
from bs4 import BeautifulSoup
import re
import time
import os

app = Flask(__name__)

# ============================================================
# RATE LIMITING (In-memory - resets on each Vercel invocation)
# ============================================================
rate_limit_store = {}
RATE_LIMIT = 10  # requests per minute
TIME_WINDOW = 60  # seconds

def is_rate_limited(ip):
    now = time.time()
    if ip in rate_limit_store:
        timestamps = [t for t in rate_limit_store[ip] if now - t < TIME_WINDOW]
        if len(timestamps) >= RATE_LIMIT:
            return True
        timestamps.append(now)
        rate_limit_store[ip] = timestamps
    else:
        rate_limit_store[ip] = [now]
    return False

# ============================================================
# PHONE VALIDATION
# ============================================================
def validate_phone(phone):
    """Validate Indian phone numbers"""
    pattern = r'^[6-9]\d{9}$|^\+91[6-9]\d{9}$|^0?[6-9]\d{9}$|^91[6-9]\d{9}$'
    return re.match(pattern, phone) is not None

def clean_phone(phone):
    """Remove all non-digit characters"""
    return re.sub(r'\D', '', phone)

def format_phone_for_api(phone):
    """Format phone number for API call"""
    cleaned = clean_phone(phone)
    if len(cleaned) == 10:
        return '+91' + cleaned
    elif len(cleaned) == 12 and cleaned.startswith('91'):
        return '+' + cleaned
    elif not cleaned.startswith('+'):
        return '+' + cleaned
    return cleaned

# ============================================================
# REAL API LOOKUP - NO MOCK DATA
# ============================================================
def lookup_phone_number(phone_number):
    """
    Real phone number lookup using calltracer.in
    Returns: (data_dict, status_code)
    """
    url = "https://calltracer.in"
    headers = {
        "Host": "calltracer.in",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://calltracer.in",
        "Referer": "https://calltracer.in/",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "Connection": "keep-alive",
    }
    payload = {
        "country": "IN",
        "q": phone_number
    }

    try:
        # Send POST request with timeout
        response = requests.post(url, headers=headers, data=payload, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        def get_value(label):
            """Extract value from table by label"""
            patterns = [
                lambda: soup.find('td', string=re.compile(label, re.I)),
                lambda: soup.find('th', string=re.compile(label, re.I)),
                lambda: soup.find(string=re.compile(label, re.I))
            ]
            
            for pattern in patterns:
                try:
                    cell = pattern()
                    if cell:
                        tr = cell.find_parent('tr')
                        if tr:
                            tds = tr.find_all(['td', 'th'])
                            if len(tds) > 1:
                                for td in tds:
                                    if td != cell:
                                        text = td.get_text(strip=True)
                                        if text:
                                            return text
                except:
                    continue
            
            return "N/A"

        # Extract all available data
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

        # Check if we got any real data
        has_data = any(v != "N/A" and v != "" for v in data.values())
        
        if not has_data:
            return {"error": "No data found for this number."}, 404

        return data, 200

    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Please try again."}, 408
    except requests.exceptions.ConnectionError:
        return {"error": "Connection error. Please check your internet."}, 503
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {str(e)}"}, 500
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}, 500

# ============================================================
# HTML TEMPLATE - COMPLETE FRONTEND (VERCEL OPTIMIZED)
# ============================================================
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Samarth Phone Tracker Pro</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }

        body {
            background: #0a0a0a;
            color: #00ff41;
            font-family: 'Courier New', 'Consolas', monospace;
            height: 100vh;
            overflow: hidden;
            position: relative;
            user-select: none;
        }

        .page {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            transition: all 0.8s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            z-index: 10;
            padding: 16px;
        }

        .page.hidden {
            opacity: 0;
            transform: scale(0.8) rotateX(10deg);
            pointer-events: none;
            z-index: 1;
        }

        .page.active {
            opacity: 1;
            transform: scale(1) rotateX(0deg);
            pointer-events: auto;
            z-index: 20;
        }

        #welcomePage {
            background: radial-gradient(ellipse at center, #0f1f0f 0%, #050505 100%);
            flex-direction: column;
            gap: 20px;
        }

        #welcomePage::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: repeating-linear-gradient(0deg, 
                rgba(0,255,65,0.02) 0px, 
                rgba(0,255,65,0.02) 2px,
                transparent 2px,
                transparent 4px);
            pointer-events: none;
            animation: matrixRain 20s linear infinite;
        }

        @keyframes matrixRain {
            0% { background-position: 0 0; }
            100% { background-position: 0 100px; }
        }

        .welcome-content {
            position: relative;
            z-index: 2;
            text-align: center;
            max-width: 500px;
            width: 100%;
            padding: 20px;
        }

        .glitch-title {
            font-size: clamp(2rem, 8vw, 4.5rem);
            font-weight: 900;
            text-transform: uppercase;
            text-shadow: 
                0 0 10px #00ff41,
                0 0 20px #00ff41,
                0 0 40px rgba(0,255,65,0.3),
                0 0 80px rgba(0,255,65,0.1);
            animation: glitch 3s infinite;
            letter-spacing: 4px;
            line-height: 1.1;
            margin-bottom: 8px;
        }

        .glitch-title .highlight {
            color: #00ff41;
            display: inline-block;
            animation: pulseGlow 2s ease-in-out infinite;
        }

        @keyframes glitch {
            0%, 90%, 100% { transform: translate(0); }
            92% { transform: translate(-3px, 2px) skewX(2deg); }
            94% { transform: translate(3px, -2px) skewX(-2deg); }
            96% { transform: translate(-2px, 1px); }
            98% { transform: translate(2px, -1px); }
        }

        @keyframes pulseGlow {
            0%, 100% { text-shadow: 0 0 20px #00ff41, 0 0 40px rgba(0,255,65,0.3); }
            50% { text-shadow: 0 0 30px #00ff41, 0 0 60px rgba(0,255,65,0.5), 0 0 100px rgba(0,255,65,0.2); }
        }

        .subtitle {
            font-size: clamp(0.8rem, 2vw, 1.2rem);
            color: #006622;
            letter-spacing: 6px;
            text-transform: uppercase;
            margin-bottom: 30px;
            opacity: 0.8;
            animation: fadeInOut 3s ease-in-out infinite;
        }

        @keyframes fadeInOut {
            0%, 100% { opacity: 0.5; }
            50% { opacity: 1; }
        }

        .feature-box {
            background: rgba(0, 255, 65, 0.03);
            border: 1px solid rgba(0, 255, 65, 0.15);
            border-radius: 16px;
            padding: 20px 24px;
            margin: 20px 0 30px;
            backdrop-filter: blur(10px);
            position: relative;
            overflow: hidden;
        }

        .feature-box::after {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: conic-gradient(from 0deg, transparent, rgba(0,255,65,0.05), transparent, rgba(0,255,65,0.05), transparent);
            animation: spinBorder 8s linear infinite;
        }

        @keyframes spinBorder {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .feature-box .content {
            position: relative;
            z-index: 1;
        }

        .feature-box .feature-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 6px 0;
            font-size: clamp(0.7rem, 1.5vw, 0.9rem);
            color: #66ff99;
            border-bottom: 1px solid rgba(0,255,65,0.05);
        }

        .feature-box .feature-item:last-child {
            border-bottom: none;
        }

        .feature-box .feature-item .icon {
            font-size: 1.2rem;
            min-width: 28px;
        }

        .enter-btn {
            position: relative;
            padding: 18px 50px;
            font-size: clamp(1rem, 2.5vw, 1.4rem);
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 4px;
            color: #0a0a0a;
            background: #00ff41;
            border: none;
            border-radius: 50px;
            cursor: pointer;
            font-family: 'Courier New', monospace;
            transition: all 0.3s ease;
            box-shadow: 0 0 30px rgba(0, 255, 65, 0.3);
            touch-action: manipulation;
            width: 100%;
            max-width: 300px;
        }

        .enter-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 0 50px rgba(0, 255, 65, 0.5);
        }

        .enter-btn:active {
            transform: scale(0.95);
        }

        .enter-btn::before {
            content: '';
            position: absolute;
            top: -2px;
            left: -2px;
            right: -2px;
            bottom: -2px;
            background: linear-gradient(45deg, #00ff41, #00cc33, #00ff41, #00cc33);
            background-size: 300% 300%;
            border-radius: 52px;
            z-index: -1;
            animation: btnBorder 3s ease-in-out infinite;
        }

        @keyframes btnBorder {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        #bootingPage {
            background: #050505;
            flex-direction: column;
            gap: 20px;
            padding: 20px;
        }

        .boot-container {
            max-width: 500px;
            width: 100%;
            text-align: center;
        }

        .boot-title {
            font-size: clamp(1.2rem, 4vw, 2.5rem);
            color: #00ff41;
            text-shadow: 0 0 20px rgba(0,255,65,0.3);
            margin-bottom: 10px;
            animation: pulseGlow 1.5s ease-in-out infinite;
        }

        .boot-progress {
            width: 100%;
            height: 4px;
            background: #0a1a0a;
            border-radius: 4px;
            overflow: hidden;
            margin: 20px 0;
            border: 1px solid rgba(0,255,65,0.1);
        }

        .boot-progress-bar {
            height: 100%;
            width: 0%;
            background: linear-gradient(90deg, #00ff41, #66ff99, #00ff41);
            background-size: 200% 100%;
            border-radius: 4px;
            animation: progressGlow 2s linear infinite;
            transition: width 0.3s ease;
        }

        @keyframes progressGlow {
            0% { background-position: 0% 0%; }
            100% { background-position: 200% 0%; }
        }

        .boot-log {
            background: rgba(0, 255, 65, 0.02);
            border: 1px solid rgba(0, 255, 65, 0.05);
            border-radius: 10px;
            padding: 16px;
            height: 200px;
            overflow-y: auto;
            font-size: clamp(0.6rem, 1.2vw, 0.75rem);
            color: #006622;
            text-align: left;
            font-family: 'Courier New', monospace;
            line-height: 1.8;
            scroll-behavior: smooth;
        }

        .boot-log::-webkit-scrollbar {
            width: 3px;
        }
        .boot-log::-webkit-scrollbar-track {
            background: #0a0a0a;
        }
        .boot-log::-webkit-scrollbar-thumb {
            background: #00ff41;
            border-radius: 3px;
        }

        .boot-log .log-line {
            opacity: 0;
            animation: logFade 0.5s ease forwards;
        }

        .boot-log .log-line .timestamp {
            color: #003311;
            margin-right: 10px;
        }

        .boot-log .log-line .status {
            color: #00ff41;
        }

        .boot-log .log-line .status.error {
            color: #ff4444;
        }

        .boot-log .log-line .status.warning {
            color: #ffaa00;
        }

        @keyframes logFade {
            0% { opacity: 0; transform: translateX(-10px); }
            100% { opacity: 1; transform: translateX(0); }
        }

        .boot-percent {
            font-size: clamp(1.5rem, 4vw, 3rem);
            color: #00ff41;
            font-weight: 900;
            text-shadow: 0 0 30px rgba(0,255,65,0.2);
            margin: 10px 0;
            font-variant-numeric: tabular-nums;
        }

        #mainPage {
            background: #0a0a0a;
            padding: 12px;
            align-items: flex-start;
            padding-top: 10px;
            overflow-y: auto;
            background-image: 
                radial-gradient(circle at 10% 20%, rgba(0,255,65,0.02) 0%, transparent 50%),
                radial-gradient(circle at 90% 80%, rgba(0,255,65,0.02) 0%, transparent 50%);
        }

        .main-container {
            max-width: 500px;
            width: 100%;
            margin: 0 auto;
            padding: 16px 14px 20px;
            background: rgba(13, 13, 13, 0.95);
            border: 1px solid rgba(0, 255, 65, 0.12);
            border-radius: 16px;
            backdrop-filter: blur(10px);
            box-shadow: 0 0 40px rgba(0, 255, 65, 0.03);
            position: relative;
            overflow: hidden;
        }

        .main-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, #00ff41, transparent);
            animation: scan 3s infinite linear;
        }

        @keyframes scan {
            0% { opacity: 0.2; transform: scaleX(0.8); }
            50% { opacity: 1; transform: scaleX(1); }
            100% { opacity: 0.2; transform: scaleX(0.8); }
        }

        .main-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 12px;
            border-bottom: 1px solid rgba(0, 255, 65, 0.08);
            margin-bottom: 14px;
            flex-wrap: wrap;
            gap: 6px;
        }

        .main-header .brand {
            font-size: clamp(0.9rem, 2vw, 1.2rem);
            font-weight: 900;
            color: #00ff41;
            text-shadow: 0 0 20px rgba(0,255,65,0.15);
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .main-header .brand .badge {
            font-size: 0.5rem;
            background: #003311;
            padding: 2px 8px;
            border-radius: 10px;
            color: #00ff41;
            border: 1px solid rgba(0,255,65,0.15);
        }

        .main-header .status-dot {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 0.6rem;
            color: #006622;
        }

        .main-header .status-dot .dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: #00ff41;
            animation: pulse 1.5s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.2; }
        }

        .input-section {
            display: flex;
            flex-direction: column;
            gap: 10px;
            margin: 10px 0 14px;
        }

        .input-row {
            display: flex;
            gap: 10px;
            width: 100%;
        }

        .input-row input {
            flex: 1;
            padding: 14px 16px;
            background: #080808;
            border: 1px solid rgba(0, 255, 65, 0.15);
            color: #00ff41;
            font-size: clamp(0.9rem, 2vw, 1.05rem);
            font-family: 'Courier New', monospace;
            border-radius: 10px;
            outline: none;
            transition: 0.3s;
            min-width: 0;
            width: 100%;
            -webkit-appearance: none;
        }

        .input-row input:focus {
            box-shadow: 0 0 25px rgba(0, 255, 65, 0.08);
            border-color: #00ff41;
            background: #050505;
        }

        .input-row input::placeholder {
            color: #003311;
            font-size: 0.75rem;
        }

        .input-row button {
            padding: 14px 20px;
            background: #00ff41;
            color: #0a0a0a;
            font-weight: 900;
            font-size: clamp(0.8rem, 1.8vw, 1rem);
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-family: 'Courier New', monospace;
            transition: 0.3s;
            text-transform: uppercase;
            letter-spacing: 1px;
            white-space: nowrap;
            touch-action: manipulation;
            min-width: 70px;
        }

        .input-row button:active {
            transform: scale(0.95);
        }

        .input-row button:hover {
            box-shadow: 0 0 30px rgba(0, 255, 65, 0.15);
        }

        .input-row button:disabled {
            opacity: 0.4;
            cursor: not-allowed;
            transform: none;
        }

        .quick-actions {
            display: flex;
            gap: 6px;
            flex-wrap: wrap;
            margin-top: 2px;
        }

        .quick-actions button {
            padding: 5px 12px;
            background: rgba(0, 255, 65, 0.04);
            border: 1px solid rgba(0, 255, 65, 0.08);
            color: #006622;
            font-size: 0.55rem;
            border-radius: 6px;
            cursor: pointer;
            font-family: 'Courier New', monospace;
            transition: 0.2s;
            touch-action: manipulation;
        }

        .quick-actions button:active {
            transform: scale(0.95);
            background: rgba(0, 255, 65, 0.08);
        }

        .status-msg {
            font-size: 0.7rem;
            color: #006622;
            min-height: 1.2rem;
            padding: 4px 8px;
            border-left: 2px solid rgba(0, 255, 65, 0.1);
            margin: 6px 0 10px;
            word-break: break-word;
        }

        .status-msg.error {
            color: #ff4444;
            border-left-color: #ff4444;
        }

        .status-msg.success {
            color: #66ff99;
            border-left-color: #66ff99;
        }

        .result-box {
            background: rgba(8, 8, 8, 0.8);
            border: 1px solid rgba(0, 255, 65, 0.05);
            border-radius: 10px;
            padding: 4px 0;
            max-height: 350px;
            overflow-y: auto;
            -webkit-overflow-scrolling: touch;
        }

        .result-box::-webkit-scrollbar {
            width: 3px;
        }
        .result-box::-webkit-scrollbar-track {
            background: #0a0a0a;
        }
        .result-box::-webkit-scrollbar-thumb {
            background: #00ff41;
            border-radius: 3px;
        }

        .result-box .empty {
            color: #003311;
            text-align: center;
            padding: 30px 16px;
            font-size: 0.7rem;
        }

        .result-box .empty .icon {
            font-size: 2rem;
            display: block;
            margin-bottom: 6px;
        }

        .result-box .field {
            display: flex;
            justify-content: space-between;
            padding: 8px 14px;
            border-bottom: 1px solid rgba(0, 255, 65, 0.03);
            gap: 12px;
            align-items: flex-start;
        }

        .result-box .field .label {
            color: #00cc44;
            font-size: 0.65rem;
            min-width: 80px;
            flex-shrink: 0;
            text-transform: uppercase;
            letter-spacing: 0.3px;
            padding-top: 1px;
        }

        .result-box .field .value {
            color: #66ff99;
            word-break: break-word;
            text-align: right;
            font-size: 0.75rem;
            line-height: 1.4;
        }

        .result-box .field .value.na {
            color: #003311;
        }

        .result-box .field-highlight {
            background: rgba(0, 255, 65, 0.03);
            border-left: 2px solid #00ff41;
        }

        .result-box .loading {
            text-align: center;
            color: #00ff41;
            padding: 30px 16px;
            font-size: 0.8rem;
        }

        .result-box .loading .spinner {
            display: inline-block;
            animation: spin 1s linear infinite;
            margin-right: 8px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .result-box .error-msg {
            color: #ff4444;
            text-align: center;
            padding: 25px 16px;
            font-size: 0.8rem;
        }

        .result-box .error-msg .icon {
            font-size: 1.5rem;
            display: block;
            margin-bottom: 6px;
        }

        .main-footer {
            margin-top: 14px;
            text-align: center;
            font-size: 0.5rem;
            color: #002211;
            border-top: 1px solid rgba(0, 255, 65, 0.05);
            padding-top: 10px;
            display: flex;
            justify-content: center;
            gap: 14px;
            flex-wrap: wrap;
        }

        .main-footer a {
            color: #003311;
            text-decoration: none;
            transition: 0.2s;
        }

        .main-footer a:active {
            color: #00aa33;
        }

        .toast {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%) translateY(100px);
            background: rgba(13, 13, 13, 0.95);
            border: 1px solid #00ff41;
            color: #00ff41;
            padding: 10px 20px;
            border-radius: 10px;
            font-size: 0.65rem;
            font-family: 'Courier New', monospace;
            opacity: 0;
            transition: 0.4s ease;
            z-index: 999;
            max-width: 90%;
            text-align: center;
            box-shadow: 0 0 30px rgba(0, 255, 65, 0.05);
            backdrop-filter: blur(10px);
        }

        .toast.show {
            opacity: 1;
            transform: translateX(-50%) translateY(0);
        }

        .toast.error {
            border-color: #ff4444;
            color: #ff4444;
        }

        .toast.success {
            border-color: #66ff99;
            color: #66ff99;
        }

        .exit-boot-btn {
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            padding: 12px 30px;
            background: rgba(255, 68, 68, 0.1);
            border: 1px solid rgba(255, 68, 68, 0.2);
            color: #ff4444;
            border-radius: 30px;
            font-size: 0.7rem;
            cursor: pointer;
            font-family: 'Courier New', monospace;
            transition: 0.3s;
            z-index: 50;
            touch-action: manipulation;
            letter-spacing: 2px;
            text-transform: uppercase;
            backdrop-filter: blur(5px);
        }

        .exit-boot-btn:active {
            transform: translateX(-50%) scale(0.95);
            background: rgba(255, 68, 68, 0.2);
        }

        .exit-boot-btn:hover {
            border-color: #ff4444;
            box-shadow: 0 0 30px rgba(255, 68, 68, 0.1);
        }

        .exit-boot-btn.hidden {
            display: none;
        }

        @media (max-width: 480px) {
            .page { padding: 10px; }
            .main-container { padding: 12px 10px 16px; }
            .result-box .field {
                flex-direction: column;
                gap: 2px;
                padding: 6px 12px;
            }
            .result-box .field .label {
                min-width: auto;
                font-size: 0.55rem;
                color: #006622;
            }
            .result-box .field .value {
                text-align: left;
                font-size: 0.7rem;
                padding-left: 4px;
            }
            .result-box { max-height: 280px; }
            .boot-log { height: 150px; }
            .feature-box { padding: 14px 16px; }
        }

        @media (max-width: 380px) {
            .main-container { padding: 8px 6px 12px; }
            .input-row input { padding: 10px 12px; font-size: 0.8rem; }
            .input-row button { padding: 10px 14px; font-size: 0.7rem; min-width: 55px; }
            .result-box .field { padding: 4px 10px; }
        }

        @media (min-width: 600px) {
            .main-container { padding: 24px 28px 20px; }
            .result-box .field { padding: 10px 18px; }
            .result-box .field .label { font-size: 0.75rem; min-width: 110px; }
            .result-box .field .value { font-size: 0.85rem; }
            .result-box { max-height: 400px; }
        }

        .hidden { display: none !important; }
    </style>
</head>
<body>

    <div class="toast" id="toast"></div>

    <button class="exit-boot-btn hidden" id="exitBootBtn">⏏️ Skip Boot</button>

    <!-- Welcome Page -->
    <div class="page active" id="welcomePage">
        <div class="welcome-content">
            <div class="glitch-title">
                <span class="highlight">SAMARTH</span>
            </div>
            <div style="font-size: clamp(0.6rem, 1.5vw, 0.9rem); color: #003311; letter-spacing: 8px; margin-bottom: 4px;">
                PHONE TRACER
            </div>
            <div class="subtitle">⚡ Turn Numbers Into Information ⚡</div>

            <div class="feature-box">
                <div class="content">
                    <div class="feature-item">
                        <span class="icon">📡</span>
                        <span>Real-time Phone Intelligence</span>
                    </div>
                    <div class="feature-item">
                        <span class="icon">🔒</span>
                        <span>Secure & Anonymous Lookup</span>
                    </div>
                    <div class="feature-item">
                        <span class="icon">🇮🇳</span>
                        <span>India Number Database</span>
                    </div>
                    <div class="feature-item">
                        <span class="icon">⚡</span>
                        <span>Instant Results</span>
                    </div>
                </div>
            </div>

            <button class="enter-btn" id="enterBtn">
                ⚡ ENTER THE MATRIX
            </button>

            <div style="margin-top: 16px; font-size: 0.5rem; color: #001a0a; letter-spacing: 2px;">
                v3.0 • For Educational Use Only
            </div>
        </div>
    </div>

    <!-- Booting Page -->
    <div class="page hidden" id="bootingPage">
        <div class="boot-container">
            <div class="boot-title">⟳ INITIALIZING SYSTEM...</div>
            <div class="boot-percent" id="bootPercent">0%</div>
            <div class="boot-progress">
                <div class="boot-progress-bar" id="bootProgressBar"></div>
            </div>
            <div class="boot-log" id="bootLog">
                <div class="log-line"><span class="timestamp">[00:00]</span> <span class="status">⟳ Booting Samarth OS...</span></div>
            </div>
        </div>
    </div>

    <!-- Main Page -->
    <div class="page hidden" id="mainPage">
        <div class="main-container">

            <div class="main-header">
                <div class="brand">
                    📡 SAMARTH
                    <span class="badge">PRO</span>
                </div>
                <div class="status-dot">
                    <span class="dot"></span>
                    <span id="liveStatus">Online</span>
                </div>
            </div>

            <div class="input-section">
                <div class="input-row">
                    <input type="tel" id="phoneInput" 
                           placeholder="Enter 10-digit number" 
                           maxlength="15"
                           inputmode="numeric"
                           pattern="[0-9]*"
                           autocomplete="tel">
                    <button id="lookupBtn">🔍</button>
                </div>
            </div>

            <div class="quick-actions">
                <button data-number="9876543210">📌 Sample</button>
                <button data-number="1234567890">🧪 Test</button>
                <button id="clearBtn">🗑️ Clear</button>
                <button id="copyBtn">📋 Copy</button>
                <button id="exportBtn">📤 Export</button>
            </div>

            <div class="status-msg" id="statusMsg">▶ Ready — enter a number to begin</div>

            <div class="result-box" id="resultBox">
                <div class="empty">
                    <span class="icon">⚡</span>
                    Enter a number and click 🔍<br>
                    <span style="font-size:0.55rem; color:#002211;">For legitimate use only</span>
                </div>
            </div>

            <div class="main-footer">
                <a href="#" id="clearLink">Clear</a>
                <a href="#" id="helpLink">❓ Help</a>
                <span style="color:#001a0a;">|</span>
                <span style="color:#001a0a;">⚠️ Use responsibly</span>
            </div>

        </div>
    </div>

    <audio id="bgMusic" loop preload="auto" style="display:none;">
        <source src="/download/neww.mp3" type="audio/mpeg">
    </audio>

    <script>
        (function() {
            'use strict';

            const welcomePage = document.getElementById('welcomePage');
            const bootingPage = document.getElementById('bootingPage');
            const mainPage = document.getElementById('mainPage');
            const enterBtn = document.getElementById('enterBtn');
            const exitBootBtn = document.getElementById('exitBootBtn');
            const bootLog = document.getElementById('bootLog');
            const bootPercent = document.getElementById('bootPercent');
            const bootProgressBar = document.getElementById('bootProgressBar');
            const bgMusic = document.getElementById('bgMusic');

            const phoneInput = document.getElementById('phoneInput');
            const lookupBtn = document.getElementById('lookupBtn');
            const resultBox = document.getElementById('resultBox');
            const statusMsg = document.getElementById('statusMsg');
            const liveStatus = document.getElementById('liveStatus');
            const toast = document.getElementById('toast');

            let isLookingUp = false;
            let currentData = null;
            let toastTimer = null;
            let bootComplete = false;
            let bootInterval = null;
            let isBooting = false;

            function showToast(msg, type) {
                if (toastTimer) {
                    clearTimeout(toastTimer);
                    toast.classList.remove('show', 'error', 'success');
                }
                toast.textContent = msg;
                toast.className = 'toast';
                if (type === 'error') toast.classList.add('error');
                else if (type === 'success') toast.classList.add('success');
                void toast.offsetWidth;
                toast.classList.add('show');
                toastTimer = setTimeout(() => {
                    toast.classList.remove('show');
                    toastTimer = null;
                }, 3000);
            }

            function showPage(pageId) {
                document.querySelectorAll('.page').forEach(p => {
                    p.classList.remove('active', 'hidden');
                    p.classList.add('hidden');
                });
                const page = document.getElementById(pageId);
                page.classList.remove('hidden');
                void page.offsetWidth;
                page.classList.add('active');
            }

            const bootMessages = [
                { p: 5, msg: '⟳ Loading kernel modules...' },
                { p: 10, msg: '⟳ Initializing network stack...' },
                { p: 15, msg: '⟳ Connecting to secure database...' },
                { p: 22, msg: '⟳ Verifying encryption protocols...' },
                { p: 28, msg: '⟳ Loading user interface...' },
                { p: 35, msg: '⟳ Establishing secure channel...' },
                { p: 42, msg: '⟳ Loading phone number database...' },
                { p: 50, msg: '⟳ Initializing AI models...' },
                { p: 58, msg: '⟳ Setting up real-time tracking...' },
                { p: 65, msg: '⟳ Loading regional data (IN)...' },
                { p: 72, msg: '⟳ Configuring security layers...' },
                { p: 80, msg: '⟳ Starting main services...' },
                { p: 88, msg: '⟳ Finalizing system boot...' },
                { p: 95, msg: '⟳ All systems operational...' },
                { p: 100, msg: '✅ Boot complete. Welcome to SAMARTH.' },
            ];

            function addBootLog(msg, type) {
                const timestamp = new Date().toTimeString().slice(0, 8);
                const line = document.createElement('div');
                line.className = 'log-line';
                const statusClass = type === 'error' ? 'error' : type === 'warning' ? 'warning' : '';
                line.innerHTML = `
                    <span class="timestamp">[${timestamp}]</span>
                    <span class="status ${statusClass}">${msg}</span>
                `;
                bootLog.appendChild(line);
                bootLog.scrollTop = bootLog.scrollHeight;
            }

            function startBooting() {
                if (isBooting) return;
                isBooting = true;
                bootComplete = false;
                bootLog.innerHTML = '';
                exitBootBtn.classList.remove('hidden');

                showPage('bootingPage');

                try {
                    bgMusic.volume = 0.3;
                    bgMusic.loop = true;
                    bgMusic.play().catch(() => {});
                } catch(e) {}

                addBootLog('⟳ Booting Samarth OS...', '');
                addBootLog('⟳ Loading system components...', '');

                let progress = 0;
                let msgIndex = 0;

                bootInterval = setInterval(() => {
                    progress += Math.random() * 3 + 1;
                    if (progress > 100) progress = 100;

                    bootPercent.textContent = Math.floor(progress) + '%';
                    bootProgressBar.style.width = progress + '%';

                    while (msgIndex < bootMessages.length && bootMessages[msgIndex].p <= progress) {
                        const entry = bootMessages[msgIndex];
                        const isError = entry.msg.includes('error') || entry.msg.includes('fail');
                        const isWarning = entry.msg.includes('warning') || entry.msg.includes('slow');
                        addBootLog(entry.msg, isError ? 'error' : isWarning ? 'warning' : '');
                        msgIndex++;
                    }

                    if (progress >= 100) {
                        clearInterval(bootInterval);
                        bootInterval = null;
                        bootComplete = true;
                        isBooting = false;
                        exitBootBtn.classList.add('hidden');

                        if (msgIndex < bootMessages.length) {
                            addBootLog('✅ System ready. Welcome to SAMARTH.', '');
                        }

                        setTimeout(() => {
                            showPage('mainPage');
                            showToast('🚀 System ready!', 'success');
                            try { bgMusic.play(); } catch(e) {}
                        }, 1500);
                    }
                }, 200);

                setTimeout(() => {
                    if (!bootComplete) {
                        clearInterval(bootInterval);
                        bootInterval = null;
                        bootPercent.textContent = '100%';
                        bootProgressBar.style.width = '100%';
                        addBootLog('⚠️ Force complete (timeout)', 'warning');
                        bootComplete = true;
                        isBooting = false;
                        exitBootBtn.classList.add('hidden');
                        setTimeout(() => {
                            showPage('mainPage');
                            showToast('🚀 System ready!', 'success');
                            try { bgMusic.play(); } catch(e) {}
                        }, 1000);
                    }
                }, 25000);
            }

            function skipBoot() {
                if (bootInterval) {
                    clearInterval(bootInterval);
                    bootInterval = null;
                }
                isBooting = false;
                bootComplete = true;
                exitBootBtn.classList.add('hidden');
                bootPercent.textContent = '100%';
                bootProgressBar.style.width = '100%';
                addBootLog('⏩ Boot skipped by user', 'warning');
                addBootLog('✅ System ready.', '');
                setTimeout(() => {
                    showPage('mainPage');
                    showToast('⏩ Boot skipped', 'success');
                    try { bgMusic.play(); } catch(e) {}
                }, 500);
            }

            function cleanPhone(raw) {
                return raw.replace(/[^0-9]/g, '');
            }

            function validateIndianPhone(phone) {
                const p = cleanPhone(phone);
                return /^[6-9]\d{9}$/.test(p) || /^91[6-9]\d{9}$/.test(p);
            }

            // REAL API LOOKUP - NO MOCK DATA
            async function performLookup() {
                if (isLookingUp) return;

                const raw = phoneInput.value.trim();
                const clean = cleanPhone(raw);

                if (!clean || clean.length < 10) {
                    setStatus('❌ Enter at least 10 digits', 'error');
                    showToast('Please enter a valid number', 'error');
                    phoneInput.focus();
                    return;
                }

                if (clean.length > 15) {
                    setStatus('❌ Number too long', 'error');
                    showToast('Maximum 15 digits', 'error');
                    phoneInput.focus();
                    return;
                }

                if (!validateIndianPhone(clean) && clean.length === 10) {
                    setStatus('⚠️ Number must start with 6,7,8,9', 'error');
                    showToast('Invalid Indian number format', 'error');
                    phoneInput.focus();
                    return;
                }

                let phoneToSend = clean;
                if (phoneToSend.length === 10) {
                    phoneToSend = '+91' + phoneToSend;
                } else if (phoneToSend.length === 12 && phoneToSend.startsWith('91')) {
                    phoneToSend = '+' + phoneToSend;
                } else if (!phoneToSend.startsWith('+')) {
                    phoneToSend = '+' + phoneToSend;
                }

                isLookingUp = true;
                lookupBtn.disabled = true;
                lookupBtn.textContent = '⏳';
                setStatus('⏳ Looking up...', '');
                liveStatus.textContent = 'Scanning...';
                resultBox.innerHTML = `
                    <div class="loading">
                        <span class="spinner">⚡</span>
                        Querying databases...
                        <br><span style="font-size:0.55rem;color:#003311;">This may take a few seconds</span>
                    </div>
                `;

                try {
                    const response = await fetch('/api/lookup', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'Accept': 'application/json'
                        },
                        body: 'phone=' + encodeURIComponent(phoneToSend)
                    });

                    const data = await response.json();

                    if (!response.ok) {
                        throw new Error(data.error || 'Lookup failed');
                    }

                    renderResults(data);
                    liveStatus.textContent = 'Ready';
                    showToast('✅ Lookup complete!', 'success');

                } catch (err) {
                    console.error('Lookup error:', err);
                    resultBox.innerHTML = `
                        <div class="error-msg">
                            <span class="icon">🚫</span>
                            ${err.message || 'Network error. Please try again.'}
                            <br><span style="font-size:0.55rem;color:#003311;">Check connection and try again</span>
                        </div>
                    `;
                    setStatus('❌ Error: ' + (err.message || 'Network failure'), 'error');
                    showToast('Error: ' + (err.message || 'Network failure'), 'error');
                    liveStatus.textContent = 'Error';
                } finally {
                    isLookingUp = false;
                    lookupBtn.disabled = false;
                    lookupBtn.textContent = '🔍';
                }
            }

            function renderResults(data) {
                if (!data || data.error) {
                    const errMsg = data?.error || 'No data returned.';
                    resultBox.innerHTML = `
                        <div class="error-msg">
                            <span class="icon">⚠️</span>
                            ${errMsg}
                        </div>
                    `;
                    setStatus('❌ ' + errMsg, 'error');
                    return;
                }

                const entries = Object.entries(data).filter(([k, v]) =>
                    v && v !== 'N/A' && v !== '' && k !== 'Number'
                );

                if (entries.length === 0) {
                    resultBox.innerHTML = `
                        <div class="empty">
                            <span class="icon">🔍</span>
                            No useful data found for this number.
                        </div>
                    `;
                    setStatus('❌ No data found', 'error');
                    return;
                }

                let html = '';
                if (data.Number) {
                    html += `
                        <div class="field field-highlight">
                            <span class="label">📱 Number</span>
                            <span class="value">${data.Number}</span>
                        </div>
                    `;
                }

                for (const [key, value] of entries) {
                    if (key === 'Number') continue;
                    const isNA = value === 'N/A' || value === '';
                    html += `
                        <div class="field">
                            <span class="label">${key}</span>
                            <span class="value ${isNA ? 'na' : ''}">${isNA ? '—' : value}</span>
                        </div>
                    `;
                }

                resultBox.innerHTML = html;
                setStatus(`✅ Found ${entries.length} fields`, 'success');
                currentData = data;
            }

            function setStatus(msg, type) {
                statusMsg.textContent = msg;
                statusMsg.className = 'status-msg';
                if (type) statusMsg.classList.add(type);
            }

            function clearAll() {
                phoneInput.value = '';
                resultBox.innerHTML = `
                    <div class="empty">
                        <span class="icon">⚡</span>
                        Enter a number and click 🔍<br>
                        <span style="font-size:0.55rem; color:#002211;">For legitimate use only</span>
                    </div>
                `;
                setStatus('▶ Ready — enter a number to begin', '');
                currentData = null;
                phoneInput.focus();
                showToast('🗑️ Cleared', 'success');
            }

            function copyResults() {
                if (!currentData) {
                    showToast('No data to copy', 'error');
                    return;
                }
                const entries = Object.entries(currentData)
                    .filter(([k, v]) => v && v !== 'N/A' && v !== '')
                    .map(([k, v]) => `${k}: ${v}`)
                    .join('\n');

                if (!entries) {
                    showToast('No data to copy', 'error');
                    return;
                }

                navigator.clipboard.writeText(entries).then(() => {
                    showToast('📋 Copied!', 'success');
                }).catch(() => {
                    const textarea = document.createElement('textarea');
                    textarea.value = entries;
                    document.body.appendChild(textarea);
                    textarea.select();
                    document.execCommand('copy');
                    document.body.removeChild(textarea);
                    showToast('📋 Copied!', 'success');
                });
            }

            function exportData() {
                if (!currentData) {
                    showToast('No data to export', 'error');
                    return;
                }
                try {
                    const json = JSON.stringify(currentData, null, 2);
                    const blob = new Blob([json], { type: 'application/json' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `samarth_lookup_${Date.now()}.json`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                    showToast('📤 Exported!', 'success');
                } catch (e) {
                    showToast('Export failed', 'error');
                }
            }

            function setSampleNumber(num) {
                phoneInput.value = num;
                phoneInput.focus();
                setTimeout(() => performLookup(), 400);
            }

            // EVENT LISTENERS
            enterBtn.addEventListener('click', startBooting);
            exitBootBtn.addEventListener('click', skipBoot);

            lookupBtn.addEventListener('click', performLookup);

            phoneInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    performLookup();
                }
            });

            phoneInput.addEventListener('input', () => {
                const val = phoneInput.value;
                const cleaned = cleanPhone(val);
                if (cleaned !== val) {
                    phoneInput.value = cleaned;
                }
            });

            document.querySelectorAll('[data-number]').forEach(btn => {
                btn.addEventListener('click', () => {
                    setSampleNumber(btn.dataset.number);
                });
            });

            document.getElementById('clearBtn').addEventListener('click', clearAll);
            document.getElementById('clearLink').addEventListener('click', (e) => {
                e.preventDefault();
                clearAll();
            });

            document.getElementById('copyBtn').addEventListener('click', copyResults);
            document.getElementById('exportBtn').addEventListener('click', exportData);

            document.getElementById('helpLink').addEventListener('click', (e) => {
                e.preventDefault();
                showToast('🔍 Enter any Indian 10-digit number to lookup public info. Use responsibly.', 'success');
            });

            function enableAudio() {
                try {
                    bgMusic.volume = 0.3;
                    bgMusic.loop = true;
                    bgMusic.play().catch(() => {});
                } catch(e) {}
            }

            document.addEventListener('click', enableAudio, { once: false });
            document.addEventListener('touchstart', enableAudio, { once: false });

            window.addEventListener('online', () => {
                liveStatus.textContent = 'Online';
                showToast('📶 Back online', 'success');
            });
            window.addEventListener('offline', () => {
                liveStatus.textContent = 'Offline';
                showToast('📶 No connection', 'error');
            });

            console.log('🔍 SAMARTH Phone Tracker Pro v3.0 - Vercel Ready');
            console.log('🎵 Audio file: /download/neww.mp3');

            showPage('welcomePage');

            window.__SAMARTH = {
                startBoot: startBooting,
                skipBoot: skipBoot,
                lookup: performLookup,
                clear: clearAll,
                copy: copyResults,
                export: exportData,
                state: () => currentData
            };

        })();
    </script>

</body>
</html>
'''

# ============================================================
# FLASK ROUTES (VERCEL COMPATIBLE)
# ============================================================

@app.route('/')
def index():
    """Serve the main page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/lookup', methods=['POST', 'GET'])
def api_lookup():
    """
    Real phone number lookup API endpoint
    NO MOCK DATA - uses real API calls only
    """
    # Rate limiting
    client_ip = request.remote_addr or '127.0.0.1'
    if is_rate_limited(client_ip):
        return jsonify({"error": "Rate limit exceeded. Please wait a moment."}), 429

    # Get phone number
    if request.method == 'GET':
        phone = request.args.get('phone', '').strip()
    else:
        phone = request.form.get('phone', '').strip()

    if not phone:
        return jsonify({"error": "Phone number is required."}), 400

    # Clean and validate
    cleaned = clean_phone(phone)
    
    if not cleaned:
        return jsonify({"error": "Invalid phone number format."}), 400
    
    if len(cleaned) < 10:
        return jsonify({"error": "Phone number must have at least 10 digits."}), 400

    if not validate_phone(cleaned):
        return jsonify({"error": "Invalid Indian phone number. Must start with 6,7,8,9 and be 10 digits."}), 400

    # Format for API
    formatted_phone = format_phone_for_api(cleaned)

    # Perform real lookup (NO MOCK DATA)
    data, status_code = lookup_phone_number(formatted_phone)
    
    if status_code == 200:
        return jsonify(data)
    else:
        return jsonify(data), status_code

@app.route('/api/health')
def health():
    """Health check endpoint for Vercel"""
    return jsonify({
        "status": "online",
        "version": "3.0",
        "service": "SAMARTH Phone Tracker Pro",
        "environment": "vercel",
        "features": ["real_lookup", "rate_limiting", "no_mock_data"]
    })

# ============================================================
# VERCEL SERVERLESS HANDLER
# ============================================================

# This is the entry point for Vercel
app.debug = False

# ============================================================
# LOCAL DEVELOPMENT SERVER
# ============================================================

if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║   ███████  █████  ███    ███  █████  ██████  ████████   ║
    ║   ██      ██   ██ ████  ████ ██   ██ ██   ██    ██      ║
    ║   ███████ ███████ ██ ████ ██ ███████ ██████     ██      ║
    ║        ██ ██   ██ ██  ██  ██ ██   ██ ██   ██    ██      ║
    ║   ███████ ██   ██ ██      ██ ██   ██ ██   ██    ██      ║
    ║                                                          ║
    ║        PHONE TRACKER PRO - VERCEL READY                 ║
    ║                                                          ║
    ║   🚀 Server: http://127.0.0.1:5000                      ║
    ║   📡 Real API calls - NO mock data                      ║
    ║   🔒 Rate limited: 10 requests/minute                   ║
    ║   🎵 Audio: /download/neww.mp3                         ║
    ║                                                          ║
    ║   ⚠️  For educational/legitimate use only              ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    app.run(debug=False, host='0.0.0.0', port=5000)
