class TextureHeatmapPreview {
    constructor() {
        this.section = document.getElementById('textureHeatmapSection');
        if (!this.section) {
            return;
        }

        this.toggle = document.getElementById('show_texture_heatmap');
        this.panel = document.getElementById('textureHeatmapPanel');
        this.canvas = document.getElementById('textureHeatmapCanvas');
        this.state = document.getElementById('textureHeatmapState');
        this.toggleLabel = document.getElementById('textureHeatmapToggleLabel');
        this.toggleHelp = document.getElementById('textureHeatmapToggleHelp');
        this.note = document.getElementById('textureHeatmapNote');
        this.viewBtn = document.getElementById('textureHeatmapView');
        this.downloadBtn = document.getElementById('textureHeatmapDownload');
        this.resultImage = document.getElementById('generatedImage');
        this.imagePlaceholder = document.getElementById('imagePlaceholder');
        this.context = this.canvas ? this.canvas.getContext('2d', { willReadFrequently: true }) : null;
        this.pendingRender = false;
        this.currentImageUrl = null;

        this.bindEvents();
        this.applyLocalizedTexts();
        this.setSectionVisible(false);
        this.setPanelVisible(false);
        this.updateDownloadLink(false);
        this.updateViewButton(false);
        this.updateStateLabel(false);
    }

    bindEvents() {
        if (this.toggle) {
            this.toggle.addEventListener('change', () => {
                const enabled = Boolean(this.toggle.checked);
                this.updateStateLabel(enabled);
                this.setPanelVisible(enabled);
                this.updateDownloadLink(false);
                this.updateViewButton(false);
                if (enabled) {
                    this.renderFromCurrentTexture();
                }
            });
        }

        if (this.viewBtn) {
            this.viewBtn.addEventListener('click', () => {
                this.openHeatmapPopup();
            });
        }

        if (this.canvas) {
            this.canvas.addEventListener('click', () => {
                this.openHeatmapPopup();
            });
        }

        if (this.resultImage) {
            this.resultImage.addEventListener('load', () => {
                if (this.toggle?.checked) {
                    this.renderFromCurrentTexture();
                }
            });
        }

        document.addEventListener('textureGenerated', (event) => {
            const imageUrl = event.detail?.imageUrl || this.resultImage?.src || '';
            if (imageUrl) {
                this.currentImageUrl = imageUrl;
                this.setSectionVisible(true);
                if (this.toggle?.checked) {
                    this.renderFromCurrentTexture();
                }
            }
        });

        document.addEventListener('languageChanged', () => {
            this.applyLocalizedTexts();
        });
    }

    getUiText(key, fallback = '') {
        if (typeof window.getFigureStageUiText === 'function') {
            return window.getFigureStageUiText(key, fallback);
        }
        return fallback;
    }

    applyLocalizedTexts() {
        if (this.toggleLabel) {
            this.toggleLabel.textContent = this.getUiText('texture-heatmap-toggle', 'Show heatmap');
        }
        if (this.toggleHelp) {
            this.toggleHelp.textContent = this.getUiText('texture-heatmap-help', 'Visualize the current texture as a heatmap below the result image.');
        }
        if (this.note) {
            this.note.textContent = this.getUiText('texture-heatmap-note', 'Heatmap is derived from the current generated texture.');
        }
        if (this.downloadBtn) {
            this.downloadBtn.innerHTML = `<i class="fas fa-download"></i> ${this.getUiText('download', 'Download')}`;
        }
        this.updateStateLabel(Boolean(this.toggle?.checked));
    }

    setSectionVisible(visible) {
        if (!this.section) return;
        this.section.hidden = !visible;
        this.section.classList.toggle('visible', visible);
    }

    setPanelVisible(visible) {
        if (!this.panel) return;
        this.panel.hidden = !visible;
        this.panel.classList.toggle('visible', visible);
    }

    updateStateLabel(enabled) {
        if (!this.state) return;
        const language = window.getFigureStageUiLanguage?.() || 'cs';
        this.state.textContent = enabled
            ? (language === 'en' ? this.getUiText('texture-heatmap-visible', 'HEATMAP SHOWN') : this.getUiText('texture-heatmap-visible', 'HEATMAP ZOBRAZENA'))
            : (language === 'en' ? this.getUiText('texture-heatmap-hidden', 'HEATMAP HIDDEN') : this.getUiText('texture-heatmap-hidden', 'HEATMAP SKRYTA'));
    }

    getDownloadFileName() {
        const sourceUrl = this.currentImageUrl || this.resultImage?.src || '';
        const cleanUrl = sourceUrl.split('?')[0].split('#')[0];
        const lastSegment = cleanUrl.split('/').pop() || 'heatmap.png';
        const dotIndex = lastSegment.lastIndexOf('.');
        const baseName = dotIndex > 0 ? lastSegment.slice(0, dotIndex) : lastSegment.replace(/\.[^.]+$/, '') || 'heatmap';
        return `${baseName}_heatmap.png`;
    }

    updateDownloadLink(available) {
        if (!this.downloadBtn) return;
        const hasCanvas = Boolean(available && this.canvas && this.canvas.width && this.canvas.height);
        this.downloadBtn.hidden = !hasCanvas;
        this.downloadBtn.setAttribute('aria-hidden', String(!hasCanvas));
        if (!hasCanvas) {
            this.downloadBtn.removeAttribute('href');
            this.downloadBtn.removeAttribute('download');
            return;
        }
        this.downloadBtn.href = this.canvas.toDataURL('image/png');
        this.downloadBtn.download = this.getDownloadFileName();
    }

    updateViewButton(available) {
        if (!this.viewBtn) return;
        const hasCanvas = Boolean(available && this.canvas && this.canvas.width && this.canvas.height);
        this.viewBtn.hidden = !hasCanvas;
        this.viewBtn.setAttribute('aria-hidden', String(!hasCanvas));
        if (this.canvas) {
            this.canvas.style.cursor = hasCanvas ? 'pointer' : 'default';
        }
    }

    openHeatmapPopup() {
        if (!this.canvas || !this.canvas.width || !this.canvas.height) {
            return;
        }
        if (typeof window.openPopup === 'function') {
            const heatmapImage = new Image();
            heatmapImage.decoding = 'async';
            heatmapImage.onload = () => window.openPopup(heatmapImage);
            heatmapImage.src = this.canvas.toDataURL('image/png');
            heatmapImage.alt = 'Texture heatmap';
        }
    }

    async renderFromCurrentTexture() {
        if (!this.resultImage || !this.canvas || !this.context) {
            return;
        }

        const sourceUrl = this.currentImageUrl || this.resultImage.src;
        if (!sourceUrl || sourceUrl.includes('#')) {
            if (this.note) {
                this.note.textContent = this.getUiText('texture-heatmap-not-available', 'Generate a texture first, then the heatmap can be shown.');
            }
            this.updateDownloadLink(false);
            this.updateViewButton(false);
            return;
        }

        if (!this.resultImage.complete || !this.resultImage.naturalWidth) {
            if (this.pendingRender) return;
            this.pendingRender = true;
            this.resultImage.addEventListener('load', () => {
                this.pendingRender = false;
                this.renderFromCurrentTexture();
            }, { once: true });
            return;
        }

        const width = this.resultImage.naturalWidth || this.resultImage.width || 0;
        const height = this.resultImage.naturalHeight || this.resultImage.height || 0;
        if (!width || !height) {
            return;
        }

        const offscreen = document.createElement('canvas');
        offscreen.width = width;
        offscreen.height = height;
        const offscreenCtx = offscreen.getContext('2d', { willReadFrequently: true });
        if (!offscreenCtx) return;
        offscreenCtx.drawImage(this.resultImage, 0, 0, width, height);
        const imageData = offscreenCtx.getImageData(0, 0, width, height);
        const data = imageData.data;

        let minLum = 255;
        let maxLum = 0;
        for (let i = 0; i < data.length; i += 4) {
            const lum = 0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2];
            if (lum < minLum) minLum = lum;
            if (lum > maxLum) maxLum = lum;
        }
        const range = Math.max(1, maxLum - minLum);

        const colors = [
            [0.0, [13, 8, 135]],
            [0.2, [76, 1, 166]],
            [0.4, [125, 3, 168]],
            [0.6, [204, 71, 120]],
            [0.8, [248, 149, 64]],
            [1.0, [240, 249, 33]],
        ];

        const lerp = (start, end, t) => start + (end - start) * t;
        const interpolateColor = (value) => {
            const clamped = Math.min(1, Math.max(0, value));
            let lower = colors[0];
            let upper = colors[colors.length - 1];
            for (let i = 0; i < colors.length - 1; i += 1) {
                if (clamped >= colors[i][0] && clamped <= colors[i + 1][0]) {
                    lower = colors[i];
                    upper = colors[i + 1];
                    break;
                }
            }
            const span = Math.max(1e-6, upper[0] - lower[0]);
            const localT = (clamped - lower[0]) / span;
            return [
                Math.round(lerp(lower[1][0], upper[1][0], localT)),
                Math.round(lerp(lower[1][1], upper[1][1], localT)),
                Math.round(lerp(lower[1][2], upper[1][2], localT)),
            ];
        };

        for (let i = 0; i < data.length; i += 4) {
            const lum = 0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2];
            const normalized = (lum - minLum) / range;
            const gammaAdjusted = Math.pow(Math.min(1, Math.max(0, normalized)), 0.92);
            const [r, g, b] = interpolateColor(gammaAdjusted);
            data[i] = r;
            data[i + 1] = g;
            data[i + 2] = b;
            data[i + 3] = 255;
        }

        this.canvas.width = width;
        this.canvas.height = height;
        this.canvas.style.width = '100%';
        this.canvas.style.height = 'auto';
        this.context.putImageData(imageData, 0, 0);
        this.updateDownloadLink(true);
        this.updateViewButton(true);
        this.setSectionVisible(true);
        this.setPanelVisible(true);
        this.updateStateLabel(true);
    }
}

window.TextureHeatmapPreview = TextureHeatmapPreview;
