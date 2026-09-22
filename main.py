import os, re, json, requests, subprocess, time, warnings, urllib3, random
urllib3.disable_warnings()
warnings.filterwarnings('ignore')

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_USER = os.getenv("TELEGRAM_USER")
GEMINI_KEY = os.getenv("GEMINI_KEY", "")

def send(m):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_USER, "text": str(m)[:4000], "parse_mode": "Markdown"},
            timeout=15, verify=False
        )
    except Exception as e:
        print(f"Send error: {e}")

def send_video(video_path, caption):
    """دالة مخصصة لإرسال الفيديوهات وتأكيد النجاح"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo"
    
    # التأكد من أن حجم الفيديو ليس صفر وقابل للإرسال
    if not os.path.exists(video_path) or os.path.getsize(video_path) < 10000:
        print(f"[!] File {video_path} is empty or missing.")
        return False

    for attempt in range(3):
        try:
            with open(video_path, 'rb') as f:
                r = requests.post(
                    url,
                    data={"chat_id": TELEGRAM_USER, "caption": caption[:1024], "parse_mode": "Markdown"},
                    files={"video": f},
                    timeout=300,
                    verify=False
                )
                if r.status_code == 200:
                    print(f"[+] Successfully sent {video_path}")
                    return True
                else:
                    print(f"[!] Telegram API error ({r.status_code}): {r.text}")
        except Exception as e:
            print(f"[!] Attempt {attempt+1} failed for {video_path}: {e}")
        time.sleep(3)
    return False

def gemini_generate(prompt):
    if not GEMINI_KEY: 
        return "🔥 Viral Clipping Clip! #fyp #viral #shorts #clipping"
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        r = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=15, verify=False)
        data = r.json()
        if 'candidates' in data and len(data['candidates']) > 0:
            return data['candidates'][0]['content']['parts'][0]['text']
        else:
            return "🔥 Epic Podcast Moments! #fyp #clipping #viral #shorts"
    except Exception as e: 
        return "🔥 Epic Podcast Moments! #fyp #clipping #viral #shorts"

def select_campaign_with_rules():
    # بنك الحملات مع الروابط الشغالة المباشرة والفيديوهات المضمونة
    campaigns = [
        {
            "name": "Clip Farm - Andrew Tate",
            "price": "$10/1K views",
            "link": "https://whop.com/clip-farm/",
            "rules": {
                "max_duration": 30,
                "style": "Vertical 9:16 High-Energy Fast Cuts",
                "required_hashtags": "#AndrewTate #ClipFarm #Motivation #Mindset #Viral",
                "caption_instructions": "Focus on high-energy motivational hooks and strong statements."
            },
            "videos": ["https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"]
        },
        {
            "name": "Clipping Culture",
            "price": "$10/1K views",
            "link": "https://whop.com/discover/",
            "rules": {
                "max_duration": 35,
                "style": "Vertical 9:16 Podcast Highlights",
                "required_hashtags": "#ClippingCulture #PodcastClips #Storytime #ViralShorts",
                "caption_instructions": "Focus on engaging storytelling hooks and intriguing questions."
            },
            "videos": ["https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4"]
        }
    ]

    selected = random.choice(campaigns)
    selected_video = random.choice(selected["videos"])

    msg = f"""🎯 *تم اختيار الحملة وتفعيل شروطها تلقائياً!*

📌 *اسم الحملة:* {selected['name']}
💰 *العائد:* {selected['price']}
🔗 *رابط الحملة المباشر:* {selected['link']}

📜 *شروط وقواعد الحملة المطلوبة:*
• **طريقة القص:** {selected['rules']['style']}
• **مدة الكليب:** حتى {selected['rules']['max_duration']} ثانية
• **الهاشتاغات الإلزامية:** `{selected['rules']['required_hashtags']}`

⏳ *جاري تحميل الفيديو المباشر ومعالجته فوراً...*"""
    
    send(msg)
    return selected, selected_video

def run_auto_factory():
    campaign, video_url = select_campaign_with_rules()
    rules = campaign["rules"]

    try:
        # تحميل أوتوماتيكي مباشر بـ curl لضمان توافق الصوت والصورة
        send("⬇️ *جاري تحميل فيديو الحملة الأصلي...*")
        subprocess.run(["curl", "-L", "-o", "original.mp4", video_url], timeout=120)

        if not os.path.exists("original.mp4") or os.path.getsize("original.mp4") < 10000:
            send("❌ تعذر تحميل فيديو الحملة المباشر.")
            return

        # تثبيت وتجهيز FFmpeg
        os.system("sudo apt-get update -qq && sudo apt-get install -y ffmpeg -qq > /dev/null 2>&1")
        
        # نقاط القص 
        timestamps = [0, 3, 6, 9, 12]
        clip_duration = rules["max_duration"]
        sent_count = 0

        for i, start in enumerate(timestamps, 1):
            out = f"clip_{i}.mp4"
            # أمر FFmpeg معدل ومضمون 100% للقص والضغط السريع لشبكة تليجرام
            cmd = f"ffmpeg -y -ss {start} -i original.mp4 -t {clip_duration} -vf 'scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280' -c:v libx264 -pix_fmt yuv420p -preset ultrafast -crf 26 -c:a aac -b:a 128k {out} -loglevel quiet"
            os.system(cmd)
            
            if os.path.exists(out) and os.path.getsize(out) > 10000:
                prompt = f"""
               Write a viral video caption for a Short video clipped from the campaign '{campaign['name']}'.
               Instructions:
               1. {rules['caption_instructions']}
               2. Include these exact mandatory hashtags at the end: {rules['required_hashtags']}
               3. Make the title bold, punchy, and captivating.
                """
                
                meta = gemini_generate(prompt)
                caption = f"🎬 *كليب مطبق عليه شروط الحملة ({i}/5)*\n\n{meta[:900]}"
                
                success = send_video(out, caption)
                if success:
                    sent_count += 1
                else:
                    send(f"⚠️ تعذر إرسال الكليب رقم {i} إلى تليجرام.")
                
                time.sleep(2)

        send(f"🎉 *تم إنجاز العملية!* تم إرسال {sent_count}/5 كليبات مطابقة لشروط ({campaign['name']}) بنجاح.")

    except Exception as e:
        send(f"❌ حدث خطأ أثناء المعالجة: {e}")

if __name__ == "__main__":
    run_auto_factory()
    
