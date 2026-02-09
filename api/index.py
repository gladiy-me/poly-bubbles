from http.server import BaseHTTPRequestHandler
import cloudscraper
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        scraper = cloudscraper.create_scraper()
        url = "https://gamma-api.polymarket.com/events?limit=50&active=true&order=volume24hr&dir=desc"
        
        try:
            response = scraper.get(url)
            if response.status_code != 200:
                raise Exception(f"API Error: {response.status_code}")
                
            events = response.json()
            bubbles = []
            
            for ev in events:
                # Берем объем для размера шара
                v_raw = float(ev.get('volume24hr', 0) or 0)
                slug = ev.get('slug')
                if slug:
                    bubbles.append({
                        "label": ev.get('title', 'Market'),
                        "pnl": v_raw,
                        "link": f"https://polymarket.com/event/{slug}"
                    })

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(bubbles).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode())