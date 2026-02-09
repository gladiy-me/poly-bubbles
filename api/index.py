from http.server import BaseHTTPRequestHandler
import cloudscraper
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        scraper = cloudscraper.create_scraper()
        # Добавляем таймаут, чтобы функция не висела вечно
        url = "https://gamma-api.polymarket.com/events?limit=50&active=true&order=volume24hr&dir=desc"
        
        try:
            response = scraper.get(url, timeout=10)
            
            if response.status_code != 200:
                self.send_response(response.status_code)
                self.end_headers()
                self.wfile.write(b"Error: API returned non-200 status")
                return

            events = response.json()
            bubbles = []
            
            for ev in events:
                # Безопасное получение объема
                v_raw = ev.get('volume24hr') or ev.get('volume') or 0
                slug = ev.get('slug')
                
                if slug:
                    bubbles.append({
                        "label": ev.get('title', 'Market'),
                        "pnl": float(v_raw),
                        "link": f"https://polymarket.com/event/{slug}"
                    })

            # Успешный ответ
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(bubbles).encode('utf-8'))

        except Exception as e:
            # Если что-то пошло не так, выводим ошибку текстом
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Server Error: {str(e)}".encode('utf-8'))