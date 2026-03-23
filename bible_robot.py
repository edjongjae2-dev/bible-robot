import requests
from bs4 import BeautifulSoup
import os

# 🔐 금고 설정
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('TELEGRAM_CHAT_ID')

def get_su_word():
    # 유저님이 이미 성공하셨던 '매일성경' 주소입니다!
    url = "https://sum.su.or.kr:8888/bible/today"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 제목 찾기
        title_tag = soup.select_one('.bible_text')
        title = title_tag.text.strip() if title_tag else "오늘의 묵상"
        
        # 본문 말씀 찾기 (너무 길지 않게 딱 5구절만 예쁘게 자르기)
        verses = soup.select('.body_list li')
        verse_text = ""
        for v in verses[:5]: 
            num = v.select_one('.num').text if v.select_one('.num') else ""
            info = v.select_one('.info').text if v.select_one('.info') else ""
            verse_text += f"{num} {info}\n\n"
            
        # 텔레그램 사진 밑에 달릴 예쁜 설명(캡션) 만들기
        caption = f"🌿 [오늘의 매일성경]\n\n📖 {title}\n\n{verse_text}...\n\n🔗 전문 묵상하기: {url}"
        return caption
    except Exception as e:
        return f"말씀 배달 중 에러가 발생했습니다: {str(e)}"

def send_telegram_card(caption):
    # 🌅 매일 무작위로 바뀌는 고화질 자연 풍경 사진 주소 (무료 API)
    photo_url = "https://picsum.photos/800/600/?nature,peace"
    
    # 🌟 글씨만 보내는 sendMessage가 아니라, 사진을 보내는 sendPhoto 명령!
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    payload = {
        "chat_id": chat_id,
        "photo": photo_url,    # 이 사진과 함께
        "caption": caption     # 매일성경 말씀을 덧붙여서 보냅니다.
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    # 1. 매일성경 텍스트 가져오기
    word_caption = get_su_word()
    
    # 2. 멋진 사진과 함께 텔레그램으로 쏘기!
    send_telegram_card(word_caption)
