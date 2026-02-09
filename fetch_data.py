import cloudscraper
import json
import time
import os

# Используем cloudscraper для обхода базовых защит API
scraper = cloudscraper.create_scraper()

def get_data():
    # Запрашиваем 50 самых активных событий по объему за 24 часа
    url = "https://gamma-api.polymarket.com/events?limit=50&active=true&order=volume24hr&dir=desc"
    print(f"[{time.strftime('%H:%M:%S')}] Сбор активных рынков из Gamma API...")
    
    try:
        headers = {'Referer': 'https://polymarket.com/'}
        response = scraper.get(url, headers=headers)
        
        if response.status_code == 200:
            events = response.json()
            bubbles = []
            
            for ev in events:
                v_raw = ev.get('volume24hr') or ev.get('volume') or 0
                slug = ev.get('slug')
                title = ev.get('title', 'Market')
                
                # Чистим числовое значение объема от символов $ и запятых
                try:
                    v_str = str(v_raw).replace('$', '').replace(',', '').split('.')[0]
                    v_int = int(v_str) if v_str and v_str != 'None' else 0
                except:
                    v_int = 0

                if slug:
                    bubbles.append({
                        "label": title,
                        "pnl": v_int if v_int > 0 else 1000, # Минимальный размер для новых рынков
                        "link": f"https://polymarket.com/event/{slug}"
                    })
            
            # Безопасная запись: пишем во временный файл, затем заменяем основной
            temp_file = "data_temp.json"
            with open(temp_file, "w", encoding='utf-8') as f:
                json.dump(bubbles, f, ensure_ascii=False)
            
            if os.path.exists("data.json"):
                os.remove("data.json")
            os.rename(temp_file, "data.json")
            print(f"УСПЕХ! Обновлено {len(bubbles)} рынков.")
        else:
            print(f"Ошибка API: {response.status_code}")
    except Exception as e:
        print(f"Ошибка при сборе данных: {e}")

if __name__ == "__main__":
    while True:
        get_data()
        time.sleep(30) # Интервал обновления данных — 30 секунд