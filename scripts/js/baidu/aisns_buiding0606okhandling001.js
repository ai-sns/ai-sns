var buildingGroup;
let lastTime = 0;
const fontLoader = new THREE.FontLoader();
const renderer = new THREE.WebGLRenderer({ antialias: true });
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

  const screenContent = createScreenContent(boardMaterial);

  // Directly return the draw function to prevent duplicate creation of screen content.
  group.userData.screenContent = screenContent;

  return group;
}

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
    ctx.font = 'bold 20px "Segoe UI", Arial, sans-serif';
    ctx.fillStyle = '#000000';
    ctx.textAlign = 'center';
    ctx.shadowColor = 'rgba(0,0,0,0.3)';
    ctx.shadowBlur = 0;
    ctx.fillText('广场播报', canvas.width / 2, 32);
    const t = time * 0.001;
    const scrollX = (canvas.width + (t * 75) % (textWidth + canvas.width)) - textWidth;
    ctx.font = 'bold 28px Arial';
    ctx.fillStyle = 'Red';
    ctx.shadowColor = '#ff0000';
    ctx.shadowBlur = 0;
    ctx.fillText(scrollText, scrollX, 82);
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

function animate(time) {
  requestAnimationFrame(animate);

  if (time - lastTime > 16) {
    if (buildingGroup) {
      const board = buildingGroup.children.find(child =>
        child instanceof THREE.Group &&
        child.children.some(mesh => mesh.material.emissiveMap)
      );
      if (board) {
        const material = board.children.find(mesh => mesh.material.emissiveMap).material;
        if (material.map && material.map.image) {
          const drawFunc = buildingGroup.userData.screenContent.draw; // Use the stored draw function
          drawFunc(time);
          material.map.needsUpdate = true;
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

function convertCoords(pos) {
  let llPoint = new BMapGL.Point(pos[0], pos[1]);
  const mcpoint = BMapGL.Projection.convertLL2MC(llPoint);
  return mcpoint;
}
alert("buiding00");
function load_aisns_building() {
  let building_model = null;

  var mesh = buildingGroup;  // 获取建筑模型组

  var mcpoint = convertCoords([121.44690152307729, 31.25875179971229]);

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
