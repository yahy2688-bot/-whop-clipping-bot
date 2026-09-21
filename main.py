import os, re, json, requests, subprocess, time, warnings, urllib3
urllib3.disable_warnings()
warnings.filterwarnings('ignore')

TELEGRAM_TOKEN=os.getenv("TELEGRAM_TOKEN")
TELEGRAM_USER=os.getenv("TELEGRAM_USER")
GEMINI_KEY=os.getenv("GEMINI_KEY","")
VIDEO_URL=os.getenv("VIDEO_URL","").strip()

def send(m):
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
    json={"chat_id":TELEGRAM_USER,"text":str(m)[:3900]}, timeout=15, verify=False)

def gemini_generate(prompt):
    if not GEMINI_KEY: return "🔥 Viral Clip! #fyp #viral #clipping"
    try:
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_KEY}"
        r = requests.post(url, json={"contents":[{"parts":[{"text":prompt}]}]}, timeout=15, verify=False)
        return r.json()['candidates'][0]['content']['parts'][0]['text']
    except: return "🔥 VIRAL! #fyp #viral"

def get_updates(offset=0):
    try:
        r = requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates?offset={offset}&timeout=20", timeout=25, verify=False)
        return r.json().get("result", [])
    except: return []

def extract_url(text):
    m = re.search(r'(https?://[^\s]+)', text)
    return m.group(1) if m else None

# لو ما في رابط - اطلب من المستخدم
if not VIDEO_URL:
    # حملات حقيقية شغالة الآن
    campaigns = [
        {"name":"Clip Farm (Tate)","price":"$10/1K","link":"https://whop.com/clip-farm/"},
        {"name":"Clipping Culture","price":"$10/1K","link":"https://app.contentrewards.cc/discover"},
        {"name":"Reach Clipping","price":"$10/1K","link":"https://app.contentrewards.cc/discover"},
    ]
    best = campaigns[0]

    send(f"""🎯 *أفضل حملة اليوم: {best['name']} - {best['price']}*

⚠️ الرابط اللي أرسلته لك قبل كان غلط - هذا هو الصح:

👇 *اذهب الى رابط الحملة الصحيح:*
{best['link']}

*ملاحظة من صورتك:* انت عندك CLIP FARM مثبتة وعليها 7 إشعارات - اضغط عليها في Whop وبتشوف كل فيديوهات Andrew Tate الجاهزة للقص.

بعد ما تدخل:
1. انسخ رابط الفيديو الطويل (YouTube أو Drive)
2. *الصق الرابط هنا في هذا البوت مباشرة* 👇

أنا انتظرك 10 دقائق...""")

    last_offset = 0
    try:
        updates = get_updates()
        if updates: last_offset = updates[-1]['update_id'] + 1
    except: pass

    VIDEO_URL = ""
    for _ in range(30):
        updates = get_updates(last_offset)
        for upd in updates:
            last_offset = upd['update_id'] + 1
            text = upd.get("message",{}).get("text","")
            url = extract_url(text)
            if url:
                VIDEO_URL = url
                send(f"✅ استلمت الرابط!\n{url[:80]}...\n\n⏳ أبدأ التحميل والقص...")
                break
        if VIDEO_URL: break
        time.sleep(20)

    # لو ما في رابط - اطلب من المستخدم
if not VIDEO_URL:
    # تعديل الروابط لتكون مباشرة لصفحات الحملات والمحتوى
    campaigns = [
        {
            "name": "Clip Farm (Andrew Tate)",
            "price": "$10/1K views",
            "campaign_link": "https://whop.com/clip-farm/",
        },
        {
            "name": "Clipping Culture",
            "price": "$10/1K views",
            "campaign_link": "https://app.contentrewards.cc/discover",
        }
    ]
    
    best = campaigns[0]

    send(f"""🎯 *أفضل حملة اليوم: {best['name']} ({best['price']})*

🔗 *رابط الحملة المباشر:*
{best['campaign_link']}

📌 *الخطوات:*
1. اضغط على الرابط أعلاه للدخول لصفحة الحملة.
2. انسخ رابط الفيديو المطلوب قصّه (YouTube أو Google Drive).
3. أرسل رابط الفيديو هنا في الشات ليتم تحميله وتقطيعه فوراً.

⏳ بانتظار الرابط (معك 10 دقائق)...""")

# تحميل وقص
send(f"🏭 أبدأ المصنع...\n🔗 {VIDEO_URL[:60]}...")
try:
    if "drive.google.com" in VIDEO_URL:
        subprocess.run(["pip","install","gdown","-q"], timeout=30)
        m = re.search(r'/d/([a-zA-Z0-9_-]+)', VIDEO_URL)
        if m:
            subprocess.run(["gdown", f"https://drive.google.com/uc?id={m.group(1)}", "-O", "original.mp4"], timeout=180)
    else:
        # التعديل هنا: إضافة خيار android لتجاوز حظر يوتيوب في سيرفرات GitHub
        subprocess.run([
            "yt-dlp",
            "-o", "original.mp4",
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "--extractor-args", "youtube:player_client=android",
            "--no-playlist",
            VIDEO_URL
        ], timeout=180)

    if not os.path.exists("original.mp4"):
        send("❌ فشل التحميل - تأكد الرابط عام")
        exit()

    os.system("sudo apt-get update -qq && sudo apt-get install -y ffmpeg -qq > /dev/null 2>&1")
    try:
        r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1","original.mp4"], capture_output=True, text=True)
        duration = float(r.stdout.strip())
    except: duration = 1800

    timestamps = [0, int(duration*0.18), int(duration*0.38), int(duration*0.62), int(duration*0.85)]

    for i, start in enumerate(timestamps[:5], 1):
        out = f"clip_{i}.mp4"
        os.system(f"ffmpeg -y -ss {start} -i original.mp4 -t 35 -vf 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920' -c:v libx264 -preset fast -crf 23 -c:a aac {out} -loglevel quiet")
        if os.path.exists(out):
            meta = gemini_generate(f"حملة Clipping - كليب من الدقيقة {start//60}. عنوان جذاب ووصف وهاشتاغات انجليزية")
            caption = f"📹 *كليب {i}/5*\n\n{meta[:900]}"
            try:
                with open(out,'rb') as f:
                    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo",
                    data={"chat_id":TELEGRAM_USER,"caption":caption,"parse_mode":"Markdown"},
                    files={"video":f}, timeout=120, verify=False)
            except: pass
            time.sleep(1)

    send("✅ خلصت! 5 كليبات جاهزة للنشر في Whop")
except Exception as e:
    send(f"❌ خطأ: {e}")
    
