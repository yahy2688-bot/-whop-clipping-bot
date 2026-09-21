import os, requests
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
        if r.status_code != 200:
            return f"Whop status {r.status_code}"
        return r.text[:12000]
    except Exception as e:
        open("campaigns.png","wb").write(b"ok")
        return f"خطأ hunt: {e}"

def analyze(t):
    if not GEMINI_KEY:
        return "خطأ: GEMINI_KEY غير موجود في GitHub Secrets!"
    try:
        from google import genai
        client=genai.Client(api_key=GEMINI_KEY)
        # جرب كل الموديلات المتاحة
        models = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-flash-8b"]
        last_err = ""
        for model in models:
            try:
                res=client.models.generate_content(
                    model=model, 
                    contents=f"حلل حملات Whop Clipping واختر افضل 3 مع السعر: {t[:7000]}"
                )
                return f"✅ بالموديل {model}:\n{res.text}"
            except Exception as e:
                last_err = str(e)[:500]
                continue
        return f"فشل كل موديلات Gemini. آخر خطأ: {last_err}"
    except Exception as e:
        return f"Gemini خطأ مكتبة: {e}"

if __name__=="__main__":
    txt=hunt()
    res=analyze(txt)
    print(res)
    send(f"📊 {res[:3800]}")
