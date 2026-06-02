(() => {
    const figurePageShared = window.FigurePageShared;
    if (!figurePageShared) {
        throw new Error('FigurePageShared helper must be loaded before activator_212.js');
    }
    const viewerBridge = window.FigurePageViewerBridge;
    if (!viewerBridge) {
        throw new Error('FigurePageViewerBridge helper must be loaded before activator_212.js');
    }
    const resultBridge = window.FigurePageResultBridge;
    if (!resultBridge) {
        throw new Error('FigurePageResultBridge helper must be loaded before activator_212.js');
    }
    const windowBridge = window.FigurePageWindowBridge;
    if (!windowBridge) {
        throw new Error('FigurePageWindowBridge helper must be loaded before activator_212.js');
    }

    class PatternFamilyPage {
        constructor() {
            this.apiEndpoint = window.FIGURE_API_ENDPOINT || '/api/generate-212';
            this.pageKind = window.FIGURE_PAGE_KIND || '212';
            this.familyLabel = this.pageKind === '212' ? 'Labyrinths' : 'Spots';
            this.form = document.getElementById('patternForm');
            this.stageSelect = document.getElementById('pattern_stage');
            this.presetInput = document.getElementById('preset');
            this.modeInput = document.getElementById('figure_pattern_mode');
            this.parameterModeInput = document.getElementById('parameter_mode');
            this.stageGroup = document.getElementById('patternStageGroup');
            this.parameterAccordion = document.getElementById('patternParameterAccordion');
            this.parameterGrid = document.getElementById('patternParameterGrid');
            this.parameterEmpty = document.getElementById('patternParameterEmpty');
            this.parameterModeLabel = document.getElementById('patternParameterModeLabel');
            this.parameterModeDesc = document.getElementById('patternParameterModeDesc');
            this.parameterState = document.getElementById('patternParameterState');
            this.parameterInputs = Array.from(document.querySelectorAll('[data-parameter-key].parameter-item input, .parameter-input[data-parameter-key]'));
            this.formTitle = document.querySelector('.form-container h3');
            this.modeDescription = document.getElementById('patternModeDescription');
            this.dynamicModeHint = document.getElementById('patternDynamicModeHint');
            this.stageLabelText = document.getElementById('patternStageLabelText');
            this.stageHelp = document.getElementById('stageHelp');
            this.randomErrorGroup = document.getElementById('patternRandomErrorGroup');
            this.randomErrorAccordion = document.getElementById('patternRandomErrorAccordion');
            this.randomErrorToggleLabel = document.getElementById('patternRandomErrorToggleLabel');
            this.randomErrorToggleHelp = document.getElementById('patternRandomErrorToggleHelp');
            this.randomErrorProfileTitle = document.getElementById('patternRandomErrorProfileTitle');
            this.randomErrorProfileDesc = document.getElementById('patternRandomErrorProfileDesc');
            this.randomErrorEditHint = document.getElementById('patternRandomErrorEditHint');
            this.randomErrorPreview = document.getElementById('patternRandomErrorPreview');
            this.randomErrorEmpty = document.getElementById('patternRandomErrorEmpty');
            this.randomErrorSummaryGrid = document.querySelector('#patternRandomErrorPreview .random-error-summary-grid');
            this.randomErrorState = document.getElementById('patternRandomErrorState');
            this.randomErrorCheckbox = document.getElementById('enable_random_error');
            this.randomErrorValues = {
                strength: document.getElementById('pattern_re_strength_value'),
                duration: document.getElementById('pattern_re_duration_value'),
                frequency: document.getElementById('pattern_re_frequency_value'),
                probability: document.getElementById('pattern_re_probability_value'),
                num_regions: document.getElementById('pattern_re_num_regions_value'),
                region_size: document.getElementById('pattern_re_region_size_value'),
                jitter: document.getElementById('pattern_re_jitter_value'),
                micro_noise: document.getElementById('pattern_re_micro_noise_value'),
                alpha_var: document.getElementById('pattern_re_alpha_var_value'),
                beta: document.getElementById('pattern_re_beta_value'),
                drift_x: document.getElementById('pattern_re_drift_x_value'),
                drift_y: document.getElementById('pattern_re_drift_y_value'),
                drift_frequency: document.getElementById('pattern_re_drift_frequency_value'),
            };
            this.randomErrorSummaryLabels = {
                strength: document.getElementById('pattern_re_strength_label'),
                duration: document.getElementById('pattern_re_duration_label'),
                frequency: document.getElementById('pattern_re_frequency_label'),
                probability: document.getElementById('pattern_re_probability_label'),
                num_regions: document.getElementById('pattern_re_num_regions_label'),
                region_size: document.getElementById('pattern_re_region_size_label'),
                jitter: document.getElementById('pattern_re_jitter_label'),
                micro_noise: document.getElementById('pattern_re_micro_noise_label'),
                alpha_var: document.getElementById('pattern_re_alpha_var_label'),
                beta: document.getElementById('pattern_re_beta_label'),
                drift_x: document.getElementById('pattern_re_drift_x_label'),
                drift_y: document.getElementById('pattern_re_drift_y_label'),
                drift_frequency: document.getElementById('pattern_re_drift_frequency_label'),
            };
            this.stageModeBtn = document.getElementById('patternStaticModeBtn');
            this.developmentModeBtn = document.getElementById('patternDynamicModeBtn');
            this.staticModeBtn = this.stageModeBtn;
            this.dynamicModeBtn = this.developmentModeBtn;
            this.modeChip = document.getElementById('patternModeChip');
            this.currentStageKey = null;
            this.currentStaticParameterValues = {};
            this.dynamicParameterValuesByStage = {};
            this.dynamicRandomErrorValuesByStage = {};
            this.currentRandomErrorProfileKey = null;
            this.currentRandomErrorProfileData = null;
            this.color1 = document.getElementById('color1');
            this.color2 = document.getElementById('color2');
            this.colorSchemeTitle = document.querySelector('.color-group h4');
            this.baseColorLabel = document.querySelector('.color-group label[for="color1"]');
            this.contrastColorLabel = document.querySelector('.color-group label[for="color2"]');
            this.shellSelect = document.getElementById('shellSelect');
            this.imagePlaceholder = document.getElementById('imagePlaceholder');
            this.imagePlaceholderText = document.querySelector('#imagePlaceholder span');
            this.generatedImage = document.getElementById('generatedImage');
            this.imageActions = document.getElementById('imageActions');
            this.downloadBtn = document.getElementById('downloadBtn');
            this.viewBtn = document.getElementById('viewBtn');
            this.stageLabel = document.getElementById('stageLabel');
            this.stageDescription = document.getElementById('stageDescription');
            this.generateBtn = document.getElementById('generateBtn');
            this.staticModeBtn = document.getElementById('patternStaticModeBtn');
            this.dynamicModeBtn = document.getElementById('patternDynamicModeBtn');
            this.currentMode = 'static';
            this.currentImageUrl = null;
            this.currentRandomErrorProfile = null;
            this.currentParameterValues = {};
            this.viewer = null;
            this.isGenerating = false;
            this.getUiBundle = figurePageShared.getUiBundle;
            this.getUiText = figurePageShared.getUiText;
            this.getStageIndexFromOption = figurePageShared.getStageIndexFromOption;
            this.getLocalizedStageLabel = figurePageShared.getLocalizedStageLabel;
            this.getLocalizedStageDescription = figurePageShared.getLocalizedStageDescription;

            this.bindEvents();
            this.applyLocalizedTexts();
            this.syncMode('static');
            if (this.stageSelect?.value) {
                this.syncStageUi(this.stageSelect.value);
            } else {
                this.clearStageUi();
            }
            this.initViewerWithRetry();
        }

        isCurrentSelectionValid() {
            return Boolean(this.stageSelect && this.stageSelect.value);
        }

        updateGenerateButtonState() {
            if (!this.generateBtn) return;
            const canGenerate = !this.isGenerating && this.isCurrentSelectionValid();
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
                    ? this.getUiText('mode-description-dynamic', 'Editable model values are used instead of the locked preset.')
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
                this.parameterModeLabel.textContent = this.getUiText(this.currentMode === 'dynamic' ? 'dynamic-mode' : 'static-mode', this.currentMode === 'dynamic' ? 'Dynamic parameters' : 'Static parameters');
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
            const headings = {
                form: this.formTitle,
                result: document.querySelector('.image-container h3'),
                model: document.querySelector('.model-container h3'),
            };
            if (headings.result) {
                headings.result.innerHTML = `<i class="fas fa-image"></i> ${this.getUiText('resultTextureTitle', 'Result Texture')}`;
            }
            if (headings.model) {
                headings.model.innerHTML = `<i class="fas fa-cube"></i> ${this.getUiText('modelTitle', '3D Visualization')}`;
            }
            const modelLabel = document.querySelector('.model-selector label');
            if (modelLabel) {
                modelLabel.innerHTML = `<i class="fas fa-list"></i> ${this.getUiText('shellSelectLabel', 'Select shell type:')}`;
            }
            this.updateStageOptionLabels();
            this.updateParameterLabels();
            this.updateParameterAccordionState(this.isCurrentSelectionValid());
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

        updateRandomErrorAccordionState(hasStage = this.isCurrentSelectionValid()) {
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

        getParameterKeys() {
            return Array.isArray(window.FIGURE_PARAMETER_KEYS) ? window.FIGURE_PARAMETER_KEYS : [];
        }

        getBaseParameterValues() {
            const bundle = window.FIGURE_MODEL_PARAMS || {};
            if (bundle && typeof bundle === 'object' && !Array.isArray(bundle)) {
                return { ...bundle };
            }
            return {};
        }

        getStageParameterValues(stageNumber) {
            const stageKey = `stage_${Number(stageNumber) || 1}`;
            const stageSpec = (window.FIGURE_STAGE_PRESETS || {})[stageKey] || {};
            const stageOverrides = { ...(stageSpec.params_override || {}) };
            ['initial_noise_a_amplitude', 'initial_noise_b_amplitude', 'initial_noise_smoothing_passes', 'early_smoothing_fraction', 'early_smoothing_strength'].forEach((key) => {
                if (stageSpec[key] !== undefined && stageSpec[key] !== null) {
                    stageOverrides[key] = stageSpec[key];
                }
            });
            return {
                ...this.getBaseParameterValues(),
                ...stageOverrides,
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
                        ? this.getUiText('mode-description-dynamic', 'Editable model values are used instead of the locked preset.')
                        : this.getUiText('mode-description-static', 'Static parameters are read-only and match the selected preset.'))
                    : this.getUiText('static-parameters-empty', 'Please select a stage first.');
            }
            if (this.parameterState) {
                this.parameterState.textContent = this.currentMode === 'dynamic'
                    ? this.getUiText('dynamicModeState', 'EDITABLE')
                    : this.getUiText('staticModeState', 'POUZE PRO ČTENÍ');
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
            this.renderRandomErrorPreview(null, null);
            this.updateParameterAccordionState(false);
            this.updateRandomErrorAccordionState(false);
            this.updateGenerateButtonState();
        }

        bindEvents() {
            if (this.form) {
                this.form.addEventListener('submit', (event) => {
                    event.preventDefault();
                    if (!this.isCurrentSelectionValid()) {
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

            if (this.randomErrorCheckbox) {
                this.randomErrorCheckbox.addEventListener('change', () => {
                    this.updateRandomErrorAccordionState();
                    this.renderRandomErrorPreview(this.currentRandomErrorProfileKey, this.currentRandomErrorProfileData || this.currentRandomErrorProfile || {});
                });
            }

            if (this.parameterAccordion) {
                this.parameterAccordion.addEventListener('toggle', () => this.syncParameterAccordionAriaState());
            }

            document.addEventListener('languageChanged', () => {
                this.applyLocalizedTexts();
                if (this.stageSelect?.value) {
                    this.syncStageUi(this.stageSelect.value);
                } else {
                    this.clearStageUi();
                }
            });

            if (this.viewBtn) {
                this.viewBtn.addEventListener('click', () => {
                    if (this.generatedImage && this.generatedImage.src && !this.generatedImage.src.includes('#')) {
                        openPopup(this.generatedImage);
                    }
                });
            }

            if (this.shellSelect) {
                this.shellSelect.addEventListener('change', () => {
                    this.handleShellChange();
                });
            }
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
                this.stageSelect.disabled = false;
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
            if (this.parameterInputs) {
                this.parameterInputs.forEach((input) => {
                    input.readOnly = !isDynamic;
                    input.setAttribute('aria-readonly', String(!isDynamic));
                    input.classList.toggle('is-readonly', !isDynamic);
                    input.classList.toggle('is-editable', isDynamic);
                });
            }
            if (this.parameterModeLabel) {
                this.parameterModeLabel.textContent = isDynamic
                    ? this.getUiText('dynamic-mode', 'Dynamic parameters')
                    : this.getUiText('static-mode', 'Static parameters');
            }
            this.applyLocalizedTexts();
            if (this.stageSelect?.value) {
                this.syncRandomErrorPreview();
            } else {
                this.clearStageUi();
            }
            this.updateGenerateButtonState();
        }

        getStageSpec(stageNumber) {
            const stageKey = `stage_${stageNumber || 1}`;
            return {
                stageKey,
                stageSpec: (window.FIGURE_STAGE_PRESETS || {})[stageKey] || null,
            };
        }

        getRandomErrorProfileForStage(stageNumber) {
            const { stageKey } = this.getStageSpec(stageNumber);
            return {
                profileKey: stageKey,
                profile: (window.FIGURE_STAGE_RANDOM_ERROR_PRESETS || {})[stageKey] || null,
            };
        }

        getActiveRandomErrorProfile() {
            const stageNumber = this.stageSelect?.value || '';
            if (!stageNumber) return this.currentRandomErrorProfile || null;
            return this.getRandomErrorProfileForStage(stageNumber).profile || this.currentRandomErrorProfile || null;
        }

        syncStageUi(stageNumber) {
            const { stageKey, stageSpec } = this.getStageSpec(stageNumber);
            if (!stageSpec) {
                this.clearStageUi();
                return;
            }

            this.currentStageKey = stageKey;
            const selectedOption = this.stageSelect?.selectedOptions?.[0] || null;
            const stageIndex = this.getStageIndexFromOption(selectedOption) || Number(stageNumber) || 1;

            if (this.presetInput) {
                this.presetInput.value = stageKey;
            }
            if (this.stageLabel) {
                this.stageLabel.textContent = this.getLocalizedStageLabel(stageIndex);
            }
            if (this.stageDescription) {
                this.stageDescription.textContent = this.getLocalizedStageDescription(stageIndex) || stageSpec.reference_report || '';
            }

            const parameterValues = this.getStageParameterValues(stageNumber);
            this.currentStaticParameterValues = parameterValues;
            const dynamicValues = this.dynamicParameterValuesByStage[stageKey] || parameterValues;
            const activeValues = this.currentMode === 'dynamic' ? dynamicValues : parameterValues;
            this.currentParameterValues = activeValues;
            this.applyParameterValues(activeValues, this.currentMode === 'dynamic', true);
            this.updateParameterAccordionState(true);

            const randomError = this.getRandomErrorProfileForStage(stageNumber);
            this.currentRandomErrorProfile = randomError.profile;
            this.currentRandomErrorProfileKey = randomError.profileKey;
            this.currentRandomErrorProfileData = randomError.profile;
            this.renderRandomErrorPreview(randomError.profileKey, randomError.profile);
            this.updateRandomErrorAccordionState(true);
            this.updateGenerateButtonState();
        }

        syncDevelopmentUi(stageNumber) {
            this.syncMode('dynamic');
            if (stageNumber) {
                this.syncStageUi(stageNumber);
            }
        }

        renderRandomErrorPreview(profileKey, profile) {
            if (!this.randomErrorPreview) return;

            const defaults = profile || {};
            this.currentRandomErrorProfileKey = profileKey || this.currentRandomErrorProfileKey;
            this.currentRandomErrorProfileData = defaults;
            const editable = Boolean(this.currentStageKey && this.currentMode === 'dynamic');
            const activeValues = this.currentStageKey ? this.getCurrentRandomErrorValues() : defaults;
            this.applyRandomErrorValues(activeValues, editable, true);

            this.updateRandomErrorLabels();
            this.randomErrorPreview.style.display = 'block';
        }

        syncRandomErrorPreview() {
            this.renderRandomErrorPreview(this.currentRandomErrorProfileKey, this.currentRandomErrorProfileData || this.getActiveRandomErrorProfile() || {});
        }

        readNumberInput(input, fallback) {
            if (!input) return fallback;
            const value = Number(input.value);
            return Number.isFinite(value) ? value : fallback;
        }

        async generateTexture() {
            if (!this.form) return;
            const stageValue = this.stageSelect?.value || '';
            if (!stageValue) {
                this.stageSelect?.reportValidity?.();
                return;
            }

            this.setGenerating(true);
            try {
                const payload = {
                    color1: this.color1?.value || '#f3e7c6',
                    color2: this.color2?.value || '#101010',
                    stage: parseInt(stageValue || '1', 10),
                    parameter_mode: this.currentMode,
                    enable_random_error: Boolean(this.randomErrorCheckbox?.checked),
                };

                if (this.currentMode === 'dynamic') {
                    const overrides = this.collectParameterOverrides();
                    if (Object.keys(overrides).length > 0) {
                        payload.params_override = overrides;
                    }
                }

                const activeRandomErrorProfile = this.currentMode === 'dynamic'
                    ? { ...(this.getActiveRandomErrorProfile() || {}), ...this.collectRandomErrorOverrides() }
                    : (this.getActiveRandomErrorProfile() || {});
                if (payload.enable_random_error && activeRandomErrorProfile) {
                    Object.assign(payload, {
                        re_strength: activeRandomErrorProfile.strength,
                        re_duration: activeRandomErrorProfile.duration,
                        re_frequency: activeRandomErrorProfile.frequency,
                        re_probability: activeRandomErrorProfile.probability,
                        re_num_regions: activeRandomErrorProfile.num_regions,
                        re_region_size: activeRandomErrorProfile.region_size,
                        re_jitter: activeRandomErrorProfile.jitter,
                        re_micro_noise: activeRandomErrorProfile.micro_noise,
                        re_alpha_var: activeRandomErrorProfile.alpha_var,
                        re_beta: activeRandomErrorProfile.beta,
                        re_drift_x: activeRandomErrorProfile.drift_x,
                        re_drift_y: activeRandomErrorProfile.drift_y,
                        re_drift_frequency: activeRandomErrorProfile.drift_frequency,
                    });
                }

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
                defaultDownloadName: 'pattern_texture.png',
                successMessage: `${this.familyLabel} texture generated.`,
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
                isSelectionValid: (page) => page.isCurrentSelectionValid(),
            });
        }

        updateGenerateButtonState() {
            resultBridge.updateGenerateButtonState(this, {
                isSelectionValid: (page) => page.isCurrentSelectionValid(),
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
        window.patternFamilyPage = new PatternFamilyPage();
    });
    windowBridge.registerPatternBridges(() => window.patternFamilyPage, {
        includeModeBridge: true,
        stageMethodName: 'syncStageUi',
        modeMethodName: 'syncMode',
    });
    viewerBridge.registerWindowBridge(() => window.patternFamilyPage);
})();
