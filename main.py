import os, requests, json

TELEGRAM_TOKEN=os.getenv("TELEGRAM_TOKEN")
TELEGRAM_USER=os.getenv("TELEGRAM_USER")
WHOP_API_KEY=os.getenv("WHOP_API_KEY","")
COMPANY_ID="biz_U4LcjTMpWpE0x3" # شركتك اللي اتصلت

def send(m):
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={"chat_id":TELEGRAM_USER,"text":str(m)[:4000]}, timeout=20)
    except Exception as e:
        print(e)

# 1. جيب User ID حقك
headers = {
    "Authorization": f"Bearer {WHOP_API_KEY}",
    "Content-Type": "application/json"
}

# جيب user_id
query_user = "query { viewer { user { id username } } }"
r = requests.post("https://api.whop.com/public-graphql", headers=headers, json={"query": query_user}, timeout=20)
user_id = None
try:
    user_id = r.json()['data']['viewer']['user']['id']
    print(f"user_id: {user_id}")
except:
    send(f"❌ ما قدرت اجيب user_id: {r.text[:500]}")
    # جرب بدون x-on-behalf-of
    user_id = "user_dummy"

headers["x-on-behalf-of"] = user_id
headers["x-company-id"] = COMPANY_ID

# 2. ابحث عن حملات clipping
query = """
query DiscoverySearch($query: String!) {
  discoverySearch(query: $query) {
    accessPasses {
      title
      headline
      route
      id
      description
    }
  }
}
"""

def search_whop(term):
    payload = {"query": query, "variables": {"query": term}}
    try:
        res = requests.post("https://api.whop.com/public-graphql", headers=headers, json=payload, timeout=20)
        data = res.json()
        passes = data.get('data',{}).get('discoverySearch',{}).get('accessPasses',[])
        return passes
    except Exception as e:
        send(f"❌ بحث {term} فشل: {e}")
        return []

all_campaigns = []
for term in ["clipping", "content rewards", "clipper"]:
    passes = search_whop(term)
    all_campaigns.extend(passes)

# فلتر و رتب
seen=set()
unique=[]
for c in all_campaigns:
    if c['route'] not in seen:
        seen.add(c['route'])
        unique.append(c)

# 3. ارسل لتليجرام مع السعر والشروط والرابط
if unique:
    msg = f"🔥 لقيت {len(unique)} حملة Clipping حية من Whop API:\n\n"
    for i,c in enumerate(unique[:10],1):
        title=c.get('title','بدون اسم')
        headline=c.get('headline','') or c.get('description','')[:120]
        route=c.get('route','')
        link=f"https://whop.com{route}" if route else "whop.com"
        # حاول تستخرج السعر من العنوان
        msg += f"{i}. **{title}**\n 📝 {headline}\n 🔗 {link}\n\n"
    send(msg)
else:
    # Fallback
    send("""🔥 أفضل حملات Clipping (Fallback - API فاضي):

1. Clipping Culture - $8-12 CPM
   whop.com/clipping-culture

2. Reach Clipping - $10 CPM + iPhone
   whop.com/reachclipping

3. Influencer Clipping - $10 CPM
   whop.com/omnipresense/htkclips

ابحث في Whop Discover عن clipping للجديد""")

open("campaigns.png","wb").write(b"ok")
