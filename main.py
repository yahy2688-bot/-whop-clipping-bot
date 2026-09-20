"""
Whop Content Rewards - Clipping Bot V2 - Fixed
"""
import os, time, requests, traceback

WHOP_EMAIL = os.getenv("WHOP_EMAIL")
WHOP_PASS = os.getenv("WHOP_PASS")
GEMINI_KEY = os.getenv("GEMINI_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_USER = os.getenv("TELEGRAM_USER", "")

def send_telegram(msg):
    if not TELEGRAM_TOKEN or not TELEGRAM_USER:
        print("Telegram not configured")
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        # جرب إرسال كـ chat_id
        data = {"chat_id": TELEGRAM_USER, "text": msg[:4000]}
        r = requests.post(url, json=data, timeout=15)
        print(f"Telegram response: {r.text[:200]}")
        if not r.ok:
            # لو فشل، جرب @username
            data["chat_id"] = f"@{TELEGRAM_USER.replace('@','')}" if not TELEGRAM_USER.startswith('@') else TELEGRAM_USER
            r2 = requests.post(url, json=data, timeout=15)
            print(f"Telegram retry: {r2.text[:200]}")
    except Exception as e:
        print(f"Telegram error: {e}")

def hunt_whop():
    print("🔍 يبدأ صيد حملات Whop...")
    send_telegram("🚀 بدأ الوكيل يفحص Whop...")
    
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            page = context.new_page()
            
            # صفحة فارغة لعمل سكرين شوت حتى لو فشل كل شيء (عشان يختفي التحذير)
            page.goto("https://example.com")
            page.screenshot(path="campaigns.png")
            
            try:
                print(f"Logging in with {WHOP_EMAIL}")
                page.goto("https://whop.com/login/", timeout=60000)
                page.wait_for_timeout(3000)
                
                # جرب كل الاحتمالات لحقول تسجيل الدخول
                email_selectors = ['input[type="email"]', 'input[name="email"]', '#email']
                for sel in email_selectors:
                    if page.locator(sel).count() > 0:
                        page.fill(sel, WHOP_EMAIL, timeout=5000)
                        break
                
                pass_selectors = ['input[type="password"]', 'input[name="password"]', '#password']
                for sel in pass_selectors:
                    if page.locator(sel).count() > 0:
                        page.fill(sel, WHOP_PASS, timeout=5000)
                        break
                
                # اضغط زر تسجيل الدخول
                page.locator('button:has-text("Log in"), button:has-text("Sign in"), button[type="submit"]').first.click(timeout=10000)
                page.wait_for_timeout(7000)
                
                print(f"After login URL: {page.url}")
                print(f"Page title: {page.title()}")
                
                # اذهب لصفحة المكافآت
                page.goto("https://whop.com/discover/content-rewards/", timeout=60000)
                page.wait_for_timeout(8000)
                
                page.screenshot(path="campaigns.png", full_page=True)
                text = page.locator("body").inner_text()
                print(f"Got text length: {len(text)}")
                
                browser.close()
                return text[:8000]
                
            except Exception as e:
                err = traceback.format_exc()[-2000:]
                print(f"Playwright inner error: {err}")
                try:
                    page.screenshot(path="campaigns.png", full_page=True)
                except:
                    pass
                browser.close()
                return f"خطأ داخل المتصفح: {e}\n{err}"
                
    except Exception as e:
        err = traceback.format_exc()[-2000:]
        print(f"General error: {err}")
        # أنشئ صورة فارغة عشان ما يطلع تحذير
        try:
            from PIL import Image
            Image.new('RGB', (800, 600), color='black').save('campaigns.png')
        except:
            open('campaigns.png','w').close()
        return f"خطأ عام: {e}\n{err}"

def analyze_with_gemini(text):
    if not GEMINI_KEY:
        return "GEMINI_KEY غير موجود"
    
    try:
        # المكتبة الجديدة
        from google import genai
        client = genai.Client(api_key=GEMINI_KEY)
        
        prompt = f"""
        حلل هذا النص من Whop Content Rewards واختر أفضل 3 حملات للـ clipping:
        المعايير: أعلى سعر لكل 1000 مشاهدة + ميزانية متبقية + مسموح النشر على تيك توك/ريلز/يوتيوب
        استخرج: اسم الحملة، السعر، الشروط (هاشتاجات، ذكر @whop، إلخ)
        
        النص:
        {text[:6000]}
        """
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        return response.text
    except Exception as e:
        try:
            # محاولة بالمكتبة القديمة كـ fallback
            import google.generativeai as genai_old
            genai_old.configure(api_key=GEMINI_KEY)
            model = genai_old.GenerativeModel('gemini-1.5-flash')
            resp = model.generate_content(f"حلل حملات Whop: {text[:4000]}")
            return resp.text + "\n\n(بالمكتبة القديمة)"
        except Exception as e2:
            return f"خطأ Gemini: {e} / Fallback: {e2}"

if __name__ == "__main__":
    text = hunt_whop()
    analysis = analyze_with_gemini(text)
    
    final_msg = f"""📊 *نتيجة فحص Whop*

*التحليل:*
{analysis[:2500]}

*النص الخام (أول 1500 حرف):*
{text[:1500]}
"""
    print(final_msg)
    send_telegram(final_msg)
    print("انتهى")
        
