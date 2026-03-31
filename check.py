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

if video_id != last:

    title_lower = title.lower()
    
    if live_type == "live":
        tag = "🔴 LIVE NOW"

    elif live_type == "upcoming":
        tag = "⏰ LIVE SCHEDULED"

    # 👇 用标题兜底（关键）
    elif "#calliolive" in title_lower:
        tag = "🔴 LIVE (title)"

    else:
        tag = "🎬 NEW VIDEO"

    # 更新 README.md
    readme_content = f"""# 最新视频 / Latest Video

{tag} - [{title}]({link})

![封面]({thumbnail})

---

"""
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            current_readme = f.read()
        # 检查是否已有最新视频部分，如果有则替换
        if current_readme.startswith("# 最新视频 / Latest Video"):
            # 找到第一个 --- 后的内容
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

        # 提交更改到 git
        try:
            subprocess.run(["git", "config", "--global", "user.name", "GitHub Actions"], check=True)
            subprocess.run(["git", "config", "--global", "user.email", "actions@github.com"], check=True)
            subprocess.run(["git", "add", "README.md"], check=True)
            result = subprocess.run(["git", "commit", "-m", f"Update README with new video: {title}"], capture_output=True, text=True)
            if result.returncode == 0:
                subprocess.run(["git", "push"], check=True)
                print("Git 提交成功")
            else:
                print("没有更改需要提交")
        except Exception as e:
            print("Git 操作失败:", e)

    except Exception as e:
        print("README.md 更新失败:", e)

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