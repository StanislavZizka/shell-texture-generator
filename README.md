# Generátor Textur pro Mušle

Webová aplikace pro generování matematických textur pomocí reakčně-difuzních algoritmů. Projekt simuluje tvorbu přírodních vzorů na površích mušlí.

## O projektu

Tento projekt zkoumá, jak vznikají komplexní vzory v přírodě pomocí jednoduchých matematických pravidel. Aplikace implementuje aktivátor-inhibitor modely pro vytváření realistických textur, které napodobují vzory nacházející se na skutečných mušlích.

## Technologie

- **Flask** - webový framework pro Python
- **NumPy** - matematické výpočty a práce s poli
- **Matplotlib** - generování a ukládání obrázků textur
- **HTML/CSS/JavaScript** - moderní webové rozhraní

## Funkce

- Interaktivní generování textur pomocí matematických modelů
- Nastavitelné parametry pro různé typy vzorů
- Vizualizace výsledků v reálném čase
- Export generovaných textur
- Vícejazyčné rozhraní (čeština/angličtina)

## Struktura projektu

```
shell-texture-generator/
├── app.py                 # Hlavní aplikace Flask
├── config.py             # Konfigurace aplikace
├── requirements.txt      # Python závislosti
├── routes/              # URL routy
│   ├── __init__.py
│   ├── pages.py         # HTML stránky
│   └── api.py           # API endpointy
├── services/            # Business logika
│   ├── __init__.py
│   └── texture_generator.py
├── utils/               # Pomocné funkce
│   ├── __init__.py
│   └── helpers.py
├── templates/           # HTML šablony
├── static/             # Statické soubory
│   ├── css/
│   ├── js/
│   └── images/
├── assets/             # 3D modely mušlí
└── models/             # Datové modely
```

## Spuštění

1. Nainstalujte závislosti:
```bash
pip install -r requirements.txt
```

2. Spusťte aplikaci:
```bash
python app.py
```

3. Otevřete prohlížeč na adrese: http://localhost:5000

## Vývoj

Projekt je strukturován pro snadnou údržbu a rozšiřování:

- **Modularita** - každá funkcionalita má svůj vlastní modul
- **Separace** - HTML, CSS a JavaScript jsou oddělené
- **Konfigurace** - všechna nastavení centralizovaná v config.py
- **Dokumentace** - komentáře v kódu vysvětlují složitější části

## Autor

Stanislav Žižka  
Diplomová práce • 2024/2025