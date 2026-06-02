(() => {
    const figurePageShared = window.FigurePageShared;
    if (!figurePageShared) {
        throw new Error('FigurePageShared helper must be loaded before figure-page-result-bridge.js');
    }

    function updateGenerateButtonState(page, options = {}) {
        if (!page?.generateBtn) return;

        const isSelectionValid = typeof options.isSelectionValid === 'function'
            ? Boolean(options.isSelectionValid(page))
            : Boolean(options.isSelectionValid);

        const canGenerate = !page.isGenerating && isSelectionValid;
        page.generateBtn.disabled = !canGenerate;
        page.generateBtn.innerHTML = page.isGenerating
            ? `<i class="fas fa-spinner fa-spin"></i> ${page.getUiText('generatingTexture', 'Generating...')}`
            : `<i class="fas fa-magic"></i> ${page.getUiText('generateTexture', 'Generate texture')}`;
    }

    function setGenerating(page, isGenerating, options = {}) {
        page.isGenerating = Boolean(isGenerating);
        updateGenerateButtonState(page, options);
    }

    function showGeneratedTexture(page, data, options = {}) {
        const imageUrl = data.image_url;
        page.currentImageUrl = imageUrl;

        if (page.imagePlaceholder) {
            page.imagePlaceholder.style.display = 'none';
        }
        if (page.generatedImage) {
            page.generatedImage.src = `${imageUrl}${imageUrl.includes('?') ? '&' : '?'}t=${Date.now()}`;
            page.generatedImage.style.display = 'block';
            page.generatedImage.draggable = true;
            if (typeof options.afterImageRendered === 'function') {
                options.afterImageRendered(page, imageUrl);
            }
        }
        if (page.imageActions) {
            page.imageActions.style.display = 'flex';
        }
        if (page.downloadBtn) {
            page.downloadBtn.href = imageUrl;
            page.downloadBtn.download = data.download_name || options.defaultDownloadName || 'pattern_texture.png';
        }
        if (typeof options.refreshStageUi === 'function') {
            options.refreshStageUi(page, data);
        }

        document.dispatchEvent(new CustomEvent('textureGenerated', {
            detail: {
                imageUrl,
                preset: data.preset,
                stageLabel: page.stageLabel?.textContent || '',
                mode: page.currentMode,
            },
        }));

        figurePageShared.notify(options.successMessage || 'Texture generated.', 'success');
    }

    window.FigurePageResultBridge = {
        updateGenerateButtonState,
        setGenerating,
        showGeneratedTexture,
    };
})();
