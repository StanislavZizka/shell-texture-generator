(() => {
    function registerStageBridge(getPageInstance, methodName = 'syncStageUi') {
        window.syncPatternStage = function syncPatternStage(value) {
            const page = getPageInstance?.();
            if (page && typeof page[methodName] === 'function') {
                page[methodName](value);
            }
        };
    }

    function registerModeBridge(getPageInstance, methodName = 'syncMode') {
        window.syncPatternMode = function syncPatternMode(value) {
            const page = getPageInstance?.();
            if (page && typeof page[methodName] === 'function') {
                page[methodName](value);
            }
        };
        window.syncPatternDevelopment = window.syncPatternMode;
    }

    function registerPatternBridges(getPageInstance, options = {}) {
        registerStageBridge(getPageInstance, options.stageMethodName || 'syncStageUi');
        if (options.includeModeBridge) {
            registerModeBridge(getPageInstance, options.modeMethodName || 'syncMode');
        }
    }

    window.FigurePageWindowBridge = {
        registerStageBridge,
        registerModeBridge,
        registerPatternBridges,
    };
})();
