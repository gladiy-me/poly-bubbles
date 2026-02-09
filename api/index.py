from http.server import BaseHTTPRequestHandler
import cloudscraper
import json
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Отправляем заголовки сразу
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        scraper = cloudscraper.create_scraper()
        # Добавляем параметр closed=false, чтобы не брать завершенные рынки
        url = "https://gamma-api.polymarket.com/events?limit=100&active=true&closed=false&order=volume24hr&dir=desc"
        
        try:
            response = scraper.get(url, timeout=15)
            if response.status_code != 200:
                self.wfile.write(json.dumps([]).encode())
                return

            events = response.json()
            bubbles = []
            now = datetime.now()
            
            for ev in events:
                # 1. Проверяем наличие торгового объема (чтобы не было пустых шаров)
                v_raw = ev.get('volume24hr') or ev.get('volume') or 0
                if float(v_raw) <= 0:
                    continue

                # 2. Проверяем дату окончания (endDate)
                # Если дата уже в прошлом, пропускаем это событие
                end_date_str = ev.get('endDate')
                if end_date_str:
                    try:
                        # Парсим дату формата 2024-05-20T00:00:00Z
                        end_date = datetime.strptime(end_date_str.split('T')[0], '%Y-%m-%d')
                        if end_date < now:
                            continue
                    except:
                        pass # Если дата битая, идем дальше

                slug = ev.get('slug')
                if slug:
                    bubbles.append({
                        "label": ev.get('title', 'Market'),
                        "pnl": float(v_raw),
                        "link": f"https://polymarket.com/event/{slug}"
                    })

            # Сортируем и берем топ-50 самых свежих и объемных
            final_bubbles = bubbles[:50]
            self.wfile.write(json.dumps(final_bubbles).encode('utf-8'))
            
        except Exception as e:
            err = [{"label": "API Error", "pnl": 1000, "link": "#", "error": str(e)}]
            self.wfile.write(json.dumps(err).encode('utf-8'))