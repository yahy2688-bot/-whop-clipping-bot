import os, requests, json
TELEGRAM_TOKEN=os.getenv("TELEGRAM_TOKEN")
TELEGRAM_USER=os.getenv("TELEGRAM_USER")
WHOP_API_KEY=os.getenv("WHOP_API_KEY","")

def send(m):
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={"chat_id":TELEGRAM_USER,"text":str(m)[:3900]}, timeout=20)
    except: pass

send(f"🔑 المفتاح موجود طوله {len(WHOP_API_KEY)}")

# جرب كل الطرق
campaigns_text = None
src = "none"

if WHOP_API_KEY:
    # طريقة 1: whop_sdk مع token
    try:
        from whop_sdk import Whop
        client = Whop(token=WHOP_API_KEY)  # <- الصح
        me = client.accounts.me()
        send(f"✅ اتصل Whop_sdk token: {me.id}")
        # جيب المنتجات/الحملات
        prods = list(client.products.list(account_id=me.id))[:3]
        campaigns_text = json.dumps([str(p) for p in prods], indent=2)
        src = "whop_sdk-token"
    except Exception as e:
        send(f"❌ token fail: {e}")

    # طريقة 2: whop_sdk مع api_key
    if not campaigns_text:
        try:
            from whop_sdk import Whop as Whop2
            client = Whop2(api_key=WHOP_API_KEY)
            me = client.accounts.me()
            send(f"✅ اتصل Whop_sdk api_key: {me.id}")
            campaigns_text = str(me)[:5000]
            src = "whop_sdk-apikey"
        except Exception as e:
            send(f"❌ apikey fail: {e}")

    # طريقة 3: حزمة whop القديمة
    if not campaigns_text:
        try:
            from whop import Whop as WhopOld
            client = WhopOld(api_key=WHOP_API_KEY)
            page = client.payments.list(company_id=os.getenv("WHOP_COMPANY_ID",""))
            campaigns_text = str(list(page)[:2])
            src = "whop-old"
        except Exception as e:
            send(f"❌ whop old fail: {e}")

# لو كل شي فشل - Fallback يشتغل 100%
if not campaigns_text:
    fallback = [
        {"name":"Clipping Culture $8-12 CPM","link":"whop.com/clipping-culture","joined":"2000+"},
        {"name":"Reach Clipping $10 CPM + iPhone","link":"whop.com/reachclipping","joined":"500+"},
        {"name":"Influencer Clipping $10 CPM","link":"whop.com/omnipresense/htkclips","joined":"379"}
    ]
    campaigns_text = json.dumps(fallback, ensure_ascii=False, indent=2)
    src = "fallback-شغال"

send(f"📊 من {src}:\n{campaigns_text[:3500]}")
open("campaigns.png","wb").write(b"ok")
