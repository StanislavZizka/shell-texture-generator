# 🧬 Biological Heatmap - Návod k Použití

## 📋 Krok za Krokem

### 1. Spusťte Aplikaci

```bash
python app.py
```

Aplikace běží na: `http://localhost:5000`

---

### 2. Otevřete Stránku Activator-Inhibitor

Klikněte v navigaci na **"Activator-Inhibitor"** nebo jděte přímo na:
```
http://localhost:5000/activator-inhibitor
```

---

### 3. Nastavte Parametry Modelu

V sekci **"Model Parameters"** nastavte:

- **Preset:** Například "Balanced"
- **Constant K:** 1.0
- **Maximum Time:** 50.0 nebo více (delší čas = výraznější vzor)
- **Time Step:** 0.1
- **Barvy:** Ponechte výchozí (modrá + červená)

---

### 4. ✨ KLÍČOVÝ KROK: Aktivujte Biological Heatmap

**PŘED** kliknutím na "Generate Texture":

1. Scrollujte dolů na stránce
2. Najděte sekci **"Analýza vzoru (Pattern Analysis)"**
3. **ZAŠKRTNĚTE** checkbox:
   ```
   ☑ Show Biological Heatmap
   ```
4. Měli byste vidět tooltip:
   > "Zobrazí biologickou heatmapu — barevné rozložení aktivity modelu..."

---

### 5. Generujte Texturu

Klikněte na tlačítko:
```
✨ Generate Texture
```

**Co se stane:**
- Zobrazí se loading spinner
- Backend vygeneruje:
  1. Normální texturu (černobílá/barevná)
  2. **Biological heatmap** (barevná mapa aktivity)
- Po dokončení se **automaticky zobrazí heatmapa**

---

### 6. Rozpoznejte, Že Je Heatmapa Aktivní

Když je heatmapa zobrazena, uvidíte:

✅ **Modrý svítící rámeček** kolem obrázku
✅ **Barevný gradient:**
- 🔵 Modrá = Stabilní oblasti (nízká aktivita)
- 🟢 Zelená = Přechodové oblasti
- 🟡 Žlutá = Zvýšená aktivita
- 🔴 Červená = Nestabilní oblasti (vysoká aktivita, poruchy)

---

### 7. Přepínání Mezi Heatmapou a Normální Texturou

**Po vygenerování** můžete přepínat zobrazení:

- **Klikněte na checkbox** ☑ Show Biological Heatmap:
  - ✅ **Zaškrtnuté** → zobrazí heatmapu (s modrým rámečkem)
  - ☐ **Odškrtnuté** → zobrazí normální texturu

Přepínání je **plynulé** (fade efekt 0.3s).

---

## 🎨 Co Znamenají Barvy?

### Biological Heatmap Colormap (Jet)

| Barva | Aktivita Aktivátoru | Význam |
|-------|---------------------|--------|
| 🔵 **Modrá** | Nízká (0-25%) | Stabilní, klidné oblasti bez poruch |
| 🟢 **Zelená** | Střední-nízká (25-50%) | Přechodové oblasti |
| 🟡 **Žlutá** | Střední-vysoká (50-75%) | Oblasti se zvýšenou aktivitou |
| 🔴 **Červená** | Vysoká (75-100%) | Nestabilní oblasti, lokální poruchy, biologické defekty |

---

## 🧪 Kombinace s Ostatními Funkcemi

### ✅ Funguje Společně S:

| Funkce | Kombinace s Heatmap |
|--------|---------------------|
| **Show analysis grid** | ✅ Zobrazí mřížku přes heatmapu |
| **Show regularity heatmap** | ✅ Funguje současně |
| **Compare with baseline** | ✅ Generuje baseline + heatmapu |
| **Dynamic Instability** | ✅ Heatmapa zobrazí rozpad pigmentu |
| **Random Error** | ✅ Heatmapa zobrazí biologické poruchy |
| **Pattern Evolution** | ⚠️ Hlavní obrázek má heatmapu, snapshoty 25-75% ne |

---

## 📥 Stahování Heatmapy

Když je heatmapa aktivní:

1. Klikněte na tlačítko **"Download"** 📥
2. Uloží se soubor: `biological_heatmap.png`

Když je vypnutá:
1. Download uloží normální texturu: `activator_inhibitor_texture.png`

---

## 🌍 Jazyková Verze

Přepínání CZ ↔ EN (vlajka 🇨🇿 / 🇺🇸 v pravém horním rohu):

**🇨🇿 Čeština:**
- "Zobrazit biologickou heatmapu"
- Tooltip: "...červené oblasti označují lokální poruchy..."
- 🔵 Stabilní • 🟢 Přechodové • 🔴 Nestabilní

**🇬🇧 Angličtina:**
- "Show Biological Heatmap"
- Tooltip: "...red areas indicate local disturbances..."
- 🔵 Stable • 🟢 Transition • 🔴 Unstable

---

## 🎯 Příklad Workflow

```
┌─────────────────────────────────────────┐
│ 1. Otevřete /activator-inhibitor        │
│ 2. Nastavte K=1.0, t_max=100            │
│ 3. ☑ Zaškrtněte "Show Biological..."   │
│ 4. Klikněte "Generate Texture"          │
│ 5. Počkejte na generování (~10-30s)     │
│ 6. Uvidíte HEATMAPU s modrým rámečkem   │
│ 7. Odškrtněte → vrátí se normální vzor  │
│ 8. Zaškrtněte → vrátí se heatmapa       │
└─────────────────────────────────────────┘
```

---

## ⚠️ Časté Chyby

### ❌ "Heatmapa není dostupná"

**Důvod:** Zaškrtli jste checkbox **PO** generování, kdy byla textura vygenerována BEZ heatmapy.

**Řešení:**
1. Ujistěte se, že checkbox je zaškrtnutý **PŘED** kliknutím na "Generate"
2. Klikněte znovu "Generate Texture"

---

### ❌ Vidím normální texturu místo heatmapy

**Důvod:** Checkbox není zaškrtnutý nebo se odškrtl.

**Řešení:**
1. Scrollujte dolů do sekce "Analýza vzoru"
2. Zaškrtněte ☑ "Show Biological Heatmap"
3. Obrázek se přepne na heatmapu (s fade efektem)

---

### ❌ Sekce "Analýza vzoru" není vidět

**Důvod:** Ještě nebyla vygenerována žádná textura.

**Řešení:**
1. Vygenerujte první texturu (s nebo bez heatmapy)
2. Sekce se automaticky zobrazí pod obrázkem

---

## 💡 Tipy

- **Delší simulace** (t_max > 100) = výraznější barevné rozdíly v heatmapě
- **Dynamic Instability** + Heatmap = vidíte rozpad pigmentu červeně
- **Random Error** + Heatmap = lokální poruchy vyniknou červenými skvrnami
- Zkuste různé **Presety** (Stable, Balanced, Active, Chaotic) a pozorujte rozdíly v heatmapě

---

## 🆘 Potřebujete Pomoc?

Pokud něco nefunguje:
1. Otevřete **Developer Console** (F12)
2. Hledejte chybové hlášky
3. Přečtěte si [HEATMAP_DEBUG_GUIDE.md](HEATMAP_DEBUG_GUIDE.md)
4. Spusťte test: `python test_heatmap.py`
