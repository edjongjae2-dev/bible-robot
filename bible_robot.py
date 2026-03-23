import requests
from bs4 import BeautifulSoup
import os
from deep_translator import GoogleTranslator
import time

# 🔐 금고 설정
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('TELEGRAM_CHAT_ID')

# ==========================================
# 1. 매일성경 가져오기
# ==========================================
def get_su_word_full():
    url = "https://sum.su.or.kr:8888/bible/today"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        title_tag = soup.select_one('.bible_text')
        title = title_tag.text.strip() if title_tag else "오늘의 묵상"
        
        passage_info = ""
        for div in soup.find_all('div'):
            text = div.get_text(separator=' ', strip=True)
            if "본문" in text and "찬송" in text and len(text) < 150:
                if title in text:
                    text = text.replace(title, "").strip()
                passage_info = " ".join(text.split())
                break
        
        verses = soup.select('.body_list li')
        verse_text = ""
        for v in verses: 
            num = v.select_one('.num').text if v.select_one('.num') else ""
            info = v.select_one('.info').text if v.select_one('.info') else ""
            verse_text += f"{num} {info}\n\n"
            
        full_text = f"🌿 [오늘의 매일성경]\n\n"
        if passage_info:
            full_text += f"📖 {passage_info}\n\n"
        full_text += f"🔖 제목: {title}\n\n"
        full_text += f"{verse_text}🔗 전문 묵상하기: {url}"
        return full_text
    except Exception as e:
        return f"매일성경 배달 중 에러: {str(e)}"

def send_telegram_photo():
    photo_url = "https://picsum.photos/800/600/?nature,peace"
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    payload = {"chat_id": chat_id, "photo": photo_url, "caption": "오늘의 묵상 배달이 도착했습니다 💌"}
    requests.post(url, json=payload)

# ==========================================
# 2. 주님은 나의 최고봉 (번역) 가져오기
# ==========================================
def get_translated_utmost():
    home_url = "https://utmost.org/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}
    try:
        res_home = requests.get(home_url, headers=headers, timeout=15)
        soup_home = BeautifulSoup(res_home.text, 'html.parser')
        
        today_link = home_url
        for a in soup_home.find_all('a', href=True):
            if 'modern-classic/' in a['href'] or 'classic/' in a['href']:
                today_link = a['href']
                break

        res = requests.get(today_link, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        title_tag = soup.find('h1')
        en_title = title_tag.text.strip() if title_tag else "Today's Devotional"
        
        en_paragraphs = []
        for p in soup.find_all('p'):
            text = p.text.strip()
            # 🌟 똑같은 문장이 두 번 들어가는 것을 막는 방어막(not in) 추가!
            if len(text) > 50 and "Read today's" not in text and "Our Daily Bread" not in text and "delivered to your inbox" not in text:
                if text not in en_paragraphs:
                    en_paragraphs.append(text)
                
        en_content = "\n\n".join(en_paragraphs[:5])
        if not en_content:
            en_content = "본문을 가져오지 못했습니다."

        translator = GoogleTranslator(source='en', target='ko')
        ko_title = translator.translate(en_title)
        try:
            ko_content = translator.translate(en_content)
        except:
            ko_content = "본문 번역 중 오류가 발생했습니다."
        
        msg = f"🌟 [주님은 나의 최고봉 / My Utmost for His Highest]\n\n"
        msg += f"🇰🇷 제목: {ko_title}\n🇺🇸 Title: {en_title}\n\n───────────────\n"
        msg += f"📖 [한국어 묵상]\n{ko_content}\n\n───────────────\n"
        msg += f"📖 [English Original]\n{en_content}\n\n🔗 원문 전체 읽기: {res.url}"
        return msg
    except Exception as e:
        return f"최고봉 배달 중 에러: {str(e)}"

# ==========================================
# 3. 텍스트 전송 공통 함수
# ==========================================
def send_telegram_text(message):
    safe_message = message[:4000]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": safe_message}
    requests.post(url, json=payload)

if __name__ == "__main__":
    send_telegram_photo()
    su_text = get_su_word_full()
    send_telegram_text(su_text)
    
    time.sleep(3)
    
    utmost_text = get_translated_utmost()
    send_telegram_text(utmost_text)
