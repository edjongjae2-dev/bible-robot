import requests
from bs4 import BeautifulSoup
import os

# 🔐 금고 설정
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('TELEGRAM_CHAT_ID')

def get_utmost_word():
    # 1. 메인 페이지 주소
    main_url = "https://www.utmost.co.kr/daily-devotional/"
    
    try:
        # 2. 메인 페이지에서 '오늘의 묵상' 링크 찾기
        res = requests.get(main_url, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 첫 번째 묵상 글 링크 가져오기
        post_link = soup.select_one('.entry-title a') or soup.select_one('article a')
        
        if post_link and 'href' in post_link.attrs:
            final_url = post_link['href']
            
            # 3. 진짜 말씀 페이지 접속
            res_content = requests.get(final_url, timeout=10)
            soup_content = BeautifulSoup(res_content.text, 'html.parser')
            
            # 제목과 본문 추출
            title = soup_content.find('h1').text.strip()
            # 말씀 구절은 주로 특정 클래스나 blockquote에 있음
            verse = ""
            verse_tags = soup_content.select('.bible-verse, blockquote, .entry-content p')
            if verse_tags:
                verse = verse_tags[0].text.strip() # 첫 번째 문단(보통 성경구절) 가져오기
            
            return f"☀️ [주님은 나의 최고봉]\n\n📖 제목: {title}\n\n📍 말씀: {verse}\n\n🔗 원문 읽기: {final_url}"
        
        return "게시글 링크를 찾지 못했습니다. 😥"
    except Exception as e:
        return f"말씀 배달 중 오류 발생: {str(e)}"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    requests.post(url, json=payload)

if __name__ == "__main__":
    content = get_utmost_word()
    send_telegram(content)
