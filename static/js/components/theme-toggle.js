// Theme Toggle Component - Light/Dark Mode Switching
class ThemeManager {
    constructor() {
        this.currentTheme = this.getStoredTheme() || this.getSystemTheme();
        this.init();
    }

    init() {
        this.applyTheme(this.currentTheme);
        this.createToggleButton();
        this.bindEvents();
        
        // Update button after language switcher might be loaded
        setTimeout(() => {
            this.updateToggleButton();
        }, 150);
    }

    getStoredTheme() {
        return localStorage.getItem('theme');
    }

    getSystemTheme() {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }

    setStoredTheme(theme) {
        localStorage.setItem('theme', theme);
    }

    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        this.currentTheme = theme;
        this.setStoredTheme(theme);
        this.updateToggleButton();
    }

    toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.applyTheme(newTheme);
        
        // Add smooth transition effect
        document.body.style.transition = 'background 0.3s ease, color 0.3s ease';
        setTimeout(() => {
            document.body.style.transition = '';
        }, 300);
    }

    createToggleButton() {
        const toggleButton = document.createElement('button');
        toggleButton.className = 'theme-toggle';
        toggleButton.setAttribute('aria-label', 'Switch light/dark mode');
        toggleButton.innerHTML = `
            <i class="fas fa-sun" id="theme-icon"></i>
            <span class="theme-label" id="theme-label">Light</span>
        `;
        
        document.body.appendChild(toggleButton);
        this.toggleButton = toggleButton;
        this.updateToggleButton();
    }

    updateToggleButton() {
        if (!this.toggleButton) return;
        
        const icon = this.toggleButton.querySelector('#theme-icon');
        const label = this.toggleButton.querySelector('#theme-label');
        
        // Get translations if language switcher is available
        const t = window.languageSwitcher ? window.languageSwitcher.t.bind(window.languageSwitcher) : (key) => {
            // Check stored language preference or use English as fallback
            const storedLang = localStorage.getItem('selectedLanguage') || 'en';
            const fallbacks = {
                en: {
                    'theme-dark': 'Dark',
                    'theme-light': 'Light',
                    'switch-to-light': 'Switch to light mode',
                    'switch-to-dark': 'Switch to dark mode'
                }
            };
            return fallbacks[storedLang] && fallbacks[storedLang][key] ? fallbacks[storedLang][key] : key;
        };
        
        if (this.currentTheme === 'dark') {
            icon.className = 'fas fa-moon';
            label.textContent = t('theme-dark');
            this.toggleButton.setAttribute('aria-label', t('switch-to-light'));
        } else {
            icon.className = 'fas fa-sun';
            label.textContent = t('theme-light');
            this.toggleButton.setAttribute('aria-label', t('switch-to-dark'));
        }
    }

    bindEvents() {
        // Toggle button click handler
        document.addEventListener('click', (e) => {
            if (e.target.closest('.theme-toggle')) {
                this.toggleTheme();
            }
        });

        // Keyboard shortcut: Ctrl/Cmd + Shift + T
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'T') {
                e.preventDefault();
                this.toggleTheme();
            }
        });

        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!this.getStoredTheme()) {
                const systemTheme = e.matches ? 'dark' : 'light';
                this.applyTheme(systemTheme);
            }
        });

        // Listen for language changes to update button text
        document.addEventListener('languageChanged', () => {
            this.updateToggleButton();
        });
    }
}

// Initialize theme manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.themeManager = new ThemeManager();
});

// Export for potential use in other scripts
window.ThemeManager = ThemeManager;