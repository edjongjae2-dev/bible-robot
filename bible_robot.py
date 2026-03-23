import requests
from bs4 import BeautifulSoup
import os

# 🔐 금고 설정
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('TELEGRAM_CHAT_ID')

def get_su_word():
    # 1. 매일성경 (한국어) 가져오기
    url = "https://sum.su.or.kr:8888/bible/today"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 제목 찾기
        title_tag = soup.select_one('.bible_text')
        title = title_tag.text.strip() if title_tag else "오늘의 묵상"
        
        # 본문 말씀 찾기 (잘리지 않게 전체 다 가져옵니다)
        verses = soup.select('.body_list li')
        verse_text = ""
        for v in verses: 
            num = v.select_one('.num').text if v.select_one('.num') else ""
            info = v.select_one('.info').text if v.select_one('.info') else ""
            verse_text += f"{num} {info}\n\n"
            
        return f"🌿 [오늘의 매일성경]\n\n📖 {title}\n\n{verse_text}🔗 전문 묵상하기: {url}"
    except Exception as e:
        return f"매일성경 배달 에러: {str(e)}"

def get_utmost_english():
    # 2. My Utmost for His Highest (영어 원문) 가져오기
    url = "https://utmost.org/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 제목 찾기
        title_tag = soup.find('h1')
        title = title_tag.text.strip() if title_tag else "Today's Devotional"
        
        # 오늘의 성경 구절 찾기 (보통 blockquote나 첫 번째 문단에 있습니다)
        verse_tag = soup.select_one('.entry-content blockquote') or soup.select_one('.entry-content p')
        verse = verse_tag.text.strip() if verse_tag else "Please click the link to read the verse."
        
        return f"🌟 [My Utmost for His Highest]\n\n📖 {title}\n\n📍 {verse}\n\n🔗 Read more: {url}"
    except Exception as e:
        return f"영어 최고봉 배달 에러: {str(e)}"

def send_telegram(message):
    # 텔레그램 메시지 전송 (긴 글도 안전하게 전송되도록 처리)
    safe_message = message[:4000]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": safe_message}
    requests.post(url, json=payload)

if __name__ == "__main__":
    # 첫 번째 배달: 매일성경 
    su_msg = get_su_word()
    send_telegram(su_msg)
    
    # 두 번째 배달: 영어 주님은 나의 최고봉
    utmost_msg = get_utmost_english()
    send_telegram(utmost_msg)
