import os, requests, json
TELEGRAM_TOKEN=os.getenv("TELEGRAM_TOKEN")
TELEGRAM_USER=os.getenv("TELEGRAM_USER")
WHOP_API_KEY=os.getenv("WHOP_API_KEY","")

def send(m):
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
    json={"chat_id":TELEGRAM_USER,"text":str(m)[:3900]}, timeout=20)

if not WHOP_API_KEY:
    send("❌ المفتاح مو موجود")
    exit()

from whop_sdk import Whop
client = Whop(token=WHOP_API_KEY)

try:
    me = client.accounts.me()
    send(f"✅ تم الاتصال! Company: {me.id}")
    # الآن جيب المنتجات
    products = list(client.products.list(account_id=me.id))[:5]
    text = "\n".join([f"- {p.title if hasattr(p,'title') else str(p)[:100]}" for p in products])
    send(f"📊 منتجاتك/حملاتك:\n{text}")
except Exception as e:
    if "balance:read" in str(e) or "403" in str(e):
        send("⚠️ المفتاح يحتاج صلاحيات - روح Developer → API keys → Edit → غيّر Role إلى Owner")
    else:
        send(f"❌ خطأ: {e}")

open("campaigns.png","wb").write(b"ok")
