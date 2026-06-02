# 🎉 Biological Heatmap - Finální Návod

## ✨ Jak To Nyní Funguje

**Heatmapa se zobrazuje JAK SAMOSTATNÝ OBRÁZEK pod hlavní texturou!**

```
┌─────────────────────────────────────┐
│  Normální Textura                   │
│  (vždy viditelná)                   │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│  📊 Analýza vzoru                   │
│  ☑ Show analysis grid               │
│  ☑ Show regularity heatmap          │
│  ☑ Show Biological Heatmap ← KLIK! │
└─────────────────────────────────────┘
         ↓
┌═════════════════════════════════════┐
║  🧬 BIOLOGICAL HEATMAP              ║
║  ┌───────────────────────────────┐  ║
║  │                               │  ║
║  │   Barevná Heatmapa           │  ║
║  │   (modrá → zelená → červená) │  ║
║  │                               │  ║
║  │   ┌─────────────────┐        │  ║
║  │   │ 🔵 Stabilní     │        │  ║
║  │   │ 🟢 Přechodové   │        │  ║
║  │   │ 🔴 Nestabilní   │        │  ║
║  │   └─────────────────┘        │  ║
║  └───────────────────────────────┘  ║
║  📥 Download Heatmap  👁 View      ║
└═════════════════════════════════════┘
```

---

## 🚀 Rychlý Start (3 Kroky)

### 1️⃣ Spusť aplikaci
```bash
python app.py
```

### 2️⃣ Otevři stránku
```
http://localhost:5000/activator-inhibitor
```

### 3️⃣ Generuj texturu

**A) První způsob - Heatmapa BĚHEM generování:**

```
1. ☑ Zaškrtni "Show Biological Heatmap" (PŘED generováním)
2. Nastav parametry (K=1.0, t_max=100, delta_t=0.1)
3. Klikni "Generate Texture"
4. Počkej...
5. ✅ Uvidíš:
   - Normální texturu nahoře
   - HEATMAPU dole (automaticky zobrazena)
```

**B) Druhý způsob - Heatmapa PO generování:**

```
1. Vygeneruj texturu BEZ zaškrtnuté heatmapy
2. Uvidíš normální texturu
3. ☑ Zaškrtni "Show Biological Heatmap"
4. ⚠️ Zobrazí se: "Heatmap not available"
5. Klikni znovu "Generate Texture"
6. ✅ Tentokrát se heatmapa zobrazí
```

---

## 🎨 Co Uvidíte

### Normální Textura (vždy nahoře)
- Černobílá nebo barevná textura podle zadaných barev
- Download ukládá: `activator_inhibitor_texture.png`

### Biological Heatmap (pod analýzou)
- 🔵 **Modrý rámeček** kolem celého kontejneru
- **Nadpis:** 🧬 Biological Heatmap
- **Barevný gradient:**
  - 🔵 Modrá = Stabilní oblasti (nízká aktivita)
  - 🟢 Zelená = Přechodové oblasti
  - 🟡 Žlutá = Zvýšená aktivita
  - 🔴 Červená = Nestabilní oblasti (poruchy)
- **Legenda** v pravém dolním rohu obrázku
- **Vlastní tlačítka:**
  - 📥 Download Heatmap
  - 👁 View (otevře v popupu)

---

## 🎯 Ovládání Checkbox

### ☑ Zaškrtnutý = Heatmapa VIDITELNÁ

```
┌────────────────────────────────┐
│ Normální Textura (nahoře)     │
└────────────────────────────────┘
┌════════════════════════════════┐
║ 🧬 Biological Heatmap          ║  ← ZOBRAZENA
║ [barevný obrázek]              ║
└════════════════════════════════┘
```

### ☐ Odškrtnutý = Heatmapa SKRYTÁ

```
┌────────────────────────────────┐
│ Normální Textura (nahoře)     │
└────────────────────────────────┘

(heatmapa kontejner je skrytý)
```

---

## 💡 Workflow

### Scenario 1: Generování S Heatmapou

```
┌─────────────────────────────────────┐
│ 1. ☑ Show Biological Heatmap       │
│ 2. Nastav parametry                 │
│ 3. Generate Texture                 │
│    ↓                                 │
│ 4. Backend generuje:                │
│    - texture.png                    │
│    - heatmap.png                    │
│    ↓                                 │
│ 5. Frontend zobrazí:                │
│    - Normální textura (nahoře)     │
│    - Heatmapa (dole) ✅            │
└─────────────────────────────────────┘
```

### Scenario 2: Přepínání Po Generování

```
┌─────────────────────────────────────┐
│ Máš vygenerovanou texturu           │
│ S HEATMAPOU                         │
│    ↓                                 │
│ ☐ Odškrtni checkbox                │
│    → Heatmapa zmizí                │
│    ↓                                 │
│ ☑ Zaškrtni zpět                    │
│    → Heatmapa se objeví            │
└─────────────────────────────────────┘
```

### Scenario 3: Bez Heatmapy

```
┌─────────────────────────────────────┐
│ Generuješ BEZ zaškrtnuté heatmapy  │
│    ↓                                 │
│ Backend generuje JEN texturu        │
│    ↓                                 │
│ ☑ Zaškrtneš checkbox PO generování │
│    → "Heatmap not available" ⚠️    │
│    ↓                                 │
│ Musíš znovu generovat!              │
└─────────────────────────────────────┘
```

---

## 🔍 Debug Console

Otevři **F12** → Console a sleduj:

```javascript
// Při generování S heatmapou:
[DEBUG] Biological Heatmap checkbox is CHECKED
[DEBUG] Final params being sent: { show_biological_heatmap: true }
[Heatmap] Preview shown: http://localhost:5000/static/images/biological_heatmap.png

// Při přepínání checkboxu:
[Heatmap] Preview shown: ...      // když zaškrtneš
[Heatmap] Preview hidden          // když odškrtneš
```

---

## 🎨 Designové Prvky

### Heatmap Kontejner
- **Modrý svítící rámeček** (`border: 2px solid primary`)
- **Animace:** Slide in from bottom (0.5s)
- **Box shadow:** Světle modrý svit

### Legenda (overlay)
- **Pozice:** Pravý dolní roh obrázku
- **Pozadí:** Tmavé poloprůhledné (rgba(20, 20, 20, 0.95))
- **Rámeček:** Modrý
- **Barevné pruhy:**
  - Stable: #0000ff → #0088ff
  - Transition: #00ff00 → #ffff00
  - Unstable: #ff8800 → #ff0000

### Tlačítka
- **Download Heatmap:** Zelené tlačítko
- **View:** Sekundární (šedé) tlačítko

---

## 🧪 Kombinace S Ostatními Funkcemi

| Funkce | Kombinace |
|--------|-----------|
| **Analysis Grid** | ✅ Grid se zobrazí NA normální textuře (ne na heatmapě) |
| **Regularity Heatmap** | ✅ Zobrazí se NA normální textuře |
| **Compare Baseline** | ✅ Zobrazí baseline + perturbed, heatmapa samostatně |
| **Pattern Evolution** | ✅ 4 snapshoty + normální textura + heatmapa |
| **Dynamic Instability** | ✅ Heatmapa zobrazí rozpad pigmentu |
| **Random Error** | ✅ Lokální poruchy vyniknou červeně |

---

## 📥 Stahování

**Dvě tlačítka:**

1. **Download** (u normální textury)
   - Ukládá: `activator_inhibitor_texture.png`

2. **Download Heatmap** (u heatmapy)
   - Ukládá: `biological_heatmap.png`

---

## ⚠️ Časté Situace

### "Heatmap not available"

**Příčina:** Vygeneroval jsi texturu BEZ zaškrtnuté heatmapy, pak jsi checkbox zaškrtl.

**Řešení:**
```
1. Ujisti se: ☑ checkbox JE zaškrtnutý
2. Klikni znovu: Generate Texture
3. → Heatmapa se vygeneruje a zobrazí
```

### Heatmapa se nezobrazila, i když byl checkbox zaškrtnutý

**Debug:**
```
1. F12 → Console
2. Hledej: [DEBUG] show_biological_heatmap
3. Mělo by být: true
4. Hledej: [Heatmap] Preview shown
5. Pokud není → zkontroluj, zda existuje soubor:
   static/images/biological_heatmap.png
```

### Chci heatmapu skrýt

```
☐ Odškrtni checkbox "Show Biological Heatmap"
→ Heatmapa zmizí
→ Normální textura zůstane
```

---

## ✨ Výhody Nového Řešení

✅ **Normální textura VŽDY viditelná**
✅ **Heatmapa jako PŘÍDAVEK**, ne náhrada
✅ **Vlastní download tlačítka** pro každý obrázek
✅ **Legenda integrovaná** přímo v heatmapě
✅ **Plynulé animace** (slide in)
✅ **Modře zvýrazněný** kontejner
✅ **Nezávislé ovládání** checkboxem

---

## 🆘 Troubleshooting

### 1. Kontejner se nezobrazuje

```bash
# Zkontroluj v browseru Developer Tools → Elements
# Hledej: id="heatmapPreviewContainer"
# Mělo by mít: style="display: block"
```

### 2. Obrázek je prázdný

```bash
# Otevři přímo URL v prohlížeči:
http://localhost:5000/static/images/biological_heatmap.png

# Pokud funguje → problém ve frontendu
# Pokud nefunguje → backend nevygeneroval
```

### 3. Backend test

```bash
python test_heatmap.py
# → Mělo by projít oba testy ✓
```

---

## 🎉 Hotovo!

**Nyní máte:**
- ✅ Normální textura VŽDY nahoře
- ✅ Heatmapa VOLITELNĚ dole
- ✅ Přepínání checkboxem
- ✅ Dvě download tlačítka
- ✅ Integrovaná legenda
- ✅ Krásné animace

**Užijte si vizualizaci biologických vzorů!** 🧬
