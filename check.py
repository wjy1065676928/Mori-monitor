import feedparser
import smtplib
from email.mime.text import MIMEText
import os

CHANNEL_ID = "UCL_qhgtOy0dy1Agp8vkySQg"

rss = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"

feed = feedparser.parse(rss)

video = feed.entries[0]
video_id = video.yt_videoid
title = video.title
link = video.link

last = ""

if os.path.exists("last_video.txt"):
    with open("last_video.txt") as f:
        last = f.read().strip()

if video_id != last:

    msg = MIMEText(f"{title}\n{link}")
    msg["Subject"] = "New YouTube Video"
    msg["From"] = os.environ["MAIL_USER"]
    msg["To"] = os.environ["MAIL_TO"]

    s = smtplib.SMTP("smtp.gmail.com",587)
    s.starttls()
    s.login(os.environ["MAIL_USER"], os.environ["MAIL_PASS"])
    s.sendmail(msg["From"],[msg["To"]],msg.as_string())
    s.quit()

    with open("last_video.txt","w") as f:
        f.write(video_id)
