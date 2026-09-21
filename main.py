import os, requests
TELEGRAM_TOKEN=os.getenv("TELEGRAM_TOKEN")
TELEGRAM_USER=os.getenv("TELEGRAM_USER")
GEMINI_KEY=os.getenv("GEMINI_KEY")

def send(m):
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", json={"chat_id":TELEGRAM_USER,"text":m[:3900]}, timeout=20)

def hunt_real():
    send("🚀 أبحث عن حملات حقيقية من API...")
    open("campaigns.png","wb").write(b"ok")
    try:
        # مصدر 1: LiquidClips API - يجيب حملات Whop الحقيقية
        r = requests.get("https://api.liquidclips.app/campaigns", timeout=20)
        if r.status_code == 200:
            data = r.json()
            campaigns = data[:5] if isinstance(data, list) else data.get('campaigns', [])[:5]
            return json.dumps(campaigns)[:10000], "liquidclips"
    except Exception as e:
        pass

    try:
        # مصدر 2: contentrewards.com
        r = requests.get("https://contentrewards.com/discover", headers={"User-Agent":"Mozilla/5.0"}, timeout=20)
        return r.text[:10000], "contentrewards"
    except Exception as e:
        return f"فشل: {e}", "none"

def analyze(campaigns_json, source):
    if not GEMINI_KEY:
        return campaigns_json[:2000]
    try:
        prompt = f"""أنت خبير Whop Clipping. هذه حملات حقيقية من {source}:
{campaigns_json[:6000]}

اختر أفضل 3 حملات تدفع أكثر. لكل حملة اذكر:
- اسم الحملة
- السعر RPM بالدولار (اقسم rpm_cents على 100)
- شروطها
- رابط الفيديو الأصلي
بالعربي وبشكل مختصر."""

        for model in ["models/gemini-1.5-flash-latest", "models/gemini-1.5-flash", "models/gemma-3-27b-it"]:
            try:
                url = f"https://generativelanguage.googleapis.com/v1/{model}:generateContent?key={GEMINI_KEY}"
                res = requests.post(url, json={"contents":[{"parts":[{"text":prompt}]}]}, timeout=30)
                if res.status_code == 200:
                    txt = res.json()['candidates'][0]['content']['parts'][0]['text']
                    return f"✅ من {source} عبر {model}:\n{txt}"
            except: continue
        return f"📊 حملات من {source}:\n{campaigns_json[:3500]}"
    except Exception as e:
        return f"خطأ تحليل: {e}\nالبيانات: {campaigns_json[:2000]}"

if __name__ == "__main__":
    import json
    data, src = hunt_real()
    result = analyze(data, src)
    print(result)
    send(result[:3900])
