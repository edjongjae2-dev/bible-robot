import requests
from bs4 import BeautifulSoup
import os
import xml.etree.ElementTree as ET
from deep_translator import GoogleTranslator

# 🔐 금고 설정
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('TELEGRAM_CHAT_ID')

def get_translated_utmost():
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        # 1. 사이트의 '비밀 통로(RSS)'에서 오늘 날짜의 진짜 주소 알아내기
        feed_url = "https://utmost.org/feed/"
        feed_res = requests.get(feed_url, headers=headers, timeout=15)
        root = ET.fromstring(feed_res.content)
        item = root.find('.//item') # 가장 최신 글 찾기
        
        en_title = item.find('title').text.strip()
        post_link = item.find('link').text.strip()
        
        # 2. 로봇이 진짜 주소로 '클릭'해서 들어가기
        page_res = requests.get(post_link, headers=headers, timeout=15)
        soup = BeautifulSoup(page_res.text, 'html.parser')
        
        # 3. 본문 텍스트 긁어오기
        content_div = soup.select_one('.entry-content')
        en_paragraphs = []
        if content_div:
            # 영어 문단들을 차곡차곡 모읍니다
            for p in content_div.find_all('p'):
                text = p.text.strip()
                if text:
                    en_paragraphs.append(text)
                    
        # 영어 본문 조립 (너무 길면 번역기가 힘들어하므로 핵심 4문단만)
        en_content = "\n\n".join(en_paragraphs[:4])
        if not en_content:
            en_content = "본문을 가져오지 못했습니다."

        # 4. 구글 번역기 가동! (영어 -> 한국어)
        translator = GoogleTranslator(source='en', target='ko')
        ko_title = translator.translate(en_title)
        ko_content = translator.translate(en_content)
        
        # 5. 텔레그램으로 보낼 편지 예쁘게 포장하기
        msg = f"🌟 [주님은 나의 최고봉 / My Utmost for His Highest]\n\n"
        msg += f"🇰🇷 제목: {ko_title}\n"
        msg += f"🇺🇸 Title: {en_title}\n\n"
        msg += f"───────────────\n"
        msg += f"📖 [한국어 묵상]\n{ko_content}\n\n"
        msg += f"───────────────\n"
        msg += f"📖 [English Original]\n{en_content}\n\n"
        msg += f"🔗 원문 전체 읽기: {post_link}"
        
        return msg
        
    except Exception as e:
        return f"번역 배달 중 에러가 발생했습니다: {str(e)}"

def send_telegram_text(message):
    safe_message = message[:4000]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": safe_message}
    requests.post(url, json=payload)

if __name__ == "__main__":
    word_text = get_translated_utmost()
    send_telegram_text(word_text)
