/**
 * Building model manager - integrates video screen
 * Improves performance, error handling, and code structure
 */

// ===== Global variables and config =====
let buildingGroup = null;
let screenContent = null;
let lastTime = 0;

// Performance config
const PERFORMANCE_CONFIG = {
    TARGET_FPS: 60,
    FRAME_INTERVAL: 1000 / 60, // ~16.67ms
    FONT_RETRY_COUNT: 3,
    FONT_RETRY_DELAY: 1000
};
const building_position = [-122.36195286954631, 37.729593622423355];
// Building config:
const BUILDING_CONFIG = {
    position: [-122.36195286954631, 37.729593622423355],
    dimensions: {
        width: 2,
        height: 3 * 1.25, // Increase height by 25%
        depth: 1.5
    },
    screen: {
        width: 1.75,
        height: 0.875,
        borderThickness: 0.05
    },
    window: {
        size: 0.15,
        spacing: 0.275,
        lightOnProbability: 0.6
    }
};

// Renderer initialization
const renderer = new THREE.WebGLRenderer({
    antialias: true,
    alpha: true,
    powerPreference: "high-performance"
});

renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2)); // Limit pixel ratio to improve performance
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap; // Better shadow quality
document.body.appendChild(renderer.domElement);

// ===== Utility class: VideoScreen =====
class VideoScreen extends THREE.Group {
    /**
     * Constructor
     * @param {number} width - screen width
     * @param {number} height - screen height
     * @param {string} videoSrc - video source URL
     */
    constructor(width, height, videoSrc) {
        super();

        this.width = width;
        this.height = height;
        this.video = null;
        this.videoTexture = null;

        this._initializeVideo(videoSrc);
        this._createScreen();
        this._createFrame();
    }

    /**
     * Initialize video element
     * @private
     */
    _initializeVideo(videoSrc) {
        this.video = document.createElement('video');

        // Video configuration
        Object.assign(this.video, {
            src: videoSrc,
            loop: true,
            muted: true,
            autoplay: true,
            playsInline: true,
            preload: 'auto',
            crossOrigin: 'anonymous'
        });

        // Create video texture
        this.videoTexture = new THREE.VideoTexture(this.video);
        this.videoTexture.minFilter = THREE.LinearFilter;
        this.videoTexture.magFilter = THREE.LinearFilter;
        this.videoTexture.format = THREE.RGBFormat;
        this.videoTexture.flipY = true; // Fix upside-down video

        // Handle video playback
        this._handleVideoPlayback();
    }

    /**
     * Handle video playback logic
     * @private
     */
    async _handleVideoPlayback() {
        try {
            // Wait for video metadata
            await new Promise((resolve, reject) => {
                this.video.addEventListener('loadedmetadata', resolve);
                this.video.addEventListener('error', reject);
                this.video.load();
            });

            // Try autoplay
            await this.video.play();
            console.log('Video autoplay successful');

        } catch (error) {
            console.warn('Video autoplay failed, waiting for user interaction:', error.message);

            // Add user interaction listener
            this._addUserInteractionListener();
        }
    }

    /**
     * Add user interaction listener to start playback
     * @private
     */
    _addUserInteractionListener() {
        const playVideo = async () => {
            try {
                await this.video.play();
                console.log('User interaction successful, video playing');
                document.removeEventListener('click', playVideo);
                document.removeEventListener('touchstart', playVideo);
            } catch (error) {
                console.error('User interaction failed to play video:', error);
            }
        };

        document.addEventListener('click', playVideo, { once: true });
        document.addEventListener('touchstart', playVideo, { once: true });
    }

    /**
     * Create screen
     * @private
     */
    _createScreen() {
        const screenGeometry = new THREE.PlaneGeometry(this.width, this.height);
        const screenMaterial = new THREE.MeshBasicMaterial({
            map: this.videoTexture,
            side: THREE.FrontSide,
            transparent: false
        });

        this.screen = new THREE.Mesh(screenGeometry, screenMaterial);
        this.add(this.screen);
    }

    /**
     * Create screen frame
     * @private
     */
    _createFrame() {
        const borderThickness = BUILDING_CONFIG.screen.borderThickness;
        const borderGeometry = new THREE.BoxGeometry(
            this.width + borderThickness,
            this.height + borderThickness,
            0.025
        );

        const borderMaterial = new THREE.MeshStandardMaterial({
            color: 0x333333,
            roughness: 0.8,
            metalness: 0.2
        });

        this.border = new THREE.Mesh(borderGeometry, borderMaterial);
        this.border.position.z = -0.0375;
        this.add(this.border);
    }

    /**
     * Update video texture (if needed)
     */
    update() {
        // VideoTexture updates automatically; keep this method for API consistency
        if (this.video && this.video.readyState >= this.video.HAVE_CURRENT_DATA) {
            this.videoTexture.needsUpdate = true;
        }
    }

    /**
     * Dispose resources
     */
    dispose() {
        if (this.video) {
            this.video.pause();
            this.video.src = '';
            this.video.load();
        }

        if (this.videoTexture) {
            this.videoTexture.dispose();
        }

        // Dispose geometry and materials
        this.traverse((child) => {
            if (child.geometry) child.geometry.dispose();
            if (child.material) {
                if (Array.isArray(child.material)) {
                    child.material.forEach(material => material.dispose());
                } else {
                    child.material.dispose();
                }
            }
        });
    }
}

// ===== Font loader =====
const fontLoader = new THREE.FontLoader();

/**
 * Font loader with retry
 * @param {string} url - font file URL
 * @param {number} retries - retry count
 * @param {number} delay - retry delay
 * @returns {Promise<THREE.Font>}
 */
const loadFontWithRetry = async (url, retries = PERFORMANCE_CONFIG.FONT_RETRY_COUNT, delay = PERFORMANCE_CONFIG.FONT_RETRY_DELAY) => {
    for (let attempt = 0; attempt < retries; attempt++) {
        try {
            return await new Promise((resolve, reject) => {
                fontLoader.load(
                    url,
                    resolve,
                    undefined, // onProgress
                    reject
                );
            });
        } catch (error) {
            const isLastAttempt = attempt === retries - 1;
            console.error(`Font loading failed (attempt ${attempt + 1}/${retries}):`, error.message);

            if (isLastAttempt) {
                throw new Error(`Font loading failed: ${url}`);
            }

            // Exponential backoff
            await new Promise(resolve => setTimeout(resolve, delay));
            delay *= 2;
        }
    }
};

// ===== Building creation =====
/**
 * Create building model
 * @param {THREE.Font} font - loaded font
 * @returns {THREE.Group} building group
 */
function createBuilding(font) {
    const group = new THREE.Group();
    console.log(1);

    // Create main building
    const building = createBuildingStructure();
    group.add(building);
    console.log(12);
    // Create windows
    const windows = createWindows();
    windows.forEach(window => group.add(window));
    console.log(13);
    // Create video screen (replaces the old billboard)
    const videoScreen = createVideoScreen();
    group.add(videoScreen);
    console.log(14);
    // Create building name
    const nameText = createBuildingName(font);
    group.add(nameText);
    console.log(15);
    return group;
}

/**
 * Create main building structure
 * @returns {THREE.Mesh}
 */
function createBuildingStructure() {
    const { width, height, depth } = BUILDING_CONFIG.dimensions;

    const geometry = new THREE.BoxGeometry(width, height, depth);
    const material = new THREE.MeshStandardMaterial({
        color: 0xe0e0e0,
        roughness: 0.5,
        metalness: 0.1
    });

    const building = new THREE.Mesh(geometry, material);
    building.position.y = height / 2;
    building.castShadow = true;
    building.receiveShadow = true;

    return building;
}

/**
 * Create windows
 * @returns {THREE.Mesh[]}
 */
function createWindows() {
    const windows = [];
    const { width, height, depth } = BUILDING_CONFIG.dimensions;
    const { size, spacing, lightOnProbability } = BUILDING_CONFIG.window;

    const windowGeometry = new THREE.PlaneGeometry(size, size);

    // Window materials
    const windowMaterials = {
        on: new THREE.MeshStandardMaterial({
            color: 0x333355,
            emissive: 0x111122,
            emissiveIntensity: 0.6,
            side: THREE.DoubleSide
        }),
        off: new THREE.MeshStandardMaterial({
            color: 0x334455,
            emissive: 0x000000,
            side: THREE.DoubleSide
        })
    };

    // Generate window grid
    for (let y = 1; y < height - 0.5; y += spacing) {
        for (let x = -width / 2 + spacing; x < width / 2 - spacing; x += spacing) {
            const isLightOn = Math.random() > (1 - lightOnProbability);
            const material = isLightOn ? windowMaterials.on : windowMaterials.off;

            const window = new THREE.Mesh(windowGeometry, material);
            window.position.set(x, y, depth / 2 + 0.01);
            window.rotation.y = Math.PI;

            windows.push(window);
        }
    }

    return windows;
}

/**
 * Create video screen
 * @returns {VideoScreen}
 */
function createVideoScreen() {
    const { width, height } = BUILDING_CONFIG.screen;
    const { height: buildingHeight, depth } = BUILDING_CONFIG.dimensions;
    const { spacing } = BUILDING_CONFIG.window;

    const videoScreen = new VideoScreen(width, height, 'cjrok.webm');

    // Position the screen
    videoScreen.position.set(
        0,
        buildingHeight - spacing - height / 2,
        depth / 2 + 0.125
    );

    // Save reference for later updates
    screenContent = videoScreen;

    return videoScreen;
}

/**
 * Create building name text
 * @param {THREE.Font} font - font
 * @returns {THREE.Mesh}
 */
function createBuildingName(font) {
    const textGeometry = new THREE.TextGeometry('AI-SNS', {
        font: font,
        size: 0.2,
        height: 0.05,
        curveSegments: 12,
        bevelEnabled: false // Disable bevel to improve performance
    });

    textGeometry.computeBoundingBox();
    const textWidth = textGeometry.boundingBox.max.x - textGeometry.boundingBox.min.x;

    const textMaterial = new THREE.MeshBasicMaterial({
        color: new THREE.Color(20 / 255, 110 / 255, 190 / 255)
    });

    const textMesh = new THREE.Mesh(textGeometry, textMaterial);
    textMesh.position.set(
        -textWidth / 2,
        BUILDING_CONFIG.dimensions.height,
        BUILDING_CONFIG.dimensions.depth / 2 + 0.1
    );

    return textMesh;
}

// ===== Initialization =====
/**
 * Initialize building model
 */
const initializeBuilding = async () => {
    try {
        console.log('Loading building model...');

        const font = await loadFontWithRetry('js/helvetiker_bold.typeface.json');
        buildingGroup = createBuilding(font);

        console.log("AI-SNS building model initialized");

        // Update model load status
        if (typeof modelLoadStatus !== 'undefined') {
            modelLoadStatus.building = true;
            checkAnimationStart();
        }

    } catch (error) {
        console.error("Building model initialization failed:", error);
        // Error recovery logic can be added here
    }
};

// ===== Animation loop =====
/**
 * Optimized animation loop
 * @param {number} time - current timestamp
 */
function animate(time) {
    requestAnimationFrame(animate);

    // Check model load status
    if (typeof modelLoadStatus !== 'undefined' &&
        (!modelLoadStatus.building || !modelLoadStatus.house ||
         !modelLoadStatus.girl || !modelLoadStatus.boy)) {
        return;
    }

    const now = performance.now();

    // FPS limiting
    if (now - lastTime > PERFORMANCE_CONFIG.FRAME_INTERVAL) {
        // Update video screen
        if (screenContent && typeof screenContent.update === 'function') {
            screenContent.update();
        }

        lastTime = now;
    }

    // Update animation mixers
    if (typeof clock !== 'undefined' && typeof mixers !== 'undefined') {
        const delta = clock.getDelta();

        mixers.forEach(mixer => {
            if (mixer && typeof mixer.update === 'function') {
                mixer.update(delta);
            }
        });
    }

    // Request redraw
    if (typeof overlay !== 'undefined' && overlay.requestRedraw) {
        overlay.requestRedraw();
    }
}

// ===== Building loading =====
/**
 * Load building model into the scene
 */
function load_aisns_building() {
    if (!buildingGroup) {
        console.error("Building model not initialized");
        return;
    }

    try {
        const mesh = buildingGroup;
        mesh.scale.setScalar(60); // setScalar is more concise

        // Set building position
        const coordinates = {
            lng: BUILDING_CONFIG.position[0],
            lat: BUILDING_CONFIG.position[1],
        };

        if (typeof overlay !== 'undefined' && overlay.latLngAltitudeToVector3) {
            overlay.latLngAltitudeToVector3(coordinates, mesh.position);
            console.log("Building model position:", mesh.position);

            overlay.scene.add(mesh);
            console.log("AI-SNS building model added to scene");
        } else {
            console.error("Overlay object not defined or missing necessary method");
        }

    } catch (error) {
        console.error("Building model loading failed:", error);
    }
}

// ===== Resource cleanup =====
/**
 * Dispose building model resources
 */
function disposeBuildingResources() {
    if (screenContent && typeof screenContent.dispose === 'function') {
        screenContent.dispose();
    }

    if (buildingGroup) {
        buildingGroup.traverse((child) => {
            if (child.geometry) child.geometry.dispose();
            if (child.material) {
                if (Array.isArray(child.material)) {
                    child.material.forEach(material => material.dispose());
                } else {
                    child.material.dispose();
                }
            }
        });
    }
}

// ===== Window events =====
window.addEventListener('beforeunload', disposeBuildingResources);
window.addEventListener('resize', () => {
    renderer.setSize(window.innerWidth, window.innerHeight);
});

// ===== Start =====
initializeBuilding();
setTimeout(load_aisns_building, 6000);