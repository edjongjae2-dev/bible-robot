import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime

# 🔐 금고에서 키 가져오기
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('TELEGRAM_CHAT_ID')

def get_utmost_word():
    # 오늘 날짜 (예: 0323)를 주소에 넣습니다.
    today = datetime.now().strftime("%m%d")
    url = f"https://www.utmost.co.kr/daily-devotional/{today}/"
    
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 제목과 말씀 가져오기
        title = soup.select_one('h1').text.strip()
        verse_element = soup.select_one('blockquote')
        verse = verse_element.text.strip() if verse_element else "본문 말씀은 링크를 확인해주세요."
        
        return f"☀️ [주님은 나의 최고봉]\n\n📖 제목: {title}\n\n📍 말씀: {verse}\n\n🔗 더 읽기: {url}"
    except:
        return "오늘의 말씀을 가져오지 못했습니다. 😥"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    requests.post(url, json=payload)

if __name__ == "__main__":
    content = get_utmost_word()
    send_telegram(content)
