/**
 * AI-SNS 3D建筑模型渲染器
 * 优化版本 - 解决PyQt6 QWebEngineView视频自动播放问题
 */

// ==================== 全局常量配置 ====================
const CONFIG = {
    BUILDING_POSITION: [-122.36195286954631, 37.729593622423355],
    FONT_URL: 'js/helvetiker_bold.typeface.json',
    VIDEO_URL: 'BigBuckBunny.mp4',
    RETRY_CONFIG: {
        maxRetries: 3,
        baseDelay: 1000,
        backoffMultiplier: 2
    },
    PERFORMANCE: {
        targetFPS: 60,
        frameInterval: 16 // ~60FPS
    },
    BUILDING: {
        dimensions: { width: 2, height: 3.75, depth: 1.5 }, // height * 1.25
        window: { size: 0.15, spacing: 0.275 },
        billboard: { width: 1.75, height: 0.875, borderThickness: 0.05 }
    }
};

// ==================== 全局变量 ====================
let buildingGroup = null;
let screenContent = null;
let lastFrameTime = 0;
let isVideoPlaybackInitialized = false;

// ==================== Three.js 初始化 ====================
const fontLoader = new THREE.FontLoader();
const renderer = new THREE.WebGLRenderer({
    antialias: true,
    powerPreference: "high-performance" // 优化GPU使用
});

// 渲染器配置优化
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2)); // 限制像素比以提升性能
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap; // 更好的阴影质量
document.body.appendChild(renderer.domElement);

// ==================== 工具函数 ====================

/**
 * 带重试机制的字体加载器
 * @param {string} url - 字体文件URL
 * @param {number} retries - 重试次数
 * @param {number} delay - 初始延迟时间
 * @returns {Promise<THREE.Font>} 加载的字体对象
 */
const loadFontWithRetry = async (url, retries = CONFIG.RETRY_CONFIG.maxRetries, delay = CONFIG.RETRY_CONFIG.baseDelay) => {
    for (let attempt = 0; attempt < retries; attempt++) {
        try {
            return await new Promise((resolve, reject) => {
                fontLoader.load(
                    url,
                    resolve,
                    undefined, // onProgress callback
                    reject
                );
            });
        } catch (error) {
            console.error(`字体加载失败 (尝试 ${attempt + 1}/${retries}):`, error.message);

            if (attempt < retries - 1) {
                await new Promise(resolve => setTimeout(resolve, delay));
                delay *= CONFIG.RETRY_CONFIG.backoffMultiplier; // 指数退避
            } else {
                throw new Error(`字体加载最终失败: ${url}`);
            }
        }
    }
};

/**
 * 创建优化的视频内容 - 专门解决PyQt6自动播放问题
 * @param {THREE.MeshStandardMaterial} material - 要应用纹理的材质
 * @returns {Object} 视频内容对象
 */
function createVideoContent(material) {
    // 创建视频元素并设置所有必要属性
    const video = document.createElement('video');

    // 关键配置：确保在PyQt6环境中能够自动播放
    video.src = CONFIG.VIDEO_URL;
    video.loop = true;
    video.muted = true; // 必须静音才能自动播放
    video.autoplay = true;
    video.playsInline = true; // 防止全屏播放
    video.preload = 'auto';
    video.crossOrigin = 'anonymous'; // 处理跨域问题

    // PyQt6特定设置
    video.setAttribute('webkit-playsinline', 'true'); // WebKit兼容性
    video.setAttribute('playsinline', 'true');
    video.setAttribute('autoplay', 'true');
    video.setAttribute('muted', 'true');

    // 创建优化的视频纹理
    const texture = new THREE.VideoTexture(video);
    texture.minFilter = THREE.LinearFilter;
    texture.magFilter = THREE.LinearFilter;
    texture.format = THREE.RGBFormat;
    texture.generateMipmaps = false; // 视频纹理不需要mipmap
    texture.flipY = false; // 优化视频纹理性能

    // 多重播放策略：处理不同环境的播放限制
    const initializeVideoPlayback = async () => {
        if (isVideoPlaybackInitialized) return;

        try {
            // 策略1：直接播放
            await video.play();
            isVideoPlaybackInitialized = true;
            console.log('视频自动播放成功');
        } catch (error) {
            console.warn('自动播放失败，设置用户交互触发:', error.message);

            // 策略2：用户交互触发（一次性）
            const playOnInteraction = async () => {
                try {
                    await video.play();
                    isVideoPlaybackInitialized = true;
                    console.log('用户交互触发播放成功');
                } catch (e) {
                    console.error('用户交互播放失败:', e);
                }
            };

            // 监听多种用户交互事件
            const interactionEvents = ['click', 'touchstart', 'keydown', 'mousemove'];
            const cleanup = () => {
                interactionEvents.forEach(event =>
                    document.removeEventListener(event, playOnInteraction)
                );
            };

            interactionEvents.forEach(event => {
                document.addEventListener(event, () => {
                    playOnInteraction();
                    cleanup();
                }, { once: true, passive: true });
            });
        }
    };

    // 视频加载完成后初始化播放
    video.addEventListener('loadeddata', initializeVideoPlayback, { once: true });
    video.addEventListener('canplay', initializeVideoPlayback, { once: true });

    // 错误处理
    video.addEventListener('error', (e) => {
        console.error('视频加载错误:', e);
    });

    // 应用纹理到材质
    material.map = texture;
    material.emissiveMap = texture;
    material.needsUpdate = true;

    return {
        texture,
        video,
        /**
         * 绘制函数 - 保持接口一致性
         */
        draw() {
            // 视频纹理自动更新，但我们可以在这里添加额外的逻辑
            if (video.readyState >= 2 && !video.paused) {
                texture.needsUpdate = true;
            }
        },

        /**
         * 手动触发播放
         */
        async forcePlay() {
            if (!isVideoPlaybackInitialized && video.paused) {
                try {
                    await video.play();
                    isVideoPlaybackInitialized = true;
                } catch (error) {
                    console.error('强制播放失败:', error);
                }
            }
        }
    };
}

/**
 * 创建建筑模型
 * @param {THREE.Font} font - 加载的字体对象
 * @returns {THREE.Group} 建筑模型组
 */
function createBuilding(font) {
    const group = new THREE.Group();
    const { dimensions, window: windowConfig, billboard } = CONFIG.BUILDING;

    // ==================== 主建筑体 ====================
    const buildingGeometry = new THREE.BoxGeometry(
        dimensions.width,
        dimensions.height,
        dimensions.depth
    );

    const buildingMaterial = new THREE.MeshStandardMaterial({
        color: 0xe0e0e0,
        roughness: 0.5,
        metalness: 0.1
    });

    const building = new THREE.Mesh(buildingGeometry, buildingMaterial);
    building.position.y = dimensions.height / 2;
    building.castShadow = true;
    building.receiveShadow = true;
    group.add(building);

    // ==================== 窗户系统 ====================
    const windowGeometry = new THREE.PlaneGeometry(windowConfig.size, windowConfig.size);

    // 预创建材质以提升性能
    const windowMaterials = {
        on: new THREE.MeshStandardMaterial({
            color: 0x333355,
            emissive: 0x111133,
            emissiveIntensity: 0.6,
            side: THREE.DoubleSide
        }),
        off: new THREE.MeshStandardMaterial({
            color: 0x334455,
            emissive: 0x000000,
            side: THREE.DoubleSide
        })
    };

    // 批量创建窗户
    for (let y = 1; y < dimensions.height - 0.5; y += windowConfig.spacing) {
        for (let x = -dimensions.width / 2 + windowConfig.spacing;
             x < dimensions.width / 2 - windowConfig.spacing;
             x += windowConfig.spacing) {

            const isLightOn = Math.random() > 0.4;
            const windowMesh = new THREE.Mesh(
                windowGeometry,
                isLightOn ? windowMaterials.on : windowMaterials.off
            );

            windowMesh.position.set(x, y, dimensions.depth / 2 + 0.01);
            windowMesh.rotation.y = Math.PI;
            group.add(windowMesh);
        }
    }

    // ==================== 广告牌系统 ====================
    const boardGroup = new THREE.Group();

    // 主广告牌
    const boardGeometry = new THREE.BoxGeometry(billboard.width, billboard.height, 0.075);
    const boardMaterial = new THREE.MeshStandardMaterial({
        color: 0xffffff,
        emissive: 0xffffff,
        emissiveIntensity: 1.0
    });
    const board = new THREE.Mesh(boardGeometry, boardMaterial);

    // 边框
    const borderGeometry = new THREE.BoxGeometry(
        billboard.width + billboard.borderThickness,
        billboard.height + billboard.borderThickness,
        0.025
    );
    const borderMaterial = new THREE.MeshStandardMaterial({ color: 0x333333 });
    const border = new THREE.Mesh(borderGeometry, borderMaterial);
    border.position.z = -0.0375;

    boardGroup.add(border);
    boardGroup.add(board);
    boardGroup.position.set(
        0,
        dimensions.height - windowConfig.spacing - billboard.height / 2,
        dimensions.depth / 2 + 0.125
    );
    group.add(boardGroup);

    // ==================== 建筑名称 ====================
    const nameGeometry = new THREE.TextGeometry('AI-SNS', {
        font: font,
        size: 0.2,
        height: 0.05,
        curveSegments: 12,
        bevelEnabled: false // 禁用斜角以提升性能
    });

    nameGeometry.computeBoundingBox();
    const nameWidth = nameGeometry.boundingBox.max.x - nameGeometry.boundingBox.min.x;

    const nameMaterial = new THREE.MeshBasicMaterial({
        color: new THREE.Color(20/255, 110/255, 190/255)
    });

    const nameMesh = new THREE.Mesh(nameGeometry, nameMaterial);
    nameMesh.position.set(
        -nameWidth / 2,
        dimensions.height,
        dimensions.depth / 2 + 0.1
    );
    group.add(nameMesh);

    // ==================== 视频内容初始化 ====================
    screenContent = createVideoContent(boardMaterial);

    return group;
}

/**
 * 异步初始化建筑模型
 */
const initializeBuilding = async () => {
    try {
        console.log('开始初始化AI-SNS建筑模型...');

        const font = await loadFontWithRetry(CONFIG.FONT_URL);
        buildingGroup = createBuilding(font);

        console.log('AI-SNS建筑模型初始化完成');

        // 如果存在全局状态管理，更新状态
        if (typeof modelLoadStatus !== 'undefined') {
            modelLoadStatus.building = true;
            if (typeof checkAnimationStart === 'function') {
                checkAnimationStart();
            }
        }

    } catch (error) {
        console.error('建筑模型初始化失败:', error);
        throw error; // 重新抛出错误以便上层处理
    }
};

/**
 * 优化的动画循环
 * @param {number} time - 当前时间戳
 */
function animate(time) {
    requestAnimationFrame(animate);

    // 性能优化：检查模型加载状态
    if (typeof modelLoadStatus !== 'undefined') {
        if (!modelLoadStatus.building || !modelLoadStatus.house ||
            !modelLoadStatus.girl || !modelLoadStatus.boy) {
            return;
        }
    }

    const currentTime = performance.now();

    // 帧率限制：维持稳定的60FPS
    if (currentTime - lastFrameTime > CONFIG.PERFORMANCE.frameInterval) {
        // 更新视频内容
        if (screenContent) {
            screenContent.draw();
        }

        lastFrameTime = currentTime;
    }

    // 动画混合器更新（如果存在）
    if (typeof clock !== 'undefined' && typeof mixers !== 'undefined' && mixers.length > 0) {
        const delta = clock.getDelta();
        mixers.forEach(mixer => {
            if (mixer && typeof mixer.update === 'function') {
                mixer.update(delta);
            }
        });
    }

    // 重绘覆盖层（如果存在）
    if (typeof overlay !== 'undefined' && overlay.requestRedraw) {
        overlay.requestRedraw();
    }
}

/**
 * 加载并放置AI-SNS建筑到场景中
 */
function load_aisns_building() {
    if (!buildingGroup) {
        console.error('建筑模型未初始化，请先调用 initializeBuilding()');
        return false;
    }

    if (typeof overlay === 'undefined') {
        console.error('Overlay对象未定义');
        return false;
    }

    try {
        // 设置模型缩放
        buildingGroup.scale.setScalar(60);

        // 计算世界坐标位置
        const coordinates = {
            lng: CONFIG.BUILDING_POSITION[0],
            lat: CONFIG.BUILDING_POSITION[1]
        };

        const position = overlay.latLngAltitudeToVector3(coordinates, buildingGroup.position);
        console.log('建筑模型世界坐标:', position);

        // 添加到场景
        overlay.scene.add(buildingGroup);
        console.log('AI-SNS建筑模型已成功添加到场景');

        // 设置全局点击事件作为视频播放的最终后备方案
        setupGlobalVideoPlaybackFallback();

        return true;

    } catch (error) {
        console.error('建筑模型加载到场景失败:', error);
        return false;
    }
}

/**
 * 设置全局视频播放后备方案
 */
function setupGlobalVideoPlaybackFallback() {
    const globalPlaybackHandler = async () => {
        if (screenContent?.video?.paused && !isVideoPlaybackInitialized) {
            try {
                await screenContent.forcePlay();
                console.log('全局后备播放成功');
            } catch (error) {
                console.error('全局后备播放失败:', error);
            }
        }
    };

    // 添加一次性全局点击监听器
    document.addEventListener('click', globalPlaybackHandler, {
        once: true,
        passive: true
    });
}

/**
 * 公共API：手动触发视频播放
 */
function triggerVideoPlayback() {
    if (screenContent) {
        return screenContent.forcePlay();
    }
    return Promise.reject(new Error('视频内容未初始化'));
}

// ==================== 模块导出（如果使用模块系统） ====================
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initializeBuilding,
        load_aisns_building,
        triggerVideoPlayback,
        animate
    };
}

// ==================== 自动初始化 ====================
// 启动建筑模型初始化
initializeBuilding().catch(error => {
    console.error('建筑模型自动初始化失败:', error);
});
