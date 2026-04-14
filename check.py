import feedparser
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import subprocess

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

print(f"Last video ID: {last}")
print(f"Current video ID: {video_id}")

# 生成当前视频的标签
title_lower = title.lower()

if live_type == "live":
    tag = "🔴 LIVE NOW"

elif live_type == "upcoming":
    tag = "⏰ LIVE SCHEDULED"

elif "#calliolive" in title_lower:
    tag = "🔴 LIVE (title)"

else:
    tag = "🎬 NEW VIDEO"

# 总是更新 README.md 为当前最新视频
readme_content = f"""# 最新视频/直播

{tag} - [{title}]({link})

![封面]({thumbnail})

---

"""
try:
    with open("README.md", "r", encoding="utf-8") as f:
        current_readme = f.read()
    if current_readme.startswith("# 最新视频/直播"):
        parts = current_readme.split("---", 1)
        if len(parts) > 1:
            new_readme = readme_content + parts[1].lstrip()
        else:
            new_readme = readme_content + "\n" + current_readme
    else:
        new_readme = readme_content + current_readme
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_readme)
    print("README.md 更新成功")
    
    # 提交 README.md 到 git
    try:
        subprocess.run(["git", "config", "--global", "user.name", "bot"], check=True)
        subprocess.run(["git", "config", "--global", "user.email", "bot@github.com"], check=True)
        subprocess.run(["git", "add", "README.md"], check=True)
        result = subprocess.run(["git", "commit", "-m", f"Update README with latest video"], capture_output=True, text=True)
        if result.returncode == 0:
            subprocess.run(["git", "push"], check=True)
            print("README.md 提交成功")
        else:
            print("README.md 无需提交（没有变化）")
    except Exception as e:
        print("README.md git操作失败:", e)
except Exception as e:
    print("README.md 更新失败:", e)

if video_id != last:
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