/**
 * Texture Generator Component - Form handling and API communication
 * 
 * Manages the texture generation form, validates user inputs, and handles
 * communication with the backend API for mathematical pattern generation.
 */
class TextureGenerator {
    constructor() {
        this.isGenerating = false;
        this.init();
    }

    init() {
        this.bindEvents();
        this.setupFormValidation();
    }

    bindEvents() {
        // Bind generate button click event
        const generateBtn = document.getElementById('generateBtn');
        if (generateBtn) {
            generateBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.generateTexture();
            });
        }

        // Bind parameter input changes for real-time validation
        const inputs = ['kValue', 'tMaxValue', 'deltaT', 'color1', 'color2'];
        inputs.forEach(inputId => {
            const input = document.getElementById(inputId);
            if (input) {
                input.addEventListener('input', () => this.validateInput(input));
                input.addEventListener('change', () => this.validateInput(input));
            }
        });
    }

    setupFormValidation() {
        // Initialize form with default values
        this.setDefaultValues();
    }

    setDefaultValues() {
        // Default parameter values for reaction-diffusion simulation
        const defaults = {
            'kValue': '1.0',
            'tMaxValue': '10.0',
            'deltaT': '0.1',
            'color1': '#0000ff',
            'color2': '#ff0000'
        };

        Object.entries(defaults).forEach(([id, value]) => {
            const input = document.getElementById(id);
            if (input && !input.value) {
                input.value = value;
            }
        });
    }

    validateInput(input) {
        const value = input.value;
        let isValid = true;
        let errorMessage = '';

        // Validate based on input type and mathematical constraints
        switch (input.id) {
            case 'kValue':
                const k = parseFloat(value);
                isValid = k >= 0.1 && k <= 5.0;
                errorMessage = 'K must be between 0.1 and 5.0';
                break;
            case 'tMaxValue':
                const tMax = parseFloat(value);
                isValid = tMax >= 1.0 && tMax <= 10000.0;
                errorMessage = 'Max time must be between 1.0 and 10000.0';
                break;
            case 'deltaT':
                const deltaT = parseFloat(value);
                isValid = deltaT >= 0.001 && deltaT <= 1.0;
                errorMessage = 'Time step must be between 0.001 and 1.0';
                break;
            case 'color1':
            case 'color2':
                isValid = /^#[0-9A-Fa-f]{6}$/.test(value);
                errorMessage = 'Invalid color format';
                break;
        }

        this.updateInputValidation(input, isValid, errorMessage);
        return isValid;
    }

    updateInputValidation(input, isValid, errorMessage) {
        const errorElement = input.parentNode.querySelector('.error-message');
        
        if (isValid) {
            input.classList.remove('invalid');
            if (errorElement) {
                errorElement.remove();
            }
        } else {
            input.classList.add('invalid');
            if (!errorElement) {
                const error = document.createElement('div');
                error.className = 'error-message';
                error.textContent = errorMessage;
                input.parentNode.appendChild(error);
            }
        }
    }

    async generateTexture() {
        if (this.isGenerating) return;

        // Validate all form inputs before submission
        const params = this.getFormParams();
        if (!params) return;

        this.setGeneratingState(true);

        try {
            // Send POST request to texture generation API
            const response = await fetch('/calculate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(params)
            });

            const data = await response.json();

            if (response.ok) {
                this.handleGenerationSuccess(data.image_url);
            } else {
                this.handleGenerationError(data.error || 'Unknown error occurred');
            }
        } catch (error) {
            this.handleGenerationError('Network error: ' + error.message);
        } finally {
            this.setGeneratingState(false);
        }
    }

    getFormParams() {
        // Extract form parameters for API submission
        const inputs = {
            K: document.getElementById('kValue'),
            t_max: document.getElementById('tMaxValue'),
            delta_t: document.getElementById('deltaT'),
            color1: document.getElementById('color1'),
            color2: document.getElementById('color2')
        };

        const params = {};
        let isValid = true;

        Object.entries(inputs).forEach(([key, input]) => {
            if (!input) {
                isValid = false;
                return;
            }

            if (!this.validateInput(input)) {
                isValid = false;
            }

            params[key] = input.value;
        });

        return isValid ? params : null;
    }

    setGeneratingState(generating) {
        this.isGenerating = generating;
        const btn = document.getElementById('generateBtn');
        
        if (btn) {
            if (generating) {
                btn.disabled = true;
                btn.textContent = window.t ? window.t('generating') : 'Generating...';
            } else {
                btn.disabled = false;
                btn.textContent = window.t ? window.t('generate-texture') : 'Generate Texture';
            }
        }
    }

    handleGenerationSuccess(imageUrl) {
        // Display generated texture with action buttons
        const resultDiv = document.getElementById('textureResult');
        if (resultDiv) {
            resultDiv.innerHTML = `
                <img src="${imageUrl}?${Date.now()}" alt="Generated texture" class="generated-texture">
                <div class="texture-actions">
                    <button onclick="window.open('${imageUrl}', '_blank')" class="btn-secondary">
                        ${window.t ? window.t('view') : 'View'}
                    </button>
                    <a href="${imageUrl}" download="texture.png" class="btn-primary">
                        ${window.t ? window.t('download') : 'Download'}
                    </a>
                </div>
            `;
        }

        // Show success notification
        if (typeof showToast === 'function') {
            showToast(window.t ? window.t('texture-generated') : 'Texture generated successfully!', 'success');
        }

        // Trigger custom event for other components
        document.dispatchEvent(new CustomEvent('textureGenerated', {
            detail: { imageUrl }
        }));
    }

    handleGenerationError(error) {
        console.error('Texture generation error:', error);
        
        // Show error notification
        if (typeof showToast === 'function') {
            showToast(error, 'error');
        } else {
            alert('Error: ' + error);
        }
    }
}

// Export for use in other modules
window.TextureGenerator = TextureGenerator;