from http.server import BaseHTTPRequestHandler
import cloudscraper
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1. Сразу отправляем заголовки, чтобы браузер понимал: это JSON-текст
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        try:
            scraper = cloudscraper.create_scraper()
            url = "https://gamma-api.polymarket.com/events?limit=50&active=true&order=volume24hr&dir=desc"
            
            response = scraper.get(url, timeout=10)
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
            
            # 2. Отправляем сами данные
            self.wfile.write(json.dumps(bubbles).encode('utf-8'))
            
        except Exception as e:
            # Если ошибка — отправляем её текстом, а не крашим сервер
            error_data = [{"label": "Error", "pnl": 1000, "link": "#", "error": str(e)}]
            self.wfile.write(json.dumps(error_data).encode('utf-8'))