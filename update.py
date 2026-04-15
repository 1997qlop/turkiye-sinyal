import anthropic
import json
import os
from datetime import datetime

client = anthropic.Anthropic(api_key=os.environ[“ANTHROPIC_API_KEY”])

today = datetime.now().strftime(”%d %B %Y”)

PROMPT = f””“Bugün {today}. Türkiye piyasa analisti olarak görev yapıyorsun.

Aşağıdaki 30 Türk hissesi için bugünün piyasa koşullarına göre analiz yap.
Türkiye ekonomisi, TCMB politikası, döviz kuru, global gelişmeler, enerji fiyatları ve sektörel haberleri dikkate al.

HİSSELER: THYAO, TUPRS, ASELS, EREGL, BIMAS, GARAN, AKBNK, KCHOL, SAHOL, SISE, TOASO, FROTO, PETKM, TTKOM, TAVHL, PGSUS, DOHOL, YKBNK, HALKB, ARCLK, VESTL, TKFEN, KOZAL, IPEKE, ENKAI, MAVI, LOGO, GUBRF, NETAS, AEFES

SADECE JSON döndür, başka hiçbir şey yazma, markdown kullanma:

{{
“overall”: “RİSK KAPALI”,
“overall_class”: “risk-off”,
“overall_sub”: “tek cümle piyasa özeti Türkçe”,
“confidence”: 82,
“stocks”: [
{{
“ticker”: “THYAO”,
“name”: “Türk Hava Yolları”,
“pct”: -2.1,
“action”: “SAT”,
“tag”: “OLUMSUZ”,
“tag_class”: “tag-red”,
“news”: “Hissenin neden bu yönde gittiğini 2 cümle Türkçe açıkla”
}}
]
}}

Kurallar:

- Tüm 30 hisseyi dahil et
- pct sayısal olsun örn: -2.1 veya 3.4 (artı işareti koyma)
- action: AL veya SAT veya TUT
- tag: OLUMLU veya OLUMSUZ veya NÖTR
- tag_class: tag-green veya tag-red veya tag-yellow
- overall_class: risk-on veya risk-off veya neutral
- Sadece JSON döndür, başka hiçbir şey yazma”””

print(“Analiz yapılıyor…”)
print(f”API Key mevcut: {‘EVET’ if os.environ.get(‘ANTHROPIC_API_KEY’) else ‘HAYIR - EKSİK!’}”)

response = client.messages.create(
model=“claude-3-5-haiku-20241022”,
max_tokens=4000,
messages=[{“role”: “user”, “content”: PROMPT}]
)

text = response.content[0].text.strip()
print(f”Ham yanit ilk 200 karakter: {text[:200]}”)

# Markdown temizle

if “`json" in text: text = text.split("`json”)[1].split(”`")[0].strip() elif "`” in text:
text = text.split(”```”)[1].strip()

start = text.find(”{”)
end   = text.rfind(”}”) + 1
if start == -1 or end == 0:
print(“HATA: JSON bulunamadi!”)
print(f”Tam yanit: {text}”)
exit(1)

data = json.loads(text[start:end])
print(f”Analiz tamam: {data[‘overall’]} — Guven: {data[‘confidence’]}/100”)
print(f”Hisse sayisi: {len(data[‘stocks’])}”)

# pct float yap

for s in data[“stocks”]:
try:
s[“pct”] = float(str(s[“pct”]).replace(”+”,””))
except:
s[“pct”] = 0.0

# Template oku

with open(“template.html”, “r”, encoding=“utf-8”) as f:
template = f.read()

stocks_js = json.dumps(data[“stocks”], ensure_ascii=False, indent=2)
now = datetime.now().strftime(”%d.%m.%Y %H:%M”)

html = template   
.replace(”{{OVERALL}}”, data[“overall”])   
.replace(”{{OVERALL_CLASS}}”, data[“overall_class”])   
.replace(”{{OVERALL_SUB}}”, data[“overall_sub”])   
.replace(”{{CONFIDENCE}}”, str(data[“confidence”]))   
.replace(”{{STOCKS_JSON}}”, stocks_js)   
.replace(”{{UPDATE_TIME}}”, now)

with open(“index.html”, “w”, encoding=“utf-8”) as f:
f.write(html)

print(f”index.html guncellendi! ({now})”)