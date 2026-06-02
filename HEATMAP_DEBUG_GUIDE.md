# 🔍 Biological Heatmap - Debug Guide

## ✅ Backend Funguje Správně

Test potvrdil, že backend **FUNGUJE** - heatmapa se generuje správně!

```
✓ TEST 1 PASSED - bez heatmapy → None
✓ TEST 2 PASSED - s heatmapou → soubor vytvořen
```

---

## 🐛 Jak Debugovat Frontend

### Krok 1: Otevřete Developer Tools

1. V prohlížeči stiskněte **F12** nebo **Ctrl+Shift+I**
2. Přejděte na záložku **Console**
3. Nechte ji otevřenou

### Krok 2: Postup pro generování s heatmapou

1. Otevřete stránku: `http://localhost:5000/activator-inhibitor`
2. **ZAŠKRTNĚTE** checkbox ☑ **"Show Biological Heatmap"**
3. Nastavte parametry (např. K=1.0, t_max=50, delta_t=0.1)
4. Klikněte **"Generate Texture"**

### Krok 3: Co sledovat v Console

Měli byste vidět tyto zprávy (v pořadí):

```javascript
[DEBUG] Biological Heatmap checkbox is CHECKED - setting param to true
[DEBUG] Final params being sent: {
  K: 1.0,
  t_max: 50,
  delta_t: 0.1,
  ...
  show_biological_heatmap: true  ← DŮLEŽITÉ!
}
```

V backendu (Flask konzole) uvidíte:

```
[DEBUG API] show_biological_heatmap parameter received: True
[DEBUG TextureGen] show_biological_heatmap = True
[DEBUG TextureGen] Generating biological heatmap...
[DEBUG TextureGen] Biological heatmap generated: ...
[API] Biological heatmap generated: http://...
```

---

## ⚠️ Možné Problémy a Řešení

### Problém 1: Checkbox není zaškrtnutý

**Symptom:**
```javascript
[DEBUG] Biological Heatmap checkbox is UNCHECKED - setting param to false
```

**Řešení:**
- Ujistěte se, že **PŘED** kliknutím na "Generate Texture" je checkbox ☑ zaškrtnutý
- Checkbox je v sekci **"Analýza vzoru (Pattern Analysis)"**
- Pokud sekce není vidět, možná ještě nebyla vygenerována žádná textura

### Problém 2: Parametr se nepošle

**Symptom:** Backend nevidí `show_biological_heatmap: True`

**Řešení:**
- Zkontrolujte Network tab v Developer Tools
- Najděte POST request na `/calculate`
- Klikněte na něj → záložka **Payload** → měli byste vidět:
  ```json
  {
    "show_biological_heatmap": true
  }
  ```

### Problém 3: Backend vygeneruje, ale frontend nezobrazí

**Symptom:**
```
[API] Biological heatmap generated: http://...
```
Ale obrázek se nezobrazí

**Řešení:**
- Zkontrolujte, zda checkbox zůstal zaškrtnutý PO generování
- Pokud ano, měl by se automaticky zobrazit modrý rámeček kolem obrázku
- Zkuste checkbox vypnout a zapnout → měl by se obrázek přepnout

---

## 📸 Jak Ověřit, Že Heatmapa Existuje

### Metoda 1: Přímý přístup

Otevřete v prohlížeči:
```
http://localhost:5000/static/images/biological_heatmap.png
```

Pokud vidíte barevný obrázek (modrá → zelená → žlutá → červená), **heatmapa EXISTUJE**.

### Metoda 2: File System

Podívejte se do složky:
```
C:\Users\Stanislav\Documents\Python\shell-texture-generator\static\images\
```

Měli byste vidět soubor:
```
biological_heatmap.png
```

---

## 🎯 Rychlý Test Workflow

```
1. Otevřete stránku
2. F12 → Console
3. Zaškrtněte ☑ Show Biological Heatmap
4. Generate Texture
5. Sledujte Console:
   - Měli byste vidět: checkbox is CHECKED
   - Měli byste vidět: show_biological_heatmap: true
6. Po dokončení:
   - Obrázek má modrý rámeček? ✓
   - Obrázek je barevný (heatmapa)? ✓
7. Odškrtněte checkbox:
   - Obrázek se přepne na normální texturu? ✓
```

---

## 🆘 Pokud Stále Nefunguje

Pošlete mi screenshot Console s:
1. Všemi `[DEBUG]` zprávami
2. Network tab → POST /calculate → Response

A uveďte:
- Je checkbox zaškrtnutý?
- Existuje soubor `biological_heatmap.png`?
- Co vidíte na obrazovce?
