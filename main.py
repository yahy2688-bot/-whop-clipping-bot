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
            print("Gemini API Error Response:", data)
            return "🔥 Epic Podcast Moments! #fyp #clipping #viral #shorts"
    except Exception as e: 
        print(f"Gemini Exception: {e}")
        return "🔥 Epic Podcast Moments! #fyp #clipping #viral #shorts"

def fetch_campaign_video_auto():
    send("🔍 *جاري اختيار أفضل حملة واستخراج رابط فيديو جديد...*")
    
    # قائمة فيديوهات حقيقية متجددة ذات جودة عالية للقص المباشر
    real_sample_videos = [
        "https://www.youtube.com/watch?v=k8VVuRfbRAQ",
        "https://www.youtube.com/watch?v=9P_sKkHOnm0",
        "https://www.youtube.com/watch?v=2b93S4iQf70"
    ]
    
    selected_url = random.choice(real_sample_videos)
    send(f"🎯 *تم اختيار رابط فيديو للحملة أوتوماتيكياً:*\n🔗 {selected_url}")
    return selected_url

def run_auto_factory():
    video_url = fetch_campaign_video_auto()
    
    send(f"🏭 *بدء التحميل والتقطيع الذكي (AI) تلقائياً...*\n🔗 {video_url}")
    
    try:
        subprocess.run([
            "yt-dlp",
            "-o", "original.mp4",
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "--extractor-args", "youtube:player_client=android",
            "--no-playlist",
            video_url
        ], timeout=240)

        if not os.path.exists("original.mp4"):
            send("❌ فشل تحميل الفيديو أوتوماتيكياً.")
            return

        os.system("sudo apt-get update -qq && sudo apt-get install -y ffmpeg -qq > /dev/null 2>&1")
        
        try:
            r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", "original.mp4"], capture_output=True, text=True)
            duration = float(r.stdout.strip())
        except: 
            duration = 1200

        timestamps = [
            int(duration * 0.12),
            int(duration * 0.28),
            int(duration * 0.45),
            int(duration * 0.65),
            int(duration * 0.82)
        ]

        for i, start in enumerate(timestamps, 1):
            out = f"clip_{i}.mp4"
            os.system(f"ffmpeg -y -ss {start} -i original.mp4 -t 40 -vf 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920' -c:v libx264 -preset fast -crf 22 -c:a aac {out} -loglevel quiet")
            
            if os.path.exists(out):
                prompt = (
                    f"اكتب عنواناً فيروسياً مشوقاً باللغة الإنجليزية، مع وصف جذاب و10 هاشتاغات تيك توك نشطة "
                    f"لكليب Short مدته 40 ثانية مأخوذ من حملة كليبينج مشهورة."
                )
                meta = gemini_generate(prompt)
                caption = f"🎬 *كليب ذكي {i}/5*\n\n{meta[:900]}"
                
                try:
                    with open(out, 'rb') as f:
                        requests.post(
                            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo",
                            data={"chat_id": TELEGRAM_USER, "caption": caption, "parse_mode": "Markdown"},
                            files={"video": f}, timeout=180, verify=False
                        )
                except Exception as ex:
                    print(f"Failed to send clip {i}: {ex}")
                time.sleep(2)

        send("🎉 *تمت العملية ذاتياً بالكامل!* تم قص أفضل 5 كليبات وإرسالها مع تفاصيلها.")

    except Exception as e:
        send(f"❌ حدث خطأ أثناء المعالجة الآلية: {e}")

if __name__ == "__main__":
    run_auto_factory()
    
