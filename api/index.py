from http.server import BaseHTTPRequestHandler
import cloudscraper
import json
import logging

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        scraper = cloudscraper.create_scraper()
        url = "https://gamma-api.polymarket.com/events?limit=50&active=true&order=volume24hr&dir=desc"
        
        try:
            # Запрос к API Polymarket
            response = scraper.get(url, timeout=15)
            
            if response.status_code != 200:
                self.send_response(response.status_code)
                self.end_headers()
                self.wfile.write(f"Polymarket API Error: {response.status_code}".encode())
                return

            events = response.json()
            bubbles = []
            
            for ev in events:
                v_raw = ev.get('volume24hr') or ev.get('volume') or 0
                slug = ev.get('slug')
                if slug:
                    bubbles.append({
                        "label": ev.get('title', 'Market'),
                        "pnl": float(v_raw),
                        "link": f"https://polymarket.com/event/{slug}"
                    })

            # Успешная отправка данных
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(bubbles).encode('utf-8'))

        except Exception as e:
            # Логируем ошибку для Vercel Dashboard
            logging.error(f"