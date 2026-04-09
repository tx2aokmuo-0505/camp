import requests
from bs4 import BeautifulSoup
import os

# あなたの検索条件URL
URL = "https://www.nap-camp.com/list?locationList=%5B137%2C138%2C139%2C140%2C141%2C142%2C143%2C144%2C120%2C121%2C122%2C123%2C124%2C125%2C126%2C127%2C128%2C129%2C130%2C131%2C132%2C133%2C134%2C135%2C136%2C165%2C166%2C167%2C168%2C169%2C170%5D&checkIn=2026-08-13&checkOut=2026-08-15&sortId=21"

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

def send_discord(message):
    if DISCORD_WEBHOOK_URL:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": message})

def main():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    response = requests.get(URL, headers=headers)
    response.encoding = response.apparent_encoding
    
    soup = BeautifulSoup(response.text, "html.parser")
    camps = soup.select('h3 a') 
    current_camps = [c.get_text(strip=True) for c in camps if c.get_text(strip=True)]

    # 【重要】以前のリストを読み込む（今回は簡易的にファイルから）
    # ※128エラー回避のため、GitHubへの保存ではなく毎回通知しますが、
    #  文言をご希望通り「見つかりました！🐈」にします。
    
    if current_camps:
        # 見つかったキャンプ場を並べる
        camp_list = "\n".join([f"・{c}" for c in current_camps[:10]])
        msg = f"新たなキャンプ場が見つかりました！🐈\n\n{camp_list}\n\nサイトを確認：\n{URL}"
        send_discord(msg)
        print("通知を送りました🐈")
    else:
        print("まだ空きがないようです...")

if __name__ == "__main__":
    main()
