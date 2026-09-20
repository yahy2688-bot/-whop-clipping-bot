import os, requests, traceback
WHOP_EMAIL=os.getenv("WHOP_EMAIL"); WHOP_PASS=os.getenv("WHOP_PASS")
GEMINI_KEY=os.getenv("GEMINI_KEY"); TELEGRAM_TOKEN=os.getenv("TELEGRAM_TOKEN"); TELEGRAM_USER=os.getenv("TELEGRAM_USER")

def send_telegram(m):
    try:
        url=f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_USER, "text": m[:3900]}, timeout=15)
    except: pass

def hunt():
    send_telegram("🚀 بدأ الفحص...")
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b=p.chromium.launch(headless=True)
            pg=b.new_page()
            pg.goto("https://whop.com/login/", timeout=60000)
            pg.wait_for_timeout(4000)
            # الطريقة الجديدة - بدون أخطاء كتابة
            pg.get_by_placeholder("Email").fill(WHOP_EMAIL, timeout=15000)
            pg.locator('input[type="password"]').fill(WHOP_PASS, timeout=15000)
            pg.locator('button[type="submit"]').click()
            pg.wait_for_timeout(8000)
            pg.goto("https://whop.com/discover/content-rewards/", timeout=60000)
            pg.wait_for_timeout(8000)
            pg.screenshot(path="campaigns.png", full_page=True)
            t=pg.inner_text("body")
            b.close()
            return t
    except Exception as e:
        traceback.print_exc()
        open("campaigns.png","w").close()
        return f"خطأ: {e}"

def analyze(t):
    try:
        from google import genai
        c=genai.Client(api_key=GEMINI_KEY)
        r=c.models.generate_content(model="gemini-3.6-flash", contents=f"حلل حملات Whop واختر افضل 3: {t[:7000]}")
        return r.text
    except Exception as e:
        return f"Gemini خطأ: {e}"

if __name__=="__main__":
    txt=hunt()
    res=analyze(txt)
    send_telegram(f"📊 {res[:3000]}")
