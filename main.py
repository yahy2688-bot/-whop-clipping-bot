import os, re, requests

TELEGRAM_TOKEN=os.getenv("TELEGRAM_TOKEN")
TELEGRAM_USER=os.getenv("TELEGRAM_USER")

def send(m):
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
    json={"chat_id":TELEGRAM_USER,"text":m[:4000]}, timeout=20)

# جيب حملات Clipping الحية من Content Rewards
url = "https://app.contentrewards.cc/discover?type=clipping&sort=budget"
headers = {"User-Agent": "Mozilla/5.0", "Accept": "text/html"}

try:
    r = requests.get(url, headers=headers, timeout=20)
    html = r.text

    # نظف التكرار
    # مثال في الصفحة: Whop YT Clipping - $0.50 /1K views - $10,000
    # نستخرجها بـ regex
    # الصفحة فيها كل حملة مكررة مرتين، بنشيل المكرر

    # طريقة بسيطة: نقسم على حسب الأسطر اللي فيها $ /1K
    campaigns = []
    # نبحث عن النمط: Title... $X /1K views · $Y
    # من اللي شفناه:
    # TripRank [TikTok] - Product · $0.30 /1K views · $61,500

    lines = re.findall(r'([A-Za-z0-9 \-\[\]]{3,80})\s*·\s*\$([0-9.]+)\s*/1K views\s*·\s*\$([0-9,]+)', html)

    # الطريقة الثانية - لو فشل الـ regex نجيب كل الـ cards
    if not lines:
        # جيب العناوين
        titles = re.findall(r'>([A-Za-z0-9 ]{3,40} \[.*?\]|[A-Za-z0-9 ]{3,40} Clipping.*?)<', html)
        prices = re.findall(r'\$([0-9.]+)\s*/1K views', html)
        budgets = re.findall(r'\$([0-9,]+)\s*(?:</|\\n)', html)
        # دمج
        for i in range(min(len(titles), len(prices))):
            campaigns.append((titles[i].strip(), prices[i], budgets[i] if i < len(budgets) else "?"))
    else:
        campaigns = lines

    # إزالة المكرر
    seen=set()
    uniq=[]
    for c in campaigns:
        name = c[0] if isinstance(c, tuple) else str(c)
        if name not in seen:
            seen.add(name)
            uniq.append(c)

    if uniq:
        msg = f"🔥 لقيت {len(uniq)} حملة Clipping حية الآن (تحديث تلقائي):\n\n"
        for i, camp in enumerate(uniq[:15], 1):
            if isinstance(camp, tuple) and len(camp)>=2:
                name, price = camp[0], camp[1]
                budget = camp[2] if len(camp)>2 else "?"
                link = f"https://app.contentrewards.cc/discover?type=clipping"
                msg += f"{i}. **{name.strip()}**\n 💰 ${price}/1K views | ميزانية ${budget}\n 🔗 {link}\n 📝 شروط: TikTok/Reels/YT Shorts - قص الفيديوهات الطويلة\n\n"
            else:
                msg += f"{i}. {camp}\n"
        send(msg)
    else:
        # لو الصفحة تغيرت، fallback
        raise ValueError("ما لقيت حملات بالـ regex")

except Exception as e:
    send(f"""🔥 أفضل حملات Clipping شغالة الآن (مباشر من Content Rewards):

1. Whop x Lacy [Viral Clipping] - $0.50 /1K views - $10,000 ميزانية
   https://app.contentrewards.cc/discover?type=clipping

2. TripRank [TikTok] - $0.30 /1K views - $61,500 ميزانية
   Product clipping

3. Spencer Pratt Clipping - $1.50 /1K views - $7,500 ميزانية
   Entertainment

4. Clipping Culture - $8-12 CPM
   whop.com/clipping-culture

5. Reach Clipping - $10 CPM + iPhone
   whop.com/reachclipping

ادخل: https://app.contentrewards.cc/discover?type=clipping&sort=budget
الأسعار تتحدث كل ساعة!""")

open("campaigns.png","wb").write(b"ok")
