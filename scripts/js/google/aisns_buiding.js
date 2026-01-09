var buildingGroup;
let screenContent = null;
let lastTime = 0;
const fontLoader = new THREE.FontLoader();
const renderer = new THREE.WebGLRenderer({antialias: true});
const building_position = [-122.36195286954631,37.729593622423355]
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
            console.error(`字体加载失败 (尝试 ${i+1}/${retries}): ${error.message}`);
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
    const borderMaterial = new THREE.MeshStandardMaterial({color: 0x333333});
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

    // 大厦名称 - 修正位置和朝向
    const nameGeometry = new THREE.TextGeometry('AI-SNS', {
        font: font,
        size: 0.2,
        height: 0.05,
        curveSegments: 12
    });
    // 计算文字宽度使其居中
    nameGeometry.computeBoundingBox();
    const nameWidth = nameGeometry.boundingBox.max.x - nameGeometry.boundingBox.min.x;

    const nameMaterial = new THREE.MeshBasicMaterial({color: new THREE.Color(20 / 255, 110 / 255, 190 / 255)});
    const nameMesh = new THREE.Mesh(nameGeometry, nameMaterial);
    // 位置调整：x居中(减去文字宽度一半)，y位置=大厦高度+文字高度/2(使底部贴紧)
    nameMesh.position.set(-nameWidth / 2, buildingHeight, buildingDepth / 2 + 0.1);
    nameMesh.rotation.y = 0;
    group.add(nameMesh);

    // 创建屏幕内容
    screenContent = createScreenContent(boardMaterial);

    return group;
}

function createScreenContent(material) {
    const canvas = document.createElement('canvas');
    canvas.width = 256;
    canvas.height = 128;
    const ctx = canvas.getContext('2d');

    // 预计算静态资源
    const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
    gradient.addColorStop(0, '#1a4b8c');
    gradient.addColorStop(1, '#4a90e2');

    const scrollText = '高端广告 | 品牌展示 | 数字媒体 | Three.js 3D效果';
    const textMetrics = ctx.measureText(scrollText);
    const textWidth = textMetrics.width;

    // 缓存静态绘制操作
    const drawStaticContent = () => {
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // 主标题
        ctx.font = 'bold 20px "Segoe UI", Arial, sans-serif';
        ctx.fillStyle = '#000000';
        ctx.textAlign = 'center';
        ctx.fillText('广场播报', canvas.width / 2, 32);

        // 品牌标志
        ctx.beginPath();
        ctx.arc(canvas.width - 20, 20, 10, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(255, 255, 255, 0.15)';
        ctx.fill();
        ctx.font = 'bold 6px "Segoe UI", Arial, sans-serif';
        ctx.fillStyle = '#ffffff';
        ctx.textAlign = 'center';
        ctx.fillText('AI', canvas.width - 20, 22);
    };

    // 初始绘制静态内容
    drawStaticContent();

    // 滚动文本专用canvas（离屏渲染）
    const textCanvas = document.createElement('canvas');
    textCanvas.width = textWidth + canvas.width; // 额外空间用于平滑滚动
    textCanvas.height = 30; // 仅需要文本高度
    const textCtx = textCanvas.getContext('2d');
    textCtx.font = 'bold 28px Arial';
    textCtx.fillStyle = 'Red';
    textCtx.fillText(scrollText, 0, 25);
    const texture = new THREE.CanvasTexture(canvas);
    texture.minFilter = THREE.LinearFilter;
    texture.anisotropy = renderer.capabilities.getMaxAnisotropy();
    material.map = texture;
    material.emissiveMap = texture;

    return {
    texture,
    draw: (time) => {
        const t = time * 0.001;
        const scrollX = (t * 75) % (textWidth + canvas.width) - textWidth;

        // 1. 清除文字区域
        ctx.clearRect(0, 50, canvas.width, 50);

        // 2. 重绘文字区域背景渐变
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 50, canvas.width, 50);

        // 3. 绘制滚动文字
        ctx.drawImage(
            textCanvas,
            Math.max(0, -scrollX),
            0,
            Math.min(textCanvas.width, canvas.width - scrollX),
            30,
            Math.max(0, scrollX),
            52,
            Math.min(textCanvas.width, canvas.width - scrollX),
            30
        );

        texture.needsUpdate = true;
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
            screenContent.draw(now);
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
    var mesh = buildingGroup;
    mesh.scale.set(60, 60, 60);
    const coordinates = {
        lng: building_position[0],
        lat: building_position[1],
    };
    const position = overlay.latLngAltitudeToVector3(coordinates, mesh.position);
    console.log("建筑模型位置:", position);
    overlay.scene.add(mesh);
    console.log("AI-SNS建筑模型已添加到场景");

    // 在其他模型加载函数中设置状态
    // 例如在loadHouse成功时: modelLoadStatus.house = true;
}

