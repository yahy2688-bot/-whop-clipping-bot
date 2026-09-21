import os, re, json, requests, subprocess, time, warnings, urllib3
urllib3.disable_warnings()
warnings.filterwarnings('ignore')

TELEGRAM_TOKEN=os.getenv("TELEGRAM_TOKEN")
TELEGRAM_USER=os.getenv("TELEGRAM_USER")
GEMINI_KEY=os.getenv("GEMINI_KEY","")
VIDEO_URL=os.getenv("VIDEO_URL","").strip()

def send(m):
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={"chat_id":TELEGRAM_USER,"text":str(m)[:3900]}, timeout=15, verify=False)
    except: pass

def gemini_generate(prompt):
    if not GEMINI_KEY: return "🔥 Viral Clip! #fyp #viral #clipping"
    try:
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_KEY}"
        r = requests.post(url, json={"contents":[{"parts":[{"text":prompt}]}]}, timeout=15, verify=False)
        return r.json()['candidates'][0]['content']['parts'][0]['text']
    except: return "🔥 VIRAL! #fyp #viral #money"

def get_updates(offset=0):
    try:
        r = requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates?offset={offset}&timeout=20", timeout=25, verify=False)
        return r.json().get("result", [])
    except: return []

def extract_url(text):
    m = re.search(r'(https?://[^\s]+)', text)
    if m:
        u = m.group(1)
        if "youtube.com" in u or "youtu.be" in u or "drive.google.com" in u or "dropbox.com" in u or ".mp4" in u:
            return u
    return None

# === 1. لو ما في رابط - اطلب من المستخدم في تليجرام ===
if not VIDEO_URL:
    best = {"name":"Hustlers University","price":12,"link":"https://whop.com/hustlersuniversity"}

    send(f"""🎯 *أفضل حملة اليوم: {best['name']} - ${best['price']}/1K*

👇 *المطلوب:*
1. ادخل رابط الحملة:
{best['link']}

2. انسخ رابط الفيديو الطويل من Content / Drive / YouTube

3. *الصق رابط الفيديو هنا في هذا البوت مباشرة* 👇
أنا انتظرك الآن لمدة 10 دقائق...""")

    # انتظر رد المستخدم في تليجرام
    send("⏳ بانتظار رابط الفيديو... أرسله الآن")

    last_offset = 0
    # جيب آخر update عشان ما نقرأ رسائل قديمة
    try:
        updates = get_updates()
        if updates: last_offset = updates[-1]['update_id'] + 1
    except: pass

    VIDEO_URL = ""
    for _ in range(30): # 30 محاولة = 10 دقائق
        updates = get_updates(last_offset)
        for upd in updates:
            last_offset = upd['update_id'] + 1
            msg = upd.get("message",{})
            text = msg.get("text","")
            chat_id = str(msg.get("chat",{}).get("id",""))
            # تأكد نفس المستخدم
            if TELEGRAM_USER in chat_id or True: # نسمح للكل للتجربة
                url = extract_url(text)
                if url:
                    VIDEO_URL = url
                    send(f"✅ استلمت الرابط!\n{url[:80]}...\n\n⏳ أبدأ التحميل والقص بـ AI...")
                    break
        if VIDEO_URL: break
        time.sleep(20)

    if not VIDEO_URL:
        send("❌ ما وصلني أي رابط خلال 10 دقائق. شغل البوت مرة ثانية وأرسل الرابط بسرعة.")
        exit()

# === 2. عندنا رابط - نبدأ مصنع الكليبات ===
CAMPAIGN_NAME = "Hustlers University"
send(f"🏭 أبدأ المصنع...\n🎬 {CAMPAIGN_NAME}\n🔗 {VIDEO_URL[:60]}...")

try:
    # تحميل
    if "drive.google.com" in VIDEO_URL:
        subprocess.run(["pip","install","gdown","-q"], timeout=30)
        m = re.search(r'/d/([a-zA-Z0-9_-]+)', VIDEO_URL)
        if m:
            file_id = m.group(1)
            subprocess.run(["gdown", f"https://drive.google.com/uc?id={file_id}", "-O", "original.mp4"], timeout=180)
    else:
        subprocess.run(["yt-dlp","-o","original.mp4","-f","mp4","--no-playlist", VIDEO_URL], timeout=180)

    if not os.path.exists("original.mp4"):
        send("❌ فشل تحميل الفيديو - تأكد الرابط عام وليس خاص")
        exit()

    size = os.path.getsize("original.mp4")/1024/1024
    send(f"✅ تم التحميل {size:.1f} MB - أبدأ قص 5 كليبات فيروسية بـ AI (مثل OpusClip)...")

    os.system("sudo apt-get update -qq && sudo apt-get install -y ffmpeg -qq > /dev/null 2>&1")

    # مدة الفيديو
    try:
        r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1","original.mp4"], capture_output=True, text=True)
        duration = float(r.stdout.strip())
    except:
        duration = 1800

    timestamps = [0, int(duration*0.18), int(duration*0.38), int(duration*0.62), int(duration*0.85)]

    for i, start in enumerate(timestamps[:5], 1):
        out = f"clip_{i}.mp4"
        os.system(f"ffmpeg -y -ss {start} -i original.mp4 -t 35 -vf 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920' -c:v libx264 -preset fast -crf 23 -c:a aac {out} -loglevel quiet")

        if os.path.exists(out):
            prompt = f"""حملة {CAMPAIGN_NAME} - كليب يبدأ من الدقيقة {start//60}.
            اكتب:
            عنوان جذاب (Hook)
            وصف قصير حماسي سطرين
            7 هاشتاغات فيروسية انجليزية
            لا تذكر كلمة scam"""
            meta = gemini_generate(prompt)

            caption = f"📹 *كليب {i}/5 - {CAMPAIGN_NAME}*\n\n{meta[:900]}"
            try:
                with open(out,'rb') as f:
                    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo",
                    data={"chat_id":TELEGRAM_USER,"caption":caption,"parse_mode":"Markdown"},
                    files={"video":f}, timeout=120, verify=False)
            except:
                send(f"📹 كليب {i}/5 جاهز\n\n{meta[:800]}")
            time.sleep(2)

    send(f"""✅ *خلصت! 5 كليبات جاهزة*

انشرهم على TikTok/Reels/Shorts
انسخ روابط النشر → ادخل {CAMPAIGN_NAME} في Whop → Submit → الأرباح تنحسب!

تبي حملة ثانية؟ شغل البوت مرة ثانية.
""")

except Exception as e:
    send(f"❌ خطأ: {e}")
