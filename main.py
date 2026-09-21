import os, requests, json
TELEGRAM_TOKEN=os.getenv("TELEGRAM_TOKEN")
TELEGRAM_USER=os.getenv("TELEGRAM_USER")
GEMINI_KEY=os.getenv("GEMINI_KEY")

def send(m):
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={"chat_id":TELEGRAM_USER,"text":m[:3900]}, timeout=20)
    except: pass

def get_campaigns():
    send("🚀 أبحث عن حملات من API المفتوح...")
    headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    # المحاولة 1: LiquidClips API - يرجع حملات Whop جاهزة
    try:
        r=requests.get("https://api.liquidclips.app/campaigns", headers=headers, timeout=20)
        if r.status_code==200:
            data=r.json()
            if isinstance(data, list) and len(data)>0:
                return json.dumps(data[:5], indent=2), "liquidclips"
            if isinstance(data, dict) and "campaigns" in data:
                return json.dumps(data["campaigns"][:5], indent=2), "liquidclips"
    except Exception as e:
        print(f"liquidclips fail: {e}")

    # المحاولة 2: Whop Content Rewards Hub
    try:
        r=requests.get("https://whop.com/hub/content-rewards/", headers=headers, timeout=20)
        if r.status_code==200 and "clipping" in r.text.lower():
            return r.text[20000:60000], "whop-hub"
    except: pass

    return "ما لقيت حملات - API مقفل حالياً. جرب مرة ثانية.", "none"

def analyze_with_gemini(text, source):
    if not GEMINI_KEY or len(text)<50:
        return f"📊 من {source}:\n{text[:3500]}"

    prompt=f"""حلل هذه الحملات من {source} واستخرج أفضل 3:
{text[:7000]}

لكل حملة اذكر:
- اسمها
- السعر RPM (اقسم rpm_cents على 100 اذا موجود)
- الشروط
بالعربي مختصر."""

    for model in ["models/gemini-1.5-flash-latest", "models/gemini-1.5-flash", "models/gemma-3-27b-it"]:
        try:
            url=f"https://generativelanguage.googleapis.com/v1/{model}:generateContent?key={GEMINI_KEY}"
            resp=requests.post(url, json={"contents":[{"parts":[{"text":prompt}]}]}, timeout=30)
            if resp.status_code==200:
                ans=resp.json()['candidates'][0]['content']['parts'][0]['text']
                return f"✅ من {source} عبر {model}:\n{ans}"
        except Exception as e:
            print(f"{model} fail: {e}")
            continue

    return f"📊 حملات من {source}:\n{text[:3500]}"

if __name__=="__main__":
    data, src = get_campaigns()
    result = analyze_with_gemini(data, src)
    print(result)
    send(result)
