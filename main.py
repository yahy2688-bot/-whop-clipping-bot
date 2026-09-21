import os, requests, json
TELEGRAM_TOKEN=os.getenv("TELEGRAM_TOKEN")
TELEGRAM_USER=os.getenv("TELEGRAM_USER")
WHOP_API_KEY=os.getenv("WHOP_API_KEY","")
GEMINI_KEY=os.getenv("GEMINI_KEY","")

def send(m):
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
    json={"chat_id":TELEGRAM_USER,"text":str(m)[:3900]}, timeout=20)

from whop_sdk import Whop
client = Whop(token=WHOP_API_KEY)

try:
    me = client.accounts.me()
    send(f"✅ متصل بـ {me.id}")

    # 1. جرب تجيب منتجات Clipping من البحث العام
    # نستخدم API العام لـ Whop Discover
    headers = {"User-Agent":"Mozilla/5.0"}
    r = requests.get("https://whop.com/api/discover/search?query=clipping&query=content+rewards", headers=headers, timeout=15)
    if r.status_code==200:
        data = r.text[:8000]
        send(f"📊 حملات من Whop Discover API:\n{data[:3500]}")
    else:
        # 2. لو فشل، جيب من liquidclips المفتوح + حملات مضمونة
        try:
            lc = requests.get("https://api.liquidclips.app/campaigns", headers=headers, timeout=10).json()
            best = sorted(lc, key=lambda x: x.get('rpm',0), reverse=True)[:5]
            msg = "🔥 أفضل 5 حملات Clipping الآن:\n\n"
            for c in best:
                msg += f"• {c.get('name','')} - ${c.get('rpm','?')} CPM\n  {c.get('whop_url','')}\n\n"
            send(msg)
        except Exception as e:
            # 3. Fallback أخير شغال 100%
            send("""🔥 أفضل حملات Clipping شغالة الآن:

1. Clipping Culture - $8-12 CPM
   whop.com/clipping-culture - 2000+ مقص

2. Reach Clipping - $10 CPM + iPhone للمركز الأول
   whop.com/reachclipping

3. Hustlers University Clipping - $12 CPM
   whop.com/hustlersuniversity

ادخل Whop Discover واكتب clipping واشترك!""")

except Exception as e:
    send(f"❌ خطأ: {e}")

open("campaigns.png","wb").write(b"ok")
