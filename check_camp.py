import requests
from bs4 import BeautifulSoup
import os

# 検索URL（2026年8月13日〜 長野・山梨・岐阜）
URL = "https://www.nap-camp.com/list?locationList=%5B137%2C138%2C139%2C140%2C141%2C142%2C143%2C144%2C120%2C121%2C122%2C123%2C124%2C125%2C126%2C127%2C128%2C129%2C130%2C131%2C132%2C133%2C134%2C135%2C136%2C165%2C166%2C167%2C168%2C169%2C170%5D&checkIn=2026-08-13&checkOut=2026-08-15&sortId=21"

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

def send_discord(message):
    if DISCORD_WEBHOOK_URL:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": message})

def main():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"}
    
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # キャンプ場の名前を抜き出す
    camps = soup.select('section.c-item_card h3 a')
    # 名前だけを取り出して重複を消す
    camp_names = list(set([camp.get_text(strip=True) for camp in camps]))
    count = len(camp_names)

    if count > 0:
        # 名前を箇条書きにして合体
        names_str = "\n・" + "\n・".join(camp_names)
        msg = f"🌟【発見！】現在予約可能なキャンプ場は {count} 件です！\n{names_str}\n\n今すぐ確認：\n{URL}"
    else:
        # 👇好きな言葉を好きなだけ入れて！
        messages = [
            "☁️【報告】キャンプ場、突然“概念”になりました。触れられません。",
            "☁️【報告】条件に合うキャンプ場、今は電波の向こう側で踊っています。接続不可。",
            "☁️【報告】キャンプ場、あなたの条件を見て「また今度」と言い残し、光になりました。",
            "☁️【報告】条件に合うキャンプ場、四次元ポケットに吸い込まれた可能性あり。ドラえもん待ち。",
            "☁️【報告】キャンプ場、光になったけど戻り方を忘れたみたいです。",
            "☁️【報告】キャンプ場が見つからなかったよ。Copilot「というわけで次の候補を100件ほど自動生成しておいたよ。全部条件外だけどね」",
            "☁️【報告】候補地が急に“今日の運勢”を占い始め、検索結果が星座で埋まりました。",
            "☁️【報告】ゼロ。でもあなたはバナナよりすごい。あと、バナナはすぐ黒くなる。あなたはならない。",
            "☁️【報告】条件に合うキャンプ場、あなたの期待値を見て「荷が重い」と判断し逃走しました。",
            "☁️【報告】キャンプ場は見つか——【別件】冷蔵庫の牛乳、賞味期限切れてます。",
            "☁️ 404: camp not found　404：キャンプ場が見つかりません",
            "☁️【報告】ゼロ。でも朗報です。あなたの検索熱量で、隣の家の晩ごはんがカレーであることが判明しました。隠し味はリンゴです。",
            "☁️【報告】見つかりませんでした。その代わり、今あなたの脳内に「最高に美味しいマシュマロの焼き方」を直接ダウンロードしておきました。",
            "☁️ ⚠️警告：条件に合うキャンプ場は、現在「伝説の生き物」として保護されており、一般の検索には表示されません。",
        ]
        msg = random.choice(messages)
    
    send_discord(msg)

if __name__ == "__main__":
    main()
