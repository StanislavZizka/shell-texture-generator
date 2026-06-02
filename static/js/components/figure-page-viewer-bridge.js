(() => {
    function initViewerWithRetry(page, config = {}, retries = 0) {
        const loadersReady = typeof THREE !== 'undefined' &&
            typeof THREE.OBJLoader !== 'undefined' &&
            typeof THREE.MTLLoader !== 'undefined' &&
            typeof THREE.OrbitControls !== 'undefined' &&
            typeof window.ShellViewer === 'function';

        if (!loadersReady) {
            const maxRetries = Number.isFinite(config.maxRetries) ? config.maxRetries : 20;
            const retryDelayMs = Number.isFinite(config.retryDelayMs) ? config.retryDelayMs : 250;
            if (retries < maxRetries) {
                setTimeout(() => initViewerWithRetry(page, config, retries + 1), retryDelayMs);
            }
            return;
        }

        page.viewer = new window.ShellViewer({
            containerId: config.containerId || 'threejs-container',
            loadingId: config.loadingId || 'modelLoading',
            actionsId: config.actionsId || 'modelActions',
            shellSelectId: config.shellSelectId || 'shellSelect',
            shellTypes: config.shellTypes || [],
        });
    }

    function handleShellChange(page) {
        if (!page?.viewer || !page?.shellSelect) return;
        page.viewer.changeModel(page.shellSelect.value);
    }

    function resetShellTexture(page) {
        if (!page?.viewer) return;
        page.viewer.resetTexture();
    }

    function registerWindowBridge(getPageInstance) {
        window.changeShellModel = function changeShellModel() {
            handleShellChange(getPageInstance?.());
        };

        window.resetShellTexture = function resetShellTextureBridge() {
            resetShellTexture(getPageInstance?.());
        };
    }

    window.FigurePageViewerBridge = {
        initViewerWithRetry,
        handleShellChange,
        resetShellTexture,
        registerWindowBridge,
    };
})();
