import requests
from bs4 import BeautifulSoup
import os
from deep_translator import GoogleTranslator

# 🔐 금고 설정
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('TELEGRAM_CHAT_ID')

def get_translated_utmost():
    # 1. 막히지 않았던 '정문(메인 주소)'으로 당당하게 들어갑니다.
    url = "https://utmost.org/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 2. 영문 제목 찾기 (유저님이 이미 성공하셨던 부분!)
        title_tag = soup.find('h1')
        en_title = title_tag.text.strip() if title_tag else "Today's Devotional"
        
        # 3. 영문 본문 찾기 (서랍 이름 안 따지고, 긴 글자만 골라내기)
        # 보통 본문은 article 태그나 main 태그 안에 있습니다.
        container = soup.find('article') or soup.find('main') or soup.body
        
        en_paragraphs = []
        if container:
            for p in container.find_all('p'):
                text = p.text.strip()
                # 메뉴나 버튼 글씨를 빼고, '진짜 문장(길이 30자 이상)'만 수집합니다.
                if len(text) > 30:
                    en_paragraphs.append(text)
                    
        # 번역기가 멈추지 않게 핵심 3~4문단만 챙깁니다.
        en_content = "\n\n".join(en_paragraphs[:4])
        if not en_content:
            en_content = "본문을 가져오지 못했습니다. 사이트 구조가 변경되었을 수 있습니다."

        # 4. 구글 번역기 가동! (영어 -> 한국어)
        translator = GoogleTranslator(source='en', target='ko')
        ko_title = translator.translate(en_title)
        ko_content = translator.translate(en_content)
        
        # 5. 텔레그램 발송용 메시지 조립
        msg = f"🌟 [주님은 나의 최고봉 / My Utmost for His Highest]\n\n"
        msg += f"🇰🇷 제목: {ko_title}\n"
        msg += f"🇺🇸 Title: {en_title}\n\n"
        msg += f"───────────────\n"
        msg += f"📖 [한국어 묵상]\n{ko_content}\n\n"
        msg += f"───────────────\n"
        msg += f"📖 [English Original]\n{en_content}\n\n"
        msg += f"🔗 원문 전체 읽기: {res.url}"
        
        return msg
        
    except Exception as e:
        return f"말씀 배달 중 에러가 발생했습니다: {str(e)}"

def send_telegram_text(message):
    safe_message = message[:4000]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": safe_message}
    requests.post(url, json=payload)

if __name__ == "__main__":
    word_text = get_translated_utmost()
    send_telegram_text(word_text)
