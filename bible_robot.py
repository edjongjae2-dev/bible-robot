import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime

# 🔐 금고에서 키 가져오기
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('TELEGRAM_CHAT_ID')

def get_utmost_word():
    # 📅 오늘 날짜 (예: 3월 23일 -> 3-23)
    # 사이트 주소 형식에 맞춰 월-일로 변경합니다.
    today_str = datetime.now().strftime("%m-%d").replace("0", "") # 03-23을 3-23으로 변경 시도
    
    # 여러 가지 주소 패턴을 시도해봅니다 (사이트 업데이트 대비)
    urls = [
        f"https://www.utmost.co.kr/daily-devotional/{datetime.now().strftime('%m%d')}/",
        f"https://www.utmost.co.kr/{datetime.now().strftime('%m-%d')}/"
    ]
    
    for url in urls:
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                
                # 제목 가져오기
                title = soup.find('h1').text.strip() if soup.find('h1') else "오늘의 묵상"
                
                # 말씀 본문 가져오기 (클래스 이름 위주로 찾기)
                verse_element = soup.select_one('.bible-verse') or soup.select_one('blockquote')
                verse = verse_element.text.strip() if verse_element else "본문 내용은 링크를 통해 확인해 주세요."
                
                return f"🌟 [주님은 나의 최고봉]\n\n📖 제목: {title}\n\n📍 말씀: {verse}\n\n🔗 더 읽기: {url}"
        except:
            continue
            
    return "오늘의 말씀 주소를 찾지 못했습니다. 😥 링크 형식을 확인해볼게요."

def send_telegram(message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    requests.post(url, json=payload)

if __name__ == "__main__":
    content = get_utmost_word()
    send_telegram(content)
