import requests
from bs4 import BeautifulSoup
import os

# 🔐 금고 설정
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('TELEGRAM_CHAT_ID')

def get_utmost_rss():
    # 📡 웹사이트의 '새 글 알림' 채널(RSS) 주소 두 가지
    urls = [
        "https://www.utmost.co.kr/feed/",
        "https://www.utmost.co.kr/daily-devotional/feed/"
    ]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for url in urls:
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                # html 대신 xml(피드) 모드로 읽습니다
                soup = BeautifulSoup(res.text, 'html.parser')
                item = soup.find('item') # 가장 최신 글 찾기
                
                if item:
                    title = item.find('title').text if item.find('title') else "제목 없음"
                    link = item.find('link').text if item.find('link') else "링크 없음"
                    
                    # 본문 내용 (HTML 태그 제거)
                    desc_html = item.find('description').text if item.find('description') else ""
                    desc_text = BeautifulSoup(desc_html, 'html.parser').text.strip()
                    
                    # 텔레그램에 맞게 본문이 너무 길면 자릅니다
                    snippet = desc_text[:300] + "\n...(더 보기는 링크 클릭!)" if len(desc_text) > 300 else desc_text
                    
                    return f"🌟 [주님은 나의 최고봉]\n\n📖 제목: {title}\n\n📍 말씀: {snippet}\n\n🔗 원문 읽기: {link}"
        except Exception:
            continue
            
    # 피드마저 막혔을 때, 로봇이 본 화면(증거)을 가져옵니다.
    try:
        res = requests.get("https://www.utmost.co.kr/", headers=headers, timeout=10)
        return f"🚨 사이트가 깃허브 로봇을 튕겨내고 있습니다!\n\n[로봇이 본 화면 증거]\n{res.text[:300]}..."
    except Exception as e:
        return f"사이트에 아예 접속할 수 없습니다. 😥 ({str(e)})"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    requests.post(url, json=payload)

if __name__ == "__main__":
    content = get_utmost_rss()
    send_telegram(content)
