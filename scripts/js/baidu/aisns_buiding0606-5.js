var buildingGroup;
let lastTime = 0;
const fontLoader = new THREE.FontLoader();
const renderer = new THREE.WebGLRenderer({antialias: true});
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
    createScreenContent(boardMaterial);

    return group;
}

function createScreenContentbak(material) {
    const canvas = document.createElement('canvas');
    canvas.width = 256;
    canvas.height = 128;
    const ctx = canvas.getContext('2d');

    const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
    gradient.addColorStop(0, '#1a4b8c');
    gradient.addColorStop(1, '#4a90e2');

    const scrollText = '高端广告 | 品牌展示 | 数字媒体 | Three.js 3D效果';
    ctx.font = 'bold 8px "Segoe UI", Arial, sans-serif';
    const textWidth = ctx.measureText(scrollText).width;

    function draw(time) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // 主标题
        ctx.font = 'bold 20px "Segoe UI", Arial, sans-serif';
        ctx.fillStyle = '#ffffff';
        ctx.textAlign = 'center';
        ctx.shadowColor = 'rgba(0,0,0,0.3)';
        ctx.shadowBlur = 10;
        ctx.fillText('广场播报', canvas.width / 2, 32);


        // 滚动文字
        const t = time * 0.001;
        const scrollX = (canvas.width + (t * 75) % (textWidth + canvas.width)) - textWidth;
        ctx.font = 'bold 28px Arial';
        ctx.fillStyle = 'Red';
        ctx.shadowColor = '#ff0000';
        ctx.shadowBlur = 0;

        ctx.fillText(scrollText, scrollX, 82);

        // 品牌标志
        ctx.beginPath();
        ctx.arc(canvas.width - 20, 20, 10, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(255, 255, 255, 0.15)';
        ctx.fill();

        ctx.font = 'bold 6px "Segoe UI", Arial, sans-serif';
        ctx.fillStyle = '#ffffff';
        ctx.textAlign = 'center';
        ctx.shadowBlur = 0;
        ctx.fillText('AI', canvas.width - 20, 22);
    }

    const texture = new THREE.CanvasTexture(canvas);
    texture.minFilter = THREE.LinearFilter;
    texture.anisotropy = renderer.capabilities.getMaxAnisotropy();

    material.map = texture;
    material.emissiveMap = texture;

    return {texture, draw};
}
alert("buidinggo");

function createScreenContent(material) {
    const canvas = document.createElement('canvas');
    canvas.width = 256;
    canvas.height = 128;
    const ctx = canvas.getContext('2d');
    const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
    gradient.addColorStop(0, '#1a4b8c');
    gradient.addColorStop(1, '#4a90e2');
    const scrollText = '高端广告 | 品牌展示 | 数字媒体 | Three.js 3D效果';
    ctx.font = 'bold 8px "Segoe UI", Arial, sans-serif';
    const textWidth = ctx.measureText(scrollText).width;
    function draw(time) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        // 主标题
        ctx.font = 'bold 20px "Segoe UI", Arial, sans-serif';
        ctx.fillStyle = '#000000';
        ctx.textAlign = 'center';
        ctx.shadowColor = 'rgba(0,0,0,0.3)';
        ctx.shadowBlur = 0;
        ctx.fillText('广场播报', canvas.width / 2, 32);
        // 滚动文字
        const t = time * 0.001;
        const scrollX = (canvas.width + (t * 75) % (textWidth + canvas.width)) - textWidth;
        ctx.font = 'bold 28px Arial';
        ctx.fillStyle = 'Red';
        ctx.shadowColor = '#ff0000';
        ctx.shadowBlur = 0;
        ctx.fillText(scrollText, scrollX, 82);
        // 品牌标志
        ctx.beginPath();
        ctx.arc(canvas.width - 20, 20, 10, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(255, 255, 255, 0.15)';
        ctx.fill();
        ctx.font = 'bold 6px "Segoe UI", Arial, sans-serif';
        ctx.fillStyle = '#ffffff';
        ctx.textAlign = 'center';
        ctx.shadowBlur = 0;
        ctx.fillText('AI', canvas.width - 20, 22);
    }
    const texture = new THREE.CanvasTexture(canvas);
    texture.minFilter = THREE.LinearFilter;
    texture.anisotropy = renderer.capabilities.getMaxAnisotropy();
    material.map = texture;
    material.emissiveMap = texture;
    return { texture, draw };
}


function animate_new(time) {
    requestAnimationFrame(animate_new);

    if (time - lastTime > 16) {
        if (buildingGroup) {
            const board = buildingGroup.children.find(child =>
                child instanceof THREE.Group &&
                child.children.some(mesh => mesh.material.emissiveMap)
            );
            if (board) {
                const material = board.children.find(mesh => mesh.material.emissiveMap).material;
                if (material.map && material.map.image) {
                    const ctx = material.map.image.getContext('2d');
                    if (ctx) {
                        const drawFunc = createScreenContent(material).draw;
                        drawFunc(time);
                        material.map.needsUpdate = true;
                    }
                }
            }
        }
        lastTime = time;
    }

    const delta = clock.getDelta();

    mixers.forEach(mixer => {
        if (mixer) mixer.update(delta);
    })

    threeLayer.update();


}

// 自定义坐标转换函数（替代 customCoords）
function convertCoords(pos) {
    // 您可能需要根据具体情况调整转换逻辑
    // 例如，使用地图实例提供的坐标转换方法

    let llPoint = new BMapGL.Point(pos[0], pos[1]);

    const mcpoint = BMapGL.Projection.convertLL2MC(llPoint);

    return mcpoint;
}

function load_aisns_building() {
    //添加3D覆盖物

    let building_model = null;

    var mesh = buildingGroup;  // 获取建筑模型组

    var mcpoint = convertCoords([121.44690152307729, 31.25875179971229]);

    // mesh.position.set(result[0].x, result[0].y, 0);  // 设置位置
    mesh.scale.set(40, 40, 40);  // 设置缩放

    mesh.rotation.x = Math.PI / 2;  // 旋转模型 (90度)

    mesh.rotation.y = 0;  // 旋转模型 (0度)

    let model = mesh;

    let geoGroup = new THREE.Group();
    geoGroup.add(model);

    geoGroup.position.set(mcpoint.lng, mcpoint.lat, 0);
    threeLayer.add(geoGroup);

    threeLayer.render();  // 手动触发渲染



}

setTimeout(load_aisns_building, 6000);



