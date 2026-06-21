from http.server import BaseHTTPRequestHandler
import json
import requests
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests for phone number lookup"""
        try:
            # Parse query parameters
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            
            # Extract parameters
            query_type = query_params.get('type', [''])[0]
            api_key = query_params.get('key', [''])[0]
            phone_query = query_params.get('query', [''])[0]
            
            # Validate inputs
            if not query_type or not phone_query:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Missing parameters'}).encode())
                return
            
            # Clean phone number
            clean_num = ''.join(filter(str.isdigit, phone_query))
            
            if len(clean_num) < 10:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Invalid phone number length'}).encode())
                return
            
            # Mock response data (replace with actual API call as needed)
            response_data = {
                'results': {
                    'name': 'User Profile Data',
                    'fname': 'First Name',
                    'address': 'City! State! Country',
                    'circle': 'Mobile Carrier'
                }
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
