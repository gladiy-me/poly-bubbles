from http.server import BaseHTTPRequestHandler
import cloudscraper
import json
from datetime import datetime
# Добавляем инструменты для чтения параметров URL
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Отправляем заголовки сразу
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # --- НОВАЯ ЛОГИКА ТАЙМФРЕЙМОВ ---
        # Извлекаем параметр 't' из запроса (например, /api?t=7d)
        query = parse_qs(urlparse(self.path).query)
        timeframe = query.get('t', ['24h'])[0]
        
        # Определяем поле для сортировки и данных
        sort_field = "volume24hr"
        if timeframe == "7d":
            sort_field = "volume7d"
        elif timeframe == "all":
            sort_field = "volume"
        # -------------------------------

        scraper = cloudscraper.create_scraper()
        # Динамически подставляем sort_field в URL
        url = f"https://gamma-api.polymarket.com/events?limit=100&active=true&closed=false&order={sort_field}&dir=desc"
        
        try:
            response = scraper.get(url, timeout=15)
            if response.status_code != 200:
                self.wfile.write(json.dumps([]).encode())
                return

            events = response.json()
            bubbles = []
            now = datetime.now()
            
            for ev in events:
                # Берем данные именно из того поля, которое запросил пользователь
                v_raw = ev.get(sort_field) or 0
                if float(v_raw) <= 0:
                    continue

                end_date_str = ev.get('endDate')
                if end_date_str:
                    try:
                        end_date = datetime.strptime(end_date_str.split('T')[0], '%Y-%m-%d')
                        if end_date < now:
                            continue
                    except:
                        pass

                slug = ev.get('slug')
                if slug:
                    bubbles.append({
                        "label": ev.get('title', 'Market'),
                        "pnl": float(v_raw),
                        "link": f"https://polymarket.com/event/{slug}"
                    })

            # Оставляем топ-50 для красоты на экране
            final_bubbles = bubbles[:50]
            self.wfile.write(json.dumps(final_bubbles).encode('utf-8'))
            
        except Exception as e:
            err = [{"label": "API Error", "pnl": 1000, "link": "#", "error": str(e)}]
            self.wfile.write(json.dumps(err).encode('utf-8'))