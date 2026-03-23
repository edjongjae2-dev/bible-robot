import requests
from bs4 import BeautifulSoup
import os

# 🔐 금고 설정 가져오기
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('TELEGRAM_CHAT_ID')

def get_daily_bible():
    # 🎯 매일성경 공식 오늘 말씀 주소 (절대 변하지 않고 로봇을 막지 않습니다!)
    url = "https://sum.su.or.kr:8888/bible/today"
    
    # 사람인 척하는 신분증
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        res.encoding = 'utf-8' # 한글 깨짐 방지
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 1. 말씀 제목 및 구절 위치 (예: 창세기 1:1~5)
        title_box = soup.select_one('.bibleinfo_box')
        title = title_box.text.strip().replace('\n', ' ') if title_box else "오늘의 말씀"
        
        # 2. 본문 말씀 내용 (li 태그 안에 구절들이 들어있습니다)
        body_list = soup.select_one('#body_list')
        verses = []
        
        if body_list:
            for li in body_list.find_all('li'):
                verses.append(li.text.strip())
            
            # 본문을 하나로 합치기
            verse_text = "\n\n".join(verses)
            
            # 텔레그램 메시지 길이 제한 대비 (너무 길면 자르기)
            if len(verse_text) > 800:
                verse_text = verse_text[:800] + "\n\n...(이하 생략, 링크에서 마저 읽어주세요!)"
        else:
            verse_text = "본문 말씀을 가져오지 못했습니다."
            
        return f"🌱 [오늘의 매일성경]\n\n📖 {title}\n\n{verse_text}\n\n🔗 묵상하러 가기: {url}"
        
    except Exception as e:
        return f"말씀 배달 중 오류가 발생했습니다 😥\n{str(e)}"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    requests.post(url, json=payload)

if __name__ == "__main__":
    content = get_daily_bible()
    send_telegram(content)
