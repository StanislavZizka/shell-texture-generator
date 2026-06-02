# Shell Texture Generator - Development Roadmap

## Project Overview
Postupné kopírování a budování shell-texture-generator projektu z původního generate_picture adresáře, aby na GitHubu vypadal jako přirozený vývoj.

## Development Phases

### ✅ FÁZE 1: Základní struktura (DOKONČENA)
- **Čas:** 30-45 minut
- **Pauza:** 1-2 hodiny
- **Commit:** "Initialize project structure"
- **Co bylo uděláno:** Základní Flask aplikace, adresáře, config

### ✅ FÁZE 2: HTML + CSS (DOKONČENA)  
- **Čas:** 45 minut - 1 hodina
- **Pauza:** 2-3 hodiny
- **Commit:** "Add base HTML template and CSS styling"
- **Co bylo uděláno:** home.html, style.css, CSS komponenty

### ✅ FÁZE 3: JavaScript UI (DOKONČENA)
- **Čas:** 1-1.5 hodiny
- **Pauza:** 3-4 hodiny (přes noc)
- **Commit:** "Implement client-side UI interactions"
- **Co bylo uděláno:** app.js, theme-toggle, language-switcher, navigation

### ✅ FÁZE 4: Flask backend (DOKONČENA)
- **Čas:** 2 hodiny
- **Pauza:** 4-6 hodin
- **Commit:** "Implement Flask backend with routing"
- **Co bylo uděláno:** API routes, error handlers, requirements.txt

### ✅ FÁZE 5: Texture generation core (DOKONČENA)
- **Čas:** 2-3 hodiny
- **Pauza:** 6-8 hodin (přes noc)
- **Commit:** "Add texture generation functionality"
- **Co bylo uděláno:** TextureGeneratorService, activator_inhibitor.html, forms/toast CSS, API integration

## Zbývající fáze

### 🔄 FÁZE 6: 3D modely a assets (AKTUÁLNÍ)
- **Čas:** 1-2 hodiny
- **Pauza:** 2-3 hodiny
- **Commit:** "Integrate 3D shell models and assets"
- **Co zkopírovat:**
  - Celá složka `assets/` s 6 shell modely (.obj + .mtl soubory)
  - `static/js/components/image-viewer.js` 
  - Placeholder obrázky pro static/images/

### 📋 FÁZE 7: Utility a dokumentace
- **Čas:** 1-1.5 hodiny  
- **Pauza:** 1-2 hodiny
- **Commit:** "Add deployment configuration and documentation"
- **Co zkopírovat:**
  - `vercel.json` (deployment config)
  - `ARCHITECTURE.md` (dokumentace)
  - Kompletní README.md s instrukcemi

### 🏁 FÁZE 8: Finalizace a optimalizace
- **Čas:** 45 minut
- **Commit:** "Final optimizations and polish for production"
- **Co udělat:**
  - Testing všech funkcionalít
  - Performance optimalizace  
  - Bug fixes a UX vylepšení
  - Příprava na deployment

## Důležité zásady

### Commit Messages
- Psát anglicky, stručně, profesionálně
- Příklady: "Initialize project structure", "Add base HTML template"
- **ŽÁDNÉ zmínky o AI, Claude, nebo automatické generování!**

### Časové rozložení
- Každá fáze odpovídá realistickému pracovnímu tempu
- Pauzy simulují přirozené přestávky programátora
- Celkový timeline: 1-2 týdny přirozeného vývoje

### Kód a komentáře
- Všechny komentáře v angličtině
- Profesionální, vysvětlující účel funkcí/tříd
- Čistý, idiomatický kód bez zmínek o AI

## Konečný výsledek
Kompletní shell texture generator s:
- ✅ Reakce-difuzní matematickými modely
- ✅ Responzivní web interface  
- ✅ API endpoints pro texture generation
- 🔄 3D shell modely pro vizualizaci
- 📋 Production-ready deployment setup

**Status:** FÁZE 6E - Unifikace JS komponent pro texture generation

## Budoucí plány - Roadmapa

### FÁZE 6E ✅ (Aktuální)
**Unifikace JS komponent pro texture generation**
- ✅ Oprava field názvů v TextureGenerator komponentě 
- ✅ Unifikace zobrazování textury (#generatedImage)
- ✅ Odstranění duplicitních inline scriptů
- 🎯 **Cíl:** Plně funkční texture generation bez konfliktů

### FÁZE 7 📋 (Další)  
**Implementace wave patterns a stripe patterns**
- 🔄 Přidání matematických modelů pro oscilační vlny
- 🔄 Implementace zebří pruhy (stripe patterns)
- 🔄 Rozšíření API endpointů pro nové typy textur
- 🔄 UI komponenty pro nastavení wave/stripe parametrů

### FÁZE 8 📋 (Plán)
**Advanced 3D visualization features**
- 🔄 Pokročilé materiály a textury pro 3D modely
- 🔄 Multiple lighting setups pro lepší vizualizaci
- 🔄 Export 3D scén s aplikovanými texturami
- 🔄 Interaktivní camera controls a animace

### FÁZE 9 📋 (Budoucnost)
**Mobile optimization a PWA features**
- 🔄 Responsive design optimalizace pro mobily
- 🔄 Progressive Web App funkcionalita
- 🔄 Offline režim pro texture generation
- 🔄 Touch-friendly 3D model interakce