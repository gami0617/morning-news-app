import email.message
import datetime
import os
import smtplib
import feedparser
from supabase import create_client

# 環境変数の取得
GMAIL_USER = os.environ.get("ikegamiseimaseima.14012828@gmail.com")
GMAIL_PASS = os.environ.get("maza gqll qqii vndo")
SUPABASE_URL = os.environ.get("https://lalbvmmigfkthliihjil.supabase.co/rest/v1/")
SUPABASE_KEY = os.environ.get("g7WYzExhUw4-ivkla-GURQ_luS59YLN")

# Supabase初期化
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 現在の日本時間（例: "07:00"）を取得
now_jst = datetime.datetime.now(
    datetime.timezone(datetime.timedelta(hours=9))
).strftime("%H:00")

# 1. 現在の時間に配信設定している宛先を取得
response = (
    supabase.table("subscribers")
    .select("email")
    .eq("dispatch_time", now_jst)
    .execute()
)
target_emails = [item["email"] for item in response.data]

if not target_emails:
    print(f"{now_jst}: 対象ユーザーはいません。")
    exit()

# 2. Yahoo!ニュース RSS取得
feed = feedparser.parse("https://news.yahoo.co.jp/rss/topics/top-picks.xml")
content = f"📰 Morning Digest ({now_jst}版)\n\n"
for entry in feed.entries[:3]:
    content += f"・{entry.title}\n{entry.link}\n\n"

# 3. 該当のメールアドレスへ送信
with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login(GMAIL_USER, GMAIL_PASS)

    for target in target_emails:
        msg = email.message.EmailMessage()
        msg["Subject"] = "【Morning Digest】本日のニュース"
        msg["From"] = GMAIL_USER
        msg["To"] = target
        msg.set_content(content)

        server.send_message(msg)

print(f"{len(target_emails)} 件送信完了")
