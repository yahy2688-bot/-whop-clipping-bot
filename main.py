import os, re, requests

TELEGRAM_TOKEN=os.getenv("TELEGRAM_TOKEN")
TELEGRAM_USER=os.getenv("TELEGRAM_USER")
GEMINI_KEY=os.getenv("GEMINI_KEY")

def send(m):
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
    json={"chat_id":TELEGRAM_USER,"text":str(m)[:4000]}, timeout=20)

url = "https://app.contentrewards.cc/discover?type=clipping&sort=budget"
headers = {"User-Agent": "Mozilla/5.0"}

try:
    r = requests.get(url, headers=headers, timeout=20)
    html = r.text
    
    # استخرج كل الحملات: الاسم + السعر
    # النمط: Name · $X /1K views · $Y budget
    pattern = r'([A-Za-z0-9\s\-\[\]\(\)]{5,80}?)\s*(?:·|•).*?\$([0-9]+\.?[0-9]*)\s*/1K'
    matches = re.findall(pattern, html)
    
    # نظف المكرر
    seen=set()
    campaigns=[]
    for name, price in matches:
        name=name.strip()
        if len(name)<5 or name.lower() in seen: continue
        try:
            p=float(price)
            # فلتر فقط الغالي > $1
            if p >= 1.0:
                campaigns.append((name, p))
                seen.add(name.lower())
        except: continue
    
    # رتب من الأغلى للأرخص
    campaigns = sorted(campaigns, key=lambda x: x[1], reverse=True)
    
    if campaigns:
        msg = f"🔥 {len(campaigns)} حملة غالية (فوق $1/1K) - تحديث حي:\n\n"
        for i,(name,price) in enumerate(campaigns[:10],1):
            msg += f"{i}. {name} - **${price}/1K**\n   🔗 https://app.contentrewards.cc/discover?type=clipping\n\n"
        
        # لو عندك Gemini، خليه يلخص الأفضل
        if GEMINI_KEY and len(msg)>100:
            try:
                prompt=f"رتب هذه الحملات من الأفضل: {msg}. اذكر السعر والرابط باختصار عربي حماسي."
                url_g=f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_KEY}"
                res=requests.post(url_g, json={"contents":[{"parts":[{"text":prompt}]}]}, timeout=20)
                if res.status_code==200:
                    msg=res.json()['candidates'][0]['content']['parts'][0]['text']
            except: pass
        
        send(msg)
    else:
        send("ما لقيت حملات فوق $1 اليوم، هذه أرخص حملات:\nhttps://app.contentrewards.cc/discover?type=clipping&sort=budget")

except Exception as e:
    send(f"❌ خطأ: {e}\nhttps://app.contentrewards.cc/discover?type=clipping")

open("campaigns.png","wb").write(b"ok")
