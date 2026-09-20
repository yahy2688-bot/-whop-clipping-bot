  """
Whop Clipping Bot V3 - FINAL FIX
"""
import os, time, requests, traceback

WHOP_EMAIL = os.getenv("WHOP_EMAIL")
WHOP_PASS = os.getenv("WHOP_PASS")
GEMINI_KEY = os.getenv("GEMINI_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_USER = os.getenv("TELEGRAM_USER", "")

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_USER, "text": msg[:4000], "parse_mode": "Markdown"}, timeout=15)
    except Exception as e:
        print(f"Telegram error {e}")

def hunt_whop():
    send_telegram("🚀 *بدأ الفحص...* جاري تسجيل الدخول لـ Whop")
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            print("Opening Whop login...")
            page.goto("https://whop.com/login/", timeout=90000)
            page.wait_for_timeout(5000)
            page.screenshot(path="campaigns.png")
            
            # ابحث عن حقل الإيميل بأي طريقة
            try:
                email_input = page.locator('input[type="email"], input[name="email"], input[placeholder*="Email" i]').first
                email_input.wait_for(state="visible", timeout=15000)
                email_input.fill(WHOP_EMAIL)
                print("Email filled")
            except Exception as e:
                print(f"Email fill failed: {e}")
                # جرب الطريقة الثانية
                page.get_by_placeholder("Email").fill(WHOP_EMAIL, timeout=10000)

            page.wait_for_timeout(1000)
            
            # ابحث عن حقل الباسورد
            try:
                pass_input = page.locator('input[type="password"]').first
                pass_input.wait_for(state="visible", timeout=15000)
                pass_input.fill(WHOP_PASS)
                print("Password filled")
            except Exception as e:
                print(f"Pass fill failed: {e}")
                page.get_by_placeholder("Password").fill(WHOP_PASS, timeout=10000)

            page.wait_for_timeout(1000)
            
            # اضغط زر الدخول
            page.locator('button[type="submit"]').first.click(timeout=10000)
            page.wait_for_timeout(8000)
            
            print(f"URL after login: {page.url}")
            
            # روح لصفحة المكافآت
            page.goto("https://whop.com/discover/content-rewards/", timeout=90000)
            page.wait_for_timeout(10000)
            page.screenshot(path="campaigns.png", full_page=True)
            
            text = page.inner_text("body")
            print(f"Text len: {len(text)}")
            browser.close()
            return text

    except Exception as e:
        err = traceback.format_exc()[-3000:]
        print(err)
        try:
            page.screenshot(path="campaigns.png", full_page=True)
        except: pass
        return f"فشل: {e}\n{err}"

def analyze(text):
    if not GEMINI_KEY: return "لا يوجد مفتاح Gemini"
    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_KEY)
        prompt = f"حلل حملات Whop هذه واعطني أفضل 3 للقص والنشر (السعر، الشروط، الهاشتاقات):\n\n{text[:7000]}"
        res = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        return res.text
    except Exception as e:
        return f"خطأ Gemini: {e}"

if __name__ == "__main__":
    t = hunt_whop()
    a = analyze(t)
    final = f"📊 *تحليل Whop:*\n\n{a[:3000]}\n\n---\n*خام (500 حرف):*\n{t[:500]}"
    print(final)
    send_telegram(final)
