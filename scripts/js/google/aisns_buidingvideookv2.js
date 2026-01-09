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
    FRAME_INTERVAL: 1000 / 60, // ~16.67ms
    FONT_RETRY_COUNT: 3,
    FONT_RETRY_DELAY: 1000
};
const building_position = [-122.36195286954631, 37.729593622423355];
// 建筑配置:
const BUILDING_CONFIG = {
    position: [-122.36195286954631, 37.729593622423355],
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

renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2)); // 限制像素比以提升性能
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap; // 更好的阴影质量
document.body.appendChild(renderer.domElement);

// ===== 工具类：VideoScreen =====
class VideoScreen extends THREE.Group {
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
     * 初始化视频元素
     * @private
     */
    _initializeVideo(videoSrc) {
        this.video = document.createElement('video');

        // 视频配置
        Object.assign(this.video, {
            src: videoSrc,
            loop: true,
            muted: true,
            autoplay: true,
            playsInline: true,
            preload: 'auto',
            crossOrigin: 'anonymous'
        });

        // 创建视频纹理
        this.videoTexture = new THREE.VideoTexture(this.video);
        this.videoTexture.minFilter = THREE.LinearFilter;
        this.videoTexture.magFilter = THREE.LinearFilter;
        this.videoTexture.format = THREE.RGBFormat;
        this.videoTexture.flipY = true; // 修复视频翻转问题

        // 处理视频播放
        this._handleVideoPlayback();
    }

    /**
     * 处理视频播放逻辑
     * @private
     */
    async _handleVideoPlayback() {
        try {
            // 等待视频元数据加载
            await new Promise((resolve, reject) => {
                this.video.addEventListener('loadedmetadata', resolve);
                this.video.addEventListener('error', reject);
                this.video.load();
            });

            // 尝试自动播放
            await this.video.play();
            console.log('视频自动播放成功');

        } catch (error) {
            console.warn('视频自动播放失败，等待用户交互:', error.message);

            // 添加用户交互监听器
            this._addUserInteractionListener();
        }
    }

    /**
     * 添加用户交互监听器以启动视频播放
     * @private
     */
    _addUserInteractionListener() {
        const playVideo = async () => {
            try {
                await this.video.play();
                console.log('用户交互后视频播放成功');
                document.removeEventListener('click', playVideo);
                document.removeEventListener('touchstart', playVideo);
            } catch (error) {
                console.error('用户交互后视频播放仍然失败:', error);
            }
        };

        document.addEventListener('click', playVideo, { once: true });
        document.addEventListener('touchstart', playVideo, { once: true });
    }

    /**
     * 创建屏幕
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

        this.border = new THREE.Mesh(borderGeometry, borderMaterial);
        this.border.position.z = -0.0375;
        this.add(this.border);
    }

    /**
     * 更新视频纹理（如果需要）
     */
    update() {
        // VideoTexture会自动更新，但保留此方法以保持接口一致性
        if (this.video && this.video.readyState >= this.video.HAVE_CURRENT_DATA) {
            this.videoTexture.needsUpdate = true;
        }
    }

    /**
     * 销毁资源
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
 * @param {number} retries - 重试次数
 * @param {number} delay - 重试延迟
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
            console.error(`字体加载失败 (尝试 ${attempt + 1}/${retries}):`, error.message);

            if (isLastAttempt) {
                throw new Error(`字体加载最终失败: ${url}`);
            }

            // 指数退避策略
            await new Promise(resolve => setTimeout(resolve, delay));
            delay *= 2;
        }
    }
};

// ===== 建筑创建函数 =====
/**
 * 创建建筑模型
 * @param {THREE.Font} font - 加载的字体
 * @returns {THREE.Group} 建筑组
 */
function createBuilding(font) {
    const group = new THREE.Group();
    console.log(1);

    // 创建主体建筑
    const building = createBuildingStructure();
    group.add(building);
console.log(12);
    // 创建窗户
    const windows = createWindows();
    windows.forEach(window => group.add(window));
console.log(13);
    // 创建视频屏幕（替代原来的广告牌）
    const videoScreen = createVideoScreen();
    group.add(videoScreen);
console.log(14);
    // 创建建筑名称
    const nameText = createBuildingName(font);
    group.add(nameText);
console.log(15);
    return group;
}

/**
 * 创建建筑主体结构
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
 * 创建窗户
 * @returns {THREE.Mesh[]}
 */
function createWindows() {
    const windows = [];
    const { width, height, depth } = BUILDING_CONFIG.dimensions;
    const { size, spacing, lightOnProbability } = BUILDING_CONFIG.window;

    const windowGeometry = new THREE.PlaneGeometry(size, size);

    // 窗户材质
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

    // 生成窗户网格
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
 * 创建视频屏幕
 * @returns {VideoScreen}
 */
function createVideoScreen() {
    const { width, height } = BUILDING_CONFIG.screen;
    const { height: buildingHeight, depth } = BUILDING_CONFIG.dimensions;
    const { spacing } = BUILDING_CONFIG.window;

    const videoScreen = new VideoScreen(width, height, 'cjrok.webm');

    // 定位屏幕
    videoScreen.position.set(
        0,
        buildingHeight - spacing - height / 2,
        depth / 2 + 0.125
    );

    // 保存引用以便后续更新
    screenContent = videoScreen;

    return videoScreen;
}

/**
 * 创建建筑名称文字
 * @param {THREE.Font} font - 字体
 * @returns {THREE.Mesh}
 */
function createBuildingName(font) {
    const textGeometry = new THREE.TextGeometry('AI-SNS', {
        font: font,
        size: 0.2,
        height: 0.05,
        curveSegments: 12,
        bevelEnabled: false // 禁用斜角以提升性能
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
/**
 * 初始化建筑模型
 */
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
        // 可以在这里添加错误恢复逻辑
    }
};

// ===== 动画循环 =====
/**
 * 优化的动画循环
 * @param {number} time - 当前时间戳
 */
function animate(time) {
    requestAnimationFrame(animate);

    // 检查模型加载状态
    if (typeof modelLoadStatus !== 'undefined' &&
        (!modelLoadStatus.building || !modelLoadStatus.house ||
         !modelLoadStatus.girl || !modelLoadStatus.boy)) {
        return;
    }

    const now = performance.now();

    // 帧率限制
    if (now - lastTime > PERFORMANCE_CONFIG.FRAME_INTERVAL) {
        // 更新视频屏幕
        if (screenContent && typeof screenContent.update === 'function') {
            screenContent.update();
        }

        lastTime = now;
    }

    // 更新动画混合器
    if (typeof clock !== 'undefined' && typeof mixers !== 'undefined') {
        const delta = clock.getDelta();

        mixers.forEach(mixer => {
            if (mixer && typeof mixer.update === 'function') {
                mixer.update(delta);
            }
        });
    }

    // 请求重绘
    if (typeof overlay !== 'undefined' && overlay.requestRedraw) {
        overlay.requestRedraw();
    }
}

// ===== 建筑加载函数 =====
/**
 * 将建筑模型加载到场景中
 */
function load_aisns_building() {
    if (!buildingGroup) {
        console.error("建筑模型未初始化");
        return;
    }

    try {
        const mesh = buildingGroup;
        mesh.scale.setScalar(60); // 使用setScalar更简洁

        // 设置建筑位置
        const coordinates = {
            lng: BUILDING_CONFIG.position[0],
            lat: BUILDING_CONFIG.position[1],
        };

        if (typeof overlay !== 'undefined' && overlay.latLngAltitudeToVector3) {
            overlay.latLngAltitudeToVector3(coordinates, mesh.position);
            console.log("建筑模型位置:", mesh.position);

            overlay.scene.add(mesh);
            console.log("AI-SNS建筑模型已添加到场景");
        } else {
            console.error("Overlay对象未定义或缺少必要方法");
        }

    } catch (error) {
        console.error("建筑模型加载失败:", error);
    }
}

// ===== 资源清理函数 =====
/**
 * 清理建筑模型资源
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

// ===== 窗口事件处理 =====
window.addEventListener('beforeunload', disposeBuildingResources);
window.addEventListener('resize', () => {
    renderer.setSize(window.innerWidth, window.innerHeight);
});

// ===== 启动初始化 =====
initializeBuilding();
