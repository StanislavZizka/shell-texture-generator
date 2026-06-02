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
        this.setupTooltips();
        // Ensure Random Error panel is not duplicated on load
        this.dedupeRandomErrorPanel();
        this.syncRandomErrorUI();
    }

    bindEvents() {
        const figureMode = document.body && document.body.dataset ? document.body.dataset.figureMode : '';
        if (figureMode === '23') {
            return;
        }

        // Bind form submit event (more reliable than button click)
        const form = document.getElementById('activatorForm');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.generateTexture();
            });
        }

        // Bind parameter input changes for real-time validation
        const inputs = ['preset', 'K', 't_max', 'delta_t', 'color1', 'color2'];
        inputs.forEach(inputId => {
            const input = document.getElementById(inputId);
            if (input) {
                input.addEventListener('input', () => this.validateInput(input));
                input.addEventListener('change', () => this.validateInput(input));
            }
        });

        // Dynamic Instability Toggle
        const enableNoiseToggle = document.getElementById('enable_noise');
        const noisePanel = document.getElementById('noise_parameters_panel');
        if (enableNoiseToggle && noisePanel) {
            enableNoiseToggle.addEventListener('change', (e) => {
                if (e.target.checked) {
                    noisePanel.style.display = 'block';
                    // Trigger reflow for animation
                    noisePanel.offsetHeight;
                    noisePanel.classList.add('expanded');
                } else {
                    noisePanel.classList.remove('expanded');
                    setTimeout(() => {
                        noisePanel.style.display = 'none';
                    }, 300);
                }
            });
        }

        // Update slider output value in real-time
        const noiseStrength = document.getElementById('noise_strength');
        const noiseStrengthValue = document.getElementById('noise_strength_value');
        if (noiseStrength && noiseStrengthValue) {
            noiseStrength.addEventListener('input', (e) => {
                noiseStrengthValue.textContent = parseFloat(e.target.value).toFixed(3);
            });
        }

        // Random Error (Biological Perturbation) Toggle
        const enableRandomErrorToggle = document.getElementById('enable_random_error');
        const randomErrorPanel = document.getElementById('random_error_panel');
        this.randomErrorPreview = document.getElementById('random_error_preview');
        if (enableRandomErrorToggle && randomErrorPanel) {
            enableRandomErrorToggle.addEventListener('change', (e) => {
                this.syncRandomErrorUI(e.target.checked);
            });
        }

        // Random Error slider value updates (all 6 parameters)
        const randomErrorSliders = [
            { id: 're_strength', decimals: 3 },
            { id: 're_duration', decimals: 0 },
            { id: 're_frequency', decimals: 2 },
            { id: 're_probability', decimals: 3 },
            { id: 're_num_regions', decimals: 0 },
            { id: 're_region_size', decimals: 0 }
        ];

        randomErrorSliders.forEach(({ id, decimals }) => {
            const slider = document.getElementById(id);
            const output = document.getElementById(`${id}_value`);
            if (slider && output) {
                slider.addEventListener('input', (e) => {
                    output.textContent = parseFloat(e.target.value).toFixed(decimals);
                });
            }
        });

        // Random Error preset buttons
        const randomErrorPresetBtns = document.querySelectorAll('.random-error-section .preset-btn');
        randomErrorPresetBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const presetType = e.target.dataset.preset;
                this.applyRandomErrorPreset(presetType);
            });
        });

        // On preset change, call backend to set preset globally and keep user on page
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

        // Biological Heatmap Toggle - show/hide heatmap preview
        const bioHeatmapToggle = document.getElementById('show_biological_heatmap');
        if (bioHeatmapToggle) {
            bioHeatmapToggle.addEventListener('change', (e) => {
                this.toggleBiologicalHeatmapPreview(e.target.checked);
            });
        }
    }

    setupFormValidation() {
        // Initialize form with default values
        this.setDefaultValues();
    }

    setDefaultValues() {
        // Default parameter values for reaction-diffusion simulation
        const defaults = {
            'preset': 'stable',
            'K': '1.0',
            't_max': '100.0',
            'delta_t': '0.1',
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

        applyRandomErrorPreset(presetType) {
        // Biologicky realistické Random Error presety podle typu difúze
        // Vyladěno podle referenčního snapshot_step0300.png s biologickou variabilitou
        // R(x,y,t) = α_varied · M_irregular(x,y) · sin(2πft + φ)
        const presets = {
            'low_diffusion': {
                're_strength': 0.070,
                're_duration': 22,
                're_frequency': 0.070,
                're_probability': 0.075,
                're_num_regions': 6,
                're_region_size': 8,
                're_jitter': 0.12,
                're_micro_noise': 0.06,
                're_alpha_var': 0.24,
                're_beta': 0.14,
                're_drift_x': 1.35,
                're_drift_y': 1.15,
                're_drift_frequency': 0.002
            },
            'medium_diffusion': {
                're_strength': 0.058,
                're_duration': 28,
                're_frequency': 0.060,
                're_probability': 0.060,
                're_num_regions': 5,
                're_region_size': 10,
                're_jitter': 0.11,
                're_micro_noise': 0.05,
                're_alpha_var': 0.22,
                're_beta': 0.11,
                're_drift_x': 1.10,
                're_drift_y': 1.00,
                're_drift_frequency': 0.002
            },
            'high_diffusion': {
                're_strength': 0.046,
                're_duration': 34,
                're_frequency': 0.052,
                're_probability': 0.050,
                're_num_regions': 4,
                're_region_size': 13,
                're_jitter': 0.14,
                're_micro_noise': 0.06,
                're_alpha_var': 0.20,
                're_beta': 0.08,
                're_drift_x': 0.85,
                're_drift_y': 0.80,
                're_drift_frequency': 0.002
            },
            'balanced': {
                're_strength': 0.062,
                're_duration': 30,
                're_frequency': 0.058,
                're_probability': 0.065,
                're_num_regions': 5,
                're_region_size': 10,
                're_jitter': 0.12,
                're_micro_noise': 0.06,
                're_alpha_var': 0.23,
                're_beta': 0.10,
                're_drift_x': 1.20,
                're_drift_y': 1.05,
                're_drift_frequency': 0.002
            }
        };

        const preset = presets[presetType];
        if (!preset) return;

        // Apply preset values to sliders and update outputs
        Object.entries(preset).forEach(([paramId, value]) => {
            const slider = document.getElementById(paramId);
            const output = document.getElementById(`${paramId}_value`);
            const previewMap = {
                re_strength: 'random_error_preview_strength',
                re_duration: 'random_error_preview_duration',
                re_frequency: 'random_error_preview_frequency',
                re_probability: 'random_error_preview_probability',
                re_num_regions: 'random_error_preview_num_regions',
                re_region_size: 'random_error_preview_region_size',
                re_jitter: 'random_error_preview_jitter',
                re_micro_noise: 'random_error_preview_micro_noise',
                re_alpha_var: 'random_error_preview_alpha_var',
                re_beta: 'random_error_preview_beta',
                re_drift_x: 'random_error_preview_drift_x',
                re_drift_y: 'random_error_preview_drift_y',
                re_drift_frequency: 'random_error_preview_drift_frequency',
            };
            const previewOutput = document.getElementById(previewMap[paramId] || '');

            if (slider) {
                slider.value = value;

                // Update output display
                if (output) {
                    const decimals = paramId.includes('strength') || paramId.includes('probability') ? 3 :
                                    paramId.includes('frequency') ? 2 : 0;
                    output.textContent = value.toFixed(decimals);
                }
                if (previewOutput) {
                    const decimals = paramId.includes('strength') || paramId.includes('probability') ? 3 :
                                    paramId.includes('frequency') ? 2 : 0;
                    previewOutput.textContent = value.toFixed(decimals);
                }
            }
        });

        // Show success notification
        if (typeof showToast === 'function') {
            showToast(`Random Error preset applied: ${presetType}`, 'success');
        }
    }

    validateInput(input) {
        const value = input.value;
        let isValid = true;
        let errorMessage = '';

        // Validate based on input type and mathematical constraints
        switch (input.id) {
            case 'preset':
                // Always valid; backend maps to presets
                isValid = !!value;
                errorMessage = '';
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

        const figureMode = document.body && document.body.dataset ? document.body.dataset.figureMode : '';
        if (figureMode === '23') {
            return;
        }

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

            console.log('=== Response received from backend ===');
            console.log('Full response data:', data);
            console.log('data.snapshots:', data.snapshots);
            console.log('data.image_url:', data.image_url);
            console.log('data.heatmap_values:', data.heatmap_values ? 'Present' : 'None');

            if (response.ok) {
                // Check if export_snapshots was enabled
                const exportSnapshots = document.getElementById('export_snapshots')?.checked || false;
                console.log('Export snapshots checkbox is:', exportSnapshots ? 'CHECKED' : 'UNCHECKED');

                // Check if comparison mode or snapshots were used
                if (data.baseline_url && data.perturbed_url) {
                    console.log('Using COMPARISON mode');
                    this.handleComparisonSuccess(data.baseline_url, data.perturbed_url);
                } else if (exportSnapshots && data.snapshots && data.snapshots.length > 0) {
                    console.log('Using PATTERN EVOLUTION mode with', data.snapshots.length, 'snapshots');
                    // Show Pattern Evolution instead of single image
                    this.displayPatternEvolution(data.snapshots);
                    this.hideNormalImage();
                } else {
                    console.log('Using NORMAL single image mode');
                    console.log('Reason: exportSnapshots =', exportSnapshots, ', has snapshots =', !!(data.snapshots && data.snapshots.length > 0));
                    // Show normal single image with optional heatmap data
                    this.handleGenerationSuccess(data.image_url, data.heatmap_values);
                    this.hidePatternEvolution();
                }
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
        const params = {};
        let isValid = true;

        const staticPresetGroup = document.getElementById('staticPresetGroup');
        const currentMode = (staticPresetGroup && staticPresetGroup.style.display !== 'none') ? 'static' : 'dynamic';

        const basicInputs = {
            K: document.getElementById('K'),
            t_max: document.getElementById('t_max'),
            delta_t: document.getElementById('delta_t'),
            color1: document.getElementById('color1'),
            color2: document.getElementById('color2')
        };

        Object.entries(basicInputs).forEach(([key, input]) => {
            if (!input || !this.validateInput(input)) {
                isValid = false;
            }
            params[key] = input.value;
        });

        if (!isValid) return null;

        // Handle main simulation parameters
        if (currentMode === 'static') {
            const presetSelect = document.getElementById('static_preset');
            params.preset = presetSelect.value;
        } else {
            params.preset = '';
            params.custom_s = parseFloat(document.getElementById('s_param')?.value || 0.11);
            params.custom_D_b = parseFloat(document.getElementById('D_b_param')?.value || 0.35);
            params.custom_r_a = parseFloat(document.getElementById('r_a_param')?.value || 0.10);
            params.custom_r_b = parseFloat(document.getElementById('r_b_param')?.value || 0.18);
        }

        // Handle Random Error (Biological Perturbation) parameters
        const enableRandomError = document.getElementById('enable_random_error');
        if (enableRandomError && enableRandomError.checked) {
            params.enable_random_error = true;

            if (currentMode === 'static') {
                // In Static Mode, use the RE values from the selected preset
                const presetName = params.preset;
                const presetData = window.STATIC_PRESETS ? window.STATIC_PRESETS[presetName] : null;
                if (presetData) {
                    params.re_strength = presetData.re_strength;
                    params.re_duration = presetData.re_duration;
                    params.re_frequency = presetData.re_frequency;
                    params.re_num_regions = presetData.re_num_regions;
                    params.re_region_size = presetData.re_region_size;
                    params.re_probability = presetData.re_probability || 0.05;
                    params.re_jitter = presetData.re_jitter || 0.10;
                    params.re_micro_noise = presetData.re_micro_noise || 0.05;
                    params.re_alpha_var = presetData.re_alpha_var || 0.20;
                    // New biologically-calibrated parameters
                    params.re_beta = presetData.re_beta;
                    params.re_drift_x = presetData.re_drift_x;
                    params.re_drift_y = presetData.re_drift_y;
                    params.re_drift_frequency = presetData.re_drift_frequency;
                }
            } else {
                // In Dynamic Mode, use the values from the sliders
                params.re_strength = parseFloat(document.getElementById('re_strength')?.value || 0.03);
                params.re_duration = parseInt(document.getElementById('re_duration')?.value || 30);
                params.re_frequency = parseFloat(document.getElementById('re_frequency')?.value || 0.05);
                params.re_probability = parseFloat(document.getElementById('re_probability')?.value || 0.05);
                params.re_num_regions = parseInt(document.getElementById('re_num_regions')?.value || 3);
                params.re_region_size = parseInt(document.getElementById('re_region_size')?.value || 10);
                params.re_jitter = parseFloat(document.getElementById('re_jitter')?.value || 0.10);
                params.re_micro_noise = parseFloat(document.getElementById('re_micro_noise')?.value || 0.05);
                params.re_alpha_var = parseFloat(document.getElementById('re_alpha_var')?.value || 0.20);

                // Always enrich with new preset-driven params (no new sliders required)
                const staticPresetSelect = document.getElementById('static_preset');
                const presetNameDyn = staticPresetSelect ? staticPresetSelect.value : null;
                const presetDataDyn = (presetNameDyn && window.STATIC_PRESETS) ? window.STATIC_PRESETS[presetNameDyn] : null;
                if (presetDataDyn) {
                    // Only set values that are not provided by sliders
                    params.re_beta = presetDataDyn.re_beta;
                    params.re_drift_x = presetDataDyn.re_drift_x;
                    params.re_drift_y = presetDataDyn.re_drift_y;
                    params.re_drift_frequency = presetDataDyn.re_drift_frequency;
                }
            }
        } else {
            params.enable_random_error = false;
        }

        // Handle other parameters
        const exportSnapshots = document.getElementById('export_snapshots');
        params.export_snapshots = !!(exportSnapshots && exportSnapshots.checked);

        const showBioHeatmap = document.getElementById('show_biological_heatmap');
        params.show_biological_heatmap = !!(showBioHeatmap && showBioHeatmap.checked);
        
        // Deprecated params
        params.enable_noise = false;
        params.compare_baseline = false;

        console.log('[DEBUG] Final params being sent:', params);
        return params;
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

    handleGenerationSuccess(imageUrl, heatmapData = null) {
        // Store data for later use
        this.currentTextureUrl = imageUrl;
        this.currentHeatmapData = heatmapData;

        // Display generated texture in the designated image element
        const img = document.getElementById('generatedImage');
        const placeholder = document.querySelector('.image-placeholder');
        const imageWrapper = document.getElementById('imageWrapper');

        // Show image wrapper
        if (imageWrapper) imageWrapper.style.display = 'flex';

        if (img) {
            img.src = imageUrl + "?t=" + new Date().getTime();
            img.style.display = "block";
            if (placeholder) placeholder.style.display = "none";
        }

        // Update download button
        const downloadBtn = document.getElementById("downloadBtn");
        if (downloadBtn) {
            downloadBtn.href = imageUrl;
            downloadBtn.download = "activator_inhibitor_texture.png";
        }

        // Show image actions
        const imageActions = document.getElementById('imageActions');
        if (imageActions) {
            imageActions.style.display = 'flex';
        }

        // Show heatmap if data is available and checkbox is checked
        const bioHeatmapToggle = document.getElementById('show_biological_heatmap');
        if (heatmapData) {
            // Data is available - check if user wants to see it
            if (bioHeatmapToggle && bioHeatmapToggle.checked) {
                this.renderBiologicalHeatmapOverlay(heatmapData);
            } else {
                // Data exists but checkbox is off - just hide the section
                this.hideBiologicalHeatmapOverlay();
            }
        } else {
            // No heatmap data generated - hide section and clear stored data
            this.currentHeatmapData = null;
            this.hideBiologicalHeatmapOverlay();
        }

        // Show success notification
        if (typeof showToast === 'function') {
            showToast(window.t ? window.t('texture-generated') : 'Texture generated successfully!', 'success');
        }

        // Trigger custom event for other components
        document.dispatchEvent(new CustomEvent('textureGenerated', {
            detail: { imageUrl, heatmapData }
        }));

        // Refresh analysis grid if enabled
        if (window.analysisGrid) {
            window.analysisGrid.refresh();
        }
    }

    renderBiologicalHeatmapOverlay(heatmapData) {
        const canvas = document.getElementById('biologicalHeatmapCanvas');
        const section = document.getElementById('biologicalHeatmapSection');

        if (!canvas || !section || !heatmapData) {
            console.warn('[Heatmap] Missing elements or data');
            return;
        }

        console.log('[Heatmap] Rendering heatmap overlay');

        // Render heatmap
        const height = heatmapData.length;
        const width = heatmapData[0].length;

        // Only re-render canvas if dimensions changed or it's empty
        const needsRedraw = canvas.width !== width || canvas.height !== height || !canvas.getContext('2d').getImageData(0, 0, 1, 1);

        if (needsRedraw) {
            console.log('[Heatmap] Redrawing canvas:', width, 'x', height);

            // Set canvas size to match data dimensions
            canvas.width = width;
            canvas.height = height;

            const ctx = canvas.getContext('2d');
            const imageData = ctx.createImageData(width, height);

            // Jet colormap function (blue → cyan → green → yellow → red)
            const jetColormap = (value) => {
                // value is [0, 1]
                let r, g, b;

                if (value < 0.125) {
                    r = 0; g = 0; b = 128 + 127 * (value / 0.125);
                } else if (value < 0.375) {
                    r = 0; g = 255 * ((value - 0.125) / 0.25); b = 255;
                } else if (value < 0.625) {
                    r = 255 * ((value - 0.375) / 0.25); g = 255; b = 255 * (1 - (value - 0.375) / 0.25);
                } else if (value < 0.875) {
                    r = 255; g = 255 * (1 - (value - 0.625) / 0.25); b = 0;
                } else {
                    r = 255 * (1 - 0.5 * (value - 0.875) / 0.125); g = 0; b = 0;
                }

                return [Math.round(r), Math.round(g), Math.round(b), 255]; // Full opacity
            };

            // Render heatmap data to canvas
            for (let y = 0; y < height; y++) {
                for (let x = 0; x < width; x++) {
                    const value = heatmapData[y][x];
                    const [r, g, b, a] = jetColormap(value);

                    const idx = (y * width + x) * 4;
                    imageData.data[idx] = r;
                    imageData.data[idx + 1] = g;
                    imageData.data[idx + 2] = b;
                    imageData.data[idx + 3] = a;
                }
            }

            ctx.putImageData(imageData, 0, 0);
        } else {
            console.log('[Heatmap] Canvas already rendered, just showing section');
        }

        // Show section with visible class
        section.classList.add('visible');

        console.log('[Heatmap] Section visible');
    }

    hideBiologicalHeatmapOverlay() {
        const section = document.getElementById('biologicalHeatmapSection');

        if (section) {
            section.classList.remove('visible');
        }

        console.log('[Heatmap] Section hidden');
    }

    toggleBiologicalHeatmapPreview(enabled) {
        console.log('[Heatmap Toggle] Checkbox changed to:', enabled);
        console.log('[Heatmap Toggle] Current heatmap data available:', !!this.currentHeatmapData);

        if (!this.currentHeatmapData) {
            // Heatmap data not available
            if (enabled) {
                console.warn('[Heatmap Toggle] No data available - showing warning');
                if (typeof showToast === 'function') {
                    const message = window.t ? window.t('heatmap-not-available') : 'Heatmap not available. Please regenerate texture with "Show Biological Heatmap" enabled.';
                    showToast(message, 'warning');
                }
                // Uncheck the toggle since there's no data to show
                const bioHeatmapToggle = document.getElementById('show_biological_heatmap');
                if (bioHeatmapToggle) {
                    bioHeatmapToggle.checked = false;
                }
            }
            return;
        }

        // Data is available - toggle display
        if (enabled) {
            console.log('[Heatmap Toggle] Showing heatmap section');
            this.renderBiologicalHeatmapOverlay(this.currentHeatmapData);
            if (typeof showToast === 'function') {
                const message = window.t ? window.t('heatmap-active') : 'Biological heatmap shown';
                showToast(message, 'info');
            }
        } else {
            console.log('[Heatmap Toggle] Hiding heatmap section');
            this.hideBiologicalHeatmapOverlay();
            if (typeof showToast === 'function') {
                const message = window.t ? window.t('heatmap-disabled') : 'Biological heatmap hidden';
                showToast(message, 'info');
            }
        }
    }

        // Ensure only one Random Error panel and unique inputs exist in DOM
        dedupeRandomErrorPanel() {
        const panels = document.querySelectorAll('#random_error_panel');
        if (panels.length > 1) {
            // Keep the first, remove the rest
            for (let i = 1; i < panels.length; i++) {
                panels[i].remove();
            }
        }

        const panel = document.getElementById('random_error_panel');
        if (!panel) return;

        // Remove duplicate inputs/outputs by id inside the panel
        const seen = new Set();
            panel.querySelectorAll('[id]').forEach(el => {
                const id = el.id;
                if (seen.has(id)) {
                    el.remove();
                } else {
                    seen.add(id);
                }
            });
        }

        getRandomErrorMode() {
            const bodyMode = document.body && document.body.dataset ? document.body.dataset.generatorMode : '';
            if (bodyMode === 'static' || bodyMode === 'dynamic') {
                return bodyMode;
            }
            const staticPresetGroup = document.getElementById('staticPresetGroup');
            return staticPresetGroup && staticPresetGroup.style.display !== 'none' ? 'static' : 'dynamic';
        }

        syncRandomErrorUI(checked = Boolean(document.getElementById('enable_random_error')?.checked)) {
            const mode = this.getRandomErrorMode();
            const randomErrorPanel = document.getElementById('random_error_panel');
            const randomErrorPreview = document.getElementById('random_error_preview');
            const randomErrorState = document.getElementById('random_error_state');

            if (randomErrorPreview) {
                randomErrorPreview.style.display = mode === 'static' ? 'block' : 'none';
                randomErrorPreview.classList.toggle('is-disabled', !checked);
            }
            if (randomErrorState) {
                randomErrorState.textContent = checked ? 'ON' : 'OFF';
            }

            if (!randomErrorPanel) {
                return;
            }

            if (mode === 'static') {
                randomErrorPanel.style.display = 'none';
                randomErrorPanel.classList.remove('expanded');
                return;
            }

            if (checked) {
                this.dedupeRandomErrorPanel();
                randomErrorPanel.style.display = 'block';
                randomErrorPanel.offsetHeight;
                randomErrorPanel.classList.add('expanded');
            } else {
                randomErrorPanel.classList.remove('expanded');
                setTimeout(() => {
                    randomErrorPanel.style.display = 'none';
                }, 300);
            }
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

    handleComparisonSuccess(baselineUrl, perturbedUrl) {
        // Hide single image container
        const imageWrapper = document.getElementById('imageWrapper');
        const comparisonContainer = document.getElementById('comparisonContainer');

        if (imageWrapper) {
            imageWrapper.style.display = 'none';
        }

        // Show comparison container
        if (comparisonContainer) {
            comparisonContainer.style.display = 'block';

            // Set baseline image
            const baselineImg = document.getElementById('baselineImage');
            const downloadBaselineBtn = document.getElementById('downloadBaselineBtn');
            if (baselineImg) {
                baselineImg.src = baselineUrl + "?t=" + new Date().getTime();
            }
            if (downloadBaselineBtn) {
                downloadBaselineBtn.href = baselineUrl;
            }

            // Set perturbed image
            const perturbedImg = document.getElementById('perturbedImage');
            const downloadPerturbedBtn = document.getElementById('downloadPerturbedBtn');
            if (perturbedImg) {
                perturbedImg.src = perturbedUrl + "?t=" + new Date().getTime();
            }
            if (downloadPerturbedBtn) {
                downloadPerturbedBtn.href = perturbedUrl;
            }
        }

        // Show success notification
        if (typeof showToast === 'function') {
            showToast('Baseline and perturbed textures generated successfully!', 'success');
        }

        // Trigger custom event
        document.dispatchEvent(new CustomEvent('textureGenerated', {
            detail: { baselineUrl, perturbedUrl }
        }));

        // Show image actions
        const imageActions = document.getElementById('imageActions');
        if (imageActions) {
            imageActions.style.display = 'flex';
        }
    }

    displaySnapshots(snapshots) {
        const snapshotsContainer = document.getElementById('snapshotsContainer');
        const snapshotsGrid = document.getElementById('snapshotsGrid');
        const snapshotsInfo = document.getElementById('snapshotsInfo');

        if (!snapshotsContainer || !snapshotsGrid) return;

        // Show container
        snapshotsContainer.style.display = 'block';

        // Update info text
        if (snapshotsInfo) {
            snapshotsInfo.textContent = `${snapshots.length} snapshots exported during simulation`;
        }

        // Clear previous snapshots
        snapshotsGrid.innerHTML = '';

        // Create snapshot items
        snapshots.forEach((snapshotUrl, index) => {
            const snapshotItem = document.createElement('div');
            snapshotItem.className = 'snapshot-item';

            const img = document.createElement('img');
            img.src = snapshotUrl + "?t=" + new Date().getTime();
            img.alt = `Snapshot ${index + 1}`;
            img.onclick = () => {
                if (typeof openPopup === 'function') {
                    openPopup(img);
                }
            };

            const label = document.createElement('div');
            label.className = 'snapshot-label';
            label.textContent = `Step ${index + 1} (${25 * (index + 1)}%)`;

            snapshotItem.appendChild(img);
            snapshotItem.appendChild(label);
            snapshotsGrid.appendChild(snapshotItem);
        });

        // Show success message
        if (typeof showToast === 'function') {
            showToast(`${snapshots.length} snapshots exported successfully!`, 'success');
        }
    }

    hideNormalImage() {
        const imageWrapper = document.getElementById('imageWrapper');
        const imageActions = document.getElementById('imageActions');
        const comparisonContainer = document.getElementById('comparisonContainer');
        const snapshotsContainer = document.getElementById('snapshotsContainer');

        if (imageWrapper) imageWrapper.style.display = 'none';
        if (imageActions) imageActions.style.display = 'none';
        if (comparisonContainer) comparisonContainer.style.display = 'none';
        if (snapshotsContainer) snapshotsContainer.style.display = 'none';
    }

    hidePatternEvolution() {
        const evolutionContainer = document.getElementById('patternEvolutionContainer');
        if (evolutionContainer) evolutionContainer.style.display = 'none';
    }

    displayPatternEvolution(snapshots) {
        console.log('=== displayPatternEvolution called ===');
        console.log('Snapshots received:', snapshots);
        console.log('Number of snapshots:', snapshots ? snapshots.length : 0);

        const evolutionContainer = document.getElementById('patternEvolutionContainer');
        const evolutionGrid = document.getElementById('evolutionGrid');

        console.log('Evolution container found:', !!evolutionContainer);
        console.log('Evolution grid found:', !!evolutionGrid);

        if (!evolutionContainer || !evolutionGrid) {
            console.error('ERROR: Container or grid element not found!');
            return;
        }

        // Show container with explicit styles
        evolutionContainer.style.display = 'block';
        evolutionContainer.style.visibility = 'visible';
        evolutionContainer.style.opacity = '1';

        console.log('Container display set to:', evolutionContainer.style.display);

        // Clear previous snapshots
        evolutionGrid.innerHTML = '';

        // Validate snapshots array
        if (!snapshots || snapshots.length === 0) {
            console.error('ERROR: No snapshots provided!');
            evolutionGrid.innerHTML = '<p style="color: red; padding: 20px;">No snapshots available. Please enable "Show Pattern Evolution" before generating.</p>';
            return;
        }

        // Store snapshots for stage selector
        this.currentSnapshots = snapshots;

        // Define evolution stages (25%, 50%, 75%, 100%)
        const stages = [
            {
                index: 0,
                percentage: 25,
                label: 'Early Stage',
                description: 'První náznaky reakce – objevují se drobné ostrůvky aktivátoru, pigmentace je slabá a rozptýlená'
            },
            {
                index: 1,
                percentage: 50,
                label: 'Mid Stage',
                description: 'Aktivátor se začíná organizovat do větších struktur, vznikají shluky a základní texturové vzory'
            },
            {
                index: 2,
                percentage: 75,
                label: 'Late Stage',
                description: 'Struktura se stabilizuje, vzor nabírá kontrast, objevují se oddělené oblasti aktivátoru a inhibitoru'
            },
            {
                index: 3,
                percentage: 100,
                label: 'Final Stage',
                description: 'Rovnováha systému, vznik finálního vzoru s ustáleným rozložením pigmentu'
            }
        ];

        console.log('Creating', stages.length, 'evolution items...');

        // Create evolution items
        let itemsCreated = 0;
        stages.forEach(stage => {
            if (stage.index < snapshots.length) {
                const snapshotUrl = snapshots[stage.index];
                console.log(`Creating item ${stage.index + 1}:`, snapshotUrl);

                const evolutionItem = document.createElement('div');
                evolutionItem.className = 'evolution-item';

                const img = document.createElement('img');
                img.src = snapshotUrl + "?t=" + new Date().getTime();
                img.alt = `${stage.label} - ${stage.percentage}%`;
                img.loading = 'eager'; // Force immediate loading

                // Add error handling for image loading
                img.onerror = () => {
                    console.error(`Failed to load image: ${img.src}`);
                    img.alt = `[Failed to load: ${stage.percentage}%]`;
                    img.style.border = '2px solid red';
                };

                img.onload = () => {
                    console.log(`Successfully loaded image: ${stage.percentage}%`);
                };

                img.onclick = () => {
                    if (typeof openPopup === 'function') {
                        openPopup(img);
                    }
                };

                const label = document.createElement('div');
                label.className = 'evolution-label';
                label.innerHTML = `<strong>${stage.percentage}%</strong><br><span>${stage.label}</span>`;

                const description = document.createElement('div');
                description.className = 'evolution-item-description';
                description.textContent = stage.description;

                evolutionItem.appendChild(img);
                evolutionItem.appendChild(label);
                evolutionItem.appendChild(description);
                evolutionGrid.appendChild(evolutionItem);

                itemsCreated++;
                console.log(`Item ${itemsCreated} added to grid`);
            }
        });

        console.log(`Total items created: ${itemsCreated}`);
        console.log('Grid innerHTML length:', evolutionGrid.innerHTML.length);
        console.log('Grid children count:', evolutionGrid.children.length);

        // Setup stage selector buttons
        this.setupStageSelector();

        // Automatically show 100% stage (final) in main image
        if (snapshots.length >= 4) {
            console.log('Auto-showing 100% stage in main image');
            this.showStageInMainImage(3, '100');  // Index 3 = 100% stage
        }

        // Show success message
        if (typeof showToast === 'function') {
            showToast(`Pattern Evolution displayed - showing ${itemsCreated} stages of development!`, 'success');
        }

        console.log('=== displayPatternEvolution finished ===');
    }

    setupStageSelector() {
        const stageButtons = document.querySelectorAll('.stage-btn');

        stageButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const button = e.currentTarget;
                const stageIndex = parseInt(button.dataset.stage);
                const percentage = button.dataset.percentage;

                console.log(`Stage selector clicked: ${percentage}% (index ${stageIndex})`);

                // Update active state
                stageButtons.forEach(b => b.classList.remove('active'));
                button.classList.add('active');

                // Show selected stage in main image
                this.showStageInMainImage(stageIndex, percentage);
            });
        });
    }

    showStageInMainImage(stageIndex, percentage) {
        if (!this.currentSnapshots || stageIndex >= this.currentSnapshots.length) {
            console.error('ERROR: Snapshot not available for stage', stageIndex);
            return;
        }

        const snapshotUrl = this.currentSnapshots[stageIndex];
        console.log(`Showing stage ${percentage}% in main image:`, snapshotUrl);

        // Show the main image container
        const imageWrapper = document.getElementById('imageWrapper');
        const img = document.getElementById('generatedImage');
        const placeholder = document.querySelector('.image-placeholder');

        if (imageWrapper) imageWrapper.style.display = 'flex';

        if (img) {
            img.src = snapshotUrl + "?t=" + new Date().getTime();
            img.style.display = "block";
            if (placeholder) placeholder.style.display = "none";
        }

        // Update download button
        const downloadBtn = document.getElementById("downloadBtn");
        if (downloadBtn) {
            downloadBtn.href = snapshotUrl;
            downloadBtn.download = `pattern_evolution_${percentage}percent.png`;
        }

        // Show image actions
        const imageActions = document.getElementById('imageActions');
        if (imageActions) {
            imageActions.style.display = 'flex';
        }

        // Show success notification
        if (typeof showToast === 'function') {
            showToast(`Now viewing ${percentage}% stage in detail`, 'success');
        }

        // Trigger custom event for analysis tools
        document.dispatchEvent(new CustomEvent('textureGenerated', {
            detail: {
                imageUrl: snapshotUrl,
                stage: percentage
            }
        }));

        // Refresh analysis grid if enabled
        if (window.analysisGrid) {
            window.analysisGrid.refresh();
        }
    }

    setupTooltips() {
        // Create tooltip portal container if it doesn't exist
        let tooltipPortal = document.getElementById('tooltip-portal');
        if (!tooltipPortal) {
            tooltipPortal = document.createElement('div');
            tooltipPortal.id = 'tooltip-portal';
            tooltipPortal.style.cssText = 'position: fixed; top: 0; left: 0; z-index: 9999; pointer-events: none;';
            document.body.appendChild(tooltipPortal);
        }

        const tooltipIcons = document.querySelectorAll('.tooltip-icon');
        let activeTooltip = null;

        const positionTooltip = (icon, tooltipElement) => {
            const iconRect = icon.getBoundingClientRect();

            console.log('[Tooltip] Icon position:', {
                left: iconRect.left,
                top: iconRect.top,
                width: iconRect.width,
                height: iconRect.height
            });

            // Calculate center position of icon
            const iconCenterX = iconRect.left + (iconRect.width / 2);
            const iconCenterY = iconRect.top + (iconRect.height / 2);

            console.log('[Tooltip] Icon center:', { x: iconCenterX, y: iconCenterY });

            // Determine if tooltip should be above or below icon
            const spaceAbove = iconRect.top;
            const spaceBelow = window.innerHeight - iconRect.bottom;
            const showBelow = spaceAbove < 200; // If less than 200px above, show below

            console.log('[Tooltip] Space above:', spaceAbove, 'Space below:', spaceBelow, 'Show below?', showBelow);

            // Set position to icon center
            // CSS transform will handle centering: translate(-50%, -100%) for above, translate(-50%, 0%) for below
            tooltipElement.style.left = `${iconCenterX}px`;
            tooltipElement.style.top = showBelow ? `${iconRect.bottom}px` : `${iconRect.top}px`;

            // Add class to indicate direction (CSS handles transform)
            tooltipElement.classList.toggle('tooltip-below', showBelow);

            console.log('[Tooltip] Final position:', {
                left: iconCenterX,
                top: showBelow ? iconRect.bottom : iconRect.top,
                showBelow
            });
        };

        const showTooltip = (icon) => {
            // Hide any existing tooltip
            hideTooltip();

            const tooltipContent = icon.querySelector('.tooltip-content');
            if (!tooltipContent) return;

            // Clone tooltip content to portal
            const tooltipClone = tooltipContent.cloneNode(true);
            tooltipClone.classList.add('tooltip-portal-content');
            tooltipClone.classList.remove('tooltip-content'); // Remove original class
            tooltipClone.style.opacity = '0';
            tooltipClone.style.visibility = 'visible';
            tooltipPortal.appendChild(tooltipClone);

            // Position tooltip after it's rendered (so we get correct dimensions)
            requestAnimationFrame(() => {
                requestAnimationFrame(() => {
                    positionTooltip(icon, tooltipClone);
                    tooltipClone.style.opacity = '1';
                });
            });

            activeTooltip = { icon, element: tooltipClone };
            icon.classList.add('active');
        };

        const hideTooltip = () => {
            if (activeTooltip) {
                activeTooltip.icon.classList.remove('active');
                if (activeTooltip.element && activeTooltip.element.parentNode) {
                    activeTooltip.element.remove();
                }
                activeTooltip = null;
            }
        };

        tooltipIcons.forEach(icon => {
            // Hover for desktop
            icon.addEventListener('mouseenter', () => {
                showTooltip(icon);
            });

            icon.addEventListener('mouseleave', () => {
                hideTooltip();
            });

            // Click toggle for mobile
            icon.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();

                if (activeTooltip && activeTooltip.icon === icon) {
                    hideTooltip();
                } else {
                    showTooltip(icon);
                }
            });

            // Keyboard accessibility
            icon.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    if (activeTooltip && activeTooltip.icon === icon) {
                        hideTooltip();
                    } else {
                        showTooltip(icon);
                    }
                }
                if (e.key === 'Escape') {
                    hideTooltip();
                }
            });
        });

        // Close tooltips when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.tooltip-icon')) {
                hideTooltip();
            }
        });

        // Reposition tooltip on scroll/resize
        window.addEventListener('scroll', () => {
            if (activeTooltip) {
                positionTooltip(activeTooltip.icon, activeTooltip.element);
            }
        }, true);

        window.addEventListener('resize', () => {
            if (activeTooltip) {
                positionTooltip(activeTooltip.icon, activeTooltip.element);
            }
        });

        console.log(`Tooltip system initialized for ${tooltipIcons.length} icons`);
    }
}

// Export for use in other modules
window.TextureGenerator = TextureGenerator;
