/**
 * Main application entry point for Shell Texture Generator
 * Initializes all components and manages global application state
 */
class App {
    constructor() {
        this.components = {};
        this.init();
    }

    init() {
        this.setupGlobalErrorHandling();
        this.initializeComponents();
        this.bindGlobalEvents();
        this.setupToastSystem();
    }

    setupGlobalErrorHandling() {
        window.addEventListener('error', (event) => {
            console.error('Global error:', event.error);
            const message = event.error?.message || event.message || 'Unexpected error';
            this.showToast(message, 'error');
        });

        window.addEventListener('unhandledrejection', (event) => {
            console.error('Unhandled promise rejection:', event.reason);
            const message = event.reason?.message || String(event.reason || 'Network error occurred');
            this.showToast(message, 'error');
        });
    }

    initializeComponents() {
        // Initialize components in order of dependency
        this.initializeLanguageSwitcher();
        this.initializeThemeManager();
        this.initializeNavigation();
        this.initializeTextureGenerator();
        this.initializeHeatmapPreview();
        this.initializeImageViewer();
    }

    initializeLanguageSwitcher() {
        if (typeof LanguageSwitcher !== 'undefined') {
            this.components.languageSwitcher = new LanguageSwitcher();
            window.languageSwitcher = this.components.languageSwitcher;
            window.t = (key) => this.components.languageSwitcher.t(key);
        }
    }

    initializeThemeManager() {
        if (typeof ThemeManager !== 'undefined') {
            this.components.themeManager = new ThemeManager();
            window.themeManager = this.components.themeManager;
        }
    }

    initializeNavigation() {
        // Navigation handling - ensure navigation component is loaded
        if (typeof toggleMobileMenu !== 'undefined') {
            console.log('Navigation component loaded');
        }
    }

    initializeTextureGenerator() {
        if (typeof TextureGenerator !== 'undefined') {
            this.components.textureGenerator = new TextureGenerator();
        }
    }

    initializeHeatmapPreview() {
        if (typeof TextureHeatmapPreview !== 'undefined') {
            this.components.textureHeatmapPreview = new TextureHeatmapPreview();
        }
    }

    initializeImageViewer() {
        // Image viewer component ready for initialization
        console.log('Image viewer component ready');
    }

    bindGlobalEvents() {
        // Listen for custom events between components
        document.addEventListener('languageChanged', (event) => {
            console.log('Language changed to:', event.detail.language);
            // Update components that need language updates
            if (this.components.textureGenerator) {
                this.components.textureGenerator.setGeneratingState(false);
            }
        });

        document.addEventListener('textureGenerated', (event) => {
            console.log('Texture generated:', event.detail.imageUrl);
            // Handle global actions after texture generation
        });

        // Handle page visibility changes for performance optimization
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                // Page is hidden - pause animations or long-running processes
                console.log('Page hidden');
            } else {
                // Page is visible - resume processes
                console.log('Page visible');
            }
        });
    }

    setupToastSystem() {
        // Create toast container if it doesn't exist
        if (!document.getElementById('toast-container')) {
            const container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container';
            document.body.appendChild(container);
        }

        // Make showToast globally available
        window.showToast = this.showToast.bind(this);
    }

    showToast(message, type = 'info', duration = 3000) {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <span class="toast-message">${message}</span>
                <button class="toast-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;

        container.appendChild(toast);

        // Show toast with animation
        setTimeout(() => toast.classList.add('show'), 10);

        // Auto remove after duration
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }

    // Utility methods for performance optimization
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
}

window.FIGURE_STAGE_UI_TEXTS = {
    "cs": {
    "nav-home": "Dom\u016f",
    "nav-activator-inhibitor": "Aktiv\u00e1tor-Inhibitor",
    "nav-random-error": "N\u00e1hodn\u00e1 porucha",
    "nav-waves": "Oscila\u010dn\u00ed vlny",
    "nav-stripes": "Zeb\u0159\u00ed pruhy",
    "page-title-home": "Gener\u00e1tor p\u0159\u00edrodn\u00edch textur pro mo\u0159sk\u00e9 schr\u00e1nky",
    "page-subtitle-home": "Diplomov\u00e1 pr\u00e1ce zam\u011b\u0159en\u00e1 na modelov\u00e1n\u00ed vzor\u016f pomoc\u00ed reak\u010dn\u011b-difuzn\u00edch syst\u00e9m\u016f a jejich aplikaci ve virtu\u00e1ln\u00ed realit\u011b.",
    "home-thesis-badge": "Zalo\u017eeno na modelu aktiv\u00e1tor\u2013inhibitor dle Meinhardta",
    "home-description": "Objevte s\u00edlu matematiky v p\u0159\u00edrodn\u00edch textur\u00e1ch. Aplikace vyu\u017e\u00edv\u00e1 reak\u010dn\u011b-difuzn\u00ed modely pro generov\u00e1n\u00ed vzor\u016f mu\u0161l\u00ed a jejich aplikaci na 3D modely.",
    "features-title": "Funkce aplikace",
    "feature-1-title": "Reak\u010dn\u011b-difuzn\u00ed modely",
    "feature-1-desc": "Generujte komplexn\u00ed vzory pomoc\u00ed aktiv\u00e1tor-inhibitor model\u016f",
    "feature-2-title": "3D vizualizace",
    "feature-2-desc": "Vytv\u00e1\u0159ejte vlnov\u00e9 vzory s r\u016fzn\u00fdmi frekvencemi",
    "feature-3-title": "Interaktivn\u00ed rozhran\u00ed",
    "feature-3-desc": "Generujte pruhovan\u00e9 textury s nastaviteln\u00fdmi parametry",
    "feature-4-title": "Export a sta\u017een\u00ed",
    "feature-4-desc": "Ulo\u017ete si vygenerovan\u00e9 textury ve vysok\u00e9 kvalit\u011b",
    "get-started": "Za\u010d\u00edt vytv\u00e1\u0159et",
    "stagePlaceholder": "Vyberte mo\u017enost",
    "stageLabel": "F\u00e1ze",
    "stageSelectionHelp": "Nejd\u0159\u00edv vyberte konkr\u00e9tn\u00ed f\u00e1zi.",
    "formTitle": "Parametry modelu",
    "resultTextureTitle": "V\u00fdsledn\u00e1 textura",
    "generateTexture": "Generovat texturu",
    "generatingTexture": "Generuji...",
    "imagePlaceholder": "Vygenerovan\u00e1 textura se zobraz\u00ed zde",
    "colorScheme": "Barevn\u00e9 sch\u00e9ma",
    "baseColor": "Z\u00e1kladn\u00ed barva",
    "contrastColor": "Kontrastn\u00ed barva",
    "view": "Zobrazit",
    "download": "St\u00e1hnout",
    "modelTitle": "3D vizualizace",
    "shellSelectLabel": "Vyberte typ mu\u0161le:",
    "loading-model": "Na\u010d\u00edt\u00e1m 3D model...",
    "instruction-drag": "P\u0159et\u00e1hn\u011bte texturu na mu\u0161li pro aplikaci",
    "instruction-mouse": "Lev\u00e9 tla\u010d\u00edtko: ot\u00e1\u010den\u00ed \u2022 Kole?ko my\u0161i: p\u0159ibl\u00ed\u017een\u00ed / odd\u00e1len\u00ed",
    "instruction-mobile": "Mobil: 1 prst = ot\u00e1\u010den\u00ed \u2022 2 prsty = p\u0159ibl\u00ed\u017een\u00ed sev\u0159en\u00edm",
    "reset-texture": "Resetovat texturu",
    "change-model": "Zm\u011bnit model",
    "popup-close-info": "ESC / Kliknut\u00ed mimo / Sta\u017een\u00edm dol\u016f zav\u0159ete",
    "popup-zoom-info": "Dvojklik pro p\u0159ibl\u00ed\u017een\u00ed \u2022 Na mobilu p\u0159ibl\u00ed\u017e\u00edte sev\u0159en\u00edm",
    "page-title-ai": "Aktiv\u00e1tor-Inhibitor Model",
    "page-subtitle-ai": "Nastavte parametry reak\u010dn\u011b-difuzn\u00edho modelu pro generov\u00e1n\u00ed komplexn\u00edch vzor\u016f a textur",
    "page-title-re": "Model n\u00e1hodn\u00e9 poruchy",
    "page-subtitle-re": "Lok\u00e1ln\u00ed stochastick\u00e1 porucha b\u011bhem v\u00fdvoje vzoru",
    "model-params": "Parametry modelu",
    "constant-k": "Konstanta K",
    "constant-k-help": "Rychlost reak\u010dn\u00edho procesu (0.0001 - 5.0)",
    "max-time": "Maxim\u00e1ln\u00ed \u010das",
    "max-time-help": "Doba simulace v \u010dasov\u00fdch jednotk\u00e1ch",
    "time-step": "\u010casov\u00fd krok (\u0394t)",
    "time-step-help": "P\u0159esnost simula\u010dn\u00edho kroku",
    "source-density": "Hustota zdroje (s)",
    "source-density-help": "S\u00edla autokatal\u00fdzy (0.01 - 0.20)",
    "inhibitor-diffusion": "Difuze inhibitoru (D_b)",
    "inhibitor-diffusion-help": "Rychlost difuze inhibitoru (0.10 - 0.80)",
    "activator-decay": "Rozpad aktiv\u00e1toru (r_a)",
    "activator-decay-help": "Rychlost rozpadu aktiv\u00e1toru (0.01 - 0.30)",
    "inhibitor-decay": "Rozpad inhibitoru (r_b)",
    "inhibitor-decay-help": "Rychlost rozpadu inhibitoru (0.01 - 0.30)",
    "param-K": "Konstanta K",
    "param-t_max": "Maxim\u00e1ln\u00ed \u010das",
    "param-dt": "\u010casov\u00fd krok (\u0394t)",
    "param-size": "Velikost m\u0159\u00ed\u017eky",
    "param-s": "Hustota zdroje (s)",
    "param-r_a": "Rozpad aktiv\u00e1toru (r_a)",
    "param-r_b": "Rozpad inhibitoru (r_b)",
    "param-b_a": "Produkce aktiv\u00e1toru (b_a)",
    "param-b_b": "Produkce inhibitoru (b_b)",
    "param-D_a": "Difuze aktiv\u00e1toru (D_a)",
    "param-D_b": "Difuze inhibitoru (D_b)",
    "param-seed": "N\u00e1hodn\u00e9 semeno",
    "param-delta_t": "\u010casov\u00fd krok (\u0394t)",
    "param-dx": "Prostorov\u00fd krok (\u0394x)",
    "param-random_seed": "N\u00e1hodn\u00e9 semeno",
    "param-initial_noise_a_amplitude": "Po\u010d\u00e1te\u010dn\u00ed \u0161um aktiv\u00e1toru (A)",
    "param-initial_noise_b_amplitude": "Po\u010d\u00e1te\u010dn\u00ed \u0161um inhibitoru (B)",
    "param-initial_noise_smoothing_passes": "Vyhlazen\u00ed po\u010d\u00e1te\u010dn\u00edho \u0161umu",
    "param-early_smoothing_fraction": "Pod\u00edl ran\u00e9ho vyhlazen\u00ed",
    "param-early_smoothing_strength": "S\u00edla ran\u00e9ho vyhlazen\u00ed",
    "randomErrorToggleLabel": "N\u00e1hodn\u00e1 porucha",
    "randomErrorToggleHelp": "Zap\u00edn\u00e1 nebo vyp\u00edn\u00e1 stochastickou poruchu b\u011bhem simulace.",
    "randomErrorProfileTitle": "Profil n\u00e1hodn\u00e9 poruchy",
    "randomErrorProfileDesc": "Pouze pro \u010dten\u00ed. V\u00fdchoz\u00ed hodnoty pro vybranou f\u00e1zi.",
    "randomErrorProfileHelp": "Rozbalte nebo sbalte parametry disturbance.",
    "randomParametersEmpty": "Nejprve vyberte konkr\u00e9tn\u00ed f\u00e1zi.",
    "randomErrorLabels": {
        "strength": "S\u00edla",
        "duration": "Trv\u00e1n\u00ed",
        "frequency": "Frekvence",
        "probability": "Pravd\u011bpodobnost",
        "num_regions": "Oblasti",
        "region_size": "Velikost oblasti",
        "jitter": "Jitter",
        "micro_noise": "Mikro-\u0161um",
        "alpha_var": "Alpha var",
        "beta": "Beta",
        "drift_x": "Drift X",
        "drift_y": "Drift Y",
        "drift_frequency": "Drift frequency"
    },
    "stageLabels": {
        "1": "F\u00e1ze 1 / Ran\u00e1 formace",
        "2": "F\u00e1ze 2 / Vznikaj\u00edc\u00ed vzor",
        "3": "F\u00e1ze 3 / Vyvinut\u00fd vzor",
        "4": "F\u00e1ze 4 / Stabilizovan\u00fd vzor",
        "5": "F\u00e1ze 5 / Fin\u00e1ln\u00ed vzor"
    },
    "stageDescriptions": {
        "1": "Ran\u00fd pre-pattern s jemnou konkurenc\u00ed kandid\u00e1t\u016f.",
        "2": "Vznikaj\u00edc\u00ed vzor s postupnou selekc\u00ed.",
        "3": "Jasn\u011b \u010diteln\u00fd a vyvinut\u00fd vzor.",
        "4": "Stabilizovan\u00e1 struktura s ust\u00e1lenou geometri\u00ed.",
        "5": "Fin\u00e1ln\u00ed textura s \u010dist\u00fdm a stabiln\u00edm vzhledem."
    },
    "3d-visualization": "3D vizualizace",
    "select-shell-type": "Vyberte typ mu\u0161le:",
    "shell-buccinidae": "Buccinidae (Littorina)",
    "shell-fasciolariidae": "Fasciolariidae (T\u0159\u00edslovky)",
    "shell-moon-snail": "M\u011bs\u00ed\u010dn\u00ed \u0161nek",
    "shell-muricidae": "Muricidae (Murexov\u00e9)",
    "shell-pecten": "Pecten (H\u0159ebenatka)",
    "shell-whelk": "Mo\u0159sk\u00fd pl\u017e",
    "texture-generated": "Textura byla \u00fasp\u011b\u0161n\u011b vygenerov\u00e1na!",
    "texture-applied": "Textura byla \u00fasp\u011b\u0161n\u011b aplikov\u00e1na na mu\u0161li!",
    "texture-reset": "Textura byla resetov\u00e1na na p\u016fvodn\u00ed barvy!",
    "model-loading": "Na\u010d\u00edt\u00e1m model:",
    "texture-generation-error": "Chyba p\u0159i generov\u00e1n\u00ed textury",
    "server-error": "Chyba p\u0159i komunikaci se serverem",
    "model-not-ready": "Model nen\u00ed p\u0159ipraven pro aplikaci textury",
    "enter-valid-values": "Zadejte platn\u00e9 hodnoty pro v\u0161echny parametry",
    "fallback-model": "Pou\u017eit n\u00e1hradn\u00ed model",
    "language": "Jazyk",
    "czech": "\u010ce\u0161tina",
    "english": "Angli\u010dtina",
    "language-switched": "Jazyk byl zm\u011bn\u011bn",
    "theme-dark": "Tmav\u00fd",
    "theme-light": "Sv\u011btl\u00fd",
    "switch-to-light": "P\u0159epnout na sv\u011btl\u00fd re\u017eim",
    "switch-to-dark": "P\u0159epnout na tmav\u00fd re\u017eim",
    "coming-soon": "Brzy k dispozici",
    "pattern-evolution": "V\u00fdvoj vzoru",
    "pattern-evolution-info": "Vizualizace 4 f\u00e1z\u00ed v\u00fdvoje vzoru podle aktu\u00e1ln\u00edch parametr\u016f",
    "pattern-evolution-param-info": "Pattern Evolution pou\u017e\u00edv\u00e1 aktu\u00e1ln\u011b nastaven\u00e9 parametry modelu (K, \u010das, krok, stabilitu apod.) a pouze sleduje v\u00fdvoj vzoru v \u010dase. Pokud uprav\u00edte parametry, zm\u011bn\u00ed se i tvar a pr\u016fb\u011bh jednotliv\u00fdch f\u00e1z\u00ed (25 %, 50 %, 75 %, 100 %).",
    "show-pattern-evolution": "Zobrazit v\u00fdvoj vzoru",
    "early-stage": "Ran\u00e1 f\u00e1ze",
    "mid-stage": "St\u0159edn\u00ed f\u00e1ze",
    "late-stage": "Pozdn\u00ed f\u00e1ze",
    "final-stage": "Fin\u00e1ln\u00ed f\u00e1ze",
    "random-error-title": "Random Error (Biologick\u00e9 poruchy)",
    "random-error-desc": "V\u011bdecky podlo\u017een\u00e9 lok\u00e1ln\u00ed poruchy vzoru \u2013 simuluje biologick\u00e9 defekty v p\u0159irozen\u00fdch mu\u0161l\u00edch",
    "random-error-info": "P\u0159id\u00e1v\u00e1 biologick\u00e9 poruchy pigmentu, napodobuj\u00edc\u00ed defekty p\u0159irozen\u00fdch mu\u0161l\u00ed",
    "random-error-formula-desc": "P\u0159id\u00e1v\u00e1 \u010dasov\u011b omezen\u00e9 lok\u00e1ln\u00ed perturbace do aktiv\u00e1torov\u00e9 rovnice",
    "strength-label": "S\u00edla (\u03b1)",
    "strength-range": "0.01-0.05",
    "strength-help": "Amplituda perturbace - vy\u0161\u0161\u00ed = siln\u011bj\u0161\u00ed poruchy",
    "duration-label": "Trv\u00e1n\u00ed",
    "duration-range": "10-50 steps",
    "duration-help": "Jak dlouho ka\u017ed\u00e1 perturbace trv\u00e1",
    "frequency-label": "Frekvence",
    "frequency-range": "0.05-0.2",
    "frequency-help": "\u010casov\u00e1 oscilace sin(2\u03c0ft)",
    "probability-label": "Pravd\u011bpodobnost",
    "probability-range": "0.01-0.1",
    "probability-help": "\u0160ance na spu\u0161t\u011bn\u00ed nov\u00e9 perturbace ka\u017ed\u00fd krok",
    "num-regions-label": "Po\u010det z\u00f3n",
    "num-regions-range": "1-10",
    "num-regions-help": "Kolik oblast\u00ed bude sou\u010dasn\u011b naru\u0161eno",
    "region-size-label": "Velikost z\u00f3ny",
    "region-size-range": "5-20 px",
    "region-size-help": "Velikost ka\u017ed\u00e9 naru\u0161en\u00e9 oblasti v pixelech",
    "quick-presets": "Rychl\u00e9 p\u0159edvolby:",
    "preset-gentle": "Jemn\u00e9",
    "preset-moderate": "St\u0159edn\u00ed",
    "preset-active": "Aktivn\u00ed",
    "dynamic-instability": "Dynamick\u00e1 nestabilita",
    "dynamic-instability-help": "Simuluje rozpad pigmentu b\u011bhem v\u00fdvoje vzoru",
    "tooltip-preset": "Vybere p\u0159ednastaven\u00fd re\u017eim simulace.<br><strong>Stable</strong> = klidn\u00e9 vzory,<br><strong>Balanced</strong> = rovnov\u00e1ha mezi aktivac\u00ed a inhibic\u00ed,<br><strong>Active</strong> = rychl\u00e9 r\u016fstov\u00e9 zm\u011bny,<br><strong>Chaotic</strong> = nestabiln\u00ed struktury",
    "tooltip-k": "Ovliv\u0148uje rychlost reakce.<br><strong>Vy\u0161\u0161\u00ed K</strong> \u2192 rychlej\u0161\u00ed v\u00fdvoj a kontrastn\u011bj\u0161\u00ed vzor<br><strong>Ni\u017e\u0161\u00ed K</strong> \u2192 jemn\u011bj\u0161\u00ed a pomalej\u0161\u00ed zm\u011bny",
    "tooltip-tmax": "Ur\u010duje d\u00e9lku simulace.<br><strong>Del\u0161\u00ed \u010das</strong> \u2192 vznik stabiln\u011bj\u0161\u00edch a slo\u017eit\u011bj\u0161\u00edch struktur<br><strong>Krat\u0161\u00ed \u010das</strong> \u2192 zachyt\u00ed ran\u011bj\u0161\u00ed f\u00e1ze v\u00fdvoje",
    "tooltip-dt": "P\u0159esnost v\u00fdpo\u010dtu.<br><strong>Men\u0161\u00ed krok</strong> = p\u0159esn\u011bj\u0161\u00ed, ale pomalej\u0161\u00ed<br><strong>V\u011bt\u0161\u00ed krok</strong> = rychlej\u0161\u00ed, ale m\u00e9n\u011b p\u0159esn\u00e9",
    "tooltip-strength": "Ur\u010duje intenzitu lok\u00e1ln\u00edch poruch. Vy\u0161\u0161\u00ed = v\u00fdrazn\u011bj\u0161\u00ed poruchy, ni\u017e\u0161\u00ed = jemn\u00e9 biologick\u00e9 \u0161umy",
    "tooltip-duration": "D\u00e9lka p\u016fsoben\u00ed defektu. Del\u0161\u00ed trv\u00e1n\u00ed \u2192 v\u011bt\u0161\u00ed z\u00e1sah do v\u00fdvoje vzoru, krat\u0161\u00ed trv\u00e1n\u00ed \u2192 rychl\u00e9 impulsy",
    "tooltip-frequency": "Jak \u010dasto se poruchy objevuj\u00ed b\u011bhem simulace. Vy\u0161\u0161\u00ed frekvence \u2192 v\u00edce drobn\u00fdch defekt\u016f, ni\u017e\u0161\u00ed frekvence \u2192 ojedin\u011bl\u00e9 v\u011bt\u0161\u00ed poruchy",
    "tooltip-dynamic-inst": "Simuluje spont\u00e1nn\u00ed rozpad nebo slu\u010dov\u00e1n\u00ed pigmentov\u00fdch oblast\u00ed.<br><strong>Aktiv\u00e1tor</strong> destabilizuje r\u016fstov\u00e9 oblasti<br><strong>Inhibitor</strong> je rozkl\u00e1d\u00e1",
    "preset-label": "Preset",
    "preset-help": "Vyberte p\u0159ednastaven\u00e9 parametry",
    "noise-target-label": "C\u00edl modifikace (Target)",
    "noise-target-help": "Kter\u00e1 pole rovnic modifikovat",
    "noise-target-a": "Aktiv\u00e1tor (A)",
    "noise-target-b": "Inhibitor (B)",
    "noise-target-both": "Oba (Both)",
    "noise-strength-label": "S\u00edla nestability (Instability Strength)",
    "noise-strength-help": "Amplituda multiplikativn\u00ed modifikace (0.001 - 0.05)",
    "stage-selector-label": "Vyberte f\u00e1zi pro n\u00e1hled v detailu:",
    "stage-selector-help": "Vyberte f\u00e1zi pro zobrazen\u00ed v pln\u00e9 velikosti v\u00fd\u0161e s mo\u017enost\u00ed anal\u00fdzy",
    "dynamic-instability-title": "Dynamick\u00e1 nestabilita",
    "dynamic-instability-desc": "Modifikuje rovnice pro lok\u00e1ln\u00ed rozpad vzoru a shlukov\u00e1n\u00ed pigmentu",
    "option-stable": "Stable (m\u011bkk\u00e9 vzory)",
    "option-balanced": "Balanced (st\u0159edn\u00ed kontrast)",
    "option-active": "Active (vysok\u00fd kontrast)",
    "option-chaotic": "Chaotic (nestabiln\u00ed)",
    "show-biological-heatmap": "Zobrazit biologickou heatmapu",
    "biological-heatmap-tooltip": "Zobraz\u00ed biologickou heatmapu \u2014 barevn\u00e9 rozlo\u017een\u00ed aktivity modelu, kde \u010erven\u00e9 oblasti ozna\u010duj\u00ed lok\u00e1ln\u00ed poruchy nebo nestabilitu",
    "biological-heatmap-title": "Biologick\u00e1 heatmapa",
    "heatmap-legend-title": "Legenda",
    "heatmap-legend-stable": "Stabiln\u00ed",
    "heatmap-legend-transition": "P\u0159echodov\u00e9",
    "heatmap-legend-unstable": "Nestabiln\u00ed",
    "heatmap-active": "Biologick\u00e1 heatmapa zobrazena",
    "heatmap-disabled": "Biologick\u00e1 heatmapa skryta",
    "heatmap-not-available": "Heatmapa nen\u00ed dostupn\u00e1. Pros\u00edm vygenerujte texturu s povolenou volbou \"Zobrazit biologickou heatmapu\".",
    "texture-heatmap-toggle": "Zobrazit heatmapu",
    "texture-heatmap-tooltip": "Zobraz\u00ed barevnou heatmapu odvozenou z aktu\u00e1ln\u00ed textury.",
    "texture-heatmap-help": "Vizualizuje aktu\u00e1ln\u00ed texturu jako heatmapu pod v\u00fdsledn\u00fdm obr\u00e1zkem.",
    "texture-heatmap-title": "Heatmapa textury",
    "texture-heatmap-note": "Heatmapa je odvozena z aktu\u00e1ln\u011b vygenerovan\u00e9 textury.",
    "texture-heatmap-visible": "HEATMAPA ZOBRAZENA",
    "texture-heatmap-hidden": "HEATMAPA SKRYTA",
    "texture-heatmap-not-available": "Nejprve vygenerujte texturu, pak lze heatmapu zobrazit.",
    "static-mode": "Statick\u00e9 parametry",
    "dynamic-mode": "Dynamick\u00e9 parametry",
    "mode-description-static": "Statick\u00e9 parametry jsou pouze pro \u010dten\u00ed a odpov\u00eddaj\u00ed zvolen\u00e9mu presetu.",
    "mode-description-dynamic": "Dynamick\u00e9 parametry lze upravovat ru\u010dn\u011b a generovat s nimi vlastn\u00ed v\u00fdsledek.",
    "dynamic-parameter-hint": "Tip: za\u010dn\u011bte s presety a upravte jen to, co opravdu chcete zm\u011bnit.",
    "dynamic-random-error-hint": "Tip: v dynamick\u00e9m re\u017eimu m\u016f\u017eete doladit i random error p\u0159ed generov\u00e1n\u00edm.",
    "randomErrorProfileDescDynamic": "Editovateln\u00e9 v\u00fdchoz\u00ed hodnoty pro zvolenou f\u00e1zi. Zapn\u011bte random error, aby se pou\u017eily.",
    "static-parameters-empty": "Nejprve vyberte konkr\u00e9tn\u00ed f\u00e1zi.",
    "static-parameters-panel-title": "P\u0159ednastaven\u00e9 hodnoty",
    "static-parameters-panel-desc": "Hodnoty pro vybranou f\u00e1zi jsou pouze pro \u010dten\u00ed.",
    "staticModeState": "POUZE PRO \u010cTEN\u00cd",
    "dynamicModeState": "EDITOVATELN\u00c9",
    "parameterModeTitle": "Parametry re\u017eimu",
    "progressionMode": "Dynamick\u00e9 parametry",
    "progressionModeDescription": "Dynamick\u00e9 parametry \u0159\u00edd\u00ed pr\u016fb\u011bh v\u00fdvoje a vytv\u00e1\u0159ej\u00ed space-time diagram.",
    "select-preset": "Vyberte preset",
    "tooltip-preset-new": "Vyberte p\u0159ednastaven\u00fd set:<br><strong>Low Diffusion:</strong> Ostr\u00e9 vzory,<br><strong>Medium Diffusion:</strong> Vyv\u00e1\u017een\u00e9 vlny,<br><strong>High Diffusion:</strong> Jemn\u00e9 p\u0159echody,<br><strong>Balanced:</strong> Obecn\u011b vyv\u00e1\u017een\u00fd",
    "preset-low-diffusion": "N\u00edzk\u00e1 difuze (ostr? vzory)",
    "preset-medium-diffusion": "St\u0159edn\u00ed difuze (vyv\u00e1\u017een\u00e9)",
    "preset-high-diffusion": "Vysok\u00e1 difuze (jemn\u00e9 p\u0159echody)",
    "preset-balanced": "Vyv\u00e1\u017een\u00fd",
    "preset-help-new": "Parametry budou nastaveny automaticky",
    "nav-figure211": "Obr\u00e1zek 2.11 - Skvrny",
    "nav-figure23": "Obr\u00e1zek 2.3 - Periodick\u00e9 vzory",
    "nav-figure212": "Obr\u00e1zek 2.12 - Labyrinty",
    "home-figure211-title": "Obr\u00e1zek 2.11 - Skvrny",
    "home-figure211-desc": "Reprodukovateln\u00fd v\u00fdvoj skvrnov\u00e9ho vzoru s v\u00fdvojov\u00fdmi kontroln\u00edmi body a pr\u016fzkumem n\u00e1hodn\u00e9 poruchy.",
    "home-figure211-button": "Otev\u0159\u00edt skvrny",
    "home-figure23-title": "Obr\u00e1zek 2.3 - Periodick\u00e9 vzory",
    "home-figure23-desc": "V\u00fdvoj pruh\u016f v re\u017eimu statick\u00fdch i dynamick\u00fdch parametr\u016f s postupn\u00fdmi presety a volitelnou n\u00e1hodnou poruchou.",
    "home-figure23-button": "Otev\u0159\u00edt periodick\u00e9 vzory",
    "home-figure212-title": "Obr\u00e1zek 2.12 - Labyrinty",
    "home-figure212-desc": "Vznik kan\u00e1l\u016f a labyrint\u016f se stejnou reprodukovatelnou simulac\u00ed a v\u00fdvojov\u00fdm workflow.",
    "home-figure212-button": "Otev\u0159\u00edt labyrinty",
    "figure23-page-title": "Obr\u00e1zek 2.3 - Periodick\u00e9 vzory",
    "figure23-page-subtitle": "Dominantn\u00ed, jasn\u011b odd\u011blen\u00e9 svisl\u00e9 pruhy",
    "figure211-page-title": "Obr\u00e1zek 2.11 - Skvrny",
    "figure211-page-subtitle": "Meinhardt\u016fv v\u00fdvoj skvrn z obr\u00e1zku 2.11",
    "figure212-page-title": "Obr\u00e1zek 2.12 - Labyrinty",
    "figure212-page-subtitle": "V\u00fdvoj labyrint\u016f v etap\u00e1ch a v\u00fdvojov\u00e9m re\u017eimu",
    "stage-tooltip-info": "F\u00e1ze reprezentuj\u00ed v\u00fdvoj vzoru od ran\u00e9 formace po stabiln\u00ed strukturu.",
    "random-error-tooltip-info": "Random error zav\u00e1d\u00ed lok\u00e1ln\u00ed stochastickou poruchu b\u011bhem v\u00fdvoje; jeho efekt se li\u0161\u00ed podle typu modelu."
    },
    "en": {
        "nav-home": "Home",
        "nav-activator-inhibitor": "Activator-Inhibitor",
        "nav-random-error": "Random Error",
        "nav-waves": "Oscillating Waves",
        "nav-stripes": "Zebra Stripes",
        "page-title-home": "Natural Texture Generator for Sea Shells",
        "page-subtitle-home": "Master's thesis focused on modeling patterns using reaction-diffusion systems and their application in virtual reality.",
        "home-thesis-badge": "Based on activator-inhibitor models by Meinhardt",
        "home-description": "Discover the power of mathematics in natural textures. The application uses reaction-diffusion models to generate shell patterns and apply them to 3D models.",
        "features-title": "Application Features",
        "feature-1-title": "Reaction-Diffusion Models",
        "feature-1-desc": "Generate complex patterns using activator-inhibitor models",
        "feature-2-title": "3D Visualization",
        "feature-2-desc": "Create wave patterns with various frequencies",
        "feature-3-title": "Interactive Interface",
        "feature-3-desc": "Generate striped textures with configurable parameters",
        "feature-4-title": "Export and Download",
        "feature-4-desc": "Save generated textures in high quality",
        "get-started": "Start Creating",
        "stagePlaceholder": "Select an option",
        "stageLabel": "Stage",
        "stageSelectionHelp": "Select a concrete stage before generating.",
        "formTitle": "Model Parameters",
        "resultTextureTitle": "Result Texture",
        "generateTexture": "Generate texture",
        "generatingTexture": "Generating...",
        "imagePlaceholder": "Generated texture will appear here",
        "colorScheme": "Color scheme",
        "baseColor": "Base color",
        "contrastColor": "Contrast color",
        "view": "View",
        "download": "Download",
        "modelTitle": "3D Visualization",
        "shellSelectLabel": "Select shell type:",
        "loading-model": "Loading 3D model...",
        "instruction-drag": "Drag texture onto shell to apply",
        "instruction-mouse": "Left click: rotate ? Mouse wheel: zoom in/out",
        "instruction-mobile": "Mobile: 1 finger = rotate ? 2 fingers = pinch zoom",
        "reset-texture": "Reset Texture",
        "change-model": "Change Model",
        "popup-close-info": "ESC / Click outside / Swipe down to close",
        "popup-zoom-info": "Double click to zoom ? Pinch to zoom on mobile",
        "page-title-ai": "Activator-Inhibitor Model",
        "page-subtitle-ai": "Set parameters for the reaction-diffusion model to generate complex patterns and textures",
        "page-title-re": "Random Error Model",
        "page-subtitle-re": "Local stochastic disturbance during pattern evolution",
        "model-params": "Model Parameters",
        "constant-k": "Constant K",
        "constant-k-help": "Reaction process rate (0.0001 - 5.0)",
        "max-time": "Maximum Time",
        "max-time-help": "Simulation duration in time units",
        "time-step": "Time Step (?t)",
        "time-step-help": "Simulation step precision",
        "source-density": "Source Density (s)",
        "source-density-help": "Autocatalysis strength (0.01 - 0.20)",
        "inhibitor-diffusion": "Inhibitor Diffusion (D_b)",
        "inhibitor-diffusion-help": "Inhibitor diffusion rate (0.10 - 0.80)",
        "activator-decay": "Activator Decay (r_a)",
        "activator-decay-help": "Activator decay rate (0.01 - 0.30)",
        "inhibitor-decay": "Inhibitor Decay (r_b)",
        "inhibitor-decay-help": "Inhibitor decay rate (0.01 - 0.30)",
        "param-K": "Constant K",
        "param-t_max": "Maximum Time",
        "param-dt": "Time Step (\u0394t)",
        "param-size": "Grid Size",
        "param-s": "Source Density (s)",
        "param-r_a": "Activator Decay (r_a)",
        "param-r_b": "Inhibitor Decay (r_b)",
        "param-b_a": "Activator Production (b_a)",
        "param-b_b": "Inhibitor Production (b_b)",
        "param-D_a": "Activator Diffusion (D_a)",
        "param-D_b": "Inhibitor Diffusion (D_b)",
        "param-seed": "Seed",
        "param-delta_t": "Time Step (\u0394t)",
        "param-dx": "Spatial Step (\u0394x)",
        "param-random_seed": "Random Seed",
        "param-initial_noise_a_amplitude": "Initial Noise Amplitude (A)",
        "param-initial_noise_b_amplitude": "Initial Noise Amplitude (B)",
        "param-initial_noise_smoothing_passes": "Initial Smoothing Passes",
        "param-early_smoothing_fraction": "Early Smoothing Fraction",
        "param-early_smoothing_strength": "Early Smoothing Strength",
        "randomErrorToggleLabel": "Random error",
        "randomErrorToggleHelp": "Toggle the stochastic disturbance during simulation.",
        "randomErrorProfileTitle": "Random error profile",
        "randomErrorProfileDesc": "Read-only defaults for the selected stage.",
        "randomErrorProfileHelp": "Expand or collapse the disturbance parameters.",
        "randomParametersEmpty": "Please select a stage first.",
        "texture-heatmap-toggle": "Show heatmap",
        "texture-heatmap-tooltip": "Show a color-coded heatmap derived from the current texture.",
        "texture-heatmap-help": "Visualize the current texture as a heatmap below the result image.",
        "texture-heatmap-title": "Texture heatmap",
        "texture-heatmap-note": "The heatmap is derived from the current generated texture.",
        "texture-heatmap-visible": "HEATMAP SHOWN",
        "texture-heatmap-hidden": "HEATMAP HIDDEN",
        "texture-heatmap-not-available": "Generate a texture first, then the heatmap can be shown.",
        "randomErrorLabels": {
            "strength": "Strength",
            "duration": "Duration",
            "frequency": "Frequency",
            "probability": "Probability",
            "num_regions": "Regions",
            "region_size": "Region size",
            "jitter": "Jitter",
            "micro_noise": "Micro noise",
            "alpha_var": "Alpha var",
        "beta": "Beta",
        "drift_x": "Drift X",
        "drift_y": "Drift Y",
        "drift_frequency": "Drift frequency"
    },
    "stageLabels": {
        "1": "Stage 1 / Early formation",
        "2": "Stage 2 / Emerging pattern",
        "3": "Stage 3 / Developed pattern",
        "4": "Stage 4 / Stabilized pattern",
        "5": "Stage 5 / Final pattern"
    },
    "stageDescriptions": {
        "1": "Early pre-pattern with gentle candidate competition.",
        "2": "Emerging pattern with gradual selection.",
        "3": "Clear and developed pattern.",
        "4": "Stabilized structure with settled geometry.",
        "5": "Final texture with a clean, stable look."
    },
        "3d-visualization": "3D Visualization",
        "select-shell-type": "Select shell type:",
        "shell-buccinidae": "Buccinidae (Whelk)",
        "shell-fasciolariidae": "Fasciolariidae (Tulip Shell)",
        "shell-moon-snail": "Moon snail",
        "shell-muricidae": "Muricidae (Murex)",
        "shell-pecten": "Pecten (Scallop)",
        "shell-whelk": "Whelk",
        "texture-generated": "Texture generated successfully!",
        "texture-applied": "Texture applied successfully to shell!",
        "texture-reset": "Texture reset to original colors!",
        "model-loading": "Loading model:",
        "texture-generation-error": "Error generating texture",
        "server-error": "Server communication error",
        "model-not-ready": "Model not ready for texture application",
        "enter-valid-values": "Enter valid values for all parameters",
        "fallback-model": "Using fallback model",
        "language": "Language",
        "czech": "Czech",
        "english": "English",
        "language-switched": "Language switched",
        "theme-dark": "Dark",
        "theme-light": "Light",
        "switch-to-light": "Switch to light mode",
        "switch-to-dark": "Switch to dark mode",
        "coming-soon": "Coming Soon",
        "pattern-evolution": "Pattern Evolution",
        "pattern-evolution-info": "Visualization of 4 pattern development phases based on current parameters",
        "pattern-evolution-param-info": "Pattern Evolution uses your current simulation parameters (K, max time, step size, stability mode, etc.) and visualizes how the pattern evolves over time. Adjusting parameters will affect all 4 stages (25%, 50%, 75%, 100%).",
        "show-pattern-evolution": "Show Pattern Evolution",
        "early-stage": "Early Stage",
        "mid-stage": "Mid Stage",
        "late-stage": "Late Stage",
        "final-stage": "Final Stage",
        "random-error-title": "Random Error (Biological Perturbation)",
        "random-error-desc": "Scientifically based local pattern disturbances - simulates biological defects in natural shells",
        "random-error-info": "Adds biological pigment disturbances, mimicking defects in natural shells",
        "random-error-formula-desc": "Adds time-limited local perturbations to the activator equation",
        "strength-label": "Strength",
        "strength-range": "0.01-0.05",
        "strength-help": "Perturbation amplitude - higher = stronger disturbances",
        "duration-label": "Duration",
        "duration-range": "10-50 steps",
        "duration-help": "How long each perturbation lasts",
        "frequency-label": "Frequency",
        "frequency-range": "0.05-0.2",
        "frequency-help": "Temporal oscillation sin(2?ft)",
        "probability-label": "Probability",
        "probability-range": "0.01-0.1",
        "probability-help": "Chance of triggering a new perturbation each step",
        "num-regions-label": "Number of Regions",
        "num-regions-range": "1-10",
        "num-regions-help": "How many areas will be disturbed simultaneously",
        "region-size-label": "Region Size",
        "region-size-range": "5-20 px",
        "region-size-help": "Size of each disturbed region in pixels",
        "quick-presets": "Quick Presets:",
        "preset-gentle": "Gentle",
        "preset-moderate": "Moderate",
        "preset-active": "Active",
        "dynamic-instability": "Dynamic Instability",
        "dynamic-instability-help": "Simulates pigment breakdown during pattern development",
        "tooltip-preset": "Selects the simulation preset mode.<br><strong>Stable</strong> = calm patterns,<br><strong>Balanced</strong> = balance between activation and inhibition,<br><strong>Active</strong> = fast growth changes,<br><strong>Chaotic</strong> = unstable structures",
        "tooltip-k": "Affects reaction rate.<br><strong>Higher K</strong> ? faster development and higher contrast pattern<br><strong>Lower K</strong> ? smoother and slower changes",
        "tooltip-tmax": "Determines simulation length.<br><strong>Longer time</strong> ? more stable and complex structures emerge<br><strong>Shorter time</strong> ? captures earlier development phases",
        "tooltip-dt": "Calculation precision.<br><strong>Smaller step</strong> = more precise, but slower<br><strong>Larger step</strong> = faster, but less precise",
        "tooltip-strength": "Determines intensity of local disturbances. Higher = more prominent defects, Lower = subtle biological noise",
        "tooltip-duration": "Duration of defect action. Longer duration ? greater impact on pattern development, Shorter duration ? quick impulses",
        "tooltip-frequency": "How often disturbances appear during simulation. Higher frequency ? more small defects, Lower frequency ? rare large disturbances",
        "tooltip-dynamic-inst": "Simulates spontaneous breakdown or merging of pigment regions.<br><strong>Activator</strong> destabilizes growth areas<br><strong>Inhibitor</strong> breaks them down",
        "preset-label": "Preset",
        "preset-help": "Choose a pre-tuned parameter set",
        "noise-target-label": "Modification Target",
        "noise-target-help": "Which equation fields to modify",
        "noise-target-a": "Activator (A)",
        "noise-target-b": "Inhibitor (B)",
        "noise-target-both": "Both",
        "noise-strength-label": "Instability Strength",
        "noise-strength-help": "Multiplicative modification amplitude (0.001 - 0.05)",
        "stage-selector-label": "Choose stage to preview in detail:",
        "stage-selector-help": "Select a stage to view it in full size above with analysis options",
        "dynamic-instability-title": "Dynamic Instability",
        "dynamic-instability-desc": "Modifies equations for local pattern breakdown and pigment clustering",
        "option-stable": "Stable (soft patterns)",
        "option-balanced": "Balanced (medium contrast)",
        "option-active": "Active (high contrast)",
        "option-chaotic": "Chaotic (unstable)",
        "show-biological-heatmap": "Show Biological Heatmap",
        "biological-heatmap-tooltip": "Displays a biological heatmap ? color-coded model activity distribution, where red areas indicate local disturbances or instability",
        "biological-heatmap-title": "Biological Heatmap",
        "heatmap-legend-title": "Legend",
        "heatmap-legend-stable": "Stable",
        "heatmap-legend-transition": "Transition",
        "heatmap-legend-unstable": "Unstable",
        "heatmap-active": "Biological heatmap shown",
        "heatmap-disabled": "Biological heatmap hidden",
        "heatmap-not-available": "Heatmap not available. Please regenerate texture with \"Show Biological Heatmap\" enabled.",
        "static-mode": "Static parameters",
        "dynamic-mode": "Dynamic parameters",
        "mode-description-static": "Static parameters are read-only and match the selected preset.",
        "mode-description-dynamic": "Dynamic parameters can be edited manually and generate custom results.",
        "dynamic-parameter-hint": "Tip: start from the preset values and change only the fields you need.",
        "dynamic-random-error-hint": "Tip: in dynamic mode you can fine-tune random error before generating.",
        "randomErrorProfileDescDynamic": "Editable defaults for the selected stage. Turn on random error to use them.",
        "static-parameters-empty": "Please select a stage first.",
        "static-parameters-panel-title": "Preset values",
        "static-parameters-panel-desc": "Values for the selected stage are read-only.",
        "staticModeState": "READ ONLY",
        "dynamicModeState": "EDITABLE",
        "parameterModeTitle": "Parameter mode",
        "progressionMode": "Dynamic parameters",
        "progressionModeDescription": "Dynamic parameters drive the selected development stage and its space-time diagram.",
        "select-preset": "Select Preset",
        "tooltip-preset-new": "Choose a preset configuration:<br><strong>Low Diffusion:</strong> Sharp patterns<br><strong>Medium Diffusion:</strong> Balanced waves<br><strong>High Diffusion:</strong> Soft gradients<br><strong>Balanced:</strong> General balanced preset",
        "preset-low-diffusion": "Low Diffusion (Sharp Patterns)",
        "preset-medium-diffusion": "Medium Diffusion (Balanced)",
        "preset-high-diffusion": "High Diffusion (Soft Gradients)",
        "preset-balanced": "Balanced",
        "preset-help-new": "Parameters will be set automatically",
        "nav-figure211": "Figure 2.11 - Spots",
        "nav-figure23": "Figure 2.3 - Periodic Patterns",
        "nav-figure212": "Figure 2.12 - Labyrinths",
        "home-figure211-title": "Figure 2.11 - Spots",
        "home-figure211-desc": "Reproducible spot-pattern evolution with development checkpoints and random-error exploration.",
        "home-figure211-button": "Open Spots",
        "home-figure23-title": "Figure 2.3 - Periodic Patterns",
        "home-figure23-desc": "Stripe evolution in static and dynamic parameter modes, with progressive presets and optional random error.",
        "home-figure23-button": "Open Periodic Patterns",
        "home-figure212-title": "Figure 2.12 - Labyrinths",
        "home-figure212-desc": "Channel and labyrinth formation with the same reproducible simulation and development workflow.",
        "home-figure212-button": "Open Labyrinths",
        "figure23-page-title": "Figure 2.3 - Periodic Patterns",
        "figure23-page-subtitle": "Dominant, well-separated vertical stripe bands",
        "figure211-page-title": "Figure 2.11 - Spots",
        "figure211-page-subtitle": "Meinhardt spot evolution from Figure 2.11",
        "figure212-page-title": "Figure 2.12 - Labyrinths",
        "figure212-page-subtitle": "Stage and development views of labyrinth evolution",
        "stage-tooltip-info": "Stages represent pattern development from early formation to a stable structure.",
        "random-error-tooltip-info": "Random error introduces a local stochastic disturbance during development; the effect depends on the model type."
    }
};

window.getFigureStageUiLanguage = function getFigureStageUiLanguage() {
    const language = window.languageSwitcher?.currentLanguage
        || localStorage.getItem('selectedLanguage')
        || 'cs';
    return language === 'en' ? 'en' : 'cs';
};

window.getFigureStageUiText = function getFigureStageUiText(key, fallback = '') {
    const language = window.getFigureStageUiLanguage();
    const bundle = window.FIGURE_STAGE_UI_TEXTS?.[language] || window.FIGURE_STAGE_UI_TEXTS?.en || {};
    const english = window.FIGURE_STAGE_UI_TEXTS?.en || {};
    const value = bundle[key];
    if (value !== undefined && value !== null) {
        return value;
    }
    const fallbackValue = english[key];
    if (fallbackValue !== undefined && fallbackValue !== null) {
        return fallbackValue;
    }
    return fallback || key;
};

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new App();
    console.log('Shell Texture Generator App initialized');
});

// Export for potential external use
window.App = App;
