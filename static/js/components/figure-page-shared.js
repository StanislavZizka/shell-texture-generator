(() => {
    function notify(message, type = 'info') {
        if (typeof window.showToast === 'function') {
            window.showToast(message, type);
            return;
        }
        console.log(`[${type}] ${message}`);
    }

    function getUiBundle() {
        const language = window.getFigureStageUiLanguage ? window.getFigureStageUiLanguage() : 'cs';
        return window.FIGURE_STAGE_UI_TEXTS?.[language] || window.FIGURE_STAGE_UI_TEXTS?.en || {};
    }

    function getUiText(key, fallback = '') {
        return window.getFigureStageUiText ? window.getFigureStageUiText(key, fallback) : fallback;
    }

    function getStageIndexFromOption(option) {
        if (!option) return 0;
        const index = Number(option.dataset?.stageIndex || option.value || 0);
        return Number.isFinite(index) ? index : 0;
    }

    function getLocalizedStageLabel(index) {
        const bundle = getUiBundle();
        return bundle.stageLabels?.[index] || `Stage ${index}`;
    }

    function getLocalizedStageDescription(index) {
        const bundle = getUiBundle();
        return bundle.stageDescriptions?.[index] || '';
    }

    window.FigurePageShared = {
        notify,
        getUiBundle,
        getUiText,
        getStageIndexFromOption,
        getLocalizedStageLabel,
        getLocalizedStageDescription,
    };
})();
