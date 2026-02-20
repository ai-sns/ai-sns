// 创建渲染器
const renderer = new THREE.WebGLRenderer({antialias: true});
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
document.body.appendChild(renderer.domElement);
// 创建广告牌结构
// 字体加载
const fontLoader = new THREE.FontLoader();
let buildingGroup; // 用于存储建筑组

fontLoader.load('js/helvetiker_bold.typeface.json', function (font) {
    buildingGroup = createBuilding(font);
    animate_new(0);
});

// 创建大厦
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
        color: 0xaaccff,
        emissive: 0x88bbff,
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

// 创建屏幕内容
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
        ctx.fillStyle = '#ffffff';
        ctx.textAlign = 'center';
        ctx.shadowColor = 'rgba(0,0,0,0.3)';
        ctx.shadowBlur = 10;
        ctx.fillText('广场播报', canvas.width / 2, 32);

        // // 副标题
        // ctx.font = 'bold 9px "Segoe UI", Arial, sans-serif';
        // ctx.fillText('智能社交网络中心', canvas.width/2, 50);

        // 滚动文字
        const t = time * 0.001;
        const scrollX = (canvas.width + (t * 75) % (textWidth + canvas.width)) - textWidth;
        ctx.font = 'bold 28px Arial';
        ctx.fillStyle = 'Red';
        ctx.shadowColor = '#ff0000';
        ctx.shadowBlur = 0;
        // ctx.font = 'bold 8px "Segoe UI", Arial, sans-serif';
        // ctx.fillStyle = 'rgba(255,255,255,0.8)';
        // ctx.shadowBlur = 5;
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

// 动画循环
let lastTime = 0;

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


}

// 动画循环

//添加3D覆盖物
var threev = null;

function addThreev() {
    // alert("00");
    if (threev) {
        return;
    }
    // alert(0);
    threev = new BMapGL.ThreeLayer({
        enablePicked: true,
        antialias: true,
        onInit: function (renderer, scene, camera) {

            var texture = new THREE.TextureLoader().load('https://i.ibb.co/PtWsXLY/three-Layer.png');
            texture.minFilter = THREE.LinearFilter;
            var material = new THREE.MeshPhongMaterial({
                // color: 0xff0000,
                transparent: true, // 允许材质可透明
                depthTest: true,
                map: texture,
                opacity: 1
            });
            var geometry = new THREE.BoxGeometry(500, 500, 500);
            // var mesh = new THREE.Mesh(geometry, material);
            var mesh = buildingGroup;


            // 设置立方体的位置,39.71164

            var result = threev.customCoords([[121.44690152307729, 31.25875179971229]]);
            // alert(result[0][0]);
            mesh.position.set(result[0][0], result[0][1], 0);
            mesh.scale.set(40, 40, 40);
            mesh.rotateX(90 / 180 * Math.PI); // 旋转模型
            mesh.rotateY(0 / 180 * Math.PI); // 旋转模型
            this.add(mesh);


            this.triggerRepaint();
        },
        preRender: function () {
            console.log("in prerender");

        },
        onRender: function (renderer, scene, camera) {
            renderer.render(scene, camera);

        }

    });
    var raycasterv = new THREE.Raycaster();
    var mousev = new THREE.Vector2();
    threev.addEventListener('click', function (e) {
            var fs = this.scene.children;

            // 范围-1 1,原点在中心
            mousev.x = (e.pixel.x / map.width) * 2 - 1;
            mousev.y = -(e.pixel.y / map.height) * 2 + 1;
            alert(mousev.x);
            alert(mousev.y);
            console.log(mousev);
            alert("the inside event:three is clicked");
            console.log(e.target);
            raycasterv.setFromCamera(mousev, this.camera);

            var intersects = raycasterv.intersectObjects(fs);
            intersects.length && console.log(intersects);

        }
    );
    // alert(1)
    map.addNormalLayer(threev);
    // alert(2)
}

addThreev();




