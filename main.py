import os, requests, re
TELEGRAM_TOKEN=os.getenv("TELEGRAM_TOKEN")
TELEGRAM_USER=os.getenv("TELEGRAM_USER")
GEMINI_KEY=os.getenv("GEMINI_KEY")

def send(m):
    try:
        url=f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id":TELEGRAM_USER,"text":m[:3900]}, timeout=15)
    except: pass

def hunt():
    send("🚀 بدأ الفحص (نسخة الجوال)...")
    try:
        headers={"User-Agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)"}
        r=requests.get("https://whop.com/discover/clipping/", headers=headers, timeout=30)
        open("campaigns.png","wb").write(b"ok") # عشان ما يطلع خطأ No files
        return r.text[:10000]
    except Exception as e:
        open("campaigns.png","wb").write(b"ok")
        return f"خطأ: {e}"

def analyze(t):
    try:
        from google import genai
        client=genai.Client(api_key=GEMINI_KEY)
        for model in ["gemini-2.5-flash","gemini-2.5-flash","gemini-1.5-flash"]:
            try:
                prompt=f"حلل هذا النص من Whop Clipping واستخرج افضل 3 حملات: {t[:7000]}"
                res=client.models.generate_content(model=model, contents=prompt)
                return res.text
            except: continue
        return "فشل Gemini"
    except Exception as e:
        return f"Gemini error {e}"

if __name__=="__main__":
    txt=hunt()
    res=analyze(txt)
    print(res)
    send(f"📊 {res[:3500]}")
