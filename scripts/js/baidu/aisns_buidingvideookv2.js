/**
 * 建筑模型管理器 - 集成视频屏幕功能
 * 优化了性能、错误处理和代码结构
 */

// ===== 全局变量和配置 =====
let buildingGroup = null;
let screenContent = null;
let lastTime = 0;

// 性能配置
const PERFORMANCE_CONFIG = {
    TARGET_FPS: 60,
    FRAME_INTERVAL: 1000 / 60 // ~16.67ms
};

const building_position = [121.51810835402695, 31.34035307935309];

// 建筑配置:
const BUILDING_CONFIG = {
    position: [121.51810835402695, 31.34035307935309],
    dimensions: {
        width: 2,
        height: 3 * 1.25, // 增加25%高度
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

// 渲染器初始化
const renderer = new THREE.WebGLRenderer({
    antialias: true,
    alpha: true,
    powerPreference: "high-performance"
});

renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

// ===== 工具类：VideoScreen =====
class VideoScreen extends THREE.Group {
    constructor(width, height, videoSrc) {
        super();

        this.width = width;
        this.height = height;
        this.videoTexture = new THREE.VideoTexture(this._createVideoElement(videoSrc));
        this._createScreen();
        this._createFrame();
    }

    /**
     * 初始化视频元素
     * @private
     * @param {string} videoSrc - 视频源
     * @returns {HTMLVideoElement} - 视频元素
     */
    _createVideoElement(videoSrc) {
        const video = document.createElement('video');
        Object.assign(video, {
            src: videoSrc,
            loop: true,
            muted: false,
            autoplay: true,
            playsInline: true,
            preload: 'auto',
            crossOrigin: 'anonymous'
        });

        video.addEventListener('canplay', () => {
            video.play().catch(error => {
                console.warn('视频播放失败，等待用户交互:', error.message);
                document.addEventListener('click', () => video.play().catch(e => console.error('用户交互后视频播放仍然失败:', e)), { once: true });
                document.addEventListener('touchstart', () => video.play().catch(e => console.error('用户交互后视频播放仍然失败:', e)), { once: true });
            });
        });

        return video;
    }

    /**
     * 创建屏幕
     * @private
     */
    _createScreen() {
        const screenGeometry = new THREE.PlaneGeometry(this.width, this.height);
        const screenMaterial = new THREE.MeshBasicMaterial({
            map: this.videoTexture,
            side: THREE.FrontSide
        });

        const screen = new THREE.Mesh(screenGeometry, screenMaterial);
        this.add(screen);
    }

    /**
     * 创建屏幕边框
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

        const border = new THREE.Mesh(borderGeometry, borderMaterial);
        border.position.z = -0.0375;
        this.add(border);
    }

    /**
     * 更新视频纹理（如果需要）
     */
    update() {
        this.videoTexture.needsUpdate = true;
    }

    /**
     * 销毁资源
     */
    dispose() {
        // 清理几何体和材质
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

// ===== 字体加载器 =====
const fontLoader = new THREE.FontLoader();

/**
 * 带重试机制的字体加载器
 * @param {string} url - 字体文件URL
 * @returns {Promise<THREE.Font>}
 */
const loadFontWithRetry = async (url) => {
    const retries = 3;
    const delay = 1000;
    for (let attempt = 0; attempt < retries; attempt++) {
        try {
            return await new Promise((resolve, reject) => {
                fontLoader.load(
                    url,
                    resolve,
                    undefined,
                    reject
                );
            });
        } catch (error) {
            console.error(`字体加载失败 (尝试 ${attempt + 1}/${retries}):`, error.message);
            if (attempt === retries - 1) throw new Error(`字体加载最终失败: ${url}`);
            await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, attempt)));
        }
    }
};

// ===== 建筑创建函数 =====
function createBuilding(font) {
    const group = new THREE.Group();
    group.add(createBuildingStructure());
    createWindows().forEach(window => group.add(window));
    const videoScreen = createVideoScreen();
    group.add(videoScreen);
    group.add(createBuildingName(font));

    screenContent = videoScreen; // 保存引用以便后续更新

    return group;
}

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

function createWindows() {
    const windows = [];
    const { width, height, depth } = BUILDING_CONFIG.dimensions;
    const { size, spacing, lightOnProbability } = BUILDING_CONFIG.window;
    const windowGeometry = new THREE.PlaneGeometry(size, size);

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

    for (let y = 1; y < height - 0.5; y += spacing) {
        for (let x = -width / 2 + spacing; x < width / 2 - spacing; x += spacing) {
            const material = Math.random() > (1 - lightOnProbability) ? windowMaterials.on : windowMaterials.off;
            const window = new THREE.Mesh(windowGeometry, material);
            window.position.set(x, y, depth / 2 + 0.01);
            window.rotation.y = Math.PI;
            windows.push(window);
        }
    }

    return windows;
}

function createVideoScreen() {
    const { width, height } = BUILDING_CONFIG.screen;
    const { height: buildingHeight, depth } = BUILDING_CONFIG.dimensions;
    const { spacing } = BUILDING_CONFIG.window;

    const videoScreen = new VideoScreen(width, height, 'cjrok2.webm');
    videoScreen.position.set(0, buildingHeight - spacing - height / 2, depth / 2 + 0.125);

    return videoScreen;
}

function createBuildingName(font) {
    const textGeometry = new THREE.TextGeometry('AI-SNS', {
        font: font,
        size: 0.2,
        height: 0.05,
        curveSegments: 12,
        bevelEnabled: false
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

// ===== 初始化函数 =====
const initializeBuilding = async () => {
    try {
        console.log('开始加载建筑模型...');
        const font = await loadFontWithRetry('js/helvetiker_bold.typeface.json');
        buildingGroup = createBuilding(font);
        console.log("AI-SNS建筑模型初始化完成");
        // 更新模型加载状态
        if (typeof modelLoadStatus !== 'undefined') {
            modelLoadStatus.building = true;
            checkAnimationStart();
        }
    } catch (error) {
        console.error("建筑模型初始化失败:", error);
    }
};

// ===== 动画循环 =====
function animatebak(time) {
    requestAnimationFrame(animate);

    const now = performance.now();
    if (now - lastTime > PERFORMANCE_CONFIG.FRAME_INTERVAL) {
        if (screenContent) {
            screenContent.update();
        }
        lastTime = now;
    }

    if (typeof clock !== 'undefined' && typeof mixers !== 'undefined') {
        const delta = clock.getDelta();
        mixers.forEach(mixer => mixer.update(delta));
    }

    if (typeof threeLayer !== 'undefined') {
        threeLayer.update();
    }
}

function animate(time) {
    // alert("in ani");
    requestAnimationFrame(animate);

    const now = performance.now();

    if (now - lastTime > 16) { // 限制到~60FPS
        if (screenContent) {
            screenContent.update();
        }
        lastTime = now;
    }

    const delta = clock.getDelta();

    mixers.forEach(mixer => {
        if (mixer) mixer.update(delta);
    })

    threeLayer.update();


}


// ===== 建筑加载函数 =====
function load_aisns_building() {
    if (!buildingGroup) {
        console.error("建筑模型未初始化");
        return;
    }

    try {
        const mesh = buildingGroup;
        const mcpoint = convertCoords(building_position);
        mesh.scale.set(20, 20, 20);
        mesh.rotation.set(Math.PI / 2, Math.PI / 2, 0);

        const geoGroup = new THREE.Group();
        geoGroup.add(mesh);
        geoGroup.position.set(mcpoint.lng, mcpoint.lat, 0);
        if (typeof threeLayer !== 'undefined') {
            threeLayer.add(geoGroup);
            threeLayer.render();
        }

    } catch (error) {
        console.error("建筑模型加载失败:", error);
    }
}

// ===== 资源清理函数 =====
function disposeBuildingResources() {
    if (screenContent) screenContent.dispose();
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

// ===== 窗口事件处理 =====
window.addEventListener('beforeunload', disposeBuildingResources);
window.addEventListener('resize', () => {
    renderer.setSize(window.innerWidth, window.innerHeight);
});

// 启动初始化
initializeBuilding();

//todo
setTimeout(load_aisns_building, 6000);
//todo
function convertCoords(pos) {
    const llPoint = new BMapGL.Point(pos[0], pos[1]);
    return BMapGL.Projection.convertLL2MC(llPoint);
}
