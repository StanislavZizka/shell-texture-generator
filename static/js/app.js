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
            this.showToast('An unexpected error occurred', 'error');
        });

        window.addEventListener('unhandledrejection', (event) => {
            console.error('Unhandled promise rejection:', event.reason);
            this.showToast('Network error occurred', 'error');
        });
    }

    initializeComponents() {
        // Initialize components in order of dependency
        this.initializeLanguageSwitcher();
        this.initializeThemeManager();
        this.initializeNavigation();
        this.initializeTextureGenerator();
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

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new App();
    console.log('Shell Texture Generator App initialized');
});

// Export for potential external use
window.App = App;