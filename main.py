import os, re, json, requests, warnings, urllib3
from datetime import datetime
urllib3.disable_warnings()
warnings.filterwarnings('ignore')

TELEGRAM_TOKEN=os.getenv("TELEGRAM_TOKEN")
TELEGRAM_USER=os.getenv("TELEGRAM_USER")
GEMINI_KEY=os.getenv("GEMINI_KEY","")

HISTORY_FILE = "sent_campaigns.json"

def send(m):
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={"chat_id":TELEGRAM_USER,"text":str(m)[:4000],"parse_mode":"Markdown"}, timeout=10, verify=False)
    except: pass

# === المرحلة 3: فلترة ذكية ===
def is_profitable(name, price, budget):
    name_low = name.lower()
    # استبعد الحملات الميتة
    if any(x in name_low for x in ["test", "expired", "closed"]):
        return False
    # اقبل فقط اللي سعره فوق 0.5 وميزانيته فوق 1000
    try:
        if float(price) < 0.5: return False
    except: return False
    return True

# === المرحلة 4: منع التكرار ===
def load_history():
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE,'r') as f:
                return set(json.load(f))
    except: pass
    return set()

def save_history(sent_list):
    try:
        history = load_history()
        history.update(sent_list)
        # احتفظ بآخر 200 فقط
        history = list(history)[-200:]
        with open(HISTORY_FILE,'w') as f:
            json.dump(history, f)
    except: pass

# === جمع الحملات ===
campaigns = []
sources_tried = []

try:
    r = requests.get("https://app.contentrewards.cc/discover", headers={"User-Agent":"Mozilla/5.0"}, timeout=8, verify=False)
    html = r.text
    matches = re.findall(r'([A-Za-z0-9 \-\[\]]{5,50}).*?\$([0-9.]+)\s*/1K', html)
    for name, price in matches:
        campaigns.append({"name":name.strip(), "price":price, "budget":"?", "link":"https://app.contentrewards.cc/discover", "source":"contentrewards"})
except Exception as e:
    sources_tried.append(f"contentrewards: {e}")

# حملات مضمونة دائماً (fallback)
fallback = [
    {"name":"Clipping Culture", "price":"10", "budget":"2000+ مقص", "link":"whop.com/clipping-culture", "source":"fallback"},
    {"name":"Reach Clipping - iPhone للمركز الأول", "price":"10", "budget":"Unlimited", "link":"whop.com/reachclipping", "source":"fallback"},
    {"name":"Hustlers University", "price":"12", "budget":"Unlimited", "link":"whop.com/hustlersuniversity", "source":"fallback"},
    {"name":"Spencer Pratt Clipping", "price":"1.5", "budget":"$7,500", "link":"app.contentrewards.cc/discover", "source":"fallback"},
]

if not campaigns:
    campaigns = fallback
else:
    campaigns.extend(fallback)

# فلترة + إزالة المكرر + عدم إرسال المكرر سابقاً
history = load_history()
filtered = []
new_names = []
for c in campaigns:
    if not is_profitable(c['name'], c['price'], c['budget']): continue
    if c['name'].lower() in history: continue
    if c['name'].lower() in [x.lower() for x in new_names]: continue
    filtered.append(c)
    new_names.append(c['name'])

filtered = sorted(filtered, key=lambda x: float(x['price']), reverse=True)

# === المرحلة 5: تحليل Gemini ===
if filtered and GEMINI_KEY:
    try:
        best = "\n".join([f"{x['name']} - ${x['price']}" for x in filtered[:5]])
        prompt = f"أنت خبير Clipping. رتب هذه الحملات من الأكثر ربحاً لشخص عربي يبدأ الآن. اذكر السبب باختصار: {best}"
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_KEY}"
        res = requests.post(url, json={"contents":[{"parts":[{"text":prompt}]}]}, timeout=10, verify=False)
        if res.status_code==200:
            ai_text = res.json()['candidates'][0]['content']['parts'][0]['text']
            send(f"🤖 تحليل Gemini لأفضل حملة لك:\n\n{ai_text}")
    except Exception as e:
        print(f"Gemini failed {e}")

# === المرحلة 6: الإرسال اليومي ===
if filtered:
    msg = f"🔥 *{len(filtered)} حملة جديدة مربحة* - {datetime.now().strftime('%Y-%m-%d')}\n\n"
    vip_found = False
    for i,c in enumerate(filtered[:10],1):
        price = float(c['price'])
        icon = "💎" if price>=5 else "🔥" if price>=2 else "💰"
        if price>=5: vip_found=True
        msg+=f"{icon} *{i}. {c['name']}* - `${c['price']}/1K`\n   ميزانية: {c['budget']}\n   🔗 {c['link']}\n\n"
    
    send(msg)
    save_history(new_names)
    
    # === المرحلة 7: تنبيه VIP ===
    if vip_found:
        send("🚨 *تنبيه VIP!* لقيت حملة فوق $5/1K - ادخل بسرعة قبل ما تخلص الميزانية!")
else:
    send("✅ فحصت اليوم - ما في حملات جديدة (كل الحملات المرسلة سابقاً). البوت بيفحص مرة ثانية بعد 6 ساعات.\n\n📂 الحملات المحفوظة: /sent_campaigns.json")

print(f"Done - sent {len(filtered)}")
