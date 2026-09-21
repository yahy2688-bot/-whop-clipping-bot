import os, requests, json
TELEGRAM_TOKEN=os.getenv("TELEGRAM_TOKEN")
TELEGRAM_USER=os.getenv("TELEGRAM_USER")
GEMINI_KEY=os.getenv("GEMINI_KEY")

def send(m):
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={"chat_id":TELEGRAM_USER,"text":m[:3900]}, timeout=15)
    except: pass

def hunt():
    send("🚀 بدأ الفحص (نسخة الجوال)...")
    try:
        headers={"User-Agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 17_0)"}
        r=requests.get("https://whop.com/discover/clipping/", headers=headers, timeout=30)
        open("campaigns.png","wb").write(b"ok")
        return r.text
    except Exception as e:
        open("campaigns.png","wb").write(b"ok")
        return f"خطأ: {e}"

def analyze_with_gemini_direct(text):
    if not GEMINI_KEY:
        return "❌ GEMINI_KEY غير موجود في Secrets"

    # 1. نجيب قائمة الموديلات المتاحة من جوجل مباشرة
    try:
        list_url = f"https://generativelanguage.googleapis.com/v1/models?key={GEMINI_KEY}"
        models_res = requests.get(list_url, timeout=15).json()
        # نختار أول موديل يدعم generateContent
        available = [m['name'] for m in models_res.get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])]
        if not available:
            available = ["models/gemini-1.5-flash-latest", "models/gemini-1.5-flash", "models/gemini-pro-latest"]
    except:
        available = ["models/gemini-1.5-flash-latest", "models/gemini-1.5-flash"]

    # 2. نجرب كل موديل برابط مباشر v1 (ليس v1beta)
    clean_text = text[:8000].replace('"', "'")[:7000]
    prompt = f"حلل حملات Whop Clipping هذه واستخرج افضل 3 حملات مع السعر والشروط: {clean_text}"

    last_err = ""
    for model_name in available[:4]: # جرب أول 4 فقط
        try:
            url = f"https://generativelanguage.googleapis.com/v1/{model_name}:generateContent?key={GEMINI_KEY}"
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            r = requests.post(url, json=payload, timeout=30)
            if r.status_code == 200:
                data = r.json()
                result = data['candidates'][0]['content']['parts'][0]['text']
                return f"✅ نجح بالموديل {model_name}\n{result}"
            else:
                last_err = f"{model_name}: {r.text[:300]}"
        except Exception as e:
            last_err = str(e)[:400]
            continue

    # 3. إذا فشل كل شي، نرجع تحليل بدون ذكاء اصطناعي (عشان البوت ما يفشل)
    # نستخرج الحملات بـ regex مباشرة
    import re
    titles = re.findall(r'"name"\s*:\s*"([^"]{5,80})"', text)[:5]
    if titles:
        return f"⚠️ Gemini فشل مؤقتا ({last_err[:200]}), لكن لقيت هذه الحملات مباشرة:\n" + "\n".join([f"- {t}" for t in titles])
    else:
        return f"❌ فشل Gemini نهائي. آخر خطأ: {last_err}"

if __name__=="__main__":
    txt=hunt()
    res=analyze_with_gemini_direct(txt)
    print(res)
    send(f"📊 {res[:3800]}")
