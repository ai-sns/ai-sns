if (!map) throw new Error('百度地图实例未初始化');

// 图层管理器
const layerManager = {
    groundOverlay: null,
    threeLayers: new Map(),
    overlays: [],
    views: new Map()  // 存储mapvgl.View实例
};

/* 1. 地面覆盖物初始化 */
function initGroundOverlay() {
    const pStart = new BMapGL.Point(116.22971, 39.74441);
    const pEnd = new BMapGL.Point(116.25646, 39.76812);
    const bounds = new BMapGL.Bounds(
        new BMapGL.Point(Math.min(pStart.lng, pEnd.lng), Math.min(pStart.lat, pEnd.lat)),
        new BMapGL.Point(Math.max(pStart.lng, pEnd.lng), Math.max(pStart.lat, pEnd.lat))
    );
    layerManager.groundOverlay = new BMapGL.GroundOverlay(bounds, {
        type: 'image',
        url: 'shouhuimap.png',
        opacity: 1
    });
    map.addOverlay(layerManager.groundOverlay);
    layerManager.overlays.push(layerManager.groundOverlay);
}

/* 2. 3D模型配置中心化 */
let modelConfigs;

function initModelConfigs() {
    modelConfigs = [
        {
            id: 'mainModel',
            layerId: 'mainLayer',
            position: [116.36200604013413, 39.94527332861826],
            modelUrl: 'https://cdn.jsdelivr.net/gh/photonchen/photonchen.github.io/aisnsbuilding.glb',
            scale: 0.4,
            rotation: {x: Math.PI / 2}
        },
        {
            id: 'houseModel',
            layerId: 'mainLayer',
            position: home_position ? [home_position.lng, home_position.lat] : [121.51246021573293, 31.304969368085807],//todo
            modelUrl: 'house_red.glb',
            scale: 2,
            rotation: {x: Math.PI / 2, y: Math.PI / 10}
        },
        {
            id: 'playerModel',
            layerId: 'mainLayer',
            position: [116.30391532368695, 40.04931576869293],
            modelUrl: 'https://cdn.jsdelivr.net/gh/photonchen/photonchen.github.io/playergirl.glb',
            scale: 150,
            rotation: {x: Math.PI / 2}
        },
        {
            id: 'officeModel',
            layerId: 'mainLayer',
            position: [116.30873909340876, 40.063344012305905],
            modelUrl: 'https://cdn.jsdelivr.net/gh/photonchen/photonchen.github.io/officebuilding.glb',
            scale: 5,
            rotation: {x: Math.PI / 2}
        },
        {
            id: 'centerModel',
            layerId: 'mainLayer',
            position: [116.20683342989894, 39.96289480301391],
            modelUrl: 'http://www.ai-sns.cc/aigccentermap.glb',
            scale: 0.1,
            rotation: {x: Math.PI / 2}
        }
    ];
}

/* 3. 复用模型加载器 */
const facility_gltfLoader = new mapvgl.THREELoader.GLTFLoader();

/**
 * 加载服务模型
 * @param {mapvgl.ThreeLayer} threeLayer - ThreeLayer实例
 * @param {Object} config - 模型配置
 */
//todo  和map_common中的loadmodel的关系
function loadFacilityModel(threeLayer, config) {
    facility_gltfLoader.load(
        config.modelUrl,
        function (obj) {
            const model = obj.scene;
            const mcpoint = convertCoords(config.position);

            // 设置模型位置、旋转和缩放
            model.position.set(0, 0, 0);
            model.scale.set(config.scale, config.scale, config.scale);
            if (config.rotation) {
                model.rotation.x = config.rotation.x || 0;
                model.rotation.y = config.rotation.y || 0;
                model.rotation.z = config.rotation.z || 0;
            }

            const geoGroup = new THREE.Group();
            geoGroup.add(model);
            geoGroup.position.set(mcpoint.lng, mcpoint.lat, 0);
            geoGroup.name = config.id;

            threeLayer.add(geoGroup);
            threeLayer.render();
        },
        undefined,
        error => console.error(`模型加载失败: ${config.modelUrl}`, error)
    );
}


/**
 * 加载立方体模型
 * @param {mapvgl.ThreeLayer} threeLayer - ThreeLayer实例
 */
function loadCubeModel(threeLayer) {
    const texture = new THREE.TextureLoader().load(
        'https://i.ibb.co/PtWsXLY/three-Layer.png',
        () => console.log('立方体纹理加载成功'),
        undefined,
        error => console.error('立方体纹理加载失败:', error)
    );
    texture.minFilter = THREE.LinearFilter;

    const material = new THREE.MeshPhongMaterial({
        transparent: true,
        depthTest: true,
        map: texture,
        opacity: 1
    });

    const geometry = new THREE.BoxGeometry(500, 500, 500);
    const cube = new THREE.Mesh(geometry, material);

    const mcpoint = convertCoords([116.36270578593066, 39.931188733629675]);
    cube.position.set(mcpoint.lng, mcpoint.lat, 250);

    const group = new THREE.Group();
    group.add(cube);
    threeLayer.add(group);
    threeLayer.render();
}

/* 4. 创建ThreeLayer主函数 */
function load_all_facility(layerId) {
    if (layerManager.threeLayers.has(layerId)) return;

    // 确保 threeLayer 和 view 已正确初始化
    if (typeof threeLayer === 'undefined' || !threeLayer) {
        console.error('threeLayer 未初始化');
        return;
    }
    if (typeof view === 'undefined' || !view) {
        console.error('view 未初始化');
        return;
    }

    loadCubeModel(threeLayer);
    initModelConfigs(); // 初始化模型配置
    modelConfigs
        .filter(config => config.layerId === layerId)
        .forEach(config => loadFacilityModel(threeLayer, config));

    // 检查 threeLayer 是否支持 addEventListener 方法
    if (typeof threeLayer.addEventListener === 'function') {
        threeLayer.addEventListener('click', function (e) {
            const raycaster = new THREE.Raycaster();
            const mouse = new THREE.Vector2();

            mouse.x = (e.pixel.x / map.width) * 2 - 1;
            mouse.y = -(e.pixel.y / map.height) * 2 + 1;

            raycaster.setFromCamera(mouse, threeLayer.camera);
            const intersects = raycaster.intersectObjects(threeLayer.scene.children, true);

            if (intersects.length > 0) {
                console.log('点击检测到模型', intersects[0]);
                alert(`点击检测到模型${intersects[0].object.name || '未命名模型'}`);
            }
        });
    } else {
        console.warn('threeLayer 不支持 addEventListener 方法');
    }

    layerManager.threeLayers.set(layerId, threeLayer);
    layerManager.views.set(layerId, view);
    layerManager.overlays.push(threeLayer);
}

/* 6. 统一事件绑定 */
function bindOverlayEvents() {
    const eventHandlers = {
        click: e => console.log(`${e.target} 被单击`),
        dblclick: e => alert(`${e.target} 被双击`),
        rightclick: e => alert(`${e.target} 被右击`)
    };

    layerManager.overlays.forEach(overlay => {
        Object.entries(eventHandlers).forEach(([event, handler]) => {
            overlay.addEventListener(event, handler);
        });
    });
}

/* 7. 公共接口 */
window.mapManager = {
    init() {
        initGroundOverlay();
        load_all_facility('mainLayer');
        bindOverlayEvents();
    },
    release() {
        layerManager.overlays.forEach(overlay => {
            map.removeOverlay(overlay);
            overlay.dispose?.();
        });
        layerManager.threeLayers.clear();
        layerManager.views.clear();
        layerManager.overlays = [];
    }
};

// 初始化
