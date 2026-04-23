import requests
from bs4 import BeautifulSoup
import os
import random
import time

# --- 【設定】 ---
# 検索対象となる「なっぷ」のURL（場所・日付・条件などが含まれたもの）
URL = "https://www.nap-camp.com/list?locationList=%5B137%2C138%2C139%2C140%2C141%2C142%2C143%2C144%2C120%2C121%2C122%2C123%2C124%2C125%2C126%2C127%2C128%2C129%2C130%2C131%2C132%2C133%2C134%2C135%2C136%2C165%2C166%2C167%2C168%2C169%2C170%5D&checkIn=2026-08-13&checkOut=2026-08-15&sortId=21"
# Discordの通知先URL（環境変数から取得。なければ通知されません）
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# --- メッセージリスト (全57種類) ---
# 空きがなかった時にランダムで表示されるユニークなメッセージたち
ALL_MESSAGES = [
    "☁️【報告】キャンプ場、突然“概念”になりました。触れられません。",
    # ...（中略：57個のメッセージ）...
    "☁️ Runtime Error: Unexpected_Reality: 予期せぬ「お盆の満室」が発生しました。例外処理（やけ食い）を実行します。"
]

def get_shogo(toku):
    """
    累計の「徳ポイント（パトロール回数）」に応じて、ユーザーの称号を返す関数。
    ポイントが貯まれば貯まるほど、諏訪に精通した（？）怪しい称号に進化します。
    """
    if toku < 20: return "中央道で諏訪ICを通り過ぎた人"
    elif toku < 50: return "諏訪の迷い人"
    elif toku < 150: return "【初級】ツルヤを「ちょっと品揃えの良い静鉄ストア」と崇める民"
    # ...（中略）...
    elif toku < 1100: return "凍結した諏訪湖の上をノーマルタイヤで走る無謀な守護霊"
    else: return "⛩️ 諏訪大明神の化身 ⛩️"

def get_and_update_status():
    """
    空きがなかった時のステータス管理を行う関数。
    1. パトロール回数の記録
    2. 徳ポイントとシンクロ率の計算
    3. 57種類のメッセージから「まだ送っていないもの」を1つ選ぶ
    """
    history_file = "sent_messages.txt"      # パトロール回数を数えるためのファイル
    msg_history_file = "message_history.txt" # 既読メッセージを記録するファイル
    
    # --- パトロール回数（徳ポイント）の更新 ---
    if not os.path.exists(history_file):
        with open(history_file, "w", encoding="utf-8") as f: pass
    with open(history_file, "r", encoding="utf-8") as f:
        count = len(f.readlines()) # これまでの合計行数＝実行回数
    with open(history_file, "a", encoding="utf-8") as f:
        f.write(f"{time.ctime()}\n") # 今回のパトロール時刻を追記
    
    toku = (count + 1) * 2 # 1回パトロールするごとに2ポイント加算
    
    # --- 諏訪大明神とのシンクロ率を計算 ---
    # 基本はポイントの1/10。そこにランダムで±5%のゆらぎを与えて、それっぽく見せる
    sync_base = min(95.0, (toku / 10))
    sync_rate = round(sync_base + random.uniform(-5.0, 5.0), 2)
    sync_rate = max(0, min(100, sync_rate)) # 0〜100%の間に収める

    # --- 重複しないメッセージの選定ロジック ---
    if not os.path.exists(msg_history_file):
        with open(msg_history_file, "w", encoding="utf-8") as f: pass
    
    # すでに送信済みのメッセージを読み込む
    with open(msg_history_file, "r", encoding="utf-8") as f:
        used_msgs = [line.strip() for line in f.readlines()]
    
    # 「全てのメッセージ」の中から「既読」を除いたリストを作る
    available_msgs = [m for m in ALL_MESSAGES if m not in used_msgs]
    
    # もし全てのメッセージを使い切っていたら、履歴を消して最初からループさせる
    if not available_msgs:
        available_msgs = ALL_MESSAGES
        with open(msg_history_file, "w", encoding="utf-8") as f: pass 
    
    # 未読リストからランダムに1つ選択
    selected_msg = random.choice(available_msgs)
    
    # 選んだメッセージを「既読」としてファイルに書き込む
    with open(msg_history_file, "a", encoding="utf-8") as f:
        f.write(selected_msg + "\n")
        
    return toku, sync_rate, selected_msg

def send_discord(message):
    """DiscordのWebhookを使ってメッセージを送信する関数"""
    if DISCORD_WEBHOOK_URL:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": message})

def main():
    """プログラムのメイン処理"""
    # 相手のサイト（なっぷ）に「ブラウザからのアクセスですよ」と思わせるための設定
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"}
    
    try:
        # 1. 指定したURLのウェブサイトを読み込む
        response = requests.get(URL, headers=headers)
        # 2. HTML（サイトの構造）を解析する
        soup = BeautifulSoup(response.text, "html.parser")
        # 3. キャンプ場名のリンクがある場所を特定して抽出する
        camps = soup.select('section.c-item_card h3 a')
        # 4. 見つかったキャンプ場名をリスト化（重複は除去）
        camp_names = list(set([camp.get_text(strip=True) for camp in camps]))
        count = len(camp_names)
    except Exception as e:
        # 通信エラーなどが発生した場合の通知
        send_discord(f"⚠️ 諏訪パトロール中にシステムエラー: {e}")
        return

    # --- 判定と結果送信 ---
    if count > 0:
        # キャンプ場が見つかった（空きが出た！）場合
        names_str = "\n・" + "\n・".join(camp_names)
        msg = f"🌟【諏訪の結界、消失！】\n現在予約可能なキャンプ場は {count} 件です！\n{names_str}\n\n今すぐ御柱を立てに行く：\n{URL}"
    else:
        # 空きがなかった場合（いつものパトロール）
        current_toku, sync_rate, selected_msg = get_and_update_status()
        shogo = get_shogo(current_toku)
        msg = (
            f"{selected_msg}\n\n"
            f"--- ⛩️ 諏訪パトロール・ステータス ---\n"
            f"称号：【{shogo}】\n"
            f"累計徳ポイント：{current_toku} pt\n"
            f"諏訪大明神とのシンクロ率：{sync_rate}%"
        )

    # 最終的なメッセージをDiscordに送る
    send_discord(msg)

# このファイルが直接実行された場合にメイン処理を呼び出す
if __name__ == "__main__":
    main()
