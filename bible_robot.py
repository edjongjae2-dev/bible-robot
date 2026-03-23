import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime

# 🔐 금고 설정
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('TELEGRAM_CHAT_ID')

def get_utmost_word():
    now = datetime.now()
    month = str(now.month)
    day = str(now.day)
    mmdd = now.strftime("%m%d")
    
    # 🔍 시도해볼 주소 후보 리스트 (가장 유력한 순서)
    urls = [
        f"https://www.utmost.co.kr/{month}-{day}/",  # 예: 3-23
        f"https://www.utmost.co.kr/daily-devotional/{mmdd}/", # 예: 0323
        f"https://www.utmost.co.kr/{mmdd}/" # 예: 0323 (단축형)
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    for url in urls:
        try:
            res = requests.get(url, headers=headers, timeout=15)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                
                # 제목 찾기 (보통 h1 태그)
                title_tag = soup.find('h1')
                title = title_tag.text.strip() if title_tag else "오늘의 묵상"
                
                # 본문(성경구절) 찾기 - 여러 패턴 대응
                verse = ""
                verse_tag = soup.select_one('.bible-verse') or soup.select_one('blockquote') or soup.select_one('.entry-content p')
                if verse_tag:
                    verse = verse_tag.text.strip()
                
                return f"🌟 [주님은 나의 최고봉]\n\n📖 제목: {title}\n\n📍 말씀: {verse}\n\n🔗 원문: {url}"
        except:
            continue
            
    return "오늘의 말씀 페이지를 찾지 못했습니다. 😥 잠시 후 다시 시도해 볼게요."

def send_telegram(message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    requests.post(url, json=payload)

if __name__ == "__main__":
    content = get_utmost_word()
    send_telegram(content)
