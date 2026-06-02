# ⚡ Biological Heatmap - Rychlý Start (5 kroků)

## 🎬 Video-Style Guide

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  🚀 KROK 1: Spusť aplikaci                ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

   python app.py

   → Otevři: http://localhost:5000/activator-inhibitor
```

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  ⚙️ KROK 2: Nastav parametry               ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

   Preset:         Balanced
   Constant K:     1.0
   Maximum Time:   100
   Time Step:      0.1

   (ponech výchozí barvy)
```

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  ✨ KROK 3: ZAŠKRTNI CHECKBOX (DŮLEŽITÉ!)  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

   Scrolluj dolů → sekce "Analýza vzoru"

   ☑ Show Biological Heatmap  ← KLIKNI SEM!
   🔵 Stabilní • 🟢 Přechodové • 🔴 Nestabilní
```

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  🎯 KROK 4: Generuj                        ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

   Klikni: ✨ Generate Texture

   ⏳ Počkej 10-30 sekund...
```

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  🎨 KROK 5: Užij si heatmapu!              ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

   ✅ Vidíš MODRÝ RÁMEČEK kolem obrázku?
   ✅ Obrázek je BAREVNÝ (modrá→zelená→červená)?

   → HOTOVO! To je heatmapa! 🎉
```

---

## 🔄 Přepínání

**Vidíš heatmapu a chceš normální texturu?**

```
┌─────────────────────────────────┐
│ ☐ Show Biological Heatmap       │  ← ODŠKRTNI
└─────────────────────────────────┘

→ Fade efekt → Normální textura
```

**Chceš zpět heatmapu?**

```
┌─────────────────────────────────┐
│ ☑ Show Biological Heatmap       │  ← ZAŠKRTNI
└─────────────────────────────────┘

→ Fade efekt → Heatmapa s modrým rámečkem
```

---

## ❌ Nejčastější Chyba

```
❌ "Heatmapa není dostupná"
```

**Příčina:**
- Vygeneroval jsi texturu **BEZ** zaškrtnutého checkboxu
- Pak jsi checkbox zaškrtl až PO generování

**Řešení:**
```
1. Ujisti se: ☑ Show Biological Heatmap JE zaškrtnuté
2. Klikni znovu: Generate Texture
3. Profit! 🎉
```

---

## 🎨 Co Znamenají Barvy?

```
🔵 MODRÁ    = Stabilní (žádné poruchy)
🟢 ZELENÁ   = Přechodové oblasti
🟡 ŽLUTÁ    = Zvýšená aktivita
🔴 ČERVENÁ  = Nestabilní (lokální poruchy)
```

---

## 🧪 Experimentuj!

### Zkus Kombinace:

```
☑ Show Biological Heatmap
☑ Dynamic Instability
   → Uvidíš rozpad pigmentu červeně!
```

```
☑ Show Biological Heatmap
☑ Random Error (Biological Perturbation)
   → Lokální poruchy vyniknou jako červené skvrny!
```

```
☑ Show Biological Heatmap
☑ Show Pattern Evolution
   → 4 fáze vývoje + hlavní heatmapa!
```

---

## 📥 Stažení

```
Když je heatmapa aktivní:
  Download → biological_heatmap.png

Když je vypnutá:
  Download → activator_inhibitor_texture.png
```

---

## 🆘 Pomoc

Nefunguje? Otevři:
- [HEATMAP_USAGE.md](HEATMAP_USAGE.md) - Detailní návod
- [HEATMAP_DEBUG_GUIDE.md](HEATMAP_DEBUG_GUIDE.md) - Debug tipy

Test backendu:
```bash
python test_heatmap.py
```

---

## ✨ Hotovo!

```
   🎨 Biological Heatmap je připravena!

   🔵 Modrá = klid
   🔴 Červená = chaos

   Užij si vizualizaci biologických vzorů! 🧬
```
