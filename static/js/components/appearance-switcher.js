class AppearanceSwitcher {
    constructor() {
        if (window.appearanceSwitcherInstance) {
            return window.appearanceSwitcherInstance;
        }

        this.storageKey = 'appearancePreset';
        this.defaultAppearance = 'editorial-teal';
        this.appearances = [
            { id: 'editorial-teal', labelKey: 'appearance-editorial-teal', swatchClass: 'appearance-swatch--editorial-teal' },
            { id: 'midnight-blue', labelKey: 'appearance-midnight-blue', swatchClass: 'appearance-swatch--midnight-blue' },
            { id: 'graphite-neutral', labelKey: 'appearance-graphite-neutral', swatchClass: 'appearance-swatch--graphite-neutral' },
            { id: 'deep-forest', labelKey: 'appearance-deep-forest', swatchClass: 'appearance-swatch--deep-forest' },
            { id: 'sand-slate', labelKey: 'appearance-sand-slate', swatchClass: 'appearance-swatch--sand-slate' },
        ];
        this.currentAppearance = this.getStoredAppearance() || this.defaultAppearance;
        window.appearanceSwitcherInstance = this;
        this.init();
    }

    init() {
        this.applyAppearance(this.currentAppearance, { persist: false });
        this.createAppearanceSwitcher();
        this.bindEvents();
        this.updateControl();
    }

    getStoredAppearance() {
        return localStorage.getItem(this.storageKey);
    }

    setStoredAppearance(appearance) {
        localStorage.setItem(this.storageKey, appearance);
    }

    getLanguage() {
        const language = window.languageSwitcher?.currentLanguage
            || localStorage.getItem('selectedLanguage')
            || document.documentElement.getAttribute('lang')
            || 'cs';
        return language === 'en' ? 'en' : 'cs';
    }

    t(key, fallback = '') {
        const bundles = {
            cs: {
                'appearance-label': 'Vzhled',
                'appearance-editorial-teal': 'Editorial Teal',
                'appearance-midnight-blue': 'Midnight Blue',
                'appearance-graphite-neutral': 'Graphite Neutral',
                'appearance-deep-forest': 'Deep Forest',
                'appearance-sand-slate': 'Sand Slate',
                'appearance-open-menu': 'Otevrit vyber vzhledu',
            },
            en: {
                'appearance-label': 'Appearance',
                'appearance-editorial-teal': 'Editorial Teal',
                'appearance-midnight-blue': 'Midnight Blue',
                'appearance-graphite-neutral': 'Graphite Neutral',
                'appearance-deep-forest': 'Deep Forest',
                'appearance-sand-slate': 'Sand Slate',
                'appearance-open-menu': 'Open appearance menu',
            },
        };
        const language = this.getLanguage();
        return bundles[language]?.[key] || bundles.en[key] || fallback || key;
    }

    getAppearanceMeta(appearanceId) {
        return this.appearances.find((item) => item.id === appearanceId) || this.appearances[0];
    }

    applyAppearance(appearanceId, { persist = true } = {}) {
        const appearance = this.getAppearanceMeta(appearanceId);
        document.documentElement.setAttribute('data-appearance', appearance.id);
        this.currentAppearance = appearance.id;
        if (persist) {
            this.setStoredAppearance(appearance.id);
        }
        this.updateControl();
        document.dispatchEvent(new CustomEvent('appearanceChanged', {
            detail: { appearance: appearance.id },
        }));
    }

    createAppearanceSwitcher() {
        const existing = document.querySelector('.appearance-switcher');
        if (existing) {
            this.switcher = existing;
            this.toggleButton = existing.querySelector('.appearance-toggle');
            this.menu = existing.querySelector('.appearance-menu');
            return;
        }

        const switcher = document.createElement('div');
        switcher.className = 'appearance-switcher';

        const optionsMarkup = this.appearances.map((appearance) => `
            <button type="button" class="appearance-option" data-appearance-option="${appearance.id}">
                <span class="appearance-swatch ${appearance.swatchClass}" aria-hidden="true"></span>
                <span class="appearance-option-label" data-appearance-label="${appearance.id}">${this.t(appearance.labelKey, appearance.id)}</span>
            </button>
        `).join('');

        switcher.innerHTML = `
            <button type="button" class="appearance-toggle" aria-haspopup="true" aria-expanded="false">
                <i class="fas fa-palette" aria-hidden="true"></i>
                <span class="appearance-toggle-text">
                    <span class="appearance-toggle-caption">${this.t('appearance-label', 'Appearance')}</span>
                    <span class="appearance-current-label">${this.t(this.getAppearanceMeta(this.currentAppearance).labelKey, this.currentAppearance)}</span>
                </span>
                <i class="fas fa-chevron-down appearance-caret" aria-hidden="true"></i>
            </button>
            <div class="appearance-menu" hidden>
                ${optionsMarkup}
            </div>
        `;

        const languageSwitcher = document.querySelector('.language-switcher');
        const themeToggle = document.querySelector('.theme-toggle');

        if (languageSwitcher?.parentNode) {
            languageSwitcher.parentNode.insertBefore(switcher, languageSwitcher.nextSibling);
        } else if (themeToggle?.parentNode) {
            themeToggle.parentNode.insertBefore(switcher, themeToggle.nextSibling);
        } else {
            document.body.appendChild(switcher);
        }

        this.switcher = switcher;
        this.toggleButton = switcher.querySelector('.appearance-toggle');
        this.menu = switcher.querySelector('.appearance-menu');
    }

    bindEvents() {
        if (!this.switcher) {
            return;
        }

        this.toggleButton?.addEventListener('click', (event) => {
            event.stopPropagation();
            this.toggleMenu();
        });

        this.menu?.addEventListener('click', (event) => {
            const button = event.target.closest('[data-appearance-option]');
            if (!button) {
                return;
            }

            const appearance = button.getAttribute('data-appearance-option');
            this.applyAppearance(appearance);
            this.closeMenu();
        });

        document.addEventListener('click', (event) => {
            if (!this.switcher.contains(event.target)) {
                this.closeMenu();
            }
        });

        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') {
                this.closeMenu();
            }
        });

        document.addEventListener('languageChanged', () => {
            this.updateControl();
        });
    }

    updateControl() {
        if (!this.switcher) {
            return;
        }

        const currentMeta = this.getAppearanceMeta(this.currentAppearance);
        const caption = this.switcher.querySelector('.appearance-toggle-caption');
        const currentLabel = this.switcher.querySelector('.appearance-current-label');

        if (caption) {
            caption.textContent = this.t('appearance-label', 'Appearance');
        }

        if (currentLabel) {
            currentLabel.textContent = this.t(currentMeta.labelKey, currentMeta.id);
        }

        if (this.toggleButton) {
            this.toggleButton.setAttribute('aria-label', this.t('appearance-open-menu', 'Open appearance menu'));
        }

        this.switcher.querySelectorAll('[data-appearance-option]').forEach((button) => {
            const optionId = button.getAttribute('data-appearance-option');
            const isActive = optionId === this.currentAppearance;
            button.classList.toggle('active', isActive);
            button.setAttribute('aria-pressed', isActive ? 'true' : 'false');

            const labelNode = button.querySelector(`[data-appearance-label="${optionId}"]`);
            const meta = this.getAppearanceMeta(optionId);
            if (labelNode) {
                labelNode.textContent = this.t(meta.labelKey, meta.id);
            }
        });
    }

    toggleMenu() {
        const willOpen = !this.switcher.classList.contains('is-open');
        this.switcher.classList.toggle('is-open', willOpen);
        if (this.menu) {
            this.menu.hidden = !willOpen;
        }
        if (this.toggleButton) {
            this.toggleButton.setAttribute('aria-expanded', willOpen ? 'true' : 'false');
        }
    }

    closeMenu() {
        if (!this.switcher) {
            return;
        }
        this.switcher.classList.remove('is-open');
        if (this.menu) {
            this.menu.hidden = true;
        }
        if (this.toggleButton) {
            this.toggleButton.setAttribute('aria-expanded', 'false');
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.appearanceSwitcher = new AppearanceSwitcher();
});

window.AppearanceSwitcher = AppearanceSwitcher;
