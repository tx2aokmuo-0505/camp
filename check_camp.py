import requests
from bs4 import BeautifulSoup
import os

# あなたが設定した「8/13-15の長野・山梨・岐阜」の検索URL
URL = "https://www.nap-camp.com/list?locationList=%5B137%2C138%2C139%2C140%2C141%2C142%2C143%2C144%2C120%2C121%2C122%2C123%2C124%2C125%2C126%2C127%2C128%2C129%2C130%2C131%2C132%2C133%2C134%2C135%2C136%2C165%2C166%2C167%2C168%2C169%2C170%5D&checkIn=2026-08-13&checkOut=2026-08-15&sortId=21"

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

def send_discord(message):
    if DISCORD_WEBHOOK_URL:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": message})

def main():
    # ブラウザのふりをする（これがないとサイトに門前払いされます）
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }
    
    # サイトを見に行く
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 【ここがポイント！】
    # なぜか「0件」と判定されるのを防ぐため、
    # ページの中にキャンプ場の個別ページへのリンク（/camp/から始まる文字）があるか数えます
    camp_links = [a for a in soup.find_all('a', href=True) if '/camp/' in a['href']]
    
    # 重複を消して、純粋なキャンプ場の数を数える
    unique_camps_count = len(set([a['href'] for a in camp_links]))

    if unique_camps_count > 0:
        # 1件でも見つかったら「空きが出た！」とみなして通知
        msg = f"🌟【速報】長野・山梨・岐阜で空きキャンプ場が見つかったよ！🐈\n合計 {unique_camps_count} 箇所の候補があります。\n今すぐ確認して！\n\n{URL}"
        send_discord(msg)
        print(f"空きを発見！{unique_camps_count}件通知しました🐈")
    else:
        # 見つからなかった場合
        print("まだ空きは出ていないようです...（巡回中）")

if __name__ == "__main__":
    main()
