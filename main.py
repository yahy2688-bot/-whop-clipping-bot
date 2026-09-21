import os, requests, re, json, time
TELEGRAM_TOKEN=os.getenv("TELEGRAM_TOKEN")
TELEGRAM_USER=os.getenv("TELEGRAM_USER")
GEMINI_KEY=os.getenv("GEMINI_KEY")

def send(m):
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", json={"chat_id":TELEGRAM_USER,"text":m[:3900]}, timeout=20)
    except: pass

def hunt_with_browser():
    send("🚀 أفتح متصفح حقيقي وأنتظر الحملات...")
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")

            # جرب API الحقيقي أولاً
            try:
                resp = page.request.get("https://api.liquidclips.app/campaigns")
                if resp.status == 200:
                    data = resp.json()
                    browser.close()
                    open("campaigns.png","wb").write(b"ok")
                    return json.dumps(data)[:12000], "liquidclips-api"
            except: pass

            # لو فشل، افتح whop.com وانتظر التحميل
            page.goto("https://whop.com/discover/clipping/", wait_until="networkidle", timeout=60000)
            time.sleep(5)
            page.screenshot(path="campaigns.png", full_page=True)
            content = page.content()
            browser.close()
            return content[20000:90000], "whop-browser"
    except Exception as e:
        open("campaigns.png","wb").write(b"ok")
        return f"متصفح فشل: {e}", "error"

def analyze(text, src):
    if not GEMINI_KEY:
        return f"من {src}:\n{text[:3000]}"
    try:
        prompt = f"من هذا النص من {src} استخرج أفضل 3 حملات Whop Clipping مع السعر والشروط بالعربي:\n{text[:7000]}"
        for model in ["models/gemini-1.5-flash-latest", "models/gemma-3-27b-it", "models/gemini-1.5-flash"]:
            try:
                url = f"https://generativelanguage.googleapis.com/v1/{model}:generateContent?key={GEMINI_KEY}"
                r = requests.post(url, json={"contents":[{"parts":[{"text":prompt}]}]}, timeout=30)
                if r.status_code == 200:
                    ans = r.json()['candidates'][0]['content']['parts'][0]['text']
                    return f"✅ من {src} عبر {model}:\n{ans}"
            except: continue
        return f"📊 من {src}:\n{text[:3500]}"
    except Exception as e:
        return f"خطأ: {e}"

if __name__ == "__main__":
    txt, src = hunt_with_browser()
    res = analyze(txt, src)
    print(res)
    send(res[:3900])
