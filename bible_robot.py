import requests
from bs4 import BeautifulSoup
import os

# 🔐 금고 설정
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('TELEGRAM_CHAT_ID')

def get_su_word_full():
    url = "https://sum.su.or.kr:8888/bible/today"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 제목 찾기
        title_tag = soup.select_one('.bible_text')
        title = title_tag.text.strip() if title_tag else "오늘의 묵상"
        
        # 본문 말씀 찾기 (자르지 않고 전부 다 가져옵니다!)
        verses = soup.select('.body_list li')
        verse_text = ""
        for v in verses: 
            num = v.select_one('.num').text if v.select_one('.num') else ""
            info = v.select_one('.info').text if v.select_one('.info') else ""
            verse_text += f"{num} {info}\n\n"
            
        # 전체 텍스트 조립
        full_text = f"🌿 [오늘의 매일성경]\n\n📖 {title}\n\n{verse_text}🔗 전문 묵상하기: {url}"
        return full_text
    except Exception as e:
        return f"말씀 배달 중 에러가 발생했습니다: {str(e)}"

def send_telegram_photo():
    # 🌅 무작위 고화질 자연 풍경 사진
    photo_url = "https://picsum.photos/800/600/?nature,peace"
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    payload = {
        "chat_id": chat_id,
        "photo": photo_url,
        "caption": "오늘의 묵상 배달이 도착했습니다 💌" # 사진에는 짧은 인사말만!
    }
    requests.post(url, json=payload)

def send_telegram_text(message):
    # 📝 긴 텍스트 전송 (혹시 모를 에러 방지를 위해 4000자에서 안전하게 자름)
    safe_message = message[:4000]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": safe_message}
    requests.post(url, json=payload)

if __name__ == "__main__":
    # 1. 전체 말씀 긁어오기
    word_text = get_su_word_full()
    
    # 2. 예쁜 사진 먼저 쏘기!
    send_telegram_photo()
    
    # 3. 그 아래에 전체 본문 말씀 쏘기!
    send_telegram_text(word_text)
