import feedparser
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

CHANNEL_ID = "UCL_qhgtOy0dy1Agp8vkySQg"

rss = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
feed = feedparser.parse(rss)

if not feed.entries:
    print("RSS 返回为空，可能是网络问题")
    exit(0)

video = feed.entries[0]

video_id = video.yt_videoid
title = video.title
link = video.link
live_type = getattr(video, "yt_livebroadcastcontent", "none")

thumbnail = f"https://i3.ytimg.com/vi/{video_id}/maxresdefault.jpg"

last = ""
if os.path.exists("last_video.txt"):
    with open("last_video.txt") as f:
        last = f.read().strip()

if video_id != last:

    if live_type == "live":
        tag = "🔴 LIVE NOW"
    elif live_type == "upcoming":
        tag = "⏰ LIVE SCHEDULED"
    else:
        tag = "🎬 NEW VIDEO"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"{tag} - {title}"
    msg["From"] = os.environ["MAIL_USER"]
    msg["To"] = os.environ["MAIL_TO"]

    html = f"""
    <html>
      <body>
        <a href="{link}">
          <img src="{thumbnail}" width="900">
        </a>
        <h2>{tag}</h2>
        <h3>{title}</h3>
        <p>点击封面观看</p>
      </body>
    </html>
    """

    msg.attach(MIMEText(html, "html"))

    try:
        s = smtplib.SMTP("smtp.gmail.com", 587)
        s.starttls()
        s.login(os.environ["MAIL_USER"], os.environ["MAIL_PASS"])
        s.sendmail(msg["From"], [msg["To"]], msg.as_string())
        s.quit()
        print("邮件发送成功")

    except Exception as e:
        print("邮件发送失败:", e)

    with open("last_video.txt", "w") as f:
        f.write(video_id)