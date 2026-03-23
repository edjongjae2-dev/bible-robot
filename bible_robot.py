import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime

# 🔐 금고 설정
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('TELEGRAM_CHAT_ID')

def get_utmost_word():
    now = datetime.now()
    # 📅 사이트 주소 형식: march-23 (영문달-날짜)
    month_en = now.strftime("%B").lower() # March -> march
    day = now.day
    
    # 🔍 시도해볼 주소 (가장 정확한 영문 형식)
    url = f"https://www.utmost.co.kr/{month_en}-{day}/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 제목 찾기
            title_tag = soup.find('h1')
            title = title_tag.text.strip() if title_tag else "오늘의 묵상"
            
            # 본문 말씀 찾기
            verse = ""
            # 사이트 구조상 .bible-verse 또는 blockquote 또는 첫 번째 p 태그
            verse_tag = soup.select_one('.bible-verse') or soup.select_one('blockquote') or soup.select_one('.entry-content p')
            if verse_tag:
                verse = verse_tag.text.strip()
            
            return f"🌟 [주님은 나의 최고봉]\n\n📖 제목: {title}\n\n📍 말씀: {verse}\n\n🔗 원문: {url}"
        else:
            return f"오늘의 말씀 페이지를 찾지 못했습니다. (에러코드: {res.status_code})\n주소: {url}"
    except Exception as e:
        return f"연결 중 오류가 발생했습니다: {str(e)}"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    requests.post(url, json=payload)

if __name__ == "__main__":
    content = get_utmost_word()
    send_telegram(content)
