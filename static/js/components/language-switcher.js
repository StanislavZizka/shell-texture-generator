// Language Switcher Component - Internationalization Support
class LanguageSwitcher {
    constructor() {
        this.currentLanguage = localStorage.getItem('selectedLanguage') || 'en';
        this.translations = {
            en: {
                // Navigation
                'nav-home': 'Home',
                'nav-activator-inhibitor': 'Activator-Inhibitor',
                'nav-waves': 'Wave Patterns',
                'nav-stripes': 'Stripe Patterns',
                
                // Home page
                'page-title-home': 'Mathematical Texture Generator',
                'page-subtitle-home': 'Create stunning patterns using mathematical models',
                'feature-1-title': 'Reaction-Diffusion Models',
                'feature-1-desc': 'Generate complex patterns using activator-inhibitor mathematical models',
                'feature-2-title': 'Wave Patterns',
                'feature-2-desc': 'Create wave-based textures with various frequencies and amplitudes',
                'feature-3-title': 'Stripe Patterns',
                'feature-3-desc': 'Generate striped textures with customizable parameters and colors',
                'get-started': 'Get Started',
                'coming-soon': 'Coming Soon',
                
                // Activator-Inhibitor page
                'page-title-ai': 'Activator-Inhibitor Model',
                'page-subtitle-ai': 'Configure reaction-diffusion model parameters to generate complex patterns',
                'model-params': 'Model Parameters',
                'constant-k': 'Constant K',
                'constant-k-help': 'Reaction process rate (0.1 - 5.0)',
                'max-time': 'Maximum Time',
                'max-time-help': 'Simulation duration in time units',
                'time-step': 'Time Step',
                'time-step-help': 'Simulation step precision',
                'color-scheme': 'Color Scheme',
                'base-color': 'Base Color',
                'contrast-color': 'Contrast Color',
                'generate-texture': 'Generate Texture',
                'result-texture': 'Generated Texture',
                'placeholder-text': 'Generated texture will appear here',
                'download': 'Download',
                'view': 'View',
                'generating': 'Generating texture...',
                
                // Toast messages
                'texture-generated': 'Texture generated successfully!',
                'texture-generation-error': 'Error generating texture',
                'server-error': 'Server communication error',
                'enter-valid-values': 'Enter valid values for all parameters',
                
                // Language switcher
                'language': 'Language',
                'english': 'English',
                'language-switched': 'Language switched',
                
                // Theme toggle
                'theme-dark': 'Dark',
                'theme-light': 'Light',
                'switch-to-light': 'Switch to light mode',
                'switch-to-dark': 'Switch to dark mode'
            }
        };
        
        this.init();
    }

    init() {
        this.createLanguageSwitcher();
        this.applyLanguage(this.currentLanguage);
        this.setupEventListeners();
        
        // Update theme toggle if it exists
        const updateThemeToggle = () => {
            if (window.themeManager && window.themeManager.updateToggleButton) {
                window.themeManager.updateToggleButton();
                return true;
            }
            return false;
        };
        
        // Try to update theme toggle with delays
        if (!updateThemeToggle()) {
            setTimeout(() => {
                if (!updateThemeToggle()) {
                    setTimeout(updateThemeToggle, 200);
                }
            }, 100);
        }
    }

    createLanguageSwitcher() {
        // Create language switcher HTML structure
        const languageSwitcher = document.createElement('div');
        languageSwitcher.className = 'language-switcher';
        languageSwitcher.innerHTML = `
            <div class="language-toggle" id="languageToggle">
                <div class="language-option ${this.currentLanguage === 'en' ? 'active' : ''}" data-lang="en">
                    <span class="flag">🇺🇸</span>
                    <span class="lang-name" data-i18n="english">English</span>
                </div>
            </div>
        `;

        // Insert next to theme toggle if it exists
        const themeToggle = document.querySelector('.theme-toggle');
        if (themeToggle && themeToggle.parentNode) {
            themeToggle.parentNode.insertBefore(languageSwitcher, themeToggle.nextSibling);
        } else {
            // Fallback: add to body
            document.body.appendChild(languageSwitcher);
        }
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
        if (language !== this.currentLanguage && this.translations[language]) {
            this.currentLanguage = language;
            localStorage.setItem('selectedLanguage', language);
            
            // Update active state in UI
            document.querySelectorAll('.language-option').forEach(option => {
                option.classList.remove('active');
            });
            document.querySelector(`[data-lang="${language}"]`).classList.add('active');
            
            this.applyLanguage(language);
            
            // Update theme toggle button if available
            if (window.themeManager && window.themeManager.updateToggleButton) {
                window.themeManager.updateToggleButton();
            }
            
            // Trigger custom event for other components
            document.dispatchEvent(new CustomEvent('languageChanged', { 
                detail: { language: language } 
            }));
            
            this.showToast(this.getTranslation('language-switched', language));
        }
    }

    applyLanguage(language) {
        // Find all elements with data-i18n attribute and translate them
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
                } else {
                    element.textContent = translation;
                }
            }
        });

        // Update document language attribute for accessibility
        document.documentElement.setAttribute('lang', language);
        
        // Force update theme toggle after language change
        setTimeout(() => {
            if (window.themeManager && window.themeManager.updateToggleButton) {
                window.themeManager.updateToggleButton();
            }
        }, 10);
    }

    getTranslation(key, language = null) {
        const lang = language || this.currentLanguage;
        return this.translations[lang] && this.translations[lang][key] 
            ? this.translations[lang][key] 
            : this.translations['en'][key] || key;
    }

    showToast(message, type = 'info') {
        // Use existing toast system if available
        if (typeof showToast === 'function') {
            showToast(message, type);
        } else {
            console.log('Language switched:', message);
        }
    }

    // Public methods for external use
    getCurrentLanguage() {
        return this.currentLanguage;
    }

    // Translation method for dynamic content
    t(key) {
        return this.getTranslation(key);
    }
}

// Initialize language switcher when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.languageSwitcher = new LanguageSwitcher();
    
    // Make translation function globally available
    window.t = (key) => window.languageSwitcher.t(key);
});

// Export for potential module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LanguageSwitcher;
}