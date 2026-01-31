const FETCH_RETRIES = 30;
const INITIAL_RETRY_DELAY = 1000;
const REQUEST_TIMEOUT = 80000;

async function loadPersonsData(url, retries = FETCH_RETRIES, retryDelay = INITIAL_RETRY_DELAY) {
    // 验证输入参数
    if (typeof url !== 'string' || !url.trim()) {
        throw new Error('无效的URL参数');
    }

    // 内部函数处理请求
    async function fetchData(retriesLeft, delay) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);

        try {

            console.log(`剩余重试次数: ${retriesLeft}`);

            // 添加随机查询参数以防止缓存
            const fetchUrl = new URL(url);
            fetchUrl.searchParams.set('t', Date.now());

            const response = await fetch(fetchUrl.toString(), {
                signal: controller.signal,
                cache: 'no-cache'
            });


            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`请求失败: ${response.status} ${response.statusText}`);
            }

            // 尝试解析JSON数据
            const data = await response.json();
            // showAlert(`请求成功，返回数据: ${data}`);
            return data;

        } catch (error) {
            clearTimeout(timeoutId);

            // 检查是否是超时错误
            if (error.name === 'AbortError') {
                console.error('请求超时被取消');
                showAlert('请求超时被取消');
                throw new Error('请求超时');
            }

            // 重试逻辑
            if (retriesLeft > 0) {
                console.warn(`请求失败，错误: ${error.message}. 剩余重试次数: ${retriesLeft}。将在 ${delay}ms 后重试...`);
                showAlert(`请求数据失败，剩余重试次数: ${retriesLeft}。将在 ${delay}ms 后重试...`);
                await new Promise(resolve => setTimeout(resolve, delay));
                return fetchData(retriesLeft - 1, delay * 1);
            }

            console.error('最终请求失败:', error.message);
            showAlert(`最终请求失败: ${error.message}`);
            throw error;
        }
    }

    return fetchData(retries, retryDelay);
}

// 使用立即执行函数封装异步操作 loadPersonsData
async function load_persons_data_and_show() {
    const dataUrl = base_url+"/personsdata.json";
    const nation_id = nation_id_me;

    try {
        const data = await loadPersonsData(dataUrl); // 加载人员数据
        console.log("成功加载人员数据:", data);
        showAlert(`用户数据已加载成功。`);

        // 过滤掉nation_id等于传入值的项
        personsdata = data.filter(person => person.nation_id !== nation_id);

        // 显示更新后的数据点
        showpoints();
    } catch (error) {
        console.error("人员数据加载失败，建议:",
            error.name === 'AbortError'
                ? '检查网络连接或稍后重试'
                : '联系系统管理员');
    }
}


function findMeshes(object) {
    const meshes = [];
    object.traverse((child) => {
        if (child.isMesh) {
            meshes.push(child);
        }
    });
    return meshes;
}

var highlightedObject = null;
// 加载 3D 模型
var all_model_meshes = [];
var loader = new THREE.GLTFLoader();
var loader2 = new THREE.GLTFLoader();

// 模型加载重试函数
async function loadModelWithRetry(loaderInstance, url, retries = 3, retryDelay = 1000) {
    for (let attempt = 1; attempt <= retries; attempt++) {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 15000);

            const gltf = await new Promise((resolve, reject) => {
                // 监听加载错误
                const errorHandler = (error) => {
                    clearTimeout(timeoutId);
                    reject(error);
                };
                alert(url);

                // 加载模型
                loaderInstance.load(
                    url,
                    (gltf) => {
                        clearTimeout(timeoutId);
                        resolve(gltf);
                    },
                    undefined,
                    errorHandler
                );
            });

            return gltf;
        } catch (error) {
            console.error(`模型加载失败 (尝试 ${attempt}/${retries}): ${error.message}`);

            if (attempt < retries) {
                console.log(`将在 ${retryDelay}ms 后重试...`);
                await new Promise(resolve => setTimeout(resolve, retryDelay));
                retryDelay *= 2; // 指数退避
            } else {
                throw new Error(`模型加载失败，已重试 ${retries} 次: ${error.message}`);
            }
        }
    }
}

function initMap() {


    // 优先使用window.current_position的值作为地图中心点
    let center;
    if (typeof window.current_position !== 'undefined' && window.current_position !== null &&
        typeof window.current_position.lng !== 'undefined' && typeof window.current_position.lat !== 'undefined') {
        center = {lng: window.current_position.lng, lat: window.current_position.lat, altitude: 0};
        console.log("使用配置的位置初始化Google地图:", window.current_position);
    } else {
        center = {lng: 116.27882, lat: 39.71164, altitude: 0};
        console.log("使用默认位置初始化Google地图");
    }


    const DEFAULT_COLOR = 0xffffff;
    const HIGHLIGHT_COLOR = 0xff0000;
    const mapStyles = [
        // 隐藏所有 POI
        {
            featureType: "poi",
            elementType: "all",
            stylers: [{visibility: "off"}]
        }
    ];
    const mapOptions = {
        center,
        // mapId: "7057886e21226ff7",//没有路名等相关内容
        mapId: "b8fc4b5a8471b933",
        // renderingType: google.maps.RenderingType.VECTOR,
        // styles: mapStyles,
        zoom: 17,
        //      draggableCursor: 'crosshair',
        draggingCursor: 'crosshair',
        tilt: 67.5,
        disableDefaultUI: true,
        backgroundColor: "transparent",
        gestureHandling: "greedy",
    };

    // // 创建地图和覆盖层
    // const map = new google.maps.Map(document.getElementById("map"), mapOptions);
    //
    // const overlay = new google.maps.plugins.three.ThreeJSOverlayView({map, anchor: center, upAxis: "Y"});
    map = new google.maps.Map(document.getElementById("map"), mapOptions);
    geocoder = new google.maps.Geocoder();
    marker = new google.maps.Marker({
        map,
        draggable: true
    });
    marker.addListener("dragend", (event) => {
        const position = marker.getPosition();
        console.log(position);
        var address_input = document.getElementById("address");
        const latlng = {
            lat: parseFloat(position.lat()),
            lng: parseFloat(position.lng()),
        };
        geocoder
            .geocode({location: latlng})
            .then((response) => {
                if (response.results[0]) {
                    address_input.value = response.results[0].formatted_address;

                    const location_result = latlng;
                    //location_result is readonly
                    home_position = {
                        lng: location_result.lng,
                        lat: location_result.lat,
                        altitude: 0,
                        scale: 20
                    };
                    const home_position_str = JSON.stringify(home_position);
                    update_map_setting("home_position", home_position_str)


                } else {
                    window.alert("No results found");
                }
            })
            .catch((e) => window.alert("Geocoder failed due to: " + e));

    });
    directionsService = new google.maps.DirectionsService();
    directionsRenderer = new google.maps.DirectionsRenderer({
        draggable: true,
        map,
        // panel: document.getElementById("panel"),
    });
    directionsRenderer.addListener("directions_changed", () => {

        const directions = directionsRenderer.getDirections();
        if (directions) {
            computeTotalDistance(directions);
        }
    });
    initialize_route();
    const tmpcenter = {lat: 39.71164, lng: 116.27882};
    // overlay = new google.maps.plugins.three.ThreeJSOverlayView({map, anchor: center, upAxis: "Y"});
    overlay = new google.maps.plugins.three.ThreeJSOverlayView({
        map,
        anchor: tmpcenter,
        upAxis: "Y"
    });

    const mapDiv = map.getDiv();
    const mousePosition = new THREE.Vector2();
    console.log("intimouseposition:", mousePosition);

    map.addListener("click", (e) => {
        // alert(1);
        last_click_point = e.latLng;
        center_point = getCenter();
        // alert("lastpoint:" + JSON.stringify(e.latLng.toJSON(), null, 2));
        // alert("center_point:" + JSON.stringify(center_point.toJSON(), null, 2));
        distance = getDistance(last_click_point, center_point);
        // alert(distance);
        // showinfo();
        // setTimeout(moveinfo, 1500);
        const domEvent = e.domEvent;
        const {left, top, width, height} = mapDiv.getBoundingClientRect();
        const x = domEvent.clientX - left;
        const y = domEvent.clientY - top;
        mousePosition.x = 2 * (x / width) - 1;
        mousePosition.y = 1 - 2 * (y / height);

        // 处理坐标捕获模式
        if (coordinateCaptureMode) {
            handleMapClick(e.latLng);
        }

        if (instruct_to_move_flag == true) {
            const tmpcenter = {lat: 39.71164, lng: 116.27882};
            // overlay = new google.maps.plugins.three.ThreeJSOverlayView({map, anchor: center, upAxis: "Y"});
            // overlay.setAnchor(tmpcenter);
            const coordinates = getLastClickPoint();
            // overlay.setAnchor(coordinates);
            const position = overlay.latLngAltitudeToVector3(coordinates);
            console.log("model.positiona24", model.position)
            console.log("model.positionxa24", model.position.x)
            console.log("model.positionza24", model.position.z)
            console.log("position", position)
            const position2 = overlay.latLngAltitudeToVector3(coordinates, model.position);
            console.log("position2", position2)
            console.log("model.position", model.position)
            console.log("model.positionx", model.position.x)
            console.log("model.positionz", model.position.z)
        }

        overlay.requestRedraw();
    });
    map.addListener("zoom_changed", () => {
        const zoomLevel = map.getZoom();
        console.log("当前缩放级别:", zoomLevel);
    });

    const contentString = "<div style='font-size:20px'>Hello,I'm CBot.Nice to meet you.</div>";

    const offsetpoint = new google.maps.Size(20, -150);
    var infowindow = new google.maps.InfoWindow({
        content: contentString,
        ariaLabel: "Uluru",
        headerDisabled: true,
        position: {
            lat: 40.76971146231474,
            lng: -73.97265643012797,
            altitude: 520
        },
        pixelOffset: offsetpoint,
    });
    const uluru = {lat: 40.76971146231474, lng: -73.97265643012797};
    const latLngAltitudeLiteral2 = {
        lat: 40.76726879657253,
        lng: -73.97383222939642,
        altitude: 80,
    };

    function showinfo() {
        infowindow.open({
            anchor: null,
            map,
        });
    }

    function moveinfo() {
        infowindow.close();
        const contentString2 = "<div style='font-size:20px'>Nice to meet you.How can I go to AI-SNS Center.</div>";
        const offsetpoint2 = new google.maps.Size(-140, -150);
        var infowindow2 = new google.maps.InfoWindow({
            content: contentString2,
            ariaLabel: "Uluru",
            headerDisabled: true,
            position: {
                lat: 40.76971146231474,
                lng: -73.97265643012797,
                altitude: 520
            },
            pixelOffset: offsetpoint2,
        });

        const opt = {
            content: contentString2,
            ariaLabel: "Uluru",
            headerDisabled: true,
            position: {
                lat: 40.76971146231474,
                lng: -73.97265643012797,
                altitude: 520
            },
            pixelOffset: offsetpoint2,
        }
        infowindow2.open({
            anchor: null,
            map,
        });
        setTimeout(() => {
            // 关闭信息窗口
            infowindow2.close();
            console.log("信息窗口已关闭"); // 便于调试，输出关闭信息
        }, 2000);
    }

// 使用 async/await 处理异步加载，确保模型完全加载后再执行后续操作
    const loadHouse = async () => {
        try {
            // 使用重试机制加载模型
            const gltf = await loadModelWithRetry(loader, 'house_red.glb');
            modelhouse = gltf.scene;
            // 添加环境光
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.75);
            //overlay.scene.add(ambientLight);
            // 添加平行光
            const directionalLight = new THREE.DirectionalLight(0xffffff, 0.25);
            directionalLight.position.set(-1, -1, -1); // 光源位置设置在模型的背面
            // overlay.scene.add(directionalLight);
            // 计算模型的包围体积
            const box = new THREE.Box3().setFromObject(modelhouse);
            const size = box.getSize(new THREE.Vector3());
            const height = size.y; // 模型的高度
            console.log("房屋模型高度:", height);
            // 设置模型的缩放、旋转和位置
            modelhouse.scale.set(1, 1, 1);
            modelhouse.rotation.x = (Math.PI / 15) * 0;
            modelhouse.rotation.y = (Math.PI / 15) * 1.6;
            const position3 = overlay.latLngAltitudeToVector3(home_position, modelhouse.position);
            // 将模型添加到场景中
            overlay.scene.add(modelhouse);
            console.log("房屋模型加载成功");
            modelLoadStatus.house = true;
            checkAnimationStart();
        } catch (error) {
            console.error('房屋模型加载失败:', error);
        }
    };
    loadHouse();
    const loadModel = async () => {
        try {
            // 使用重试机制加载模型
            const gltf = await loadModelWithRetry(loader, 'avatar3d/tshirtgirl_0_0_0_0_1_0.glb');
            model = gltf.scene;
            // 添加环境光
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.75);
            //overlay.scene.add(ambientLight);
            // 添加平行光
            const directionalLight = new THREE.DirectionalLight(0xffffff, 0.25);
            directionalLight.position.set(-1, -1, -1); // 光源位置设置在模型的背面
            // overlay.scene.add(directionalLight);
            // 计算模型的包围体积
            const box = new THREE.Box3().setFromObject(model);
            const size = box.getSize(new THREE.Vector3());
            const height = size.y; // 模型的高度
            console.log("女孩模型高度:", height);
            // 根据高度调整缩放比例
            const desiredHeight = 150; // 期望的高度
            const scale = desiredHeight / height;
            // 设置模型的缩放、旋转和位置
            model.scale.set(scale, scale, scale);
            model.rotation.x = Math.PI / 30;
            model.rotation.y = Math.PI / 1.5;
            model.position.set(60, 0, -250);
            // 将模型添加到场景中
            overlay.scene.add(model);
            // 查找场景中的所有网格
            const modelMeshes_found = findMeshes(gltf.scene);
            // 将找到的网格添加到全局数组
            all_model_meshes.push(...modelMeshes_found);
            // 给模型添加点击事件
            model.traverse((child) => {
                if (child.isMesh) {
                    child.cursor = 'pointer';
                    child.userData.isClickable = true;
                }
            });
            // 创建动画混合器并播放动画
            if (gltf.animations && gltf.animations.length > 0) {
                const mixer = new THREE.AnimationMixer(gltf.scene);
                const action = mixer.clipAction(gltf.animations[0]);
                mixer.timeScale = 0.5;
                action.setDuration(1).play();
                mixers.push(mixer);
                console.log("女孩模型动画已启动");
            }
            console.log("女孩模型加载成功");
            modelLoadStatus.girl = true;
            checkAnimationStart();
        } catch (error) {
            console.error('女孩模型加载失败:', error);
        }
    };
// 调用 loadModel 函数
    loadModel();
    // 加载AI-SNS建筑模型（假设功能类似）

    load_aisns_building();
    const loadModel2 = async () => {
        try {
            // 使用重试机制加载模型
            const gltf = await loadModelWithRetry(loader, 'avatar3d/ctgirlschool_0_0_0_0_02_0.glb');
            model2 = gltf.scene;
            // 添加环境光
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.75);
            //overlay.scene.add(ambientLight);
            // 添加平行光
            const directionalLight = new THREE.DirectionalLight(0xffffff, 0.25);

            directionalLight.position.set(-1, -1, -1); // 光源位置设置在模型的背面
            // overlay.scene.add(directionalLight);
            // 计算模型的包围体积
            const box = new THREE.Box3().setFromObject(model2);
            const size = box.getSize(new THREE.Vector3());
            const height = size.y; // 模型的高度
            console.log("男孩模型高度:", height);
            // 根据高度调整缩放比例
            const desiredHeight = 150; // 期望的高度
            const scale = desiredHeight / height;
            model2.scale.set(scale, scale, scale);
            // 设置模型的旋转和位置
            // model2.rotation.x = Math.PI / 30;
            model2.rotation.x = THREE.MathUtils.degToRad(6);  // 6度 → 弧度model2.rotation.x = THREE.MathUtils.degToRad(6);  // 6度 → 弧度
            model2.rotation.z = THREE.MathUtils.degToRad(0);  // 6度 → 弧度model2.rotation.x = THREE.MathUtils.degToRad(6);  // 6度 → 弧度
            model2.rotation.y = Math.PI / 1.5;
            model2.position.set(130, 0, -250);
            // 将模型添加到场景中
            overlay.scene.add(model2);
            // 查找场景中的所有网格
            const modelMeshes_found = findMeshes(gltf.scene);
            // 将找到的网格添加到全局数组
            all_model_meshes.push(...modelMeshes_found);
            // 给模型添加点击事件
            model2.traverse((child) => {
                if (child.isMesh) {
                    child.cursor = 'pointer';
                    child.userData.isClickable = true;
                }
            });
            // 创建动画混合器并播放动画
            if (gltf.animations && gltf.animations.length > 0) {
                const mixer = new THREE.AnimationMixer(gltf.scene);
                const action = mixer.clipAction(gltf.animations[0]);
                mixer.timeScale = 0.5;
                action.setDuration(10).play();
                mixers.push(mixer);
                console.log("男孩模型动画已启动");
            }
            console.log("男孩模型加载成功");
            modelLoadStatus.boy = true;
            checkAnimationStart();
        } catch (error) {
            console.error('男孩模型加载失败:', error);
        }
    };
    loadModel2();


    //set ground overlay
    const imageBounds = {
        // north: 40.773941,
        // south: 40.712216,
        // east: -74.12544,
        // west: -74.22655,
        north: 39.76812,
        south: 39.74441,
        east: 116.25646,
        west: 116.22971,
    };

    playGroundOverlay = new google.maps.GroundOverlay(
        "shouhuimap.png",//"https://storage.googleapis.com/geo-devrel-public-buckets/newark_nj_1922-661x516.jpeg",
        imageBounds,
    );
    playGroundOverlay.setMap(map);


    //loadcube
    const webglOverlay = new google.maps.WebGLOverlayView();
    const cubePosition = { lat: 39.931188733629675, lng: 116.36270578593066 };

    let scene, camera, renderer, cube;

    webglOverlay.onAdd = () => {
        scene = new THREE.Scene();
        camera = new THREE.PerspectiveCamera();

        // 添加光源
        const light = new THREE.DirectionalLight(0xffffff, 0.5);
        light.position.set(0, 50, 100);
        scene.add(light);

        const ambient = new THREE.AmbientLight(0xffffff, 0.8);
        scene.add(ambient);

        // 加载纹理
        const textureLoader = new THREE.TextureLoader();
        const texture = textureLoader.load(
            'https://i.ibb.co/PtWsXLY/three-Layer.png',
            () => console.log("立方体纹理加载成功"),
            undefined,
            (err) => console.error("纹理加载失败", err)
        );

        // 创建立方体（单位：米）
        const geometry = new THREE.BoxGeometry(30, 30, 30);
        const material = new THREE.MeshPhongMaterial({
            map: texture,
            transparent: true,
        });

        cube = new THREE.Mesh(geometry, material);
        scene.add(cube);
    };

    webglOverlay.onContextRestored = ({gl}) => {
        renderer = new THREE.WebGLRenderer({
            canvas: gl.canvas,
            context: gl,
            ...gl.getContextAttributes(),
        });
        renderer.autoClear = false;
    };

    webglOverlay.onDraw = ({gl, transformer}) => {
        if (!cube) return;

        // 将立方体位置绑定到地理坐标（贴地 altitude=0）
        const matrix = transformer.fromLatLngAltitude({
            lat: cubePosition.lat,
            lng: cubePosition.lng,
            altitude: 0,
        });

        camera.projectionMatrix = new THREE.Matrix4().fromArray(matrix);

        // 不再旋转立方体
        renderer.render(scene, camera);
        renderer.resetState();
    };

    webglOverlay.setMap(map);


    overlay.onBeforeDraw = () => {
        if (mousePosition.x != 0 && mousePosition.y != 0) {
            var intersections = overlay.raycast(mousePosition, all_model_meshes, {
                recursive: false,
            });
            if (highlightedObject) {
                console.log("取消高亮显示");
                console.log("鼠标位置:", mousePosition);
            }
            if (intersections.length === 0) {
                highlightedObject = null;
                return;
            }
            highlightedObject = intersections[0].object;
            highlightedObject.material.color.setHex(HIGHLIGHT_COLOR);//暂停颜色变化
            if (highlightedObject.userData) {
                if (highlightedObject.userData.nation_id) {
                    console.log("检测到国家ID:", highlightedObject.userData.nation_id);
                    nation_id = highlightedObject.userData.nation_id;
                    currentModel = getPersonModelByNationId(nation_id);
                    mousePosition.x = 0;
                    mousePosition.y = 0;
                    showprofile3d(currentModel);
                }
            }
        }
    };


}


function checkAnimationStart() {
    if (animationStarted) return;

    if (modelLoadStatus.building &&
        modelLoadStatus.house &&
        modelLoadStatus.girl &&
        modelLoadStatus.boy) {

        animate(0);
        animationStarted = true;
        console.log("所有模型加载完成，启动动画");
    }
}

/**
 * 解析文件名中的模型参数
 * 文件名格式: 英文名_x旋转_y旋转_z旋转_海拔_缩放_动画索引.glb
 * 例如: ctboyblue_0_0_0_0_1_0.glb
 * @param {string} filename - 文件名
 * @returns {object|null} 解析后的参数对象，如果解析失败则返回null
 */
function parseModelFilename(filename) {
    // 移除路径，只保留文件名
    const baseName = filename.split('/').pop().split('\\').pop();
    // 移除扩展名
    const nameWithoutExt = baseName.replace(/\.[^/.]+$/, '');

    // 使用正则表达式匹配：英文字母开头，后面跟着下划线分隔的数字
    const match = nameWithoutExt.match(/^[a-zA-Z]+(.*)$/);
    if (!match || !match[1]) {
        return null;
    }

    // 从英文字母后开始解析，获取所有下划线分隔的数字
    const paramString = match[1];
    const params = paramString.split('_').filter(s => s !== '');

    if (params.length < 6) {
        console.warn(`文件名参数不足6个: ${filename}, 找到 ${params.length} 个参数`);
        return null;
    }

    // 解析缩放比例参数（第5个数字，索引为4）
    // 如果以0开头则表示小数，例如05表示0.5
    let scaleMultiplier = 1;
    const scaleParam = params[4];
    if (scaleParam.startsWith('0') && scaleParam.length > 1) {
        // 以0开头，转换为小数
        scaleMultiplier = parseFloat('0.' + scaleParam.substring(1));
    } else {
        scaleMultiplier = parseFloat(scaleParam);
    }

    return {
        rotationX: parseFloat(params[0]) || 0,      // 第1个数字：x轴旋转（角度）
        rotationY: parseFloat(params[1]) || 0,      // 第2个数字：y轴旋转（角度）
        rotationZ: parseFloat(params[2]) || 0,      // 第3个数字：z轴旋转（角度）
        altitude: parseFloat(params[3]) || 0,       // 第4个数字：海拔高度
        scaleMultiplier: scaleMultiplier,           // 第5个数字：缩放比例乘数
        animationIndex: parseInt(params[5]) || 0    // 第6个数字：动画索引
    };
}

/**
 * 判断URL是否为web地址
 * @param {string} url - URL字符串
 * @returns {boolean} 如果是web地址返回true
 */
function isWebUrl(url) {
    return url.startsWith('http://') || url.startsWith('https://') || url.startsWith('//');
}

function loadModel(persondata) {
    let url = persondata["avatar_3d"];
    let pos = persondata["location"];
    const coordinates = {
        lat: parseFloat(pos[1]),
        lng: parseFloat(pos[0]),
    };

    // 解析文件名参数
    let modelParams = null;

    // 如果不是web地址，则添加目录前缀并解析文件名参数
    if (!isWebUrl(url)) {
        // 解析文件名中的参数
        modelParams = parseModelFilename(url);
        if (modelParams) {
            console.log(`解析到模型参数:`, modelParams);
        }
        // 添加目录前缀
        url = '/scripts/avatar3d/' + url;
        console.log(`模型完整路径: ${url}`);
    }

    // 创建新的加载器实例避免冲突
    const personalLoader = new THREE.GLTFLoader();

    // 封装加载过程
    const loadPersonalModel = async () => {
        try {
            // 使用重试机制加载模型
            const gltf = await loadModelWithRetry(personalLoader, url);
            model = gltf.scene;

            // 添加光照
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.1);
            const directionalLight = new THREE.DirectionalLight(0xffffff, 0.1);
            directionalLight.position.set(-1, -1, -1);

            // 设置模型元数据
            model.name = persondata["nation_id"];
            model.userData = persondata;

            // 计算模型尺寸并缩放
            const box = new THREE.Box3().setFromObject(model);
            const size = box.getSize(new THREE.Vector3());
            const height = size.y;
            console.log(`个人模型高度 (${persondata.name}):`, height);
alert(height);
            const desiredHeight = 150;
            let scale = desiredHeight / height;

            // 如果有文件名参数，应用缩放乘数
            if (modelParams && modelParams.scaleMultiplier) {
                scale = scale * modelParams.scaleMultiplier;
                console.log(`应用缩放乘数 ${modelParams.scaleMultiplier}, 最终缩放比例: ${scale}`);
            } else {
                console.log("缩放比例:", scale);
            }

            model.scale.set(scale, scale, scale);

            // 设置旋转
            if (modelParams) {
                // 使用文件名中解析的旋转参数（转换为弧度）
                model.rotation.x = THREE.MathUtils.degToRad(modelParams.rotationX);
                model.rotation.y = THREE.MathUtils.degToRad(modelParams.rotationY);
                model.rotation.z = THREE.MathUtils.degToRad(modelParams.rotationZ);
                console.log(`应用旋转: x=${modelParams.rotationX}°, y=${modelParams.rotationY}°, z=${modelParams.rotationZ}°`);
            } else {
                // 使用默认旋转
                model.rotation.x = Math.PI / 30;
                model.rotation.y = (Math.PI / 1.5);
            }

            // 定位模型，考虑海拔高度
            let altitudeCoordinates = coordinates;
            if (modelParams && modelParams.altitude) {
                altitudeCoordinates = {
                    lat: coordinates.lat,
                    lng: coordinates.lng,
                    altitude: modelParams.altitude
                };
                console.log(`应用海拔高度: ${modelParams.altitude}`);
            }
            const position2 = overlay.latLngAltitudeToVector3(altitudeCoordinates, model.position);
            console.log("模型位置:", position2);

            // 添加到场景
            overlay.scene.add(model);
            model_loaded_list[persondata["nation_id"]] = model;

            // 处理网格
            let modelMeshes = findMeshes(gltf.scene);
            model.traverse((child) => {
                if (child.isMesh) {
                    child.cursor = 'pointer';
                    child.userData.isClickable = true;
                }
            });

            modelMeshes.forEach(mesh => {
                mesh.userData = persondata;
            });

            all_model_meshes.push(...modelMeshes);

            // 处理动画
            if (gltf.animations && gltf.animations.length > 0) {
                let mixer = new THREE.AnimationMixer(gltf.scene);

                // 确定要播放的动画索引
                let animIndex = 0;
                if (modelParams && modelParams.animationIndex !== undefined) {
                    animIndex = modelParams.animationIndex;
                    // 确保索引在有效范围内
                    if (animIndex >= gltf.animations.length) {
                        console.warn(`动画索引 ${animIndex} 超出范围，使用索引 0`);
                        animIndex = 0;
                    }
                }

                const action = mixer.clipAction(gltf.animations[animIndex]);
                mixer.timeScale = 1;
                const duration = gltf.animations[animIndex].duration;
                action.setDuration(duration).play();
                mixers.push(mixer);
                console.log(`个人模型动画已启动 (${persondata.name}), 播放动画索引: ${animIndex}`);
            }

            console.log(`个人模型加载成功: ${persondata.name}`);
        } catch (error) {
            console.error(`个人模型加载失败 (${persondata.name}):`, error);
        }
    };

    // 执行加载
    loadPersonalModel();
}

function removeModel(nation_id) {
    if (model_loaded_list[nation_id]) {
        model = model_loaded_list[nation_id];
        overlay.scene.remove(model);
        delete model_loaded_list[nation_id];
        console.log(`已移除模型: ${nation_id}`);
    } else {
        console.warn(`尝试移除不存在的模型: ${nation_id}`);
    }
}

function getLastClickPoint() {
    return last_click_point;
}

function getDistance(start_point, end_point) {
    return google.maps.geometry.spherical.computeDistanceBetween(start_point, end_point);
}

function getCenter() {
    return map.getCenter();
}


function updateHouseModel(position, scale, rotation) {
    // 检查overlay和modelhouse是否存在
    if (typeof overlay === 'undefined' || !overlay.scene) {
        console.warn('overlay未初始化，无法更新模型');
        return;
    }

    if (typeof modelhouse === 'undefined') {
        console.warn('modelhouse未初始化，无法更新模型');
        return;
    }

    try {
        // 更新模型位置
        const coordinates = {
            lat: parseFloat(position.lat),
            lng: parseFloat(position.lng)
        };

        // 转换经纬度坐标到3D场景坐标
        const position3 = overlay.latLngAltitudeToVector3(coordinates, modelhouse.position);
        modelhouse.position.copy(position3);

        // 更新模型缩放
        modelhouse.scale.set(scale, scale, scale);

        // 更新模型旋转
        modelhouse.rotation.x = rotation.x || 0;
        modelhouse.rotation.y = rotation.y || 0;
        modelhouse.rotation.z = rotation.z || 0;

        // 请求重绘
        overlay.requestRedraw();

        console.log('House model updated:', {
            position: coordinates,
            scale: scale,
            rotation: rotation
        });
    } catch (error) {
        console.error('更新房屋模型时出错:', error);
    }
}

function queryAddress() {
    //创建地址解析器实例
    var address = document.getElementById("address").value;
    geocoder
        .geocode({address: address})
        .then((result) => {
            const {results} = result;
            map.setCenter(results[0].geometry.location);
            marker.setPosition(results[0].geometry.location);
            marker.setMap(map);
            init_address = address;
            const location_result = results[0].geometry.location;
            //location_result is readonly
            home_position = {
                lng: location_result.lng(),
                lat: location_result.lat(),
                altitude: 0,
                scale: 20
            };
            const home_position_str = JSON.stringify(home_position);
            update_map_setting("home_position", home_position_str)
            return results;
        })
        .catch((e) => {
            alert("Geocode was not successful for the following reason: " + e);
        });
}


function set_move_status() {

    if (instruct_to_move_flag) {
        instruct_to_move_flag = false;
        map.setOptions({
            draggableCursor: 'default', // 默认指针
            draggingCursor: 'grabbing', // 拖动时的指针

        });
    } else {
        instruct_to_move_flag = true;
        map.setOptions({
            draggableCursor: 'crosshair', // 默认指针
            draggingCursor: 'crosshair', // 拖动时的指针
        });
        showAlert("请点击地图来指定要移动的目标位置。");
    }

}

var infowindow;

function start_talk_to_it(nation_id, content) {
    // content=""
    // alert("start_talk_to_it");
    alert(nation_id);
    let marker = hiddenMarkers[nation_id];
    hideMarker(marker);

    // alert(map.getZoom());
    person_target_point = getPersonPointByNationId(nation_id);
    person_data_me = getPersonDataByNationId(nation_id_me);
    person_target = getPersonDataByNationId(nation_id);
    loadModel(person_target);


    alert(person_data_me["account"]);
    alert(person_target["account"]);
    // map.setHeading(0);
    // map.setTilt(0);
    console.log("the user point:");
    console.log(person_target_point);
    console.log(person_target_point.lng);
    console.log(person_target_point.lat);
    console.log(person_target_point.lng);
    console.log(person_target_point.lat);


    my_new_point = new google.maps.LatLng(person_target_point.lat() - 0.01, person_target_point.lng());
    alert("newpoint");
    alert(person_target_point.lng());
    alert(person_target_point.lat() - 0.01);
    console.log("person_target_point.lat", person_target_point.lat());
    console.log("person_target_point.latt - 0.01", person_target_point.lat() - 0.01);

    console.log("my_new_point.lat", my_new_point.lat());
    console.log("my_new_point.lng", person_target_point.lat() - 0.01);

    // infowindow.close();

    setPersonModelPointByNationId(nation_id_me, my_new_point);
    setPersonPointByNationId(nation_id_me, my_new_point.lng(), my_new_point.lat());
    // return true;
    // var point = new BMapGL.Point(116.28882, 39.72164);
    let person_point = my_new_point;


    let hello_msg = "Hello";

    var contentString = `
    <p style='margin:0;line-height:1.5;font-size:13px;'>
    ${hello_msg}
    </p></div>`;
    // 创建一个 <h4> 元素
    var h4Element = document.createElement('h4');

    // 设置样式
    h4Element.style.margin = '0 0 5px 0';

    // 设置文本内容
    h4Element.textContent = person_data_me['nick_name'];


    const offsetpoint = new google.maps.Size(20, -50);
    // infowindow = new google.maps.InfoWindow({
    //     content: contentString,
    //     ariaLabel: "Profile",
    //     headerContent: h4Element,
    //     // headerDisabled: true,
    //     position: person_point,
    //     pixelOffset: offsetpoint,
    // });
    //
    //
    //     infowindow.open({
    //         anchor: null,
    //         map,
    //     });


    // send_im(person_data_me["account"], person_target["account"], hello_msg);


    let point2 = person_target_point;

    let hello_msg2 = "Nice to meet you.";

    var contentString2 = `
    <p style='margin:0;line-height:1.5;font-size:13px;'>
    ${hello_msg2}
    </p></div>`;
    // 创建一个 <h4> 元素
    var h4Element2 = document.createElement('h4');

    // 设置样式
    h4Element2.style.margin = '0 0 5px 0';

    // 设置文本内容
    h4Element2.textContent = person_target['nick_name'];


    const offsetpoint2 = new google.maps.Size(20, -50);
    // infowindow2 = new google.maps.InfoWindow({
    //     content: contentString2,
    //     ariaLabel: "Profile",
    //     headerContent: h4Element2,
    //     // headerDisabled: true,
    //     position: point2,
    //     pixelOffset: offsetpoint2,
    // });


    // setTimeout(function () {
    //     infowindow.close();
    // }, 1500);


    // setTimeout(function () {
    //     infowindow2.open({
    //         anchor: null,
    //         map,
    //     });
    // }, 1500);
    //
    //
    // setTimeout(function () {
    //     infowindow2.close();
    // }, 3000);
}

function talk_to_it(nation_id, content) {
    // content=""
    alert(nation_id);
    let marker = hiddenMarkers[nation_id];
    hideMarker(marker);

    // alert(map.getZoom());
    person_target_point = getPersonPointByNationId(nation_id);
    person_data_me = getPersonDataByNationId(nation_id_me);
    person_target = getPersonDataByNationId(nation_id);
    loadModel(person_target);


    alert(person_data_me["account"]);
    alert(person_target["account"]);
    // map.setHeading(0);
    // map.setTilt(0);
    console.log("the user point:");
    console.log(person_target_point);
    console.log(person_target_point.lng);
    console.log(person_target_point.lat);
    console.log(person_target_point.lng);
    console.log(person_target_point.lat);


    my_new_point = new google.maps.LatLng(person_target_point.lat() - 0.01, person_target_point.lng());

    console.log("person_target_point.lat", person_target_point.lat())
    console.log("person_target_point.latt - 0.01", person_target_point.lat() - 0.01)

    console.log("my_new_point.lat", my_new_point.lat())
    console.log("my_new_point.lng", person_target_point.lat() - 0.01)

    //close the window of profile
    infowindow.close();


    setPersonModelPointByNationId(nation_id_me, my_new_point);
    // return true;
    // var point = new BMapGL.Point(116.28882, 39.72164);
    let person_point = my_new_point;


    let hello_msg = "Hello";

    var contentString = `
    <p style='margin:0;line-height:1.5;font-size:13px;'>
    ${hello_msg}
    </p></div>`;
    // 创建一个 <h4> 元素
    var h4Element = document.createElement('h4');

    // 设置样式
    h4Element.style.margin = '0 0 5px 0';

    // 设置文本内容
    h4Element.textContent = person_data_me['nick_name'];


    const offsetpoint = new google.maps.Size(20, -50);
    infowindow = new google.maps.InfoWindow({
        content: contentString,
        ariaLabel: "Profile",
        headerContent: h4Element,
        // headerDisabled: true,
        position: person_point,
        pixelOffset: offsetpoint,
    });


    infowindow.open({
        anchor: null,
        map,
    });


    send_im(person_data_me["account"], person_target["account"], hello_msg);


    let point2 = person_target_point;

    let hello_msg2 = "Nice to meet you.";

    var contentString2 = `
    <p style='margin:0;line-height:1.5;font-size:13px;'>
    ${hello_msg2}
    </p></div>`;
    // 创建一个 <h4> 元素
    var h4Element2 = document.createElement('h4');

    // 设置样式
    h4Element2.style.margin = '0 0 5px 0';

    // 设置文本内容
    h4Element2.textContent = person_target['nick_name'];


    const offsetpoint2 = new google.maps.Size(20, -50);
    infowindow2 = new google.maps.InfoWindow({
        content: contentString2,
        ariaLabel: "Profile",
        headerContent: h4Element2,
        // headerDisabled: true,
        position: point2,
        pixelOffset: offsetpoint2,
    });


    setTimeout(function () {
        infowindow.close();
    }, 1500);


    setTimeout(function () {
        infowindow2.open({
            anchor: null,
            map,
        });
    }, 1500);


    setTimeout(function () {
        infowindow2.close();
    }, 3000);
}

function stop_talk_to_it(nation_id) {
    removeModel(nation_id);
    let marker = hiddenMarkers[nation_id];
    marker.setVisible(true); // 隐藏标记
    infowindow.close();
}


// 定义一个标志变量，用于指示是否正在显示信息窗口
let showing_info_flag = false;

function send_chat_msg(lng, lat, msg, send_person_name = "") {
    // 检查当前是否正在展示信息窗口
    if (showing_info_flag) {
        console.log("信息窗口仍在显示。请稍后...");

        // 递归调用，稍后再尝试发送消息
        setTimeout(() => send_chat_msg(lng, lat, msg, send_person_name), 1000);
        return; // 如果正在显示，则退出函数
    }

    // 设置标志为 true，表示信息窗口正在显示
    showing_info_flag = true;

    // 创建地图坐标点

    let person_point = new google.maps.LatLng(lat, lng);

    var contentString = `
    <p style='margin:0;line-height:1.5;font-size:13px;'>
    ${msg}

    </p></div>`;

    // 创建一个 <h4> 元素
    var h4Element = document.createElement('h4');

    // 设置样式
    h4Element.style.margin = '0 30px 5px 0';

    // 设置文本内容
    if (send_person_name) {
        h4Element.textContent = send_person_name;
    } else {
        h4Element.textContent = "Message";
    }


    const offsetpoint = new google.maps.Size(20, -50);
    infowindow = new google.maps.InfoWindow({
        content: contentString,
        ariaLabel: "Profile",
        headerContent: h4Element,
        // headerDisabled: true,
        position: person_point,
        pixelOffset: offsetpoint,
    });

    infowindow.open({
        anchor: null,
        map,
    });

    // 设置定时器，延迟5500毫秒后关闭信息窗口并重置标志
    setTimeout(function () {
        infowindow.close(); // 关闭信息窗口
        showing_info_flag = false; // 重置标志
    }, 3000);

    // 调试输出
    console.log("信息窗口已打开。");
}


function showprofile(nation_id) {
    if (infowindow) {
        infowindow.close();
    }

    let person_point = getPersonPointByNationId(nation_id);
    console.log("person_point");
    console.log(person_point);
    let person = getPersonDataByNationId(nation_id);
    var contentString = `
<div style="display: flex; justify-content: space-between; align-items: center; margin: 0; line-height: 1.5; font-size: 13px; color: black;">
    <span style="font-weight: bold;corlor:black; cursor: pointer;" >${person['nick_name']}</span>
    <span style="cursor: pointer;color:black;"  onclick="closeprofile()">X</span>
</div>

    ${person["profile"]}
    <a href="#" onclick="talk_to_it('${nation_id}','');return false;">和Ta聊天</a>
    </p></div>`;
    // 创建一个 <h4> 元素
    // var h4Element = document.createElement('h4');
    var h4Element = document.createElement('div');

    // 设置样式
    h4Element.style.margin = '0 0 5px 0';

    // 设置文本内容
    h4Element.textContent = person['nick_name'];


    const offsetpoint = new google.maps.Size(20, -50);
    infowindow = new google.maps.InfoWindow({
        content: contentString,
        ariaLabel: "Profile",
        headerContent: h4Element,
        headerDisabled: true,
        position: person_point,
        pixelOffset: offsetpoint,
    });

    infowindow.open({
        anchor: null,
        map,
    });

    open_sns_profile(person['sns_url']);
    // 图片加载完毕重绘infoWindow
    document.getElementById('imgDemo').onload = function () {
        infoWindow.redraw(); // 防止在网速较慢时生成的信息框高度比图片总高度小，导致图片部分被隐藏
    };
}

function closeprofile() {
    infowindow.close();
    close_sns_profile()
}

function showprofile3d(geoGroup) {
    let nation_id = geoGroup.userData.nation_id;
    let person_point = getPersonPointByNationId(nation_id);
    let person = geoGroup.userData;
    var contentString = `
    <p style='margin:0;line-height:1.5;font-size:13px;text-indent:2em'>
    ${person["profile"]}
    <a href="#" onclick="stop_talk_to_it('${nation_id}');return false;">结束聊天</a>
    </p></div>`;
// 创建一个 <h4> 元素
    var h4Element = document.createElement('h4');

    // 设置样式
    h4Element.style.margin = '0 0 5px 0';

    // 设置文本内容
    h4Element.textContent = person['nick_name'];


    const offsetpoint = new google.maps.Size(20, -50);
    infowindow = new google.maps.InfoWindow({
        content: contentString,
        ariaLabel: "Profile",
        headerContent: h4Element,
        // headerDisabled: true,
        position: person_point,
        pixelOffset: offsetpoint,
    });

    infowindow.open({
        anchor: null,
        map,
    });
    overlay.requestRedraw();
}


//navigate places

var auto_navigate_flag = false;

function toggleNavigate() {
    if (auto_navigate_flag) {
        cancelNavigate();
        auto_navigate_flag = false;
    } else {
        autoNavigate();
        auto_navigate_flag = true;
    }
}

function autoNavigate() {
    console.log("auto navigate");

    // 初始化街景功能
    let scene, renderer, camera, loader;


    // 将mapOptions定义移到函数内部
    const mapOptions = {
        tilt: 45,
        heading: 200,
        zoom: 18,
        center: {lat: 51.5009027372566, lng: -0.12384218788291879},
        disableDefaultUI: true,
        backgroundColor: 'transparent',
        gestureHandling: 'greedy',
        mapId: "b8fc4b5a8471b933",
    };
    map.setOptions(mapOptions);

    const webglOverlayView = new google.maps.WebGLOverlayView();

    webglOverlayView.onAdd = () => {
        scene = new THREE.Scene();
        camera = new THREE.PerspectiveCamera();

        const ambientLight = new THREE.AmbientLight(0xffffff, 0.75);
        scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
        directionalLight.position.set(0.5, -1, 0.5);
        scene.add(directionalLight);

        loader = new THREE.GLTFLoader();
        const source = "cbot.glb";

        loader.load(source, function (gltf) {
            gltf.scene.scale.set(30, 30, 30);
            gltf.scene.rotation.x = Math.PI + 29.9;
            scene.add(gltf.scene);
        });
    };

    webglOverlayView.onContextRestored = ({gl}) => {
        renderer = new THREE.WebGLRenderer({
            antialias: true,
            canvas: gl.canvas,
            context: gl,
            ...gl.getContextAttributes(),
        });
        renderer.autoClear = false;

        renderer.toneMapping = THREE.ACESFilmicToneMapping; // 设置色调映射
        renderer.toneMappingExposure = 2.0; // 设置曝光值,需要设置这个曝光值，否则颜色是很深的

        loader.manager.onLoad = () => {
            renderer.setAnimationLoop(() => {
                webglOverlayView.requestRedraw();

                const {tilt, heading, zoom} = mapOptions;
                map.moveCamera({tilt, heading, zoom});

                if (mapOptions.tilt < 67.5) {
                    mapOptions.tilt += 0.5;
                } else if (mapOptions.heading <= 720) {
                    mapOptions.heading += 0.2;
                    mapOptions.zoom -= 0.0005;
                } else {
                    renderer.setAnimationLoop(null);
                    cancelNavigate();
                }
            });
        };
    };

    webglOverlayView.onDraw = ({gl, transformer}) => {
        const latLngAltitudeLiteral = {
            lat: mapOptions.center.lat,
            lng: mapOptions.center.lng,
            altitude: 80,
        };

        const matrix = transformer.fromLatLngAltitude(latLngAltitudeLiteral);
        camera.projectionMatrix = new THREE.Matrix4().fromArray(matrix);

        webglOverlayView.requestRedraw();
        renderer.render(scene, camera);
        renderer.resetState();
    };

    webglOverlayView.setMap(map);


}

function cancelNavigate() {
    console.log("cancel");
    auto_navigate_flag = false;
    refresh();
}

