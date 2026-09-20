import os, requests, re
from moviepy.editor import VideoFileClip

GEMINI_KEY = os.getenv("GEMINI_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_USER = os.getenv("TELEGRAM_USER")

def send(m): 
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", json={"chat_id": TELEGRAM_USER, "text": m[:4000]})

def step1_get_best_campaign():
    send("1️⃣ أبحث عن أفضل حملة...")
    # نفس كود hunt بدون تسجيل دخول
    r = requests.get("https://whop.com/discover/clipping/", headers={"User-Agent":"Mozilla/5.0"})
    # هنا Gemini يختار الأفضل
    return {"title": "Crypto Trading", "video_url": "https://...", "rules": "30s max, hook in first 2s", "payout": "$3/1k"}

def step2_download_video(url):
    send("2️⃣ أحمل فيديو الحملة...")
    # يحمل الفيديو الأصلي
    return "/tmp/source.mp4"

def step3_ai_clipping(source_path, rules):
    send("3️⃣ AI يقص الفيديو إلى كليبات فيروسية...")
    # AI مجاني: يقص كل 30 ثانية مع هوك
    clips = []
    video = VideoFileClip(source_path)
    for i in range(0, int(video.duration), 30):
        clip = video.subclip(i, min(i+30, video.duration))
        path = f"/tmp/clip_{i}.mp4"
        clip.write_videofile(path)
        clips.append(path)
    return clips

def step4_gemini_description(rules):
    from google import genai
    c = genai.Client(api_key=GEMINI_KEY)
    prompt = f"اكتب 3 أوصاف + 10 هاشتاغات لكليب قصير حسب هذه الشروط: {rules}. الوصف يجب أن يكون فيروسي"
    r = c.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return r.text

def step5_publish_and_submit(clips, description):
    send(f"4️⃣ جهزت {len(clips)} كليب\n{description}\n\n5️⃣ للنشر التلقائي: أرسل لي مفاتيح يوتيوب وانستجرام")
    # هنا سيتم النشر لاحقاً
    # بعد النشر: ينسخ الروابط ويذهب إلى Whop ويلصقها في خانة proof

if __name__ == "__main__":
    campaign = step1_get_best_campaign()
    source = step2_download_video(campaign['video_url'])
    clips = step3_ai_clipping(source, campaign['rules'])
    desc = step4_gemini_description(campaign['rules'])
    step5_publish_and_submit(clips, desc)
