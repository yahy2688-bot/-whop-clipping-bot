import os, requests, json
TELEGRAM_TOKEN=os.getenv("TELEGRAM_TOKEN")
TELEGRAM_USER=os.getenv("TELEGRAM_USER")
GEMINI_KEY=os.getenv("GEMINI_KEY")
WHOP_API_KEY=os.getenv("WHOP_API_KEY","")

def send(m):
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={"chat_id":TELEGRAM_USER,"text":str(m)[:3900]}, timeout=20)
    except: pass

send(f"🔑 فحص المفتاح: {'موجود' if WHOP_API_KEY else 'مو م موجود'} - الطول {len(WHOP_API_KEY)}")

def get_campaigns():
    # جرب Whop SDK
    if WHOP_API_KEY:
        try:
            from whop_sdk import Whop
            client = Whop(api_key=WHOP_API_KEY)
            send("🚀 أحاول الاتصال بـ Whop...")
            me = client.accounts.me()
            send(f"✅ اتصلت بحساب: {me.id if hasattr(me,'id') else str(me)[:200]}")
            
            campaigns = client.ad_campaigns.list()
            if campaigns:
                return json.dumps(campaigns, default=str, indent=2)[:8000], f"whop-sdk ({len(str(campaigns))} حرف)"
            else:
                return "API اشتغل لكن ما رجع حملات", "whop-empty"
        except Exception as e:
            send(f"❌ خطأ Whop SDK: {str(e)[:1000]}")
            print(f"Whop error: {e}")

    # Fallback شغال 100%
    fallback = [
        {"name":"Clipping Culture","price":"$8-12 CPM","link":"whop.com/clipping-culture"},
        {"name":"Reach Clipping - $10 CPM + iPhone","price":"$10 CPM","link":"whop.com/reachclipping"},
        {"name":"Influencer Clipping","price":"$10 CPM","link":"whop.com/omnipresense/htkclips"}
    ]
    return json.dumps(fallback, ensure_ascii=False, indent=2), "fallback"

if __name__=="__main__":
    open("campaigns.png","wb").write(b"ok")
    data, src = get_campaigns()
    send(f"📊 من {src}:\n{data[:3500]}")
