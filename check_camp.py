import requests
from bs4 import BeautifulSoup
import os

# なっぷのURL
URL = "https://www.nap-camp.com/list?locationList=%5B137%2C138%2C139%2C140%2C141%2C142%2C143%2C144%2C120%2C121%2C122%2C123%2C124%2C125%2C126%2C127%2C128%2C129%2C130%2C131%2C132%2C133%2C134%2C135%2C136%2C165%2C166%2C167%2C168%2C169%2C170%5D&checkIn=2026-08-13&checkOut=2026-08-15&sortId=21"
# DiscordのURL（後で設定します）
DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]
DATA_FILE = "last_camp_list.txt"

def send_discord(message):
    requests.post(DISCORD_WEBHOOK_URL, json={"content": message})

def main():
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(URL, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # なっぷのキャンプ場名を取得
    camp_elements = soup.select('.c-card__title')
    current_camps = [el.get_text(strip=True) for el in camp_elements]

    if not current_camps:
        return

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            past_camps = f.read().splitlines()
    else:
        past_camps = []

    new_camps = [camp for camp in current_camps if camp not in past_camps]

    if new_camps:
        msg = "⛺ **新着キャンプ場を発見しました！**\n" + "\n".join([f"・{c}" for c in new_camps]) + f"\n\nサイトを確認: {URL}"
        send_discord(msg)
        
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(current_camps))

if __name__ == "__main__":
    main()
