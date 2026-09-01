import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone, timedelta
import feedparser
from supabase import create_client

# 1. 直接値を設定（Secrets読み込みエラーを完全に回避）
SUPABASE_URL = "https://lalbvmmigfkthliihjil.supabase.co"
SUPABASE_KEY = "sb_publishable_g7WYzExhUw4-ivkla-GURQ_luS59YLN" # ご自身の長いPublishable Key

GMAIL_USER = os.environ.get("ikegamiseimaseima.14012828@gmail.com")
GMAIL_PASS = os.environ.get("maza gqll qqii vndo")

# 読み込みチェック
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL または SUPABASE_KEY が環境変数に設定されていません。")

if not GMAIL_USER or not GMAIL_PASS:
    raise ValueError("GMAIL_USER または GMAIL_PASS が環境変数に設定されていません。")

# 2. Supabaseクライアントの初期化
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 3. 日本時間の現在時刻（HH:00 形式）を取得
JST = timezone(timedelta(hours=9))
current_time_jst = datetime.now(JST).strftime("%H:00")
print(f"現在時刻 (JST): {current_time_jst}")

# 4. RSSフィード（Googleニュース）の取得関数
def fetch_news():
    rss_url = "https://news.google.com/rss?hl=ja&gl=JP&ceid=JP:ja"
    feed = feedparser.parse(rss_url)
    articles = []
    for entry in feed.entries[:5]: # 上位5件を取得
        articles.append(f"・{entry.title}\n  {entry.link}")
    return "\n\n".join(articles)

# 5. メール送信関数
def send_email(to_email, news_content):
    msg = MIMEMultipart()
    msg['From'] = GMAIL_USER
    msg['To'] = to_email
    msg['Subject'] = f"【朝ニュース配信】{current_time_jst} の最新ニュース"

    body = f"いつもご利用ありがとうございます。\n指定時刻（{current_time_jst}）のニュースをお届けします。\n\n{news_content}\n\n--"
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_PASS)
            server.sendmail(GMAIL_USER, to_email, msg.as_string())
        print(f"送信成功: {to_email}")
    except Exception as e:
        print(f"送信失敗 ({to_email}): {e}")

# 6. メイン処理：Supabaseからユーザーを取得してメール配信
def main():
    # 現在の配信時刻に合致するユーザーを取得
    response = supabase.table("subscribers").select("*").eq("dispatch_time", current_time_jst).execute()
    users = response.data

    if not users:
        print(f"配信対象のユーザーはいません（設定時刻: {current_time_jst}）")
        return

    print(f"{len(users)} 件の配信対象ユーザーが見つかりました。")
    news_content = fetch_news()

    for user in users:
        email = user.get("email")
        if email:
            send_email(email, news_content)

if __name__ == "__main__":
    main()
    
