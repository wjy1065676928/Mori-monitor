import feedparser
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

CHANNEL_ID = "UCL_qhgtOy0dy1Agp8vkySQg"

rss = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"

feed = feedparser.parse(rss)

video = feed.entries[0]
video_id = video.yt_videoid
title = video.title
link = video.link
thumbnail = f"https://i3.ytimg.com/vi/{video_id}/hqdefault.jpg"

# 读取上一次的最新视频
last = ""
if os.path.exists("last_video.txt"):
    with open("last_video.txt") as f:
        last = f.read().strip()

if video_id != last:

    # 创建 HTML 邮件
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"New YouTube Video: {title}"
    msg["From"] = os.environ["MAIL_USER"]
    msg["To"] = os.environ["MAIL_TO"]

    # HTML 正文
    html = f"""
    <html>
      <body>
        <a href="{link}">
          <img src="{thumbnail}" alt="封面" width="800" style="display:block;margin-bottom:10px;">
        </a>
        <h2>{title}</h2>
        <p>点击封面观看视频</p>
      </body>
    </html>
    """
    msg.attach(MIMEText(html, "html"))

    # 发送邮件
    s = smtplib.SMTP("smtp.gmail.com", 587)
    s.starttls()
    s.login(os.environ["MAIL_USER"], os.environ["MAIL_PASS"])
    s.sendmail(msg["From"], [msg["To"]], msg.as_string())
    s.quit()

    # 保存最新视频 ID
    with open("last_video.txt", "w") as f:
        f.write(video_id)