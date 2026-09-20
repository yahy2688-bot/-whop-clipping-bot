"""
Whop Content Rewards - Clipping Bot
يعمل من الجوال عبر GitHub Actions + Telegram
المطلوب في Secrets: WHOP_EMAIL, WHOP_PASS, GEMINI_KEY, TELEGRAM_TOKEN, TELEGRAM_USER
"""
import os, time, requests
from playwright.sync_api import sync_playwright

WHOP_EMAIL = os.getenv("WHOP_EMAIL")
WHOP_PASS = os.getenv("WHOP_PASS")
GEMINI_KEY = os.getenv("GEMINI_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_USER = os.getenv("TELEGRAM_USER", "Hhhmb")

def send_telegram(msg):
    if not TELEGRAM_TOKEN: return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_USER, "text": msg, "parse_mode": "Markdown"})
    except Exception as e:
        print(f"Telegram error: {e}")

def hunt_whop_campaign():
    print("🔍 يبدأ صيد حملات Whop...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto("https://whop.com/login/", timeout=60000)
            page.fill('input[type="email"]', WHOP_EMAIL)
            page.fill('input[type="password"]', WHOP_PASS)
            page.click('button[type="submit"]')
            page.wait_for_timeout(5000)
            
            # اذهب لصفحة Content Rewards
            page.goto("https://whop.com/content-rewards/", timeout=60000)
            page.wait_for_timeout(5000)
            
            # احفظ سكرين شوت للحملات (ترسله لك على تليجرام)
            page.screenshot(path="campaigns.png")
            
            # قراءة النص
            content = page.content()
            # ابحث عن الحملات - Whop يعرضها كـ cards
            campaigns_text = page.locator("body").inner_text()[:5000]
            
            browser.close()
            return campaigns_text, "campaigns.png"
        except Exception as e:
            browser.close()
            return f"خطأ: {e}", None

if __name__ == "__main__":
    send_telegram("🚀 بدأ الوكيل يفحص Whop Content Rewards...")
    text, screenshot_path = hunt_whop_campaign()
    
    # استخدم Gemini لتحليل أفضل حملة
    if GEMINI_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"""
            حلل هذا النص من صفحة Whop Content Rewards واختر أفضل حملة clipping:
            المعايير: أعلى سعر لكل 1000 مشاهدة + ميزانية متبقية أكثر من 60% + مسموح فيها النشر على يوتيوب وانستجرام وتيك توك
            النص: {text[:4000]}
            أعطني: اسم الحملة، السعر، الميزانية المتبقية، والشروط المهمة (هاشتاجات مطلوبة، سكرين شوت؟)
            """
            response = model.generate_content(prompt)
            analysis = response.text
            send_telegram(f"📊 تحليل الحملات:\n\n{analysis}\n\nالنص الخام: {text[:1000]}")
        except Exception as e:
            send_telegram(f"تحليل Whop:\n{text[:2000]}\n\nخطأ Gemini: {e}")
    else:
        send_telegram(f"📋 حملات Whop:\n{text[:3000]}")
    
    print("انتهى")
  
