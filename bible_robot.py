import requests
from bs4 import BeautifulSoup
import os

# 🔐 금고 설정
token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('TELEGRAM_CHAT_ID')

def get_word_card():
    # 📡 갓피플 '오늘의 말씀' 게시판 주소
    url = "https://cnts.godpeople.com/p/category/word"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # 1. 갓피플 게시판 접속
        res = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 2. 가장 첫 번째 게시글(최신 말씀) 링크 낚아채기
        first_post = soup.select_one('.post-title a') or soup.select_one('article a')
        if not first_post:
            return None, "오늘의 말씀 게시글을 찾지 못했어요."
            
        post_url = first_post.get('href')
        
        # 3. 진짜 게시글 안에 들어가서 '이미지' 주소 꺼내오기
        res_post = requests.get(post_url, headers=headers, timeout=15)
        soup_post = BeautifulSoup(res_post.text, 'html.parser')
        
        # 보통 사이트는 og:image 태그에 가장 고화질 대표 이미지를 걸어둡니다.
        meta_img = soup_post.find('meta', property='og:image')
        title_meta = soup_post.find('meta', property='og:title')
        
        if meta_img and meta_img.get('content'):
            img_url = meta_img.get('content')
            title = title_meta.get('content') if title_meta else "오늘의 말씀 카드"
            
            # 사진 밑에 달릴 짧은 설명(캡션)
            caption = f"🌅 [{title}]\n\n오늘도 주님 안에서 승리하는 하루 보내세요!\n🔗 출처: 갓피플"
            return img_url, caption
            
        return None, "이미지를 추출하지 못했습니다."
    except Exception as e:
        return None, f"카드 배달 중 에러: {str(e)}"

def send_telegram_photo(photo_url, caption):
    # 🌟 핵심! 텍스트(sendMessage)가 아닌 사진(sendPhoto)을 보내는 텔레그램 명령!
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    payload = {
        "chat_id": chat_id,
        "photo": photo_url,
        "caption": caption
    }
    requests.post(url, json=payload)

def send_telegram_text(message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    requests.post(url, json=payload)

if __name__ == "__main__":
    # 로봇 실행
    img_url, caption = get_word_card()
    
    if img_url:
        send_telegram_photo(img_url, caption)
    else:
        # 사진을 못 찾으면 텍스트로 에러 메시지 전송
        send_telegram_text(caption)
