import requests
from bs4 import BeautifulSoup
import os

# 検索URL（長野・山梨・岐阜）
URL = "https://www.nap-camp.com/list?locationList=%5B137%2C138%2C139%2C140%2C141%2C142%2C143%2C144%2C120%2C121%2C122%2C123%2C124%2C125%2C126%2C127%2C128%2C129%2C130%2C131%2C132%2C133%2C134%2C135%2C136%2C165%2C166%2C167%2C168%2C169%2C170%5D&checkIn=2026-08-13&checkOut=2026-08-15&sortId=21"

# Discordの合言葉（Webhook）
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

def send_discord(message):
    if DISCORD_WEBHOOK_URL:
        # ここでDiscordに送信
        requests.post(DISCORD_WEBHOOK_URL, json={"content": message})
    else:
        print("WebhookのURLが設定されていないみたいだよ。GitHubのSecretsを確認して！")

def main():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"}
    
    # 【テスト1】まず「今から動くよ」とDiscordに言わせる
    #send_discord("📢【テスト】今からなっぷ見張りを開始するよ！🐈")
    
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # キャンプ場のリンクを数える
    camp_links = [a for a in soup.find_all('a', href=True) if '/camp/' in a['href']]
    unique_camps_count = len(set([a['href'] for a in camp_links]))

    # 【テスト2】見つかった件数を報告（0件でも送る！）
    if unique_camps_count > 0:
        msg = f"🌟【発見！】なっぷで {unique_camps_count} 件のキャンプ場が見つかったよ！\nすぐ見て！: {URL}"
    else:
        msg = "☁️【報告】今はなっぷに空きがないみたい...引き続き見張るね！😽"
    
    send_discord(msg)

if __name__ == "__main__":
    main()
