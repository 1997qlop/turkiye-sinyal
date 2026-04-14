import anthropic
import json
import os
from datetime import datetime

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

PROMPT = """Bugün Türkiye piyasaları için güncel haber analizi yap. Web araması kullanarak bu sabahki en önemli gelişmeleri bul.

Analiz edilecek 30 hisse: THYAO, TUPRS, ASELS, EREGL, BIMAS, GARAN, AKBNK, KCHOL, SAHOL, SISE, TOASO, FROTO, PETKM, TTKOM, TAVHL, PGSUS, DOHOL, YKBNK, HALKB, ARCLK, VESTL, TKFEN, KOZAL, IPEKE, ENKAI, MAVI, LOGO, GUBRF, NETAS, AEFES

SADECE JSON döndür, başka hiçbir şey yazma:
{
  "overall": "RİSK KAPALI",
  "overall_class": "risk-off",
  "overall_sub": "tek cümle piyasa özeti Türkçe",
  "confidence": 82,
  "stocks": [
    {
      "ticker": "THYAO",
      "name": "Türk Hava Yolları",
      "pct": -2.1,
      "action": "SAT",
      "tag": "OLUMSUZ",
      "tag_class": "tag-red",
      "news": "Bu haberin bu hisseye etkisi 2 cümle max Türkçe"
    }
  ]
}

Tüm 30 hisseyi dahil et. pct sayısal olsun (örn: -2.1, +3.4). action: AL/SAT/TUT. tag: OLUMLU/OLUMSUZ/NÖTR. tag_class: tag-green/tag-red/tag-yellow. overall_class: risk-on/risk-off/neutral."""

print("Haberler çekiliyor ve analiz yapılıyor...")

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4000,
    tools=[{"type": "web_search_20250305", "name": "web_search"}],
    messages=[{"role": "user", "content": PROMPT}]
)

# JSON çıkar
text = "".join(block.text for block in response.content if hasattr(block, "text"))
start = text.find("{")
end   = text.rfind("}") + 1
data  = json.loads(text[start:end])

print(f"Analiz tamamlandı: {data['overall']} — Güven: {data['confidence']}/100")

# HTML şablonunu oku ve güncelle
with open("template.html", "r", encoding="utf-8") as f:
    template = f.read()

stocks_js = json.dumps(data["stocks"], ensure_ascii=False, indent=2)
now = datetime.now().strftime("%d.%m.%Y %H:%M")

html = template \
    .replace("{{OVERALL}}", data["overall"]) \
    .replace("{{OVERALL_CLASS}}", data["overall_class"]) \
    .replace("{{OVERALL_SUB}}", data["overall_sub"]) \
    .replace("{{CONFIDENCE}}", str(data["confidence"])) \
    .replace("{{STOCKS_JSON}}", stocks_js) \
    .replace("{{UPDATE_TIME}}", now)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"index.html güncellendi! ({now})")
