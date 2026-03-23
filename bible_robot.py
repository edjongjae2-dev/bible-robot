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
        # 1. 홈페이지(대문)에 접속
        res_home = requests.get(home_url, headers=headers, timeout=15)
        soup_home = BeautifulSoup(res_home.text, 'html.parser')
        
        today_link = home_url
        
        # 2. 유저님이 발견하신 진짜 주소의 힌트! 'modern-classic' 방을 찾아 낚아챕니다.
        for a in soup_home.find_all('a', href=True):
            if 'modern-classic/' in a['href'] or 'classic/' in a['href']:
                today_link = a['href']
                break

        # 3. 찾아낸 진짜 말씀 방으로 입장! (예: The Burning Heart 페이지)
        res = requests.get(today_link, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 4. 제목 찾기
        title_tag = soup.find('h1')
        en_title = title_tag.text.strip() if title_tag else "Today's Devotional"
        
        # 5. 본문 찾기 (사진에서 보여주신 그 긴 문장들!)
        en_paragraphs = []
        
        # 홈페이지 간판 글씨를 피하기 위해 진짜 본문 영역(.entry-content)만 노립니다.
        content_area = soup.select_one('.entry-content') or soup.find('article') or soup.find('main')
        
        if content_area:
            for p in content_area.find_all('p'):
                text = p.text.strip()
                # 아주 짧은 메뉴 글씨나 엉뚱한 소개글을 걸러내고 '진짜 본문'만 담습니다.
                if len(text) > 40 and "Read today's daily devotional" not in text:
                    en_paragraphs.append(text)
                    
        # 번역기가 과부하 걸리지 않게 핵심 5문단만 챙깁니다.
        en_content = "\n\n".join(en_paragraphs[:5])
        if not en_content:
            en_content = "본문을 가져오지 못했습니다. 링크를 클릭해 원문을 확인해주세요."

        # 6. 구글 번역기 가동! (영어 -> 한국어)
        translator = GoogleTranslator(source='en', target='ko')
        ko_title = translator.translate(en_title)
        
        try:
            ko_content = translator.translate(en_content)
        except:
            ko_content = "본문 번역 중 오류가 발생했습니다. 본문이 너무 길 수 있습니다."
        
        # 7. 텔레그램 발송용 조립
        msg = f"🌟 [주님은 나의 최고봉 / My Utmost for His Highest]\n\n"
        msg += f"🇰🇷 제목: {ko_title}\n"
        msg += f"🇺🇸 Title: {en_title}\n\n"
        msg += f"───────────────\n"
        msg += f"📖 [한국어 묵상]\n{ko_content}\n\n"
        msg += f"───────────────\n"
        msg += f"📖 [English Original]\n{en_content}\n\n"
        msg += f"🔗 원문 전체 읽기: {today_link}"
        
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
