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
        return r.text[:12000]
    except Exception as e:
        open("campaigns.png","wb").write(b"ok")
        return f"خطأ hunt: {e}"

def analyze(t):
    if not GEMINI_KEY:
        return "خطأ: GEMINI_KEY غير موجود!"
    try:
        # نستخدم المكتبة القديمة المستقرة
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_KEY)
        
        # جرب الموديلات الصحيحة الجديدة
        models_to_try = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
        last_err = ""
        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                res = model.generate_content(f"حلل حملات Whop Clipping واختر افضل 3 مع السعر والشروط: {t[:7000]}")
                return f"✅ بالموديل {model_name}:\n{res.text}"
            except Exception as e:
                last_err = str(e)[:600]
                continue
        
        return f"فشل كل الموديلات. آخر خطأ: {last_err}"
    except Exception as e:
        return f"Gemini خطأ: {e}"

if __name__=="__main__":
    txt=hunt()
    res=analyze(txt)
    print(res)
    send(f"📊 {res[:3800]}")
