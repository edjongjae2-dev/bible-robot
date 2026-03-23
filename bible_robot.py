import requests
from bs4 import BeautifulSoup
import os

# 🔐 금고 설정
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('TELEGRAM_CHAT_ID')

def get_utmost_word():
    # 1. 묵상 목록이 나오는 메인 페이지로 갑니다.
    main_url = "https://www.utmost.co.kr/daily-devotional/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # 2. 메인 페이지 접속
        res = requests.get(main_url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 3. 목록에서 가장 위에 있는(최신) 글의 링크를 찾습니다.
        # h2 태그 안의 a 태그나 article 태그 안의 링크를 찾습니다.
        first_post = soup.select_one('h2 a') or soup.select_one('article a')
        
        if first_post and 'href' in first_post.attrs:
            final_url = first_post['href']
            
            # 4. 찾은 진짜 주소로 접속합니다.
            res_content = requests.get(final_url, headers=headers, timeout=15)
            soup_content = BeautifulSoup(res_content.text, 'html.parser')
            
            # 제목 추출
            title = soup_content.find('h1').text.strip()
            
            # 본문 말씀 추출 (.bible-verse 클래스가 가장 정확합니다)
            verse_tag = soup_content.select_one('.bible-verse') or soup_content.select_one('blockquote')
            verse = verse_tag.text.strip() if verse_tag else "본문 말씀은 링크를 통해 확인해 주세요."
            
            return f"🌟 [주님은 나의 최고봉]\n\n📖 제목: {title}\n\n📍 말씀: {verse}\n\n🔗 원문: {final_url}"
        
        return "오늘의 새 글 링크를 찾지 못했습니다. 😥"
    except Exception as e:
        return f"연결 중 오류가 발생했습니다: {str(e)}"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    requests.post(url, json=payload)

if __name__ == "__main__":
    content = get_utmost_word()
    send_telegram(content)
