import requests
from bs4 import BeautifulSoup
import os
from deep_translator import GoogleTranslator

# 🔐 금고 설정
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('TELEGRAM_CHAT_ID')

def get_translated_utmost():
    # 공식 영문 사이트 접속 (자동으로 오늘 날짜 말씀으로 이동됨)
    url = "https://utmost.org/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 1. 영문 제목 찾기
        title_tag = soup.find('h1')
        en_title = title_tag.text.strip() if title_tag else "Today's Devotional"
        
        # 2. 영문 본문 찾기 (보통 entry-content 안의 p 태그들에 있습니다)
        content_div = soup.select_one('.entry-content')
        en_paragraphs = []
        if content_div:
            # 말씀이 너무 길면 텔레그램 에러가 나므로 핵심 3문단만 가져옵니다.
            for p in content_div.find_all('p')[:3]:
                text = p.text.strip()
                if text:
                    en_paragraphs.append(text)
                    
        en_content = "\n\n".join(en_paragraphs)
        if not en_content:
            en_content = "본문을 가져오지 못했습니다. 링크를 확인해주세요."

        # 3. 구글 번역기 가동! (영어 -> 한국어)
        translator = GoogleTranslator(source='en', target='ko')
        
        ko_title = translator.translate(en_title)
        ko_content = translator.translate(en_content)
        
        # 4. 텔레그램 발송용 메시지 예쁘게 조립하기
        msg = f"🌟 [주님은 나의 최고봉 / My Utmost for His Highest]\n\n"
        msg += f"🇰🇷 제목: {ko_title}\n"
        msg += f"🇺🇸 Title: {en_title}\n\n"
        msg += f"───────────────\n"
        msg += f"📖 [한국어 묵상]\n{ko_content}\n\n"
        msg += f"───────────────\n"
        msg += f"📖 [English Original]\n{en_content}\n\n"
        msg += f"🔗 원문 이어서 읽기: {res.url}"
        
        return msg
        
    except Exception as e:
        return f"번역 배달 중 에러가 발생했습니다: {str(e)}"

def send_telegram_text(message):
    # 텔레그램 글자 수 제한(4096자) 안전장치
    safe_message = message[:4000]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": safe_message}
    requests.post(url, json=payload)

if __name__ == "__main__":
    # 번역된 말씀 긁어와서 텔레그램으로 전송!
    word_text = get_translated_utmost()
    send_telegram_text(word_text)
