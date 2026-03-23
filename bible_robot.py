import requests
from bs4 import BeautifulSoup
import os
from deep_translator import GoogleTranslator

# 🔐 금고 설정
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('TELEGRAM_CHAT_ID')

def get_translated_utmost():
    home_url = "https://utmost.org/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    }
    
    try:
        # 1. 홈페이지(대문)에서 '오늘의 말씀' 방 주소 찾기
        res_home = requests.get(home_url, headers=headers, timeout=15)
        soup_home = BeautifulSoup(res_home.text, 'html.parser')
        
        today_link = home_url
        for a in soup_home.find_all('a', href=True):
            if 'modern-classic/' in a['href'] or 'classic/' in a['href']:
                today_link = a['href']
                break

        # 2. 찾아낸 진짜 말씀 방으로 입장!
        res = requests.get(today_link, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 3. 제목 찾기
        title_tag = soup.find('h1')
        en_title = title_tag.text.strip() if title_tag else "Today's Devotional"
        
        # 4. 진공청소기 모드 작동! (서랍 이름 무시하고 긴 글자 다 쓸어담기)
        en_paragraphs = []
        for p in soup.find_all('p'):
            text = p.text.strip()
            # 길이가 50자 이상인 '진짜 문장'만 담고, 잡다한 안내 문구는 버립니다.
            if len(text) > 50 and "Read today's" not in text and "Our Daily Bread" not in text and "delivered to your inbox" not in text:
                en_paragraphs.append(text)
                
        # 번역기가 멈추지 않게 핵심 4~5문단만 챙깁니다.
        en_content = "\n\n".join(en_paragraphs[:5])
        if not en_content:
            en_content = "본문을 가져오지 못했습니다."

        # 5. 구글 번역기 가동! (영어 -> 한국어)
        translator = GoogleTranslator(source='en', target='ko')
        ko_title = translator.translate(en_title)
        
        try:
            ko_content = translator.translate(en_content)
        except:
            ko_content = "본문 번역 중 오류가 발생했습니다."
        
        # 6. 텔레그램 발송용 조립
        msg = f"🌟 [주님은 나의 최고봉 / My Utmost for His Highest]\n\n"
        msg += f"🇰🇷 제목: {ko_title}\n"
        msg += f"🇺🇸 Title: {en_title}\n\n"
        msg += f"───────────────\n"
        msg += f"📖 [한국어 묵상]\n{ko_content}\n\n"
        msg += f"───────────────\n"
        msg += f"📖 [English Original]\n{en_content}\n\n"
        msg += f"🔗 원문 전체 읽기: {res.url}" # 최종 도착한 진짜 주소를 뿌려줍니다.
        
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
