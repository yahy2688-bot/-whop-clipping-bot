import os, requests, re, json
TELEGRAM_TOKEN=os.getenv("TELEGRAM_TOKEN")
TELEGRAM_USER=os.getenv("TELEGRAM_USER")
GEMINI_KEY=os.getenv("GEMINI_KEY")

def send(m):
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={"chat_id":TELEGRAM_USER,"text":m[:3900]}, timeout=15)
    except: pass

def hunt():
    send("🚀 بدأ الفحص - أبحث في المكان المخفي...")
    try:
        headers={
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept":"text/html"
        }
        # نجرب كل الروابط الجديدة
        urls=[
            "https://whop.com/discover/clipping/",
            "https://whop.com/discover/content-rewards/",
            "https://whop.com/discover/"
        ]
        full_html = ""
        for url in urls:
            r=requests.get(url, headers=headers, timeout=30)
            if len(r.text) > 10000:
                full_html = r.text
                break

        open("campaigns.png","wb").write(b"ok")

        # الطريقة السحرية: Whop يخبئ البيانات في self.__next_f
        campaigns_text = ""
        # ابحث عن كل self.__next_f.push
        matches = re.findall(r'self\.__next_f\.push\((.*?)\)', full_html, re.DOTALL)
        for m in matches:
            if 'clipping' in m.lower() or 'cpm' in m.lower() or 'reward' in m.lower() or 'campaign' in m.lower():
                campaigns_text += m[:5000] + "\n"

        # لو ما لقينا، ناخذ كل الصفحة كاملة ونفلترها
        if not campaigns_text:
            # دور على أي كلمة تدل على حملة
            if '"title"' in full_html:
                # استخرج 20000 حرف من الوسط حيث تكون الحملات عادة
                campaigns_text = full_html[20000:80000]
            else:
                campaigns_text = full_html[:15000]

        return campaigns_text[:12000]

    except Exception as e:
        open("campaigns.png","wb").write(b"ok")
        return f"خطأ hunt: {e}"

def analyze_direct(text):
    if not GEMINI_KEY:
        return "❌ GEMINI_KEY غير موجود"
    try:
        # نفس طريقة الاتصال المباشر اللي نجحت معك
        list_url = f"https://generativelanguage.googleapis.com/v1/models?key={GEMINI_KEY}"
        models_res = requests.get(list_url, timeout=15).json()
        available = [m['name'] for m in models_res.get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])][:3]
        if not available:
            available = ["models/gemini-1.5-flash-latest"]

        clean = text[:8000].replace('"', "'")
        prompt = f"""أنت خبير Whop Clipping. حلل هذا الكود واستخرج أفضل 3 حملات clipping.
        اذكر: اسم الحملة، السعر لكل 1000 مشاهدة، الشروط.
        إذا كان الكود مشفر فك تشفيره:
        {clean}"""

        for model_name in available:
            try:
                url = f"https://generativelanguage.googleapis.com/v1/{model_name}:generateContent?key={GEMINI_KEY}"
                payload = {"contents": [{"parts": [{"text": prompt}]}]}
                r = requests.post(url, json=payload, timeout=30)
                if r.status_code == 200:
                    result = r.json()['candidates'][0]['content']['parts'][0]['text']
                    return f"✅ {model_name}\n{result}"
            except: continue

        return f"فشل، لكن هذا ما وجدته في الصفحة:\n{text[:3000]}"
    except Exception as e:
        return f"خطأ: {e}"

if __name__=="__main__":
    txt=hunt()
    res=analyze_direct(txt)
    print(res)
    send(f"📊 {res[:3800]}")
