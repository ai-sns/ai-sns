var buildingGroup;
let screenContent = null;
let lastTime = 0;
const fontLoader = new THREE.FontLoader();
const renderer = new THREE.WebGLRenderer({ antialias: true });
const building_position = [-122.36195286954631, 37.729593622423355];
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
document.body.appendChild(renderer.domElement);
const loadFontWithRetry = async (url, retries = 3, delay = 1000) => {
    for (let i = 0; i < retries; i++) {
        try {
            return await new Promise((resolve, reject) => {
                fontLoader.load(url, resolve, undefined, reject);
            });
        } catch (error) {
            console.error(`字体加载失败 (尝试 ${i + 1}/${retries}): ${error.message}`);
            if (i < retries - 1) {
                await new Promise(r => setTimeout(r, delay));
                delay *= 2; // 指数退避
            } else {
                throw new Error(`字体加载失败: ${url}`);
            }
        }
    }
};
const initializeBuilding = async () => {
    try {
        const font = await loadFontWithRetry('js/helvetiker_bold.typeface.json');
        buildingGroup = createBuilding(font);
        console.log("AI-SNS建筑模型初始化完成");
        modelLoadStatus.building = true;
        checkAnimationStart();
    } catch (error) {
        console.error("建筑模型初始化失败:", error);
    }
};
initializeBuilding();
function createBuilding(font) {
    const group = new THREE.Group();
    // 大厦主体
    const buildingWidth = 2;
    const buildingHeight = 3 * 1.25; // 高度增加四分之一
    const buildingDepth = 1.5;
    const buildingGeometry = new THREE.BoxGeometry(buildingWidth, buildingHeight, buildingDepth);
    const buildingMaterial = new THREE.MeshStandardMaterial({
        color: 0xe0e0e0,
        roughness: 0.5,
        metalness: 0.1
    });
    const building = new THREE.Mesh(buildingGeometry, buildingMaterial);
    building.position.y = buildingHeight / 2;
    group.add(building);
    // 窗户
    const windowSize = 0.15;
    const windowSpacing = 0.275;
    const windowGeometry = new THREE.PlaneGeometry(windowSize, windowSize);
    const windowMaterialOn = new THREE.MeshStandardMaterial({
        color: 0x333355,
        emissive: 0x000000,
        emissiveIntensity: 0.6,
        side: THREE.DoubleSide
    });
    const windowMaterialOff = new THREE.MeshStandardMaterial({
        color: 0x334455,
        emissive: 0x000000,
        side: THREE.DoubleSide
    });
    for (let y = 1; y < buildingHeight - 0.5; y += windowSpacing) {
        for (let x = -buildingWidth / 2 + windowSpacing; x < buildingWidth / 2 - windowSpacing; x += windowSpacing) {
            const isLightOn = Math.random() > 0.4;
            const windowMesh = new THREE.Mesh(
                windowGeometry,
                isLightOn ? windowMaterialOn : windowMaterialOff
            );
            windowMesh.position.set(x, y, buildingDepth / 2 + 0.01);
            windowMesh.rotation.y = Math.PI;
            group.add(windowMesh);
        }
    }
    // 广告牌
    const boardWidth = 1.75;
    const boardHeight = 0.875;
    const borderThickness = 0.05;
    const boardGroup = new THREE.Group();
    const boardGeometry = new THREE.BoxGeometry(boardWidth, boardHeight, 0.075);
    const boardMaterial = new THREE.MeshStandardMaterial({
        color: 0xffffff,
        emissive: 0xffffff,
        emissiveIntensity: 1.0
    });
    const board = new THREE.Mesh(boardGeometry, boardMaterial);
    const borderGeometry = new THREE.BoxGeometry(
        boardWidth + borderThickness,
        boardHeight + borderThickness,
        0.025
    );
    const borderMaterial = new THREE.MeshStandardMaterial({ color: 0x333333 });
    const border = new THREE.Mesh(borderGeometry, borderMaterial);
    border.position.z = -0.0375;
    boardGroup.add(border);
    boardGroup.add(board);
    boardGroup.position.set(
        0,
        buildingHeight - windowSpacing - boardHeight / 2,
        buildingDepth / 2 + 0.125
    );
    group.add(boardGroup);
    // 大厦名称
    const nameGeometry = new THREE.TextGeometry('AI-SNS', {
        font: font,
        size: 0.2,
        height: 0.05,
        curveSegments: 12
    });
    nameGeometry.computeBoundingBox();
    const nameWidth = nameGeometry.boundingBox.max.x - nameGeometry.boundingBox.min.x;
    const nameMaterial = new THREE.MeshBasicMaterial({ color: new THREE.Color(20 / 255, 110 / 255, 190 / 255) });
    const nameMesh = new THREE.Mesh(nameGeometry, nameMaterial);
    nameMesh.position.set(-nameWidth / 2, buildingHeight, buildingDepth / 2 + 0.1);
    nameMesh.rotation.y = 0;
    group.add(nameMesh);
    // 创建视频内容（替代滚动文字）
    screenContent = createVideoContent(boardMaterial);
    return group;
}
function createVideoContent(material) {
    // 创建视频元素
    const video = document.createElement('video');
    video.src = 'BigBuckBunny.mp4'; // 替换为实际视频路径
    video.loop = true;
    video.muted = true; // 静音以允许自动播放
    video.autoplay = true;
    video.playsInline = true; // 在移动端内联播放
    video.preload = 'auto';
    // 创建视频纹理
    const texture = new THREE.VideoTexture(video);
    texture.minFilter = THREE.LinearFilter;
    texture.magFilter = THREE.LinearFilter;
    texture.format = THREE.RGBFormat;
    // 尝试播放视频
    const playPromise = video.play();
    if (playPromise !== undefined) {
        playPromise.catch(error => {
            console.error('视频播放失败:', error);
            // 播放失败处理：添加点击事件触发播放
            document.addEventListener('click', () => {
                video.play().catch(e => console.error('点击后播放失败:', e));
            }, { once: true });
        });
    }
    // 将纹理应用到材质
    material.map = texture;
    material.emissiveMap = texture;
    return {
        texture,
        video,
        draw: () => {
            // 视频纹理会自动更新，无需额外操作
            // 保留此函数以保持接口一致性
        }
    };
}
function animate(time) {
    requestAnimationFrame(animate);
    // 安全检查：确保所有模型已加载
    if (!modelLoadStatus.building || !modelLoadStatus.house ||
        !modelLoadStatus.girl || !modelLoadStatus.boy) {
        return;
    }
    const now = performance.now();
    if (now - lastTime > 16) { // 限制到~60FPS
        if (screenContent) {
            screenContent.draw();
        }
        lastTime = now;
    }
    const delta = clock.getDelta();
    // 安全更新动画混合器
    if (mixers.length > 0) {
        mixers.forEach(mixer => {
            if (mixer && typeof mixer.update === 'function') {
                mixer.update(delta);
            }
        });
    }
    overlay.requestRedraw();
}
function load_aisns_building() {
    if (!buildingGroup) {
        console.error("建筑模型未初始化");
        return;
    }
    const mesh = buildingGroup;
    mesh.scale.set(60, 60, 60);
    const coordinates = {
        lng: building_position[0],
        lat: building_position[1],
    };
    const position = overlay.latLngAltitudeToVector3(coordinates, mesh.position);
    console.log("建筑模型位置:", position);
    overlay.scene.add(mesh);
    console.log("AI-SNS建筑模型已添加到场景");
    // 添加点击事件作为视频播放的后备方案
    document.addEventListener('click', () => {
        if (screenContent?.video?.paused) {
            screenContent.video.play().catch(e => console.error('视频播放失败:', e));
        }
    }, { once: true });
}
