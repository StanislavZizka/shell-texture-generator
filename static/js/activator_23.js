(() => {
    const figurePageShared = window.FigurePageShared;
    if (!figurePageShared) {
        throw new Error('FigurePageShared helper must be loaded before activator_23.js');
    }
    const viewerBridge = window.FigurePageViewerBridge;
    if (!viewerBridge) {
        throw new Error('FigurePageViewerBridge helper must be loaded before activator_23.js');
    }
    const resultBridge = window.FigurePageResultBridge;
    if (!resultBridge) {
        throw new Error('FigurePageResultBridge helper must be loaded before activator_23.js');
    }
    const windowBridge = window.FigurePageWindowBridge;
    if (!windowBridge) {
        throw new Error('FigurePageWindowBridge helper must be loaded before activator_23.js');
    }

    class Pattern23Page {
        constructor() {
            this.apiEndpoint = window.FIGURE_API_ENDPOINT || '/api/generate-23';
            this.form = document.getElementById('patternForm');
            this.stageSelect = document.getElementById('pattern_stage');
            this.presetInput = document.getElementById('preset');
            this.modeInput = document.getElementById('figure_pattern_mode');
            this.parameterModeInput = document.getElementById('parameter_mode');
            this.formTitle = document.querySelector('.form-container h3');
            this.modeDescription = document.getElementById('patternModeDescription');
            this.dynamicModeHint = document.getElementById('patternDynamicModeHint');
            this.stageLabelText = document.getElementById('patternStageLabelText');
            this.stageHelp = document.getElementById('stageHelp');
            this.parameterAccordion = document.getElementById('patternParameterAccordion');
            this.parameterGrid = document.getElementById('patternParameterGrid');
            this.parameterEmpty = document.getElementById('patternParameterEmpty');
            this.parameterModeLabel = document.getElementById('patternParameterModeLabel');
            this.parameterModeDesc = document.getElementById('patternParameterModeDesc');
            this.parameterState = document.getElementById('patternParameterState');
            this.parameterInputs = Array.from(document.querySelectorAll('.parameter-input[data-parameter-key]'));
            this.staticModeBtn = document.getElementById('patternStaticModeBtn');
            this.dynamicModeBtn = document.getElementById('patternDynamicModeBtn');
            this.colorSchemeTitle = document.querySelector('.color-group h4');
            this.baseColorLabel = document.querySelector('.color-group label[for="color1"]');
            this.contrastColorLabel = document.querySelector('.color-group label[for="color2"]');
            this.imagePlaceholderText = document.querySelector('#imagePlaceholder span');
            this.randomErrorGroup = document.getElementById('fig23RandomErrorGroup');
            this.randomErrorCheckbox = document.getElementById('enable_random_error');
            this.randomErrorAccordion = document.getElementById('fig23RandomErrorAccordion');
            this.randomErrorToggleLabel = document.getElementById('fig23RandomErrorToggleLabel');
            this.randomErrorToggleHelp = document.getElementById('fig23RandomErrorToggleHelp');
            this.randomErrorProfileTitle = document.getElementById('fig23RandomErrorProfileTitle');
            this.randomErrorProfileDesc = document.getElementById('fig23RandomErrorProfileDesc');
            this.randomErrorEditHint = document.getElementById('fig23RandomErrorEditHint');
            this.randomErrorPreview = document.getElementById('fig23RandomErrorPreview');
            this.randomErrorEmpty = document.getElementById('fig23RandomErrorEmpty');
            this.randomErrorSummaryGrid = document.querySelector('#fig23RandomErrorPreview .random-error-summary-grid');
            this.randomErrorState = document.getElementById('fig23RandomErrorState');
            this.resultTitle = document.querySelector('.image-container h3');
            this.randomErrorValues = {
                strength: document.getElementById('fig23_re_strength_value'),
                duration: document.getElementById('fig23_re_duration_value'),
                frequency: document.getElementById('fig23_re_frequency_value'),
                probability: document.getElementById('fig23_re_probability_value'),
                num_regions: document.getElementById('fig23_re_num_regions_value'),
                region_size: document.getElementById('fig23_re_region_size_value'),
                jitter: document.getElementById('fig23_re_jitter_value'),
                micro_noise: document.getElementById('fig23_re_micro_noise_value'),
                alpha_var: document.getElementById('fig23_re_alpha_var_value'),
                beta: document.getElementById('fig23_re_beta_value'),
                drift_x: document.getElementById('fig23_re_drift_x_value'),
                drift_y: document.getElementById('fig23_re_drift_y_value'),
                drift_frequency: document.getElementById('fig23_re_drift_frequency_value'),
            };
            this.randomErrorSummaryLabels = {
                strength: document.getElementById('fig23_re_strength_label'),
                duration: document.getElementById('fig23_re_duration_label'),
                frequency: document.getElementById('fig23_re_frequency_label'),
                probability: document.getElementById('fig23_re_probability_label'),
                num_regions: document.getElementById('fig23_re_num_regions_label'),
                region_size: document.getElementById('fig23_re_region_size_label'),
                jitter: document.getElementById('fig23_re_jitter_label'),
                micro_noise: document.getElementById('fig23_re_micro_noise_label'),
                alpha_var: document.getElementById('fig23_re_alpha_var_label'),
                beta: document.getElementById('fig23_re_beta_label'),
                drift_x: document.getElementById('fig23_re_drift_x_label'),
                drift_y: document.getElementById('fig23_re_drift_y_label'),
                drift_frequency: document.getElementById('fig23_re_drift_frequency_label'),
            };
            this.color1 = document.getElementById('color1');
            this.color2 = document.getElementById('color2');
            this.colorSchemeTitle = document.querySelector('.color-group h4');
            this.baseColorLabel = document.querySelector('.color-group label[for="color1"]');
            this.contrastColorLabel = document.querySelector('.color-group label[for="color2"]');
            this.imagePlaceholder = document.getElementById('imagePlaceholder');
            this.imagePlaceholderText = document.querySelector('#imagePlaceholder span');
            this.generatedImage = document.getElementById('generatedImage');
            this.imageActions = document.getElementById('imageActions');
            this.downloadBtn = document.getElementById('downloadBtn');
            this.viewBtn = document.getElementById('viewBtn');
            this.stageLabel = document.getElementById('stageLabel');
            this.stageDescription = document.getElementById('stageDescription');
            this.generateBtn = document.getElementById('generateBtn');
            this.shellSelect = document.getElementById('shellSelect');
            this.shellSelectLabel = document.querySelector('.model-selector label');
            this.modelTitle = document.querySelector('.model-container h3');
            this.viewer = null;
            this.currentImageUrl = null;
            this.currentRandomErrorProfile = null;
            this.currentParameterValues = {};
            this.currentStageKey = null;
            this.currentStaticParameterValues = {};
            this.dynamicParameterValuesByStage = {};
            this.dynamicRandomErrorValuesByStage = {};
            this.currentRandomErrorProfileKey = null;
            this.currentRandomErrorProfileData = null;
            this.currentMode = 'static';
            this.isGenerating = false;
            this.getUiBundle = figurePageShared.getUiBundle;
            this.getUiText = figurePageShared.getUiText;
            this.getStageIndexFromOption = figurePageShared.getStageIndexFromOption;
            this.getLocalizedStageLabel = figurePageShared.getLocalizedStageLabel;
            this.getLocalizedStageDescription = figurePageShared.getLocalizedStageDescription;

            this.bindEvents();
            this.applyLocalizedTexts();
            this.clearStageUi();
            this.updateGenerateButtonState();
            this.initViewerWithRetry();
        }

        getParameterKeys() {
            return Array.isArray(window.FIG23_PARAMETER_KEYS) ? window.FIG23_PARAMETER_KEYS : [];
        }

        getBaseParameterValues() {
            const bundle = window.FIG23_MODEL_PARAMS || {};
            if (bundle && typeof bundle === 'object' && !Array.isArray(bundle)) {
                return { ...bundle };
            }
            return {};
        }

        getStageParameterValues(levelKey) {
            const levels = window.FIG23_PROGRESSION_LEVELS || {};
            const levelSpec = levelKey ? (levels[levelKey] || null) : null;
            const stagePreset = levelSpec?.params_override || {};
            return {
                ...this.getBaseParameterValues(),
                ...stagePreset,
            };
        }

        updateParameterLabels() {
            this.getParameterKeys().forEach((key) => {
                const label = document.querySelector(`[data-i18n="param-${key}"]`);
                if (label) {
                    label.textContent = this.getUiText(`param-${key}`, label.textContent || key);
                }
            });
        }

        updateParameterAccordionState(hasStage) {
            const selected = Boolean(hasStage);
            if (this.parameterAccordion) {
                this.parameterAccordion.classList.toggle('is-empty', !selected);
            }
            if (this.parameterGrid) {
                this.parameterGrid.hidden = !selected;
            }
            if (this.parameterEmpty) {
                this.parameterEmpty.hidden = selected;
            }
            if (this.parameterModeDesc) {
                this.parameterModeDesc.textContent = selected
                    ? (this.currentMode === 'dynamic'
                        ? this.getUiText('mode-description-dynamic', 'Dynamic parameters can be edited manually and generate custom results.')
                        : this.getUiText('mode-description-static', 'Static parameters are read-only and match the selected preset.'))
                    : this.getUiText('static-parameters-empty', 'Please select a stage first.');
            }
            if (this.parameterAccordion) {
                const summary = this.parameterAccordion.querySelector('.parameter-accordion-summary');
                if (summary) {
                    summary.setAttribute('aria-expanded', String(Boolean(this.parameterAccordion.open)));
                }
            }
            if (this.parameterState) {
                this.parameterState.textContent = this.currentMode === 'dynamic'
                    ? this.getUiText('dynamicModeState', 'EDITABLE')
                    : this.getUiText('staticModeState', 'READ ONLY');
            }
            this.syncParameterAccordionAriaState();
        }

        syncParameterAccordionAriaState() {
            if (!this.parameterAccordion) return;
            const summary = this.parameterAccordion.querySelector('.parameter-accordion-summary');
            if (summary) {
                summary.setAttribute('aria-expanded', String(this.parameterAccordion.open));
            }
        }

        applyParameterValues(values, editable, clearMissing = false) {
            const paramValues = values || {};
            this.parameterInputs?.forEach((input) => {
                const key = input.dataset?.parameterKey || input.name;
                if (!key) return;
                const value = paramValues[key];
                if (value !== undefined && value !== null && value !== '') {
                    input.value = value;
                    input.dataset.defaultValue = String(value);
                } else if (clearMissing) {
                    input.value = '';
                }
                const isEditable = Boolean(editable);
                input.readOnly = !isEditable;
                input.setAttribute('aria-readonly', String(!isEditable));
                input.classList.toggle('is-readonly', !isEditable);
                input.classList.toggle('is-editable', isEditable);
            });
        }

        collectParameterOverrides() {
            const overrides = {};
            this.parameterInputs?.forEach((input) => {
                const key = input.dataset?.parameterKey || input.name;
                if (!key) return;
                const raw = String(input.value ?? '').trim();
                if (!raw) return;
                const numberValue = Number(raw);
                overrides[key] = Number.isFinite(numberValue) ? numberValue : raw;
            });
            return overrides;
        }

        isStageSelectionValid() {
            return Boolean(this.stageSelect && this.stageSelect.value);
        }

        updateGenerateButtonState() {
            if (!this.generateBtn) return;
            const canGenerate = !this.isGenerating && this.isStageSelectionValid();
            this.generateBtn.disabled = !canGenerate;
            this.generateBtn.innerHTML = this.isGenerating
                ? `<i class="fas fa-spinner fa-spin"></i> ${this.getUiText('generatingTexture', 'Generating...')}`
                : `<i class="fas fa-magic"></i> ${this.getUiText('generateTexture', 'Generate texture')}`;
        }

        applyLocalizedTexts() {
            if (this.formTitle) {
                this.formTitle.innerHTML = `<i class="fas fa-sliders-h"></i> ${this.getUiText('formTitle', 'Model Parameters')}`;
            }
            if (this.modeDescription) {
                this.modeDescription.textContent = this.currentMode === 'dynamic'
                    ? this.getUiText('mode-description-dynamic', 'Dynamic parameters can be edited manually and generate custom results.')
                    : this.getUiText('mode-description-static', 'Static parameters are read-only and match the selected preset.');
            }
            if (this.dynamicModeHint) {
                this.dynamicModeHint.hidden = this.currentMode !== 'dynamic';
                this.dynamicModeHint.textContent = this.getUiText(
                    'dynamic-parameter-hint',
                    'Tip: start from the preset values and change only the fields you need.'
                );
            }
            if (this.stageLabelText) {
                this.stageLabelText.textContent = this.getUiText('stageLabel', 'Stage');
            }
            if (this.stageHelp) {
                this.stageHelp.textContent = this.getUiText('stageSelectionHelp', 'Select a concrete stage before generating.');
            }
            if (this.staticModeBtn?.querySelector('span')) {
                this.staticModeBtn.querySelector('span').textContent = this.getUiText('static-mode', 'Static parameters');
            }
            if (this.dynamicModeBtn?.querySelector('span')) {
                this.dynamicModeBtn.querySelector('span').textContent = this.getUiText('dynamic-mode', 'Dynamic parameters');
            }
            if (this.parameterModeLabel) {
                this.parameterModeLabel.textContent = this.currentMode === 'dynamic'
                    ? this.getUiText('dynamic-mode', 'Dynamic parameters')
                    : this.getUiText('static-mode', 'Static parameters');
            }
            if (this.randomErrorToggleLabel) {
                this.randomErrorToggleLabel.textContent = this.getUiText('randomErrorToggleLabel', 'Random error');
            }
            if (this.randomErrorToggleHelp) {
                this.randomErrorToggleHelp.textContent = this.getUiText('randomErrorToggleHelp', 'Toggle the stochastic disturbance during simulation.');
            }
            if (this.randomErrorProfileTitle) {
                this.randomErrorProfileTitle.textContent = this.getUiText('randomErrorProfileTitle', 'Random error profile');
            }
            if (this.randomErrorProfileDesc) {
                this.randomErrorProfileDesc.textContent = this.currentMode === 'dynamic'
                    ? this.getUiText('randomErrorProfileDescDynamic', 'Editable defaults for the selected stage. Turn on random error to use them.')
                    : this.getUiText('randomErrorProfileDesc', 'Read-only defaults for the selected stage.');
            }
            if (this.randomErrorEditHint) {
                this.randomErrorEditHint.hidden = this.currentMode !== 'dynamic';
                this.randomErrorEditHint.textContent = this.getUiText(
                    'dynamic-random-error-hint',
                    'Tip: in dynamic mode you can fine-tune random error before generating.'
                );
            }
            if (this.colorSchemeTitle) {
                this.colorSchemeTitle.innerHTML = `<i class="fas fa-palette"></i> ${this.getUiText('colorScheme', 'Color scheme')}`;
            }
            if (this.baseColorLabel) {
                this.baseColorLabel.textContent = this.getUiText('baseColor', 'Base color');
            }
            if (this.contrastColorLabel) {
                this.contrastColorLabel.textContent = this.getUiText('contrastColor', 'Contrast color');
            }
            if (this.imagePlaceholderText) {
                this.imagePlaceholderText.textContent = this.getUiText('imagePlaceholder', 'Generated texture will appear here');
            }
            if (this.viewBtn) {
                this.viewBtn.innerHTML = `<i class="fas fa-expand"></i> ${this.getUiText('view', 'View')}`;
            }
            if (this.downloadBtn) {
                this.downloadBtn.innerHTML = `<i class="fas fa-download"></i> ${this.getUiText('download', 'Download')}`;
            }
            if (this.resultTitle) {
                this.resultTitle.innerHTML = `<i class="fas fa-image"></i> ${this.getUiText('resultTextureTitle', 'Result Texture')}`;
            }
            if (this.modelTitle) {
                this.modelTitle.innerHTML = `<i class="fas fa-cube"></i> ${this.getUiText('modelTitle', '3D Visualization')}`;
            }
            if (this.shellSelectLabel) {
                this.shellSelectLabel.innerHTML = `<i class="fas fa-list"></i> ${this.getUiText('shellSelectLabel', 'Select shell type:')}`;
            }
            this.updateParameterLabels();
            this.updateParameterAccordionState(this.isStageSelectionValid());
            this.updateStageOptionLabels();
            this.updateRandomErrorLabels();
            this.updateRandomErrorAccordionState();
        }

        updateStageOptionLabels() {
            if (!this.stageSelect) return;
            const placeholderOption = this.stageSelect.options?.[0];
            if (placeholderOption && placeholderOption.value === '') {
                placeholderOption.textContent = this.getUiText('stagePlaceholder', 'Select an option');
            }
            Array.from(this.stageSelect.options || []).forEach((option) => {
                if (!option || option.value === '') return;
                const index = this.getStageIndexFromOption(option);
                if (index > 0) {
                    option.textContent = this.getLocalizedStageLabel(index);
                }
            });
        }

        updateRandomErrorLabels() {
            const bundle = this.getUiBundle();
            const labels = bundle.randomErrorLabels || {};
            Object.entries(this.randomErrorSummaryLabels).forEach(([key, labelEl]) => {
                if (labelEl) {
                    labelEl.textContent = labels[key] || labelEl.textContent || key;
                }
            });
        }

        getCurrentRandomErrorValues() {
            if (!this.currentStageKey) return {};
            const defaults = this.currentRandomErrorProfileData || this.currentRandomErrorProfile || {};
            if (this.currentMode === 'dynamic') {
                return this.dynamicRandomErrorValuesByStage[this.currentStageKey] || defaults;
            }
            return defaults;
        }

        applyRandomErrorValues(values, editable, clearMissing = false) {
            const paramValues = values || {};
            Object.entries(this.randomErrorValues).forEach(([key, input]) => {
                if (!input) return;
                const value = paramValues[key];
                if (value !== undefined && value !== null && value !== '') {
                    input.value = String(value);
                    input.dataset.defaultValue = String(value);
                } else if (clearMissing) {
                    input.value = '';
                }
                const isEditable = Boolean(editable);
                input.readOnly = !isEditable;
                input.setAttribute('aria-readonly', String(!isEditable));
                input.classList.toggle('is-readonly', !isEditable);
                input.classList.toggle('is-editable', isEditable);
            });
        }

        collectRandomErrorOverrides() {
            const overrides = {};
            Object.entries(this.randomErrorValues).forEach(([key, input]) => {
                if (!input) return;
                const raw = String(input.value ?? '').trim();
                if (!raw) return;
                const numberValue = Number(raw);
                overrides[key] = Number.isFinite(numberValue) ? numberValue : raw;
            });
            return overrides;
        }

        updateRandomErrorAccordionState(hasStage = this.isStageSelectionValid()) {
            const enabled = Boolean(this.randomErrorCheckbox && this.randomErrorCheckbox.checked);
            const selected = Boolean(hasStage);
            const editable = Boolean(selected && this.currentMode === 'dynamic');
            if (this.randomErrorCheckbox) {
                this.randomErrorCheckbox.setAttribute('aria-checked', String(enabled));
            }
            if (this.randomErrorState) {
                this.randomErrorState.textContent = enabled
                    ? (window.getFigureStageUiLanguage?.() === 'en' ? 'ON' : 'ZAPNUTO')
                    : (window.getFigureStageUiLanguage?.() === 'en' ? 'OFF' : 'VYPNUTO');
            }
            if (this.randomErrorPreview) {
                this.randomErrorPreview.classList.toggle('is-empty', !selected);
                this.randomErrorPreview.classList.toggle('is-disabled', selected && !enabled);
            }
            if (selected) {
                this.applyRandomErrorValues(this.getCurrentRandomErrorValues(), editable, false);
            } else {
                this.applyRandomErrorValues({}, false, true);
            }
            if (this.randomErrorEmpty) {
                this.randomErrorEmpty.hidden = selected;
            }
            if (this.randomErrorSummaryGrid) {
                this.randomErrorSummaryGrid.hidden = !selected;
            }
            if (this.randomErrorProfileDesc) {
                this.randomErrorProfileDesc.textContent = selected
                    ? (this.currentMode === 'dynamic'
                        ? this.getUiText('randomErrorProfileDescDynamic', 'Editable defaults for the selected stage. Turn on random error to use them.')
                        : this.getUiText('randomErrorProfileDesc', 'Read-only defaults for the selected stage.'))
                    : this.getUiText('randomParametersEmpty', 'Please select a stage first.');
            }
            if (this.randomErrorEditHint) {
                this.randomErrorEditHint.hidden = !selected || this.currentMode !== 'dynamic';
                this.randomErrorEditHint.textContent = this.getUiText(
                    'dynamic-random-error-hint',
                    'Tip: in dynamic mode you can fine-tune random error before generating.'
                );
            }
        }

        clearStageUi() {
            if (this.presetInput) {
                this.presetInput.value = '';
            }
            if (this.stageLabel) {
                this.stageLabel.textContent = this.getUiText('stageLabel', 'Stage');
            }
            if (this.stageDescription) {
                this.stageDescription.textContent = this.getUiText('stageSelectionHelp', 'Select a concrete stage before generating.');
            }
            this.currentStageKey = null;
            this.currentStaticParameterValues = {};
            this.currentParameterValues = {};
            this.applyParameterValues({}, this.currentMode === 'dynamic', true);
            this.currentRandomErrorProfile = null;
            this.renderRandomErrorPreview(null, '');
            this.updateParameterAccordionState(false);
            this.updateRandomErrorAccordionState(false);
            this.updateGenerateButtonState();
        }

        syncMode(mode) {
            const normalized = mode === 'dynamic' ? 'dynamic' : 'static';
            this.currentMode = normalized;

            if (this.modeInput) {
                this.modeInput.value = normalized;
            }
            if (this.parameterModeInput) {
                this.parameterModeInput.value = normalized;
            }

            const isDynamic = normalized === 'dynamic';
            if (this.stageGroup) {
                this.stageGroup.hidden = false;
            }
            if (this.stageSelect) {
                this.stageSelect.required = true;
                this.stageSelect.setAttribute('aria-required', 'true');
            }
            if (this.staticModeBtn) {
                this.staticModeBtn.classList.toggle('active', !isDynamic);
                this.staticModeBtn.setAttribute('aria-pressed', String(!isDynamic));
            }
            if (this.dynamicModeBtn) {
                this.dynamicModeBtn.classList.toggle('active', isDynamic);
                this.dynamicModeBtn.setAttribute('aria-pressed', String(isDynamic));
            }
            if (this.parameterAccordion) {
                this.parameterAccordion.classList.toggle('is-dynamic', isDynamic);
                this.parameterAccordion.classList.toggle('is-static', !isDynamic);
            }
            if (isDynamic && this.currentStageKey && !this.dynamicParameterValuesByStage[this.currentStageKey]) {
                this.dynamicParameterValuesByStage[this.currentStageKey] = { ...(this.currentStaticParameterValues || this.currentParameterValues || this.getBaseParameterValues()) };
            }
            const activeValues = this.currentStageKey
                ? (
                    isDynamic
                        ? (this.dynamicParameterValuesByStage[this.currentStageKey] || this.currentStaticParameterValues || this.currentParameterValues)
                        : (this.currentStaticParameterValues || this.currentParameterValues)
                )
                : {};
            this.currentParameterValues = activeValues;
            this.applyParameterValues(activeValues, isDynamic, true);
            this.applyLocalizedTexts();
            if (this.stageSelect?.value) {
                this.syncRandomErrorPreview();
            } else {
                this.clearStageUi();
            }
            this.updateGenerateButtonState();
        }

        bindEvents() {
            if (this.form) {
                this.form.addEventListener('submit', (event) => {
                    event.preventDefault();
                    if (!this.isStageSelectionValid()) {
                        this.stageSelect?.reportValidity?.();
                        return;
                    }
                    this.generateTexture();
                });
            }

            if (this.stageSelect) {
                this.stageSelect.addEventListener('change', () => {
                    if (this.currentMode === 'dynamic' && this.currentStageKey) {
                        this.dynamicParameterValuesByStage[this.currentStageKey] = this.collectParameterOverrides();
                        this.dynamicRandomErrorValuesByStage[this.currentStageKey] = this.collectRandomErrorOverrides();
                    }
                    this.syncStageUi(this.stageSelect.value);
                });
            }

            this.parameterInputs?.forEach((input) => {
                input.addEventListener('input', () => {
                    if (this.currentMode === 'dynamic' && this.currentStageKey) {
                        this.dynamicParameterValuesByStage[this.currentStageKey] = this.collectParameterOverrides();
                    }
                });
            });

            Object.values(this.randomErrorValues || {}).forEach((input) => {
                if (!input) return;
                input.addEventListener('input', () => {
                    if (this.currentMode === 'dynamic' && this.currentStageKey) {
                        this.dynamicRandomErrorValuesByStage[this.currentStageKey] = this.collectRandomErrorOverrides();
                    }
                });
            });

            if (this.staticModeBtn) {
                this.staticModeBtn.addEventListener('click', () => this.syncMode('static'));
            }

            if (this.dynamicModeBtn) {
                this.dynamicModeBtn.addEventListener('click', () => this.syncMode('dynamic'));
            }

            if (this.viewBtn) {
                this.viewBtn.addEventListener('click', () => {
                    if (this.generatedImage?.src && !this.generatedImage.src.includes('#')) {
                        openPopup(this.generatedImage);
                    }
                });
            }

            if (this.randomErrorCheckbox) {
            this.randomErrorCheckbox.addEventListener('change', () => {
                this.updateRandomErrorAccordionState();
                this.renderRandomErrorPreview(this.currentRandomErrorProfileData || this.currentRandomErrorProfile || {}, this.currentRandomErrorProfileKey || this.stageSelect?.value || '');
            });
            }

            if (this.parameterAccordion) {
                this.parameterAccordion.addEventListener('toggle', () => {
                    const summary = this.parameterAccordion.querySelector('.parameter-accordion-summary');
                    if (summary) {
                        summary.setAttribute('aria-expanded', String(this.parameterAccordion.open));
                    }
                });
            }

            document.addEventListener('languageChanged', () => {
                this.applyLocalizedTexts();
                if (this.stageSelect?.value) {
                    this.syncStageUi(this.stageSelect.value);
                } else {
                    this.clearStageUi();
                }
            });

            if (this.shellSelect) {
                this.shellSelect.addEventListener('change', () => this.handleShellChange());
            }
        }

        syncStageUi(levelKey) {
            const levels = window.FIG23_PROGRESSION_LEVELS || {};
            const spec = levelKey ? (levels[levelKey] || null) : null;
            if (!spec) {
                this.clearStageUi();
                return;
            }

            this.currentStageKey = levelKey;

            if (this.presetInput) {
                this.presetInput.value = levelKey;
            }
            if (this.stageLabel) {
                const option = this.stageSelect?.selectedOptions?.[0] || null;
                const stageIndex = this.getStageIndexFromOption(option);
                this.stageLabel.textContent = this.getLocalizedStageLabel(stageIndex);
            }
            if (this.stageDescription) {
                const option = this.stageSelect?.selectedOptions?.[0] || null;
                const stageIndex = this.getStageIndexFromOption(option);
                this.stageDescription.textContent = this.getLocalizedStageDescription(stageIndex) || spec.reference_report || '';
            }

            const parameterValues = this.getStageParameterValues(levelKey);
            this.currentStaticParameterValues = parameterValues;
            const dynamicValues = this.dynamicParameterValuesByStage[levelKey] || parameterValues;
            const activeValues = this.currentMode === 'dynamic' ? dynamicValues : parameterValues;
            this.currentParameterValues = activeValues;
            this.applyParameterValues(activeValues, this.currentMode === 'dynamic', true);
            this.updateParameterAccordionState(true);

            const progressionRandomError = this.getProgressionRandomErrorProfile(levelKey, spec);
            this.currentRandomErrorProfile = progressionRandomError.profile;
            this.currentRandomErrorProfileKey = progressionRandomError.profileKey;
            this.currentRandomErrorProfileData = progressionRandomError.profile;
            this.renderRandomErrorPreview(progressionRandomError.profile, levelKey);
            this.updateRandomErrorAccordionState(true);
            this.updateGenerateButtonState();
        }

        getProgressionRandomErrorProfile(levelKey, spec) {
            const developmentKey = spec?.development_key || 'dev_60';
            const defaults = (window.FIG23_DEVELOPMENT_RANDOM_ERROR_PRESETS || {})[developmentKey] || {};
            const override = spec?.random_error_override || {};
            return {
                profileKey: developmentKey,
                profile: Object.assign({}, defaults, override),
            };
        }

        getActiveRandomErrorProfile() {
            const levelKey = this.stageSelect?.value || '';
            if (!levelKey) return this.currentRandomErrorProfile || null;
            const levelSpec = (window.FIG23_PROGRESSION_LEVELS || {})[levelKey] || null;
            if (!levelSpec) return this.currentRandomErrorProfile || null;
            return this.getProgressionRandomErrorProfile(levelKey, levelSpec).profile || this.currentRandomErrorProfile || null;
        }

        renderRandomErrorPreview(profile, levelKey) {
            if (!this.randomErrorPreview) return;

            const defaults = profile || {};
            this.currentRandomErrorProfileKey = levelKey || this.currentRandomErrorProfileKey;
            this.currentRandomErrorProfileData = defaults;
            const editable = Boolean(this.currentStageKey && this.currentMode === 'dynamic');
            const activeValues = this.currentStageKey ? this.getCurrentRandomErrorValues() : defaults;
            this.applyRandomErrorValues(activeValues, editable, true);

            this.updateRandomErrorLabels();
            if (this.randomErrorState) {
                this.randomErrorState.textContent = Boolean(this.randomErrorCheckbox && this.randomErrorCheckbox.checked)
                    ? (window.getFigureStageUiLanguage?.() === 'en' ? 'ON' : 'ZAPNUTO')
                    : (window.getFigureStageUiLanguage?.() === 'en' ? 'OFF' : 'VYPNUTO');
            }
            this.randomErrorPreview.style.display = 'block';
        }


        syncRandomErrorPreview() {
            this.renderRandomErrorPreview(this.currentRandomErrorProfileData || this.getActiveRandomErrorProfile(), this.currentRandomErrorProfileKey || this.stageSelect?.value || '');
        }

        async generateTexture() {
            if (!this.form) return;

            const progressionLevel = this.stageSelect?.value || '';
            if (!progressionLevel) {
                this.stageSelect?.reportValidity?.();
                return;
            }
            const payload = {
                color1: this.color1?.value || '#f3e7c6',
                color2: this.color2?.value || '#101010',
                progression_level: progressionLevel,
                parameter_mode: this.currentMode,
                enable_random_error: Boolean(this.randomErrorCheckbox?.checked),
            };

            if (this.currentMode === 'dynamic') {
                const overrides = this.collectParameterOverrides();
                if (Object.keys(overrides).length > 0) {
                    payload.params_override = overrides;
                }
            }

            const profile = this.currentMode === 'dynamic'
                ? { ...(this.getActiveRandomErrorProfile() || {}), ...this.collectRandomErrorOverrides() }
                : (this.getActiveRandomErrorProfile() || {});
            if (payload.enable_random_error && profile) {
                Object.assign(payload, {
                    re_strength: profile.strength,
                    re_duration: profile.duration,
                    re_frequency: profile.frequency,
                    re_probability: profile.probability,
                    re_num_regions: profile.num_regions,
                    re_region_size: profile.region_size,
                    re_jitter: profile.jitter,
                    re_micro_noise: profile.micro_noise,
                    re_alpha_var: profile.alpha_var,
                    re_beta: profile.beta,
                    re_drift_x: profile.drift_x,
                    re_drift_y: profile.drift_y,
                    re_drift_frequency: profile.drift_frequency,
                });
            }

            this.setGenerating(true);
            try {
                const response = await fetch(this.apiEndpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload),
                });
                const data = await response.json();
                if (!response.ok) {
                    throw new Error(data.error || 'Generation failed');
                }
                this.showGeneratedTexture(data);
            } catch (error) {
                figurePageShared.notify(error.message || 'Generation failed', 'error');
            } finally {
                this.setGenerating(false);
            }
        }

        showGeneratedTexture(data) {
            if (this.viewer) {
                this.viewer.resetTexture();
            }
            resultBridge.showGeneratedTexture(this, data, {
                defaultDownloadName: 'figure_2_3.png',
                successMessage: 'Figure 2.3 texture generated.',
                refreshStageUi: (page) => {
                    if (page.stageSelect?.value) {
                        page.syncStageUi(page.stageSelect.value);
                    } else {
                        page.clearStageUi();
                    }
                },
                afterImageRendered: (page, imageUrl) => {
                    page.bindGeneratedImageDragstart(imageUrl);
                },
            });
        }

        bindGeneratedImageDragstart(imageUrl) {
            if (!this.generatedImage) return;
            this.generatedImage.addEventListener('dragstart', (event) => {
                event.dataTransfer?.setData('text/plain', imageUrl);
                event.dataTransfer?.setData('text/uri-list', imageUrl);
            }, { once: true });
        }

        setGenerating(isGenerating) {
            resultBridge.setGenerating(this, isGenerating, {
                isSelectionValid: (page) => page.isStageSelectionValid(),
            });
        }

        updateGenerateButtonState() {
            resultBridge.updateGenerateButtonState(this, {
                isSelectionValid: (page) => page.isStageSelectionValid(),
            });
        }

        initViewerWithRetry(retries = 0) {
            viewerBridge.initViewerWithRetry(this, {
                containerId: 'threejs-container',
                loadingId: 'modelLoading',
                actionsId: 'modelActions',
                shellSelectId: 'shellSelect',
                shellTypes: window.SHELL_VIEWER_SHELLS || window.FIG23_SHELLS,
            }, retries);
        }

        handleShellChange() {
            viewerBridge.handleShellChange(this);
        }
    }

    document.addEventListener('DOMContentLoaded', () => {
        window.pattern23Page = new Pattern23Page();
    });
    windowBridge.registerPatternBridges(() => window.pattern23Page, {
        includeModeBridge: false,
        stageMethodName: 'syncStageUi',
    });
    viewerBridge.registerWindowBridge(() => window.pattern23Page);
})();
