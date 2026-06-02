(() => {
    const DEFAULT_SHELLS = [
        'Buccinidae',
        'Fasciolariidae',
        'Moon snail',
        'Muricidae',
        'Pecten',
        'Whelk',
    ];

    class ShellViewer {
        constructor(options = {}) {
            this.containerId = options.containerId || 'threejs-container';
            this.loadingId = options.loadingId || 'modelLoading';
            this.actionsId = options.actionsId || 'modelActions';
            this.shellSelectId = options.shellSelectId || 'shellSelect';
            this.shellTypes = options.shellTypes || window.SHELL_VIEWER_SHELLS || window.FIG23_SHELLS || DEFAULT_SHELLS;
            this.currentShellType = options.defaultShellType || this.shellTypes[0] || 'Buccinidae';
            this.scene = null;
            this.camera = null;
            this.renderer = null;
            this.controls = null;
            this.ambientLight = null;
            this.keyLight = null;
            this.fillLight = null;
            this.shell = null;
            this.container = null;
            this.loadingElement = null;
            this.actionsElement = null;
            this.pendingTextureUrl = null;
            this.currentTextureUrl = null;
            this.originalMaterials = [];
            this.shellBasePosition = new THREE.Vector3(0, -0.18, 0);
            this.shellMaterialProfile = this.getShellMaterialProfile(this.currentShellType);
            this.modelLoadToken = 0;
            this.textureLoadToken = 0;
            this.initialized = false;
            this.initializationAttempted = false;
            this.frameHandle = null;
            this.init();
        }

        init(retries = 0) {
            this.container = document.getElementById(this.containerId);
            this.loadingElement = document.getElementById(this.loadingId);
            this.actionsElement = document.getElementById(this.actionsId);
            if (!this.container) {
                return;
            }

            const loadersReady = typeof THREE !== 'undefined';

            if (!loadersReady) {
                if (retries < 30) {
                    setTimeout(() => this.init(retries + 1), 250);
                } else if (this.loadingElement) {
                    this.loadingElement.innerHTML = '<div class="loading-text">Three.js loaders are unavailable.</div>';
                }
                return;
            }

            if (this.initializationAttempted) {
                return;
            }
            this.initializationAttempted = true;

            this.setupScene();
            this.setupCamera();
            this.setupRenderer();
            this.ensureThreeCompatibility();
            this.setupControls();
            this.setupLights();
            this.bindAppearanceEvents();
            this.applyViewerPalette();
            this.bindContainerEvents();
            const initialLoadToken = this.modelLoadToken + 1;
            this.loadShellModel(this.currentShellType).finally(() => {
                if (!this.isActiveModelLoad(initialLoadToken)) {
                    return;
                }
                this.initialized = true;
                this.show();
                if (this.pendingTextureUrl) {
                    const queued = this.pendingTextureUrl;
                    this.pendingTextureUrl = null;
                    this.applyTexture(queued);
                }
            });
            this.animate();
        }

        ensureThreeCompatibility() {
            if (typeof THREE === 'undefined' || !THREE.Quaternion || !THREE.Quaternion.prototype) {
                return;
            }

            const quaternionProto = THREE.Quaternion.prototype;
            if (typeof quaternionProto.inverse !== 'function' && typeof quaternionProto.invert === 'function') {
                quaternionProto.inverse = function inverse() {
                    return this.invert();
                };
                console.info('[ShellViewer] Installed Quaternion.inverse compatibility shim');
            }
        }

        invalidateModelLoad() {
            this.modelLoadToken += 1;
            return this.modelLoadToken;
        }

        invalidateTextureLoad() {
            this.textureLoadToken += 1;
            return this.textureLoadToken;
        }

        isActiveModelLoad(loadToken) {
            return !this.destroyed && loadToken === this.modelLoadToken;
        }

        isActiveTextureLoad(textureToken) {
            return !this.destroyed && textureToken === this.textureLoadToken;
        }

        disposeObject3D(object3d) {
            if (!object3d || typeof object3d.traverse !== 'function') {
                return;
            }

            object3d.traverse((child) => {
                if (!child) {
                    return;
                }

                if (child.geometry && typeof child.geometry.dispose === 'function') {
                    child.geometry.dispose();
                }

                if (!child.material) {
                    return;
                }

                const materials = Array.isArray(child.material) ? child.material : [child.material];
                materials.forEach((material) => {
                    if (!material) {
                        return;
                    }

                    if (material.map && typeof material.map.dispose === 'function') {
                        material.map.dispose();
                    }
                    if (material.alphaMap && typeof material.alphaMap.dispose === 'function') {
                        material.alphaMap.dispose();
                    }
                    if (material.aoMap && typeof material.aoMap.dispose === 'function') {
                        material.aoMap.dispose();
                    }
                    if (material.emissiveMap && typeof material.emissiveMap.dispose === 'function') {
                        material.emissiveMap.dispose();
                    }
                    if (material.normalMap && typeof material.normalMap.dispose === 'function') {
                        material.normalMap.dispose();
                    }
                    if (material.roughnessMap && typeof material.roughnessMap.dispose === 'function') {
                        material.roughnessMap.dispose();
                    }
                    if (material.metalnessMap && typeof material.metalnessMap.dispose === 'function') {
                        material.metalnessMap.dispose();
                    }
                    if (typeof material.dispose === 'function') {
                        material.dispose();
                    }
                });
            });
        }

        setupScene() {
            this.scene = new THREE.Scene();
            this.scene.background = new THREE.Color(this.getViewerSceneBackgroundColor());
        }

        getComputedRootStyle() {
            return getComputedStyle(document.documentElement);
        }

        getViewerSceneBackgroundColor() {
            const rootStyle = this.getComputedRootStyle();
            const viewerBg = rootStyle.getPropertyValue('--viewer-scene-bg').trim();
            if (viewerBg) {
                return viewerBg;
            }
            const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
            return isDark ? '#171d1b' : '#f6f7f5';
        }

        getViewerAmbientColor() {
            const viewerAmbient = this.getComputedRootStyle().getPropertyValue('--viewer-ambient-light').trim();
            return viewerAmbient || '#ffffff';
        }

        getViewerKeyColor() {
            const viewerKey = this.getComputedRootStyle().getPropertyValue('--viewer-key-light').trim();
            return viewerKey || '#ffffff';
        }

        getViewerFillColor() {
            const viewerFill = this.getComputedRootStyle().getPropertyValue('--viewer-fill-light').trim();
            if (viewerFill) {
                return viewerFill;
            }
            return '#bad7ff';
        }

        setupCamera() {
            const aspect = this.container.clientWidth / Math.max(this.container.clientHeight, 1);
            this.camera = new THREE.PerspectiveCamera(42, aspect, 0.1, 1000);
            this.camera.position.set(0, 0.2, 3.2);
        }

        setupRenderer() {
            this.renderer = new THREE.WebGLRenderer({
                antialias: true,
                alpha: true,
                preserveDrawingBuffer: true,
                powerPreference: 'high-performance',
            });
            this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
            this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
            if ('outputColorSpace' in this.renderer && typeof THREE.SRGBColorSpace !== 'undefined') {
                this.renderer.outputColorSpace = THREE.SRGBColorSpace;
            } else if ('outputEncoding' in this.renderer && typeof THREE.sRGBEncoding !== 'undefined') {
                this.renderer.outputEncoding = THREE.sRGBEncoding;
            }
            this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
            this.renderer.toneMappingExposure = 1.1;
            this.container.appendChild(this.renderer.domElement);
        }

        setupControls() {
            try {
                this.ensureThreeCompatibility();

                if (typeof THREE.OrbitControls !== 'undefined') {
                    this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
                    this.controls.enableDamping = true;
                    this.controls.dampingFactor = 0.06;
                    this.controls.enablePan = true;
                    this.controls.enableZoom = true;
                    this.controls.minDistance = 1.0;
                    this.controls.maxDistance = 10;
                } else {
                    console.warn('[ShellViewer] OrbitControls unavailable, continuing without controls');
                    this.setupEnhancedControls();
                }
            } catch (error) {
                console.error('[ShellViewer] Failed to initialize OrbitControls', error);
                this.setupEnhancedControls();
            }
        }

        setupEnhancedControls() {
            if (!this.renderer || !this.camera) {
                return;
            }

            let isMouseDown = false;
            let mouseX = 0;
            let mouseY = 0;

            this.renderer.domElement.addEventListener('mousedown', (e) => {
                isMouseDown = true;
                mouseX = e.clientX;
                mouseY = e.clientY;
            });

            document.addEventListener('mouseup', () => {
                isMouseDown = false;
            });

            document.addEventListener('mousemove', (e) => {
                if (!isMouseDown || !this.shell) return;
                const deltaX = e.clientX - mouseX;
                const deltaY = e.clientY - mouseY;
                this.shell.rotation.y += deltaX * 0.01;
                this.shell.rotation.x += deltaY * 0.01;
                mouseX = e.clientX;
                mouseY = e.clientY;
            });

            this.renderer.domElement.addEventListener('wheel', (e) => {
                e.preventDefault();
                const zoomSpeed = 0.1;
                const currentZ = this.camera.position.z;
                if (e.deltaY > 0) {
                    this.camera.position.z = Math.min(currentZ + zoomSpeed, 20);
                } else {
                    this.camera.position.z = Math.max(currentZ - zoomSpeed, 0.5);
                }
            }, { passive: false });
        }

        setupLights() {
            this.ambientLight = new THREE.AmbientLight(0xffffff, 1.15);
            this.scene.add(this.ambientLight);

            this.keyLight = new THREE.DirectionalLight(0xffffff, 1.3);
            this.keyLight.position.set(4, 7, 6);
            this.scene.add(this.keyLight);

            this.fillLight = new THREE.DirectionalLight(0xbad7ff, 0.8);
            this.fillLight.position.set(-4, 2, 5);
            this.scene.add(this.fillLight);
        }

        bindAppearanceEvents() {
            document.addEventListener('appearanceChanged', () => {
                this.applyViewerPalette();
            });

            document.addEventListener('themeChanged', () => {
                this.applyViewerPalette();
            });
        }

        applyViewerPalette() {
            if (this.scene) {
                this.scene.background = new THREE.Color(this.getViewerSceneBackgroundColor());
            }

            if (this.ambientLight) {
                this.ambientLight.color.set(this.getViewerAmbientColor());
            }

            if (this.keyLight) {
                this.keyLight.color.set(this.getViewerKeyColor());
            }

            if (this.fillLight) {
                this.fillLight.color.set(this.getViewerFillColor());
            }

            if (this.renderer?.setClearColor) {
                this.renderer.setClearColor(this.getViewerSceneBackgroundColor(), 0);
            }
        }

        bindContainerEvents() {
            this.container.addEventListener('dragover', (e) => {
                e.preventDefault();
                this.container.classList.add('drag-over');
            });

            this.container.addEventListener('dragleave', () => {
                this.container.classList.remove('drag-over');
            });

            this.container.addEventListener('drop', (e) => {
                e.preventDefault();
                this.container.classList.remove('drag-over');
                const imageUrl = e.dataTransfer.getData('text/plain') || e.dataTransfer.getData('text/uri-list');
                if (imageUrl) {
                    this.applyTexture(imageUrl);
                }
            });
        }

        async loadShellModel(shellType) {
            const loadToken = this.invalidateModelLoad();
            this.currentShellType = shellType || this.currentShellType;
            this.clearCurrentModel();

            if (this.loadingElement) {
                this.loadingElement.style.display = 'flex';
                this.loadingElement.innerHTML = '<div class="loading-spinner"></div><div class="loading-text">Loading 3D model...</div>';
            }

            const shellDir = encodeURIComponent(this.currentShellType);
            const shellResourcePath = `/assets/${shellDir}/`;
            const mtlFile = `${encodeURIComponent(this.currentShellType)}.mtl`;
            const objFile = `${encodeURIComponent(this.currentShellType)}.obj`;
            const mtlPath = `${shellResourcePath}${mtlFile}`;
            const objPath = `${shellResourcePath}${objFile}`;
            console.debug?.('[ShellViewer] loading model', { shellType: this.currentShellType, mtlPath, objPath });

            return new Promise((resolve) => {
                if (typeof THREE.OBJLoader === 'undefined') {
                    console.warn('[ShellViewer] OBJLoader unavailable, using simple parser');
                    this.loadOBJWithSimpleParser(loadToken).then(resolve);
                    return;
                }

                if (typeof THREE.MTLLoader === 'undefined') {
                    console.warn('[ShellViewer] MTLLoader unavailable, loading OBJ without materials');
                    this.loadOBJWithoutMaterials(loadToken, this.loadingElement).then(resolve);
                    return;
                }

                const mtlLoader = new THREE.MTLLoader();
                if (typeof mtlLoader.setPath === 'function') {
                    mtlLoader.setPath(shellResourcePath);
                }
                if (typeof mtlLoader.setResourcePath === 'function') {
                    mtlLoader.setResourcePath(shellResourcePath);
                }
                mtlLoader.load(
                    mtlFile,
                    (materials) => {
                        if (!this.isActiveModelLoad(loadToken)) {
                            resolve(null);
                            return;
                        }
                        materials.preload();
                        const objLoader = new THREE.OBJLoader();
                        if (typeof objLoader.setPath === 'function') {
                            objLoader.setPath(shellResourcePath);
                        }
                        objLoader.setMaterials(materials);
                        objLoader.load(
                            objFile,
                            (object) => {
                                if (!this.isActiveModelLoad(loadToken)) {
                                    this.disposeObject3D(object);
                                    resolve(null);
                                    return;
                                }
                                this.prepareShellObject(object);
                                this.shell = object;
                                this.scene.add(object);
                                this.clearLoadingState();
                                resolve(object);
                            },
                            undefined,
                            (err) => {
                                if (!this.isActiveModelLoad(loadToken)) {
                                    resolve(null);
                                    return;
                                }
                                console.warn('ShellViewer OBJ load failed, falling back to parser', err, { shellType: this.currentShellType, objPath });
                                this.loadOBJWithSimpleParser(loadToken).then(resolve);
                            }
                        );
                    },
                    undefined,
                    (err) => {
                        if (!this.isActiveModelLoad(loadToken)) {
                            resolve(null);
                            return;
                        }
                        console.warn('ShellViewer MTL load failed, falling back to OBJ without materials', err, { shellType: this.currentShellType, mtlPath });
                        this.loadOBJWithoutMaterials(loadToken, this.loadingElement).then(resolve);
                    }
                );
            });
        }

        async loadOBJWithoutMaterials(loadToken, loadingEl) {
            return new Promise((resolve) => {
                console.log('Loading OBJ without materials...');
                const shellDir = encodeURIComponent(this.currentShellType);
                const shellResourcePath = `/assets/${shellDir}/`;
                const objPath = `${shellResourcePath}${encodeURIComponent(this.currentShellType)}.obj`;
                const objLoader = new THREE.OBJLoader();
                if (typeof objLoader.setPath === 'function') {
                    objLoader.setPath(shellResourcePath);
                }

                objLoader.load(`${encodeURIComponent(this.currentShellType)}.obj`, (object) => {
                    if (!this.isActiveModelLoad(loadToken)) {
                        this.disposeObject3D(object);
                        resolve(null);
                        return;
                    }
                    console.log('OBJ loaded without materials:', object);
                    this.prepareShellObject(object);
                    this.shell = object;
                    this.scene.add(this.shell);

                    this.clearLoadingState();
                    this.initialized = true;
                    resolve(object);
                }, undefined, (error) => {
                    if (!this.isActiveModelLoad(loadToken)) {
                        resolve(null);
                        return;
                    }
                    console.warn('ShellViewer fallback OBJ load failed, trying simple parser', error, { shellType: this.currentShellType, objPath });
                    this.loadOBJWithSimpleParser(loadToken).then(resolve);
                });
            });
        }

        async loadOBJWithSimpleParser(loadToken) {
            return new Promise((resolve) => {
                const loadingEl = document.getElementById('modelLoading');
                console.log('Loading OBJ with simple parser...');
                const shellDir = encodeURIComponent(this.currentShellType);
                const objPath = `/assets/${shellDir}/${encodeURIComponent(this.currentShellType)}.obj`;
                fetch(objPath)
                    .then((response) => response.text())
                    .then((objData) => {
                        if (!this.isActiveModelLoad(loadToken)) {
                            resolve(null);
                            return;
                        }
                        const geometry = this.parseOBJ(objData);
                        if (!geometry) {
                            throw new Error('Failed to parse OBJ data');
                        }

                        const material = new THREE.MeshPhongMaterial({
                            color: 0xf0f0f0,
                            shininess: 30,
                            specular: 0x111111,
                        });
                        this.originalMaterials = [material];

                        this.shell = new THREE.Mesh(geometry, material);
                        this.prepareShellObject(this.shell);
                        this.scene.add(this.shell);

                        this.clearLoadingState();
                        this.initialized = true;
                        resolve(this.shell);
                    })
                    .catch((error) => {
                        if (!this.isActiveModelLoad(loadToken)) {
                            resolve(null);
                            return;
                        }
                        console.error('Error loading OBJ with simple parser:', error);
                        this.fallbackToBasicShell(loadingEl, loadToken);
                        resolve(null);
                    });
            });
        }

        parseOBJ(data) {
            const vertices = [];
            const textureCoords = [];
            const faces = [];
            const faceUVs = [];

            const lines = data.split('\n');
            for (let line of lines) {
                line = line.trim();
                if (line.startsWith('v ')) {
                    const parts = line.split(/\s+/);
                    vertices.push(parseFloat(parts[1]), parseFloat(parts[2]), parseFloat(parts[3]));
                } else if (line.startsWith('vt ')) {
                    const parts = line.split(/\s+/);
                    textureCoords.push(parseFloat(parts[1]), parseFloat(parts[2]));
                } else if (line.startsWith('f ')) {
                    const parts = line.split(/\s+/);
                    if (parts.length >= 4) {
                        const vertexIndices = [];
                        const uvIndices = [];

                        for (let i = 1; i < parts.length; i++) {
                            const vertexData = parts[i].split('/');
                            const vertexIndex = parseInt(vertexData[0], 10) - 1;
                            const uvIndex = vertexData.length > 1 && vertexData[1] ? parseInt(vertexData[1], 10) - 1 : -1;
                            vertexIndices.push(vertexIndex);
                            uvIndices.push(uvIndex);
                        }

                        if (vertexIndices.length === 3) {
                            faces.push(vertexIndices[0], vertexIndices[1], vertexIndices[2]);
                            faceUVs.push(uvIndices[0], uvIndices[1], uvIndices[2]);
                        } else if (vertexIndices.length === 4) {
                            faces.push(vertexIndices[0], vertexIndices[1], vertexIndices[2]);
                            faces.push(vertexIndices[0], vertexIndices[2], vertexIndices[3]);
                            faceUVs.push(uvIndices[0], uvIndices[1], uvIndices[2]);
                            faceUVs.push(uvIndices[0], uvIndices[2], uvIndices[3]);
                        }
                    }
                }
            }

            if (vertices.length === 0 || faces.length === 0) {
                return null;
            }

            const geometry = new THREE.BufferGeometry();
            geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
            geometry.setIndex(faces);

            if (textureCoords.length > 0 && faceUVs.length > 0) {
                const uvBuffer = [];
                for (let i = 0; i < faceUVs.length; i++) {
                    const uvIndex = faceUVs[i];
                    if (uvIndex >= 0 && uvIndex < textureCoords.length / 2) {
                        uvBuffer.push(textureCoords[uvIndex * 2]);
                        uvBuffer.push(textureCoords[uvIndex * 2 + 1]);
                    } else {
                        uvBuffer.push(0.5, 0.5);
                    }
                }
                if (uvBuffer.length > 0) {
                    geometry.setAttribute('uv', new THREE.Float32BufferAttribute(uvBuffer, 2));
                }
            }

            geometry.computeVertexNormals();
            return geometry;
        }

        fallbackToBasicShell(loadingEl, loadToken) {
            if (!this.isActiveModelLoad(loadToken)) {
                return;
            }
            console.warn('[ShellViewer] Falling back to basic shell geometry');
            this.clearCurrentModel();
            const geometry = new THREE.SphereGeometry(1, 32, 16);
            this.shell = new THREE.Mesh(geometry, this.createShellMaterialMap());
            this.prepareShellObject(this.shell);
            this.scene.add(this.shell);
            this.clearLoadingState();
            this.initialized = true;
        }

        prepareShellObject(object) {
            if (!object) {
                return;
            }

            object.scale.setScalar(this.getShellScale());
            object.rotation.set(0, Math.PI * 0.10, 0);

            const bounds = new THREE.Box3().setFromObject(object);
            const center = bounds.getCenter(new THREE.Vector3());
            object.position.set(-center.x, -center.y, -center.z);
            object.userData = object.userData || {};
            object.userData.shellBasePosition = object.position.clone();
            this.shellBasePosition = object.userData.shellBasePosition.clone();

            this.originalMaterials = this.applyShellAppearance(object);
        }

        clearLoadingState() {
            if (this.loadingElement) {
                this.loadingElement.style.display = 'none';
                this.loadingElement.innerHTML = '<div class="loading-spinner"></div><div class="loading-text">Loading 3D model...</div>';
            }
            this.show();
        }

        getShellScale() {
            const scales = {
                'Buccinidae': 2.0,
                'Fasciolariidae': 2.6,
                'Moon snail': 2.4,
                'Muricidae': 3.0,
                'Pecten': 2.8,
                'Whelk': 2.5,
            };
            return scales[this.currentShellType] || 2.6;
        }

        getShellMaterialProfile(shellType) {
            const profiles = {
                'Buccinidae': {
                    color: 0xf5ecd6,
                    roughness: 0.78,
                    clearcoat: 0.16,
                    clearcoatRoughness: 0.42,
                },
                'Fasciolariidae': {
                    color: 0xf3e1d1,
                    roughness: 0.80,
                    clearcoat: 0.12,
                    clearcoatRoughness: 0.46,
                },
                'Moon snail': {
                    color: 0xf8f0de,
                    roughness: 0.76,
                    clearcoat: 0.18,
                    clearcoatRoughness: 0.40,
                },
                'Muricidae': {
                    color: 0xf0eadf,
                    roughness: 0.83,
                    clearcoat: 0.10,
                    clearcoatRoughness: 0.50,
                },
                'Pecten': {
                    color: 0xfcf4e3,
                    roughness: 0.72,
                    clearcoat: 0.20,
                    clearcoatRoughness: 0.36,
                },
                'Whelk': {
                    color: 0xf2e7cf,
                    roughness: 0.79,
                    clearcoat: 0.14,
                    clearcoatRoughness: 0.44,
                },
            };

            return profiles[shellType] || {
                color: 0xf4ecd9,
                roughness: 0.8,
                clearcoat: 0.14,
                clearcoatRoughness: 0.45,
            };
        }

        createShellMaterialMap(texture = null) {
            const profile = this.getShellMaterialProfile(this.currentShellType);
            const materialOptions = {
                color: profile.color,
                roughness: profile.roughness,
                metalness: 0.0,
                clearcoat: profile.clearcoat,
                clearcoatRoughness: profile.clearcoatRoughness,
                side: THREE.DoubleSide,
            };

            if (texture) {
                materialOptions.map = texture;
            }

            return new THREE.MeshPhysicalMaterial(materialOptions);
        }

        applyShellAppearance(object, texture = null) {
            if (!object || typeof object.traverse !== 'function') {
                return [];
            }

            const materials = [];
            object.traverse((child) => {
                if (!child.isMesh) {
                    return;
                }

                if (child.material && typeof child.material.dispose === 'function') {
                    child.material.dispose();
                }

                const material = this.createShellMaterialMap(texture);
                child.material = material;
                child.material.needsUpdate = true;
                materials.push(material);
            });

            return materials;
        }

        applyTexture(imageUrl) {
            if (!imageUrl) return;
            const textureLoadToken = this.invalidateTextureLoad();
            if (!this.shell || !this.initialized) {
                this.pendingTextureUrl = imageUrl;
                return;
            }

            const targetShellType = this.currentShellType;
            const loader = new THREE.TextureLoader();
            loader.load(
                imageUrl,
                (texture) => {
                    if (!this.isActiveTextureLoad(textureLoadToken) || !this.shell || targetShellType !== this.currentShellType) {
                        texture.dispose?.();
                        return;
                    }
                    texture.wrapS = THREE.RepeatWrapping;
                    texture.wrapT = THREE.RepeatWrapping;
                    texture.repeat.set(1, 1);
                    texture.anisotropy = this.renderer?.capabilities?.getMaxAnisotropy?.() || 1;
                    texture.needsUpdate = true;
                    if ('colorSpace' in texture) {
                        texture.colorSpace = THREE.SRGBColorSpace;
                    } else if ('encoding' in texture) {
                        texture.encoding = THREE.sRGBEncoding;
                    }

                    this.applyShellAppearance(this.shell, texture);

                    this.currentTextureUrl = imageUrl;
                    this.pendingTextureUrl = null;
                    if (this.actionsElement) {
                        this.actionsElement.style.display = 'flex';
                    }
                    this.show();
                },
                undefined,
                (err) => {
                    console.error('Failed to load shell texture', err);
                }
            );
        }

        changeModel(name) {
            if (!name) {
                return;
            }

            this.currentShellType = name;
            this.shellMaterialProfile = this.getShellMaterialProfile(name);
            this.currentTextureUrl = null;
            this.pendingTextureUrl = null;
            this.invalidateTextureLoad();
            this.loadShellModel(name);
        }

        resetTexture() {
            if (!this.shell || !this.originalMaterials.length) {
                return;
            }

            this.invalidateTextureLoad();
            let materialIndex = 0;
            this.shell.traverse((child) => {
                if (!child.isMesh || !child.material) return;
                const original = this.originalMaterials[materialIndex];
                if (original) {
                    child.material.dispose?.();
                    child.material = original.clone ? original.clone() : original;
                    child.material.needsUpdate = true;
                }
                materialIndex += 1;
            });
            this.currentTextureUrl = null;
            this.pendingTextureUrl = null;
        }

        clearCurrentModel({ dispose = true } = {}) {
            if (this.shell) {
                const previousShell = this.shell;
                this.scene.remove(previousShell);
                if (dispose) {
                    this.disposeObject3D(previousShell);
                }
                this.shell = null;
            }
            this.shellBasePosition = new THREE.Vector3(0, -0.18, 0);
            this.originalMaterials = [];
        }

        show() {
            if (this.container) {
                this.container.style.display = 'block';
            }

            const viewer = document.getElementById('modelViewer');
            if (viewer) {
                viewer.style.display = 'block';
            }

            const modelContainer = document.getElementById('modelContainer');
            if (modelContainer) {
                modelContainer.style.display = 'block';
            }

            if (this.loadingElement) {
                this.loadingElement.style.display = 'none';
            }
        }

        animate() {
            const loop = () => {
                this.frameHandle = requestAnimationFrame(loop);
                this.updateFloatMotion();
                if (this.controls) {
                    this.controls.update();
                }
                if (this.renderer && this.scene && this.camera) {
                    this.renderer.render(this.scene, this.camera);
                }
            };
            loop();
        }

        updateFloatMotion() {
            if (!this.shell) {
                return;
            }

            const elapsed = (performance.now() || 0) * 0.001;
            const base = this.shell.userData?.shellBasePosition || this.shellBasePosition;
            this.shell.position.x = base.x + Math.cos(elapsed * 0.55) * 0.025;
            this.shell.position.y = base.y + Math.sin(elapsed * 0.9) * 0.03;
        }
    }

    window.ShellViewer = ShellViewer;
})();
