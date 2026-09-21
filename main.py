import os, re, json, requests, subprocess, warnings, urllib3
urllib3.disable_warnings()
warnings.filterwarnings('ignore')

TELEGRAM_TOKEN=os.getenv("TELEGRAM_TOKEN")
TELEGRAM_USER=os.getenv("TELEGRAM_USER")
GEMINI_KEY=os.getenv("GEMINI_KEY","")

def send(m):
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={"chat_id":TELEGRAM_USER,"text":str(m)[:3900]}, timeout=15, verify=False)
    except: pass

def get_video_url_auto(campaign_name):
    """يجيب رابط الفيديو الأصلي لحاله من صفحة Whop"""
    slug = re.sub(r'[^a-z0-9]+','-', campaign_name.lower()).strip('-')
    # أمثلة: clipping-culture, hustlers-university
    whop_urls = [
        f"https://whop.com/{slug}",
        f"https://whop.com/discover/{slug}",
        f"https://app.contentrewards.cc/discover"
    ]

    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    for page_url in whop_urls:
        try:
            send(f"🔍 أفحص صفحة الحملة: {page_url[:40]}...")
            r = requests.get(page_url, headers=headers, timeout=10, verify=False)
            html = r.text

            # 1. دور رابط يوتيوب
            yt = re.findall(r'(https?://(?:www\.)?youtube\.com/watch\?v=[\w-]{11}|https?://youtu\.be/[\w-]{11})', html)
            if yt:
                return yt[0]

            # 2. دور Google Drive
            drive = re.findall(r'(https?://drive\.google\.com/[^"\s]+)', html)
            if drive:
                return drive[0]

        except Exception as e:
            continue

    # 3. لو ما لقى شي - ابحث في يوتيوب تلقائياً عن اسم الحملة
    # yt-dlp يقدر يبحث: ytsearch1:Clipping Culture podcast
    try:
        return f"ytsearch1:{campaign_name} official podcast"
    except:
        return None

# === البداية ===
send("🏭 المصنع الأوتوماتيكي 100% بدأ...")

# حملات اكتشفها البوت أمس (نفس اللي جاك 4 حملات)
campaigns = [
    {"name":"Hustlers University", "price":12},
    {"name":"Clipping Culture", "price":10},
    {"name":"Reach Clipping", "price":10},
    {"name":"Spencer Pratt Clipping", "price":1.5},
]

# اقرأ اللي انرسل من قبل
try:
    with open("sent_campaigns.json","r") as f:
        history=set(json.load(f))
except:
    history=set()

# اختار أفضل حملة ما انرسلت
best = None
for c in sorted(campaigns, key=lambda x: x['price'], reverse=True):
    if c['name'].lower() not in [h.lower() for h in history]:
        best = c
        break

if not best:
    send("✅ كل الحملات تم قصها! انتظر حملات جديدة بعد 6 ساعات.")
    exit()

send(f"🎯 أفضل حملة: {best['name']} - ${best['price']}/1K\n🔎 جاري جلب الفيديو الأصلي تلقائياً...")

video_url = get_video_url_auto(best['name'])

if not video_url:
    send(f"❌ ما لقيت فيديو لـ {best['name']} تلقائياً. جرب حملة ثانية.")
    exit()

send(f"📥 لقيت الفيديو: {video_url[:80]}...")

# حمل
try:
    subprocess.run(["pip","install","yt-dlp","-q"], timeout=60)
    subprocess.run(["yt-dlp","-o","original.mp4","-f","mp4","--no-playlist", video_url], timeout=180)
except Exception as e:
    send(f"❌ فشل التحميل: {e}")
    exit()

if not os.path.exists("original.mp4"):
    send("❌ فشل التحميل - الملف غير موجود")
    exit()

size = os.path.getsize("original.mp4")/1024/1024
send(f"✅ تم التحميل {size:.1f} MB - أبدأ القص...")

# قص
try:
    os.system("sudo apt-get update -qq && sudo apt-get install -y ffmpeg -qq > /dev/null 2>&1")
    clips=[]
    for i, start in enumerate([0, 40, 80]):
        out=f"clip_{i+1}.mp4"
        cmd=f"ffmpeg -y -ss {start} -i original.mp4 -t 30 -vf 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920' -c:a aac {out} -loglevel quiet"
        os.system(cmd)
        if os.path.exists(out): clips.append(out)

    # كابشن
    caption = f"{best['name']} is INSANE 🔥 Must watch!"
    if GEMINI_KEY:
        try:
            prompt = f"كابشن انجليزي فيروسي قصير + 5 هاشتاغات لـ {best['name']}"
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_KEY}"
            r = requests.post(url, json={"contents":[{"parts":[{"text":prompt}]}]}, timeout=10, verify=False)
            caption = r.json()['candidates'][0]['content']['parts'][0]['text']
        except: pass

    for clip in clips:
        with open(clip,'rb') as f:
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo",
            data={"chat_id":TELEGRAM_USER,"caption":f"{best['name']} | {clip}\n{caption[:150]}"},
            files={"video":f}, timeout=90, verify=False)

    # احفظ عشان ما يعيدها
    history = list(history) + [best['name']]
    with open("sent_campaigns.json","w") as f:
        json.dump(history[-200:], f)

    send(f"✅ خلص! {len(clips)} كليب من {best['name']} جاهز\n\nالآن: انشرهم على TikTok/Reels → انسخ الرابط → Whop → Submit → الأرباح تنحسب!")

except Exception as e:
    send(f"❌ خطأ القص: {e}")
