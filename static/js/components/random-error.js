/**
 * Random Error Generator Component - Form handling for noise injection
 *
 * Manages the random error texture generation form with noise parameters.
 * Extends the base activator-inhibitor model with biological imperfections.
 */
class RandomErrorGenerator {
    constructor() {
        this.isGenerating = false;
        this.init();
    }

    init() {
        this.bindEvents();
        this.setupFormValidation();
        this.updateNoiseFrequencyVisibility();
    }

    bindEvents() {
        // Bind form submit event
        const form = document.getElementById('activatorForm');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.generateTexture();
            });
        }

        // Bind parameter input changes for real-time validation
        const inputs = ['preset', 'K', 't_max', 'delta_t', 'color1', 'color2',
                       'noise_target', 'noise_type', 'noise_strength', 'noise_frequency'];
        inputs.forEach(inputId => {
            const input = document.getElementById(inputId);
            if (input) {
                input.addEventListener('input', () => this.validateInput(input));
                input.addEventListener('change', () => this.validateInput(input));
            }
        });

        // Update slider output values
        const noiseStrength = document.getElementById('noise_strength');
        const noiseStrengthValue = document.getElementById('noise_strength_value');
        if (noiseStrength && noiseStrengthValue) {
            noiseStrength.addEventListener('input', (e) => {
                noiseStrengthValue.textContent = parseFloat(e.target.value).toFixed(3);
            });
        }

        const noiseFrequency = document.getElementById('noise_frequency');
        const noiseFrequencyValue = document.getElementById('noise_frequency_value');
        if (noiseFrequency && noiseFrequencyValue) {
            noiseFrequency.addEventListener('input', (e) => {
                noiseFrequencyValue.textContent = e.target.value;
            });
        }

        // Toggle noise frequency visibility based on noise type
        const noiseType = document.getElementById('noise_type');
        if (noiseType) {
            noiseType.addEventListener('change', () => {
                this.updateNoiseFrequencyVisibility();
            });
        }

        // Handle preset change
        const presetSelect = document.getElementById('preset');
        if (presetSelect) {
            presetSelect.addEventListener('change', async () => {
                const preset = presetSelect.value;
                try {
                    await fetch('/set_preset', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ preset })
                    });
                    if (typeof showToast === 'function') {
                        showToast(`Preset applied: ${preset}`, 'success');
                    }
                } catch (e) {
                    if (typeof showToast === 'function') {
                        showToast('Failed to apply preset', 'error');
                    }
                }
            });
        }
    }

    updateNoiseFrequencyVisibility() {
        const noiseType = document.getElementById('noise_type');
        const frequencyGroup = document.getElementById('noise_frequency_group');

        if (noiseType && frequencyGroup) {
            if (noiseType.value === 'dynamic') {
                frequencyGroup.style.display = 'block';
            } else {
                frequencyGroup.style.display = 'none';
            }
        }
    }

    setupFormValidation() {
        // Initialize form with default values
        this.setDefaultValues();
    }

    setDefaultValues() {
        // Default parameter values
        const defaults = {
            'preset': 'stable',
            'K': '1.0',
            't_max': '100.0',
            'delta_t': '0.1',
            'color1': '#0000ff',
            'color2': '#ff0000',
            'noise_target': 'Both',
            'noise_type': 'initial',
            'noise_strength': '0.01',
            'noise_frequency': '10'
        };

        Object.entries(defaults).forEach(([id, value]) => {
            const input = document.getElementById(id);
            if (input && !input.value) {
                input.value = value;
            }
        });

        // Update output displays
        const noiseStrengthValue = document.getElementById('noise_strength_value');
        if (noiseStrengthValue) {
            noiseStrengthValue.textContent = '0.01';
        }
        const noiseFrequencyValue = document.getElementById('noise_frequency_value');
        if (noiseFrequencyValue) {
            noiseFrequencyValue.textContent = '10';
        }
    }

    validateInput(input) {
        const value = input.value;
        let isValid = true;
        let errorMessage = '';

        // Validate based on input type
        switch (input.id) {
            case 'preset':
            case 'noise_target':
            case 'noise_type':
                isValid = !!value;
                break;
            case 'K':
                const k = parseFloat(value);
                isValid = k >= 0.0001 && k <= 5.0;
                errorMessage = 'K must be between 0.0001 and 5.0';
                break;
            case 't_max':
                const tMax = parseFloat(value);
                isValid = tMax >= 1.0 && tMax <= 10000.0;
                errorMessage = 'Max time must be between 1.0 and 10000.0';
                break;
            case 'delta_t':
                const deltaT = parseFloat(value);
                isValid = deltaT >= 0.001 && deltaT <= 1.0;
                errorMessage = 'Time step must be between 0.001 and 1.0';
                break;
            case 'color1':
            case 'color2':
                isValid = /^#[0-9A-Fa-f]{6}$/.test(value);
                errorMessage = 'Invalid color format';
                break;
            case 'noise_strength':
                const strength = parseFloat(value);
                isValid = strength >= 0.001 && strength <= 0.05;
                errorMessage = 'Noise strength must be between 0.001 and 0.05';
                break;
            case 'noise_frequency':
                const freq = parseInt(value);
                isValid = freq >= 1 && freq <= 1000;
                errorMessage = 'Noise frequency must be between 1 and 1000';
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

        // Validate all form inputs
        const params = this.getFormParams();
        if (!params) return;

        this.setGeneratingState(true);

        try {
            // Send POST request to random error API
            const response = await fetch('/calculate_random', {
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
        // Extract form parameters
        const inputs = {
            preset: document.getElementById('preset'),
            K: document.getElementById('K'),
            t_max: document.getElementById('t_max'),
            delta_t: document.getElementById('delta_t'),
            color1: document.getElementById('color1'),
            color2: document.getElementById('color2'),
            noise_target: document.getElementById('noise_target'),
            noise_type: document.getElementById('noise_type'),
            noise_strength: document.getElementById('noise_strength'),
            noise_frequency: document.getElementById('noise_frequency')
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
        // Display generated texture
        const img = document.getElementById('generatedImage');
        const placeholder = document.querySelector('.image-placeholder');

        if (img) {
            img.src = imageUrl + "?t=" + new Date().getTime();
            img.style.display = "block";
            if (placeholder) placeholder.style.display = "none";
        }

        // Update download button
        const downloadBtn = document.getElementById("downloadBtn");
        if (downloadBtn) {
            downloadBtn.href = imageUrl;
            const noiseType = document.getElementById('noise_type')?.value || 'initial';
            const noiseTarget = document.getElementById('noise_target')?.value || 'Both';
            downloadBtn.download = `random_error_${noiseTarget}_${noiseType}.png`;
        }

        // Show image actions
        const imageActions = document.getElementById('imageActions');
        if (imageActions) {
            imageActions.style.display = 'flex';
        }

        // Show success notification
        if (typeof showToast === 'function') {
            showToast('Random error texture generated successfully!', 'success');
        }

        // Trigger custom event for 3D model
        document.dispatchEvent(new CustomEvent('textureGenerated', {
            detail: { imageUrl }
        }));
    }

    handleGenerationError(error) {
        console.error('Random error texture generation error:', error);

        // Show error notification
        if (typeof showToast === 'function') {
            showToast(error, 'error');
        } else {
            alert('Error: ' + error);
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new RandomErrorGenerator();
});

// Export for use in other modules
window.RandomErrorGenerator = RandomErrorGenerator;
