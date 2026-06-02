// Language Switcher System
class LanguageSwitcher {
    constructor() {
        if (window.languageSwitcherInstance) {
            return window.languageSwitcherInstance;
        }
        this.currentLanguage = localStorage.getItem('selectedLanguage') || 'cs';
        this.translations = {
            cs: {
                // Navigation
                'nav-home': 'Domů',
                'nav-activator-inhibitor': 'Aktivátor-Inhibitor',
                'nav-random-error': 'Náhodná porucha',
                'nav-waves': 'Oscilační vlny',
                'nav-stripes': 'Zebří pruhy',
                
                // Home page
                'page-title-home': 'Generátor přírodních textur pro mořské schránky',
                'page-subtitle-home': 'Diplomová práce zaměřená na modelování vzorů pomocí reakčně-difuzních systémů a jejich aplikaci ve virtuální realitě.',
                'home-thesis-badge': 'Založeno na modelu aktivátor–inhibitor dle Meinhardta',
                'home-description': 'Objevte sílu matematiky v přírodních texturách. Aplikace využívá reakčně-difuzní modely pro generování vzorů mušlí a jejich aplikaci na 3D modely.',
                'features-title': 'Funkce aplikace',
                'feature-1-title': 'Reakčně-difuzní modely',
                'feature-1-desc': 'Generujte komplexní vzory pomocí aktivátor-inhibitor modelů',
                'feature-2-title': '3D Vizualizace',
                'feature-2-desc': 'Vytvářejte vlnové vzory s různými frekvencemi',
                'feature-3-title': 'Interaktivní rozhraní',
                'feature-3-desc': 'Generujte pruhované textury s nastavitelnými parametry',
                'feature-4-title': 'Export a stažení',
                'feature-4-desc': 'Uložte si vygenerované textury ve vysoké kvalitě',
                'get-started': 'Začít vytvářet',
                
                // Activator-Inhibitor page
                'page-title-ai': 'Aktivátor-Inhibitor Model',
                'page-subtitle-ai': 'Nastavte parametry reakčně-difuzního modelu pro generování komplexních vzorů a textur',
                'page-title-re': 'Model náhodné poruchy',
                'page-subtitle-re': 'Lokální stochastická porucha během vývoje vzoru',
                'model-params': 'Parametry modelu',

                // Gierer-Meinhardt parameters
                'source-density': 'Hustota zdroje (s)',
                'source-density-help': 'Síla autokatalýzy (0.01 - 0.20)',
                'inhibitor-diffusion': 'Difúze inhibitoru (D_b)',
                'inhibitor-diffusion-help': 'Rychlost difúze inhibitoru (0.10 - 0.80)',
                'activator-decay': 'Rozpad aktivátoru (r_a)',
                'activator-decay-help': 'Rychlost rozpadu aktivátoru (0.01 - 0.30)',
                'inhibitor-decay': 'Rozpad inhibitoru (r_b)',
                'inhibitor-decay-help': 'Rychlost rozpadu inhibitoru (0.01 - 0.30)',

                // Simulation parameters
                'constant-k': 'Konstanta K',
                'constant-k-help': 'Rychlost reakčního procesu (0.0001 - 5.0)',
                'max-time': 'Maximální čas',
                'max-time-help': 'Doba simulace v časových jednotkách',
                'time-step': 'Časový krok (Δt)',
                'time-step-help': 'Přesnost simulačního kroku',
                'color-scheme': 'Barevné schéma',
                'base-color': 'Základní barva',
                'contrast-color': 'Kontrastní barva',
                'generate-texture': 'Generovat texturu',
                'result-texture': 'Výsledná textura',
                'placeholder-text': 'Zde se zobrazí vygenerovaná textura',
                'download': 'Stáhnout',
                'view': 'Zobrazit',
                'generating': 'Generuji texturu...',
                
                // 3D Visualization
                '3d-visualization': '3D Vizualizace',
                'select-shell-type': 'Vyberte typ mušle:',
                'shell-buccinidae': 'Buccinidae (Hornovec)',
                'shell-fasciolariidae': 'Fasciolariidae (Lasturovité)',
                'shell-moon-snail': 'Moon snail (Měsíční šnek)',
                'shell-muricidae': 'Muricidae (Murexovité)',
                'shell-pecten': 'Pecten (Hřebenatka)',
                'shell-whelk': 'Whelk (Růžek)',
                'loading-model': 'Načítám 3D model...',
                'instruction-drag': 'Přetáhněte texturu na mušli pro aplikaci',
                'instruction-mouse': 'Levé tlačítko: otáčení • Kolečko myši: přiblížení / oddálení',
                'instruction-mobile': 'Mobil: 1 prst = otáčení • 2 prsty = přiblížení sevřením',
                'reset-texture': 'Resetovat texturu',
                'change-model': 'Změnit model',
                
                // Popup controls
                'popup-close-info': 'ESC / Kliknutí mimo / Stažením dolů zavřete',
                'popup-zoom-info': 'Dvojklik pro přiblížení • Na mobilu přiblížíte sevřením',
                
                // Toast messages
                'texture-generated': 'Textura byla úspěšně vygenerována!',
                'texture-applied': 'Textura byla úspěšně aplikována na mušli!',
                'texture-reset': 'Textura byla resetována na původní barvy!',
                'model-loading': 'Načítám model:',
                'texture-generation-error': 'Chyba při generování textury',
                'server-error': 'Chyba při komunikaci se serverem',
                'model-not-ready': 'Model není připraven pro aplikaci textury',
                'enter-valid-values': 'Zadejte platné hodnoty pro všechny parametry',
                'fallback-model': 'Použit náhradní model',
                
                // Language switcher
                'language': 'Jazyk',
                'czech': 'Čeština',
                'english': 'Angličtina',
                'language-switched': 'Jazyk byl změněn',
                
                // Theme toggle
                'theme-dark': 'Tmavý',
                'theme-light': 'Světlý',
                'switch-to-light': 'Přepnout na světlý režim',
                'switch-to-dark': 'Přepnout na tmavý režim',
                
                // Common buttons
                'coming-soon': 'Brzy k dispozici',

                // Pattern Evolution
                'pattern-evolution': 'Vývoj vzoru',
                'pattern-evolution-info': 'Vizualizace 4 fází vývoje vzoru podle aktuálních parametrů',
                'pattern-evolution-param-info': 'Pattern Evolution používá aktuálně nastavené parametry modelu (K, čas, krok, stabilitu apod.) a pouze sleduje vývoj vzoru v čase. Pokud upravíte parametry, změní se i tvar a průběh jednotlivých fází (25 %, 50 %, 75 %, 100 %).',
                'show-pattern-evolution': 'Zobrazit vývoj vzoru',
                'early-stage': 'Raná fáze',
                'mid-stage': 'Střední fáze',
                'late-stage': 'Pozdní fáze',
                'final-stage': 'Finální fáze',

                // Random Error / Biological Perturbation
                'random-error-title': 'Random Error (Biologické poruchy)',
                'random-error-desc': 'Vědecky podložené lokální poruchy vzoru – simuluje biologické defekty v přirozených mušlích',
                'random-error-info': 'Přidává biologické poruchy pigmentu, napodobující defekty přirozených mušlí',
                'random-error-formula-desc': 'Přidává časově omezené lokální perturbace do aktivátorové rovnice',
                'strength-label': 'Síla (Strength α)',
                'strength-range': '0.01-0.05',
                'strength-help': 'Amplituda perturbace - vyšší = silnější poruchy',
                'duration-label': 'Trvání (Duration)',
                'duration-range': '10-50 steps',
                'duration-help': 'Jak dlouho každá perturbace trvá',
                'frequency-label': 'Frekvence (Frequency)',
                'frequency-range': '0.05-0.2',
                'frequency-help': 'Časová oscilace sin(2πft)',
                'probability-label': 'Pravděpodobnost (Probability)',
                'probability-range': '0.01-0.1',
                'probability-help': 'Šance na spuštění nové perturbace každý krok',
                'num-regions-label': 'Počet zón (Regions)',
                'num-regions-range': '1-10',
                'num-regions-help': 'Kolik oblastí bude současně narušeno',
                'region-size-label': 'Velikost zóny (Region Size)',
                'region-size-range': '5-20 px',
                'region-size-help': 'Velikost každé narušené oblasti v pixelech',
                'quick-presets': 'Rychlé předvolby:',
                'preset-gentle': 'Jemné',
                'preset-moderate': 'Střední',
                'preset-active': 'Aktivní',

                // Dynamic Instability
                'dynamic-instability': 'Dynamická nestabilita',
                'dynamic-instability-help': 'Simuluje rozpad pigmentu během vývoje vzoru',

                // Tooltips - Enhanced descriptions
                'tooltip-preset': 'Vybere přednastavený režim simulace.<br><strong>Stable</strong> = klidné vzory,<br><strong>Balanced</strong> = rovnováha mezi aktivací a inhibicí,<br><strong>Active</strong> = rychlé růstové změny,<br><strong>Chaotic</strong> = nestabilní struktury',
                'tooltip-k': 'Ovlivňuje rychlost reakce.<br><strong>Vyšší K</strong> → rychlejší vývoj a kontrastnější vzor<br><strong>Nižší K</strong> → jemnější a pomalejší změny',
                'tooltip-tmax': 'Určuje délku simulace.<br><strong>Delší čas</strong> → vznik stabilnějších a složitějších struktur<br><strong>Kratší čas</strong> → zachytí ranější fáze vývoje',
                'tooltip-dt': 'Přesnost výpočtu.<br><strong>Menší krok</strong> = přesnější, ale pomalejší<br><strong>Větší krok</strong> = rychlejší, ale méně přesné',
                'tooltip-strength': 'Určuje intenzitu lokálních poruch. Vyšší = výraznější poruchy, Nižší = jemné biologické šumy',
                'tooltip-duration': 'Délka působení defektu. Delší trvání → větší zásah do vývoje vzoru, Kratší trvání → rychlé impulsy',
                'tooltip-frequency': 'Jak často se poruchy objevují během simulace. Vyšší frekvence → více drobných defektů, Nižší frekvence → ojedinělé velké poruchy',
                'tooltip-dynamic-inst': 'Simuluje spontánní rozpad nebo slučování pigmentových oblastí.<br><strong>Aktivátor</strong> destabilizuje růstové oblasti<br><strong>Inhibitor</strong> je rozkládá',
                'preset-label': 'Preset',
                'preset-help': 'Vyberte přednastavené parametry',
                'noise-target-label': 'Cíl modifikace (Target)',
                'noise-target-help': 'Která pole rovnic modifikovat',
                'noise-target-a': 'Aktivátor (A)',
                'noise-target-b': 'Inhibitor (B)',
                'noise-target-both': 'Oba (Both)',
                'noise-strength-label': 'Síla nestability (Instability Strength)',
                'noise-strength-help': 'Amplituda multiplikativní modifikace (0.001 - 0.05)',
                'stage-selector-label': 'Vyberte fázi pro náhled v detailu:',
                'stage-selector-help': 'Vyberte fázi pro zobrazení v plné velikosti výše s možností analýzy',
                'dynamic-instability-title': 'Dynamická nestabilita (Dynamic Instability)',
                'dynamic-instability-desc': 'Modifikuje rovnice pro lokální rozpad vzoru a shlukování pigmentu',
                'option-stable': 'Stable (měkké vzory)',
                'option-balanced': 'Balanced (střední kontrast)',
                'option-active': 'Active (vysoký kontrast)',
                'option-chaotic': 'Chaotic (nestabilní)',

                // Biological Heatmap
                'show-biological-heatmap': 'Zobrazit biologickou heatmapu',
                'biological-heatmap-tooltip': 'Zobrazí biologickou heatmapu — barevné rozložení aktivity modelu, kde červené oblasti označují lokální poruchy nebo nestabilitu',
                'biological-heatmap-title': 'Biologická heatmapa',
                'heatmap-legend-title': 'Legenda',
                'heatmap-legend-stable': 'Stabilní',
                'heatmap-legend-transition': 'Přechodové',
                'heatmap-legend-unstable': 'Nestabilní',
                'heatmap-active': 'Biologická heatmapa zobrazena',
                'heatmap-disabled': 'Biologická heatmapa skryta',
                'heatmap-not-available': 'Heatmapa není dostupná. Prosím vygenerujte texturu s povolenou volbou "Zobrazit biologickou heatmapu".',

                // Static/Dynamic Mode
                'generation-mode': 'Režim parametrů',
                'static-mode': 'Statické parametry',
                'dynamic-mode': 'Dynamické parametry',
                'mode-description-static': 'Statické parametry jsou pouze pro čtení a odpovídají zvolenému presetu.',
                'mode-description-dynamic': 'Dynamické parametry lze upravovat ručně a připravují se pro další rozšíření.',
                'progressionMode': 'Dynamické parametry',
                'progressionModeDescription': 'Dynamické parametry řídí průběh vývoje a vytvářejí space-time diagram.',
                'select-preset': 'Vyberte preset',
                'tooltip-preset-new': 'Vyberte přednastavený set:<br><strong>Low Diffusion:</strong> Ostré vzory<br><strong>Medium Diffusion:</strong> Vyvážené vlny<br><strong>High Diffusion:</strong> Jemné přechody<br><strong>Balanced:</strong> Obecně vyvážený',
                'preset-low-diffusion': 'Nízká difúze (ostré vzory)',
                'preset-medium-diffusion': 'Střední difúze (vyvážené)',
                'preset-high-diffusion': 'Vysoká difúze (jemné přechody)',
                'preset-balanced': 'Vyvážený',
                'preset-help-new': 'Parametry budou nastaveny automaticky',
                'nav-figure211': 'Obrázek 2.11 - Skvrny',
                'nav-figure23': 'Obrázek 2.3 - Periodické vzory',
                'nav-figure212': 'Obrázek 2.12 - Labyrinty',
                'home-figure211-title': 'Obrázek 2.11 - Skvrny',
                'home-figure211-desc': 'Reprodukovatelný vývoj skvrnového vzoru s vývojovými kontrolními body a průzkumem náhodné poruchy.',
                'home-figure211-button': 'Otevřít skvrny',
                'home-figure23-title': 'Obrázek 2.3 - Periodické vzory',
                'home-figure23-desc': 'Vývoj pruhů v režimu statických i dynamických parametrů s postupnými presety a volitelnou náhodnou poruchou.',
                'home-figure23-button': 'Otevřít periodické vzory',
                'home-figure212-title': 'Obrázek 2.12 - Labyrinty',
                'home-figure212-desc': 'Vznik kanálů a labyrintů se stejnou reprodukovatelnou simulací a vývojovým workflow.',
                'home-figure212-button': 'Otevřít labyrinty',
                'figure23-page-title': 'Obrázek 2.3 - Periodické vzory',
                'figure23-page-subtitle': 'Dominantní, jasně oddělené svislé pruhy',
                'figure211-page-title': 'Obrázek 2.11 - Skvrny',
                'figure211-page-subtitle': 'Meinhardtův vývoj skvrn z obrázku 2.11',
                'figure212-page-title': 'Obrázek 2.12 - Labyrinty',
                'figure212-page-subtitle': 'Vývoj labyrintů v etapách a vývojovém režimu',
                'stage-tooltip-info': 'Fáze reprezentují vývoj vzoru od rané formace po stabilní strukturu.',
                'random-error-tooltip-info': 'Random error zavádí lokální stochastickou poruchu během vývoje; jeho efekt se liší podle typu modelu.'
            },
            en: {
                // Navigation
                'nav-home': 'Home',
                'nav-activator-inhibitor': 'Activator-Inhibitor',
                'nav-random-error': 'Random Error',
                'nav-waves': 'Oscillating Waves',
                'nav-stripes': 'Zebra Stripes',
                
                // Home page
                'page-title-home': 'Natural Texture Generator for Sea Shells',
                'page-subtitle-home': "Master's thesis focused on modeling patterns using reaction-diffusion systems and their application in virtual reality.",
                'home-thesis-badge': 'Based on activator-inhibitor models by Meinhardt',
                'home-description': 'Discover the power of mathematics in natural textures. The application uses reaction-diffusion models to generate shell patterns and apply them to 3D models.',
                'features-title': 'Application Features',
                'feature-1-title': 'Reaction-Diffusion Models',
                'feature-1-desc': 'Generate complex patterns using activator-inhibitor models',
                'feature-2-title': '3D Visualization',
                'feature-2-desc': 'Create wave patterns with various frequencies',
                'feature-3-title': 'Interactive Interface', 
                'feature-3-desc': 'Generate striped textures with configurable parameters',
                'feature-4-title': 'Export and Download',
                'feature-4-desc': 'Save generated textures in high quality',
                'get-started': 'Start Creating',
                
                // Activator-Inhibitor page
                'page-title-ai': 'Activator-Inhibitor Model',
                'page-subtitle-ai': 'Set parameters for the reaction-diffusion model to generate complex patterns and textures',
                'page-title-re': 'Random Error Model',
                'page-subtitle-re': 'Local stochastic disturbance during pattern evolution',
                'model-params': 'Model Parameters',

                // Gierer-Meinhardt parameters
                'source-density': 'Source Density (s)',
                'source-density-help': 'Autocatalysis strength (0.01 - 0.20)',
                'inhibitor-diffusion': 'Inhibitor Diffusion (D_b)',
                'inhibitor-diffusion-help': 'Inhibitor diffusion rate (0.10 - 0.80)',
                'activator-decay': 'Activator Decay (r_a)',
                'activator-decay-help': 'Activator decay rate (0.01 - 0.30)',
                'inhibitor-decay': 'Inhibitor Decay (r_b)',
                'inhibitor-decay-help': 'Inhibitor decay rate (0.01 - 0.30)',

                // Simulation parameters
                'constant-k': 'Constant K',
                'constant-k-help': 'Reaction process rate (0.0001 - 5.0)',
                'max-time': 'Maximum Time',
                'max-time-help': 'Simulation duration in time units',
                'time-step': 'Time Step (Δt)',
                'time-step-help': 'Simulation step precision',
                'color-scheme': 'Color Scheme',
                'base-color': 'Base Color',
                'contrast-color': 'Contrast Color',
                'generate-texture': 'Generate Texture',
                'result-texture': 'Result Texture',
                'placeholder-text': 'Generated texture will appear here',
                'download': 'Download',
                'view': 'View',
                'generating': 'Generating texture...',
                
                // 3D Visualization
                '3d-visualization': '3D Visualization',
                'select-shell-type': 'Select shell type:',
                'shell-buccinidae': 'Buccinidae (Whelk)',
                'shell-fasciolariidae': 'Fasciolariidae (Tulip Shell)',
                'shell-moon-snail': 'Moon snail',
                'shell-muricidae': 'Muricidae (Murex)',
                'shell-pecten': 'Pecten (Scallop)',
                'shell-whelk': 'Whelk',
                'loading-model': 'Loading 3D model...',
                'instruction-drag': 'Drag texture onto shell to apply',
                'instruction-mouse': 'Left click: rotate • Mouse wheel: zoom in/out',
                'instruction-mobile': 'Mobile: 1 finger = rotate • 2 fingers = pinch zoom',
                'reset-texture': 'Reset Texture',
                'change-model': 'Change Model',
                
                // Popup controls
                'popup-close-info': 'ESC / Click outside / Swipe down to close',
                'popup-zoom-info': 'Double click to zoom • Pinch to zoom on mobile',
                
                // Toast messages
                'texture-generated': 'Texture generated successfully!',
                'texture-applied': 'Texture applied successfully to shell!',
                'texture-reset': 'Texture reset to original colors!',
                'model-loading': 'Loading model:',
                'texture-generation-error': 'Error generating texture',
                'server-error': 'Server communication error',
                'model-not-ready': 'Model not ready for texture application',
                'enter-valid-values': 'Enter valid values for all parameters',
                'fallback-model': 'Using fallback model',
                
                // Language switcher
                'language': 'Language',
                'czech': 'Czech',
                'english': 'English',
                'language-switched': 'Language switched',
                
                // Theme toggle
                'theme-dark': 'Dark',
                'theme-light': 'Light',
                'switch-to-light': 'Switch to light mode',
                'switch-to-dark': 'Switch to dark mode',
                
                // Common buttons
                'coming-soon': 'Coming Soon',

                // Pattern Evolution
                'pattern-evolution': 'Pattern Evolution',
                'pattern-evolution-info': 'Visualization of 4 pattern development phases based on current parameters',
                'pattern-evolution-param-info': 'Pattern Evolution uses your current simulation parameters (K, max time, step size, stability mode, etc.) and visualizes how the pattern evolves over time. Adjusting parameters will affect all 4 stages (25%, 50%, 75%, 100%).',
                'show-pattern-evolution': 'Show Pattern Evolution',
                'early-stage': 'Early Stage',
                'mid-stage': 'Mid Stage',
                'late-stage': 'Late Stage',
                'final-stage': 'Final Stage',

                // Random Error / Biological Perturbation
                'random-error-title': 'Random Error (Biological Perturbation)',
                'random-error-desc': 'Scientifically based local pattern disturbances - simulates biological defects in natural shells',
                'random-error-info': 'Adds biological pigment disturbances, mimicking defects in natural shells',
                'random-error-formula-desc': 'Adds time-limited local perturbations to the activator equation',
                'strength-label': 'Strength (α)',
                'strength-range': '0.01-0.05',
                'strength-help': 'Perturbation amplitude - higher = stronger disturbances',
                'duration-label': 'Duration',
                'duration-range': '10-50 steps',
                'duration-help': 'How long each perturbation lasts',
                'frequency-label': 'Frequency',
                'frequency-range': '0.05-0.2',
                'frequency-help': 'Temporal oscillation sin(2πft)',
                'probability-label': 'Probability',
                'probability-range': '0.01-0.1',
                'probability-help': 'Chance of triggering a new perturbation each step',
                'num-regions-label': 'Number of Regions',
                'num-regions-range': '1-10',
                'num-regions-help': 'How many areas will be disturbed simultaneously',
                'region-size-label': 'Region Size',
                'region-size-range': '5-20 px',
                'region-size-help': 'Size of each disturbed region in pixels',
                'quick-presets': 'Quick Presets:',
                'preset-gentle': 'Gentle',
                'preset-moderate': 'Moderate',
                'preset-active': 'Active',

                // Dynamic Instability
                'dynamic-instability': 'Dynamic Instability',
                'dynamic-instability-help': 'Simulates pigment breakdown during pattern development',

                // Tooltips - Enhanced descriptions
                'tooltip-preset': 'Selects the simulation preset mode.<br><strong>Stable</strong> = calm patterns,<br><strong>Balanced</strong> = balance between activation and inhibition,<br><strong>Active</strong> = fast growth changes,<br><strong>Chaotic</strong> = unstable structures',
                'tooltip-k': 'Affects reaction rate.<br><strong>Higher K</strong> → faster development and higher contrast pattern<br><strong>Lower K</strong> → smoother and slower changes',
                'tooltip-tmax': 'Determines simulation length.<br><strong>Longer time</strong> → more stable and complex structures emerge<br><strong>Shorter time</strong> → captures earlier development phases',
                'tooltip-dt': 'Calculation precision.<br><strong>Smaller step</strong> = more precise, but slower<br><strong>Larger step</strong> = faster, but less precise',
                'tooltip-strength': 'Determines intensity of local disturbances. Higher = more prominent defects, Lower = subtle biological noise',
                'tooltip-duration': 'Duration of defect action. Longer duration → greater impact on pattern development, Shorter duration → quick impulses',
                'tooltip-frequency': 'How often disturbances appear during simulation. Higher frequency → more small defects, Lower frequency → rare large disturbances',
                'tooltip-dynamic-inst': 'Simulates spontaneous breakdown or merging of pigment regions.<br><strong>Activator</strong> destabilizes growth areas<br><strong>Inhibitor</strong> breaks them down',
                'preset-label': 'Preset',
                'preset-help': 'Choose a pre-tuned parameter set',
                'noise-target-label': 'Modification Target',
                'noise-target-help': 'Which equation fields to modify',
                'noise-target-a': 'Activator (A)',
                'noise-target-b': 'Inhibitor (B)',
                'noise-target-both': 'Both',
                'noise-strength-label': 'Instability Strength',
                'noise-strength-help': 'Multiplicative modification amplitude (0.001 - 0.05)',
                'stage-selector-label': 'Choose stage to preview in detail:',
                'stage-selector-help': 'Select a stage to view it in full size above with analysis options',
                'dynamic-instability-title': 'Dynamic Instability',
                'dynamic-instability-desc': 'Modifies equations for local pattern breakdown and pigment clustering',
                'option-stable': 'Stable (soft patterns)',
                'option-balanced': 'Balanced (medium contrast)',
                'option-active': 'Active (high contrast)',
                'option-chaotic': 'Chaotic (unstable)',

                // Biological Heatmap
                'show-biological-heatmap': 'Show Biological Heatmap',
                'biological-heatmap-tooltip': 'Displays a biological heatmap — color-coded model activity distribution, where red areas indicate local disturbances or instability',
                'biological-heatmap-title': 'Biological Heatmap',
                'heatmap-legend-title': 'Legend',
                'heatmap-legend-stable': 'Stable',
                'heatmap-legend-transition': 'Transition',
                'heatmap-legend-unstable': 'Unstable',
                'heatmap-active': 'Biological heatmap shown',
                'heatmap-disabled': 'Biological heatmap hidden',
                'heatmap-not-available': 'Heatmap not available. Please regenerate texture with "Show Biological Heatmap" enabled.',

                // Static/Dynamic Mode
                'generation-mode': 'Parameter mode',
                'static-mode': 'Static parameters',
                'dynamic-mode': 'Dynamic parameters',
                'mode-description-static': 'Static parameters are read-only and match the selected preset.',
                'mode-description-dynamic': 'Dynamic parameters can be edited manually and are prepared for later expansion.',
                'progressionMode': 'Dynamic parameters',
                'progressionModeDescription': 'Dynamic parameters drive the selected development stage and its space-time diagram.',
                'select-preset': 'Select Preset',
                'tooltip-preset-new': 'Choose a preset configuration:<br><strong>Low Diffusion:</strong> Sharp patterns<br><strong>Medium Diffusion:</strong> Balanced waves<br><strong>High Diffusion:</strong> Soft gradients<br><strong>Balanced:</strong> General balanced preset',
                'preset-low-diffusion': 'Low Diffusion (Sharp Patterns)',
                'preset-medium-diffusion': 'Medium Diffusion (Balanced)',
                'preset-high-diffusion': 'High Diffusion (Soft Gradients)',
                'preset-balanced': 'Balanced',
                'preset-help-new': 'Parameters will be set automatically',
                'nav-figure211': 'Figure 2.11 - Spots',
                'nav-figure23': 'Figure 2.3 - Periodic Patterns',
                'nav-figure212': 'Figure 2.12 - Labyrinths',
                'home-figure211-title': 'Figure 2.11 - Spots',
                'home-figure211-desc': 'Reproducible spot-pattern evolution with development checkpoints and random-error exploration.',
                'home-figure211-button': 'Open Spots',
                'home-figure23-title': 'Figure 2.3 - Periodic Patterns',
                'home-figure23-desc': 'Stripe evolution in static and dynamic parameter modes, with progressive presets and optional random error.',
                'home-figure23-button': 'Open Periodic Patterns',
                'home-figure212-title': 'Figure 2.12 - Labyrinths',
                'home-figure212-desc': 'Channel and labyrinth formation with the same reproducible simulation and development workflow.',
                'home-figure212-button': 'Open Labyrinths',
                'figure23-page-title': 'Figure 2.3 - Periodic Patterns',
                'figure23-page-subtitle': 'Dominant, well-separated vertical stripe bands',
                'figure211-page-title': 'Figure 2.11 - Spots',
                'figure211-page-subtitle': 'Meinhardt spot evolution from Figure 2.11',
                'figure212-page-title': 'Figure 2.12 - Labyrinths',
                'figure212-page-subtitle': 'Stage and development views of labyrinth evolution',
                'stage-tooltip-info': 'Stages represent pattern development from early formation to a stable structure.',
                'random-error-tooltip-info': 'Random error introduces a local stochastic disturbance during development; the effect depends on the model type.'
            }
        };
        
        this.translations = window.FIGURE_STAGE_UI_TEXTS || { cs: {}, en: {} };
        window.languageSwitcherInstance = this;
        this.init();
    }

    init() {
        this.createLanguageSwitcher();
        this.applyLanguage(this.currentLanguage);
        this.setupEventListeners();
        
        // Update theme toggle on page load if it exists
        // Try multiple times in case theme manager loads later
        const updateThemeToggle = () => {
            if (window.themeManager && window.themeManager.updateToggleButton) {
                window.themeManager.updateToggleButton();
                return true;
            }
            return false;
        };
        
        // Try immediately and then with delays
        if (!updateThemeToggle()) {
            setTimeout(() => {
                if (!updateThemeToggle()) {
                    setTimeout(updateThemeToggle, 200);
                }
            }, 100);
        }
    }

    createLanguageSwitcher() {
        const existingSwitcher = document.querySelector('.language-switcher');
        if (existingSwitcher) {
            this.syncExistingSwitcher(existingSwitcher);
            return;
        }

        // Create language switcher HTML
        const languageSwitcher = document.createElement('div');
        languageSwitcher.className = 'language-switcher';
        languageSwitcher.innerHTML = `
            <div class="language-toggle" id="languageToggle">
                <div class="language-option ${this.currentLanguage === 'cs' ? 'active' : ''}" data-lang="cs">
                    <span class="flag">🇨🇿</span>
                    <span class="lang-name" data-i18n="czech">Čeština</span>
                </div>
                <div class="language-option ${this.currentLanguage === 'en' ? 'active' : ''}" data-lang="en">
                    <span class="flag">🇺🇸</span>
                    <span class="lang-name" data-i18n="english">English</span>
                </div>
            </div>
        `;

        // Insert after theme toggle
        const themeToggle = document.querySelector('.theme-toggle');
        if (themeToggle && themeToggle.parentNode) {
            themeToggle.parentNode.insertBefore(languageSwitcher, themeToggle.nextSibling);
        } else {
            // Fallback: add to body
            document.body.appendChild(languageSwitcher);
        }
    }

    syncExistingSwitcher(existingSwitcher) {
        this.languageSwitcher = existingSwitcher;
        existingSwitcher.querySelectorAll('.language-option').forEach((option) => {
            option.classList.toggle(
                'active',
                option.getAttribute('data-lang') === this.currentLanguage
            );
        });
    }

    setupEventListeners() {
        const languageOptions = document.querySelectorAll('.language-option');
        languageOptions.forEach(option => {
            option.addEventListener('click', (e) => {
                const selectedLang = e.currentTarget.getAttribute('data-lang');
                this.switchLanguage(selectedLang);
            });
        });
    }

    switchLanguage(language) {
        const translations = window.FIGURE_STAGE_UI_TEXTS || this.translations || {};
        if (language !== this.currentLanguage && translations[language]) {
            this.currentLanguage = language;
            localStorage.setItem('selectedLanguage', language);
            
            // Update active state
            document.querySelectorAll('.language-option').forEach(option => {
                option.classList.remove('active');
            });
            document.querySelector(`[data-lang="${language}"]`).classList.add('active');
            
            this.applyLanguage(language);
            
            // Update theme toggle button if it exists
            if (window.themeManager && window.themeManager.updateToggleButton) {
                window.themeManager.updateToggleButton();
            }
            
            // Trigger custom event for other components to listen
            document.dispatchEvent(new CustomEvent('languageChanged', { 
                detail: { language: language } 
            }));
            
            this.showToast(this.getTranslation('language-switched', language));
        }
    }

    applyLanguage(language) {
        const elements = document.querySelectorAll('[data-i18n]');
        elements.forEach(element => {
            const key = element.getAttribute('data-i18n');
            const translation = this.getTranslation(key, language);

            if (translation) {
                if (element.tagName === 'INPUT' && element.type === 'submit') {
                    element.value = translation;
                } else if (element.hasAttribute('placeholder')) {
                    element.placeholder = translation;
                } else if (element.hasAttribute('aria-label')) {
                    element.setAttribute('aria-label', translation);
                } else if (element.tagName === 'OPTION') {
                    element.textContent = translation;
                } else if (element.classList.contains('tooltip-content')) {
                    // Tooltips can contain HTML (like <br> and <strong>)
                    element.innerHTML = translation;
                } else {
                    element.textContent = translation;
                }
            }
        });

        // Update document language attribute
        document.documentElement.setAttribute('lang', language);

        // Force update theme toggle immediately after language change
        setTimeout(() => {
            if (window.themeManager && window.themeManager.updateToggleButton) {
                window.themeManager.updateToggleButton();
            }
        }, 10);
    }

    getTranslation(key, language = null) {
        const lang = language || this.currentLanguage;
        const translations = window.FIGURE_STAGE_UI_TEXTS || {};
        const current = translations[lang] || {};
        const english = translations.en || {};
        if (current[key] !== undefined && current[key] !== null) {
            return current[key];
        }
        if (english[key] !== undefined && english[key] !== null) {
            return english[key];
        }
        return key;
    }

    showToast(message, type = 'info') {
        // Use existing toast system if available
        if (typeof showToast === 'function') {
            showToast(message, type);
        } else {
            console.log('Language switched:', message);
        }
    }

    // Global method to get current language
    getCurrentLanguage() {
        return this.currentLanguage;
    }

    // Global method to translate text dynamically
    t(key) {
        return this.getTranslation(key);
    }
}

// Initialize language switcher when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    if (!window.languageSwitcher) {
        window.languageSwitcher = new LanguageSwitcher();
    }
    
    // Make translation function globally available
    window.t = (key) => window.languageSwitcher.t(key);
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LanguageSwitcher;
}
