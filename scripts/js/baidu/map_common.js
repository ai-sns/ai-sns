//todo
// 延迟初始化地图中心点，等待 current_position 被设置
function initializeMapCenter() {
    var centerPoint;
    // 检查全局变量current_position是否存在且包含有效的lng和lat属性，如果存在则优先使用
    if (typeof window.current_position !== 'undefined' && window.current_position !== null &&
        typeof window.current_position.lng !== 'undefined' && typeof window.current_position.lat !== 'undefined') {
        centerPoint = new BMapGL.Point(window.current_position.lng, window.current_position.lat);
        console.log("使用配置的位置初始化地图:", window.current_position);
    } else {
        centerPoint = new BMapGL.Point(116.28882, 39.71164);
        console.log("使用默认位置初始化地图");
    }

    map.centerAndZoom(centerPoint, 16);
}

// 如果 current_position 已经存在，立即初始化；否则等待
if (typeof window.current_position !== 'undefined' && window.current_position !== null) {
    initializeMapCenter();
} else {
    // 延迟执行，等待 current_position 被设置,在interact_python中设置
    console.log("等待 current_position 初始化...");
}
map.setHeading(90);
map.setTilt(80);
map.enableKeyboard();
map.enableScrollWheelZoom();
map.enableInertialDragging();
map.enableContinuousZoom();
driving = new BMapGL.DrivingRouteLine(map, {
    renderOptions: {
        map: map,
        autoViewport: true,
        enableDragging: true,
    },
    onSearchComplete: function (result) {
        if (driving.getStatus() === BMAP_STATUS_SUCCESS || driving.getStatus() === 5) {
            alert("规划成功，坐标数:");
            alert(result);
            console.log("规划成功，坐标数:", result);

            // 获取规划方案
            const plan = result.getPlan(0);
            if (plan) {
                alert("距离时长");
                distance = plan.getDistance(true); // 获取距离，true表示返回数值
                duration = plan.getDuration(true); // 获取时间，true表示返回数值
                alert(distance);
                alert(duration);

                // 将distance值转换为浮点数，除以0.5，并赋值给move_duration
                // 首先从"35.5公里"这样的字符串中提取数值部分
                var distanceValue = parseFloat(String(distance).replace(/[^\d\.]/g, ''));
                if (!isNaN(distanceValue)) {
                    move_duration = distanceValue / 0.05;
                }
            }

            gpsPositions = getAllGpsPositions(result);
            console.log("规划成功，坐标数:", gpsPositions.length);

            const start = document.getElementById("start").value.trim();
            const end = document.getElementById("end").value.trim();

            // 保存起点和终点到后端
            update_map_setting("route_start", start);
            update_map_setting("route_end", end);

            // 更新路线状态为playing
            route_status = "playing";
            update_map_setting("route_status", route_status);

            // 只有用户主动发起的路线规划才重置路线进度和当前位置
            // 自动规划（如页面打开时）保持之前的进度
            if (isUserInitiatedRoutePlanning) {
                update_map_setting("route_current_position", "");
                update_map_setting("route", "");
                // 重置标志
                isUserInitiatedRoutePlanning = false;
            }

            // 获取起点和终点输入框
            const startInput = document.getElementById('start');
            const endInput = document.getElementById('end');
            const msgdiv = document.getElementById("setroute");
            const positionTypeSelect = document.getElementById("position_type");
            const startCoordLink = document.getElementById("start_coord_link");
            const endCoordLink = document.getElementById("end_coord_link");

            // 设置输入框为只读状态
            if (startInput) startInput.setAttribute('readonly', 'readonly');
            if (endInput) endInput.setAttribute('readonly', 'readonly');

            // 显示查看和重设按钮，隐藏确定按钮
            if (msgdiv) {
                const buttons = msgdiv.getElementsByTagName('button');
                for (let i = 0; i < buttons.length; i++) {
                    const button = buttons[i];
                    const buttonText = button.textContent.trim();
                    if (buttonText === '确定') {
                        button.style.display = 'none';
                    } else if (buttonText === '查看' || buttonText === '重设') {
                        button.style.display = 'inline-block';
                    }
                }
            }

            // 隐藏position_type下拉框和坐标链接
            if (positionTypeSelect) positionTypeSelect.style.display = 'none';
            if (startCoordLink) startCoordLink.style.display = 'none';
            if (endCoordLink) endCoordLink.style.display = 'none';

            // 只有在路线规划成功后才更新菜单项的勾选标记
            const randomRouteItem = document.getElementById("random_route");
            const specifiedRouteItem = document.getElementById("specified_route");
            if (randomRouteItem && specifiedRouteItem) {
                // 移除随机路线的勾选标记
                randomRouteItem.textContent = randomRouteItem.textContent.replace(' ✓', '');
                // 添加勾选标记到指定路线
                if (!specifiedRouteItem.textContent.includes('✓')) {
                    specifiedRouteItem.textContent += ' ✓';
                }
            }
        } else {
            // 路线规划失败，不更新任何状态和UI
            alert("路线规划失败，状态码: " + driving.getStatus());
        }
    }
});


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

// 初始化3D视图
var view = new mapvgl.View({map: map});
var threeLayer = new mapvgl.ThreeLayer({notUpdateSize: false});
view.addLayer(threeLayer);

// 测试threeLayer点击事件
// threeLayer.addEventListener('click', function(e) {
//     console.log('threeLayer click event triggered!', e);
// });

// 添加光源
var lights = [];
lights[0] = new THREE.PointLight(0xffffff, 1, 0);
lights[0].position.set(0, -1000, 1000);
threeLayer.scene.add(lights[0]);

// 动画循环
var clock = new THREE.Clock();
var mixers = []; // 用于保存动画混合器
var meshes = []; // 用于保存所有的 Mesh
var geoGroups = []; // 用于保存所有的 THREE.Group 实例
var person_gltfLoader = new mapvgl.THREELoader.GLTFLoader();

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
        scaleMultiplier = scaleMultiplier*10;
    } else {
        scaleMultiplier = parseFloat(scaleParam);
    }

    return {
        rotationX: parseFloat(params[0]) || 0,      // 第1个数字：x轴旋转（角度）
        rotationY: parseFloat(params[1]) || 0,      // 第2个数字：y轴旋转（角度）
        rotationZ: parseFloat(params[2]) || 0,      // 第3个数字：z轴旋转（角度）
        altitude: parseFloat(params[3]) || 0,       // 第4个数字：海拔高度
        scaleMultiplier: scaleMultiplier,     // 第5个数字：缩放比例乘数,百度比google小大约1.8倍
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

// 加载GLTF模型的函数
function loadModel(persondata) {
    let url = persondata["avatar_3d"];
    let pos = persondata["location"];
    let llPoint = new BMapGL.Point(pos[0], pos[1]);
    console.log("llPoint", llPoint);
    const mcpoint = BMapGL.Projection.convertLL2MC(llPoint);
    console.log("mcpoint", mcpoint)

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

    person_gltfLoader.load(url, function (obj) {
        let model = obj.scene;
        model.rotateX(90 / 180 * Math.PI); // 旋转模型

        // 计算模型的包围体积
        const box = new THREE.Box3().setFromObject(model);
        const size = box.getSize(new THREE.Vector3());
        const height = size.y; // 模型的高度
        alert(height);
        console.log("the height33:", height);
        // 获取模型包围盒

        const modelHeight = box.max.y - box.min.y;
        console.log("the modelHeight333:", modelHeight);

        // 根据高度调整缩放比例
        const desiredHeight = 150; // 你期望的高度
        let scale = desiredHeight / height;


        // 如果有文件名参数，应用缩放乘数
        if (modelParams && modelParams.scaleMultiplier) {
            scale = scale * modelParams.scaleMultiplier;
            console.log(`应用缩放乘数 ${modelParams.scaleMultiplier}, 最终缩放比例: ${scale}`);
        } else {
            console.log("scale", scale);
        }


        // 设置模型的缩放、旋转和位置
        model.scale.set(scale, scale, scale);

        let geoGroup = new THREE.Group();
        geoGroup.add(model);

        // 定位模型，考虑海拔高度
        let altitude = 0;
        if (modelParams && modelParams.altitude) {
            altitude = modelParams.altitude;
            console.log(`应用海拔高度: ${altitude}`);
        }
        geoGroup.position.set(mcpoint.lng, mcpoint.lat, altitude);

        // 设置旋转
        if (modelParams) {
            // 使用文件名中解析的旋转参数（转换为弧度）
            // 注意：百度地图中模型已经先旋转了90度（rotateX(90 / 180 * Math.PI)）
            model.rotation.x += THREE.MathUtils.degToRad(modelParams.rotationX) - Math.PI / 30;
            model.rotation.y = THREE.MathUtils.degToRad(modelParams.rotationY);
            model.rotation.z = THREE.MathUtils.degToRad(modelParams.rotationZ);
            console.log(`应用旋转: x=${modelParams.rotationX}°, y=${modelParams.rotationY}°, z=${modelParams.rotationZ}°`);
        } else {
            // 使用默认旋转：调整模型头部往上抬一点
            model.rotation.x -= Math.PI / 30;
        }

        console.log("mcpoint.lng", mcpoint.lng);
        console.log("mcpoint.lat", mcpoint.lat);
        geoGroup.name = persondata["nation_id"];
        geoGroup.userData = persondata;
        threeLayer.add(geoGroup);
        geoGroups.push(geoGroup); // 将 geoGroup 添加到数组中

        // 处理动画
        if (obj.animations && obj.animations.length > 0) {
            let mixer = new THREE.AnimationMixer(obj.scene);

            // 确定要播放的动画索引
            let animIndex = 0;
            if (modelParams && modelParams.animationIndex !== undefined) {
                animIndex = modelParams.animationIndex;
                // 确保索引在有效范围内
                if (animIndex >= obj.animations.length) {
                    console.warn(`动画索引 ${animIndex} 超出范围，使用索引 0`);
                    animIndex = 0;
                }
            }

            const action = mixer.clipAction(obj.animations[animIndex]);
            mixer.timeScale = 0.5;
            const duration = obj.animations[animIndex].duration || 1;
            action.setDuration(duration).play();
            mixers.push(mixer); // 将混合器添加到数组中
            console.log(`模型动画已启动, 播放动画索引: ${animIndex}`);
        }

        let modelMeshes = findMeshes(model); // 查找所有 Mesh
        modelMeshes.forEach(mesh => {
            mesh.userData = persondata; // 将数据集绑定到每个 Mesh 的 userData 属性
        });
        meshes.push(...modelMeshes); // 添加到全局 meshes 数组中
    });
}

function removeModel(nation_id) {
    const groupIndex = geoGroups.findIndex(group => group.name === nation_id);

    if (groupIndex !== -1) {
        // 从 threeLayer 中移除该 geoGroup
        threeLayer.remove(geoGroups[groupIndex]);
        // 从 geoGroups 数组中移除该 geoGroup
        geoGroups.splice(groupIndex, 1);
    }

    //  currentModel = threeLayer.scene.getObjectByName(nation_id);
    //
    // threeLayer.remove(currentModel);

    // 如果想隐藏模型（而不是删除）
    // currentModel.visible = false;
}

// 查找所有 Mesh
function findMeshes(object) {
    const meshes = [];
    object.traverse((child) => {
        if (child.isMesh) {
            meshes.push(child);
        }
    });
    return meshes;
}

// 点击事件处理
var raycaster = new THREE.Raycaster();
var mouse = new THREE.Vector2();
var currentModel = null;

map.addEventListener('click', function (e) {
    mouse.x = (e.x / window.innerWidth) * 2 - 1;
    mouse.y = -(e.y / window.innerHeight) * 2 + 1;
    raycaster.setFromCamera(mouse, threeLayer.camera);

    // 使用已找到的 Mesh 对象进行点击检测
    // const intersects = raycaster.intersectObjects([...meshes1, ...meshes2], true);
    const intersects = raycaster.intersectObjects([...meshes], true);

    if (intersects.length > 0) {
        const intersectedObject = intersects[0].object;
        alert(intersectedObject.userData.nation_id);
        alert(intersectedObject.userData["nation_id"]);
        nation_id = intersectedObject.userData.nation_id;
        currentModel = threeLayer.scene.getObjectByName(nation_id);
        showprofile3d(currentModel);


    } else {

        currentModel = null;
    }
});

map.addEventListener('click', function (e) {
    alert("in clicking");
    if (instruct_to_move_flag == true) {


        my_point = getPersonPointByNationId(nation_id_me);

        alert('我当前位置经纬度：' + my_point.lng + ',' + my_point.lat);

        alert('点击位置经纬度：' + e.latlng.lng + ',' + e.latlng.lat);


        last_click_point = new BMapGL.Point(e.latlng.lng, e.latlng.lat);

        distance = map.getDistance(my_point, last_click_point);
        alert('当前位置到点击位置相距：' + distance);


        centerpoint = map.getCenter();
        alert('地图中心点位置经纬度：' + centerpoint.lng + ',' + centerpoint.lat);


        Viewport = map.getViewport();
        viewcenter = Viewport.center;
        alert('视野中心点位置经纬度：' + viewcenter.lng + ',' + viewcenter.lat);

        // var list = cusLayer.getCustomOverlays();
        // console.log(list[0]);
        // list[0].setPoint(new BMapGL.Point(e.latlng.lng, e.latlng.lat), false);
        //
        // mercatorPoint = new BMapGL.Point(e.latlng.lng, e.latlng.lat);
        // console.log("mercatorPoint", mercatorPoint);
        // const geoCoord2 = BMapGL.Projection.convertLL2MC(mercatorPoint);
        // console.log("geoCoord2", geoCoord2)
        //
        //
        // currentAircraft.position.set(geoCoord2.lng, geoCoord2.lat, 0);
        //
        //
        // console.log(list[0]);

        setPersonModelPointByNationId(nation_id_me, e.latlng)

        service = getServiceForUser();
        if (service !== null) {
            const userConfirmed = confirm("此处有相应的应用服务，要继续吗？");
            if (userConfirmed) {
                alert("您选择了确定！");
                api_object.request_service(service.type, service.address);
            } else {
                return;
            }

        }

        // map.setDefaultCursor("url(http://webmap0.bdimg.com/image/api/openhand.cur) 8 8,default");
        // instruct_to_move_flag = false;
        map.cancelViewAnimation(animation);

    }
});
// 监听缩放事件
map.addEventListener("zoomend", function () {
    // 获取当前的缩放级别
    var currentZoom = map.getZoom();

    // 打印当前缩放级别
    // alert("当前缩放级别为: " + currentZoom);
    console.log("当前缩放级别为: " + currentZoom);

    // 可以在这里添加其他逻辑，比如根据缩放级别进行数据更新等
});

function getAllGroups(scene) {
    const groups = [];
    scene.traverse((object) => {
        if (object.isGroup) { // 检查是否是 THREE.Group
            groups.push(object);
        }
    });
    return groups;
}

function checkAnimationStart() {
    if (animationStarted) return;

    if (modelLoadStatus.building) {

        animate(0);
        animationStarted = true;
        console.log("所有模型加载完成，启动动画");
    }
}


function updateHouseModel(position, scale, rotation) {
    // 如果threeLayer未定义，直接返回
    if (typeof threeLayer === 'undefined' || !threeLayer.scene) {
        console.warn('threeLayer未初始化，无法更新模型');
        return;
    }

    // 调试：列出场景中的所有对象
    console.log('Scene objects:');
    threeLayer.scene.traverse(function(object) {
        console.log('Object name:', object.name, 'Type:', object.type);
    });

    // 查找场景中的houseModel Group（注意：这是Group，不是模型本身）
    let houseModelGroup = threeLayer.scene.getObjectByName('houseModel');

    // 如果通过名称找不到，尝试其他方式查找
    if (!houseModelGroup) {
        threeLayer.scene.traverse(function(object) {
            if (object.name && object.name.includes('house')) {
                houseModelGroup = object;
                console.log('Found house-related object:', object.name);
            }
        });
    }

    if (houseModelGroup) {
        console.log('Found houseModelGroup:', houseModelGroup);

        // 转换坐标 - 使用与参考代码相同的方式
        const llPoint = new BMapGL.Point(position.lng, position.lat);
        const mercatorPoint = BMapGL.Projection.convertLL2MC(llPoint);
        console.log("mercatorPoint", mercatorPoint);

        // 更新Group位置（模型在Group内部，Group的位置就是模型在地图上的位置）
        houseModelGroup.position.set(mercatorPoint.lng, mercatorPoint.lat, 0);

        // 确保Group可见
        houseModelGroup.visible = true;

        // 更新Group内模型的缩放
        if (houseModelGroup.children.length > 0) {
            const model = houseModelGroup.children[0];
            model.scale.set(scale, scale, scale);

            // 更新模型的旋转（保持原有的Math.PI / 2偏移）
            model.rotation.x = (rotation.x || 0) + Math.PI / 2;
            model.rotation.y = rotation.y || 0;
            model.rotation.z = rotation.z || 0;

            // 确保模型可见
            model.visible = true;
        }

        // 重新渲染
        threeLayer.render();

        console.log('House model updated:', {
            position: {lng: position.lng, lat: position.lat},
            mercator: {lng: mercatorPoint.lng, lat: mercatorPoint.lat},
            scale: scale,
            rotation: rotation
        });

        // 添加调试信息，检查模型是否在视野范围内
        const mapCenter = map.getCenter();
        const mapZoom = map.getZoom();
        console.log('Map center:', mapCenter, 'Zoom:', mapZoom);
        console.log('Model position:', mercatorPoint);

        // 计算模型与地图中心的距离
        const centerMercator = BMapGL.Projection.convertLL2MC(new BMapGL.Point(mapCenter.lng, mapCenter.lat));
        const distance = Math.sqrt(
            Math.pow(mercatorPoint.lng - centerMercator.lng, 2) +
            Math.pow(mercatorPoint.lat - centerMercator.lat, 2)
        );
        console.log('Distance from center (mercator units):', distance);

        // 检查模型边界
        const box = new THREE.Box3().setFromObject(houseModelGroup);
        console.log('Model bounding box:', box);

        // 检查模型矩阵
        console.log('Model matrix:', houseModelGroup.matrix);
    } else {
        console.warn('未找到houseModel模型Group');

        // 尝试列出所有对象再次确认
        console.log('All objects in scene:');
        threeLayer.scene.traverse(function(object) {
            console.log('Name:', object.name, 'Type:', object.type);
        });
    }
}

function queryAddress() {
    //创建地址解析器实例
    var address = document.getElementById("address").value;
    var myGeo = new BMapGL.Geocoder();
    if (marker) {
        map.removeOverlay(marker);
    }
    // 将地址解析结果显示在地图上，并调整地图视野
    myGeo.getPoint(address, function (point) {
        if (point) {
            map.centerAndZoom(point, 16);
            marker = new BMapGL.Marker(point, {title: address});
            map.addOverlay(marker)
            init_address = address;
            home_position = point;
        } else {
            alert('您选择的地址没有解析到结果！');
        }
    }, '')

}



function set_move_status() {

    if (instruct_to_move_flag) {
        instruct_to_move_flag = false;
        map.setDefaultCursor("url(http://webmap0.bdimg.com/image/api/openhand.cur) 8 8,default");
    } else {
        instruct_to_move_flag = true;
        document.body.classList.toggle('crosshair-cursor');
        // 为地图容器设置鼠标光标为十字形
        document.getElementById('map').classList.add('crosshair-cursor');
        alert(map.getDefaultCursor());
        map.getDefaultCursor();
        map.setDefaultCursor("crosshair");
        showAlert("请点击地图来指定要移动的目标位置。");
    }

}

var opts = {
    width: 200,     // 信息窗口宽度200
    height: 100,     // 信息窗口高度100
    title: "", // 信息窗口标题
    offset: new BMapGL.Size(30, -50),
}

var infoWindow = new BMapGL.InfoWindow("你好呀，我是Y宝", opts);  // 创建信息窗口对象

var infoWindow2 = new BMapGL.InfoWindow("hello,你好！", opts);  // 创建信息窗口对象

function start_talk_to_it(nation_id, content) {
    // div = hiddenPoints[nation_id];
    // div.style.display = 'none';
    alert(nation_id);
    alert(map.getZoom());
    person_target_point = getPersonPointByNationId(nation_id);
    person_data_me = getPersonDataByNationId(nation_id_me);
    person_target = getPersonDataByNationId(nation_id);

    loadModel(person_target);


    let person = getPersonDataByNationId(nation_id);
    alert(person_data_me["account"]);
    alert(person_target["account"]);
    map.setHeading(0);
    // map.setTilt(0);
    console.log("the user point:");
    console.log(person_target_point);
    console.log(person_target_point.lng);
    console.log(person_target_point.lat);
    console.log(person_target_point.lng);
    console.log(person_target_point.lat);
    // cusLayer.updateData(personsdata2);

    my_new_point = new BMapGL.Point(person_target_point.lng, person_target_point.lat - 0.01);

    setPersonModelPointByNationId(nation_id_me, my_new_point);
    setPersonPointByNationId(nation_id_me,my_new_point.lng,my_new_point.lat);

    div = document.getElementById(nation_id);
            if (!div) {
                console.warn(`Element with ID ${nation_id} not found on map`);
                return;
            }
            hiddenPoints[param_1] = div;
div = hiddenPoints[nation_id];
    div.style.display = 'none';
}

function talk_to_it(nation_id, content) {
    div = hiddenPoints[nation_id];
    div.style.display = 'none';
    alert(nation_id);
    alert(map.getZoom());
    person_target_point = getPersonPointByNationId(nation_id);
    person_data_me = getPersonDataByNationId(nation_id_me);
    person_target = getPersonDataByNationId(nation_id);

    loadModel(person_target);


    let person = getPersonDataByNationId(nation_id);
    alert(person_data_me["account"]);
    alert(person_target["account"]);
    map.setHeading(0);
    // map.setTilt(0);
    console.log("the user point:");
    console.log(person_target_point);
    console.log(person_target_point.lng);
    console.log(person_target_point.lat);
    console.log(person_target_point.lng);
    console.log(person_target_point.lat);
    // cusLayer.updateData(personsdata2);

    my_new_point = new BMapGL.Point(person_target_point.lng, person_target_point.lat - 0.01);

    setPersonModelPointByNationId(nation_id_me, my_new_point);
    // var point = new BMapGL.Point(116.28882, 39.72164);
    let point = my_new_point;

    let opts = {
        width: 200,     // 信息窗口宽度200
        height: 100,     // 信息窗口高度100
        title: person_data_me["nick_name"], // 信息窗口标题
        offset: new BMapGL.Size(30, -70),
    }
    let hello_msg = "Hello";
    let infoWindow_me = new BMapGL.InfoWindow(hello_msg, opts);  // 创建信息窗口对象

    map.openInfoWindow(infoWindow_me, point); //开启信息窗口
    if (content != "__no_info_window__") {

        send_im(person_data_me["account"], person_target["account"], hello_msg);
    }
    // var point2 = new BMapGL.Point(116.28882, 39.71564);
    point2 = person_target_point;

    let opts2 = {
        width: 200,     // 信息窗口宽度200
        height: 100,     // 信息窗口高度100
        title: person_target["nick_name"], // 信息窗口标题
        offset: new BMapGL.Size(30, -70),
    }


    // 使用setTimeout来延迟1.5秒后打开第二个信息窗口
    let infoWindow_person_target = new BMapGL.InfoWindow("Nice to meet you.", opts2);  // 创建信息窗口对象


        setTimeout(function () {
            map.openInfoWindow(infoWindow_person_target, point2);
        }, 1500);


        setTimeout(function () {
            map.closeInfoWindow();
        }, 3000);

}

function stop_talk_to_it(nation_id) {
    removeModel(nation_id);
    div = hiddenPoints[nation_id];
    div.style.display = 'block';
    map.closeInfoWindow();
}


// 定义一个标志变量，用于指示是否正在显示信息窗口
let showing_info_flag = false;

function send_chat_msg(lng, lat, msg,send_person_name="") {
    // 检查当前是否正在展示信息窗口
    if (showing_info_flag) {
        console.log("信息窗口仍在显示。请稍后...");

        // 递归调用，稍后再尝试发送消息
        setTimeout(() => send_chat_msg(lng, lat, msg,send_person_name), 1000);
        return; // 如果正在显示，则退出函数
    }

    // 设置标志为 true，表示信息窗口正在显示
    showing_info_flag = true;

    // 创建地图坐标点
    var point = new BMapGL.Point(lng, lat);


    let opts = {
    width: 200,     // 信息窗口宽度200
    height: 100,     // 信息窗口高度100
    title: send_person_name, // 信息窗口标题
    offset: new BMapGL.Size(30, -50),
}

let infoWindow_chat = new BMapGL.InfoWindow(msg, opts);  // 创建信息窗口对象




    // 打开信息窗口
    map.openInfoWindow(infoWindow_chat, point);

    // 设置定时器，延迟5500毫秒后关闭信息窗口并重置标志
    setTimeout(function () {
        map.closeInfoWindow(); // 关闭信息窗口
        showing_info_flag = false; // 重置标志
    }, 3000);

    // 调试输出
    console.log("信息窗口已打开。");
}



function showprofile(nation_id) {
    alert("showprofile");

    let person_point = getPersonPointByNationId(nation_id);
    alert("person_point");
    console.log("person_point");
    console.log(person_point);
    let person = getPersonDataByNationId(nation_id);
    var sContent = `
    <p style='margin:0;line-height:1.5;font-size:13px;text-indent:2em'>
    ${person["profile"]}
    <a href="#" onclick="talk_to_it('${nation_id}','');return false;">和Ta聊天</a>
    </p></div>`;
    alert("showprofile22");
    var opts = {
        width: 200,     // 信息窗口宽度200
        height: 100,     // 信息窗口高度100
        title: `<h4 style='margin:0 0 5px 0;'>${person["nick_name"]}</h4>`, // 信息窗口标题
        offset: new BMapGL.Size(30, -50),
    }
    let profile_info_window = new BMapGL.InfoWindow(sContent, opts);
    alert("showprofile2333cjrok");
    // 监听 InfoWindow 的关闭事件
profile_info_window.addEventListener("close", function() {
    // 当 InfoWindow 关闭时执行的代码
    alert(1);
    closeprofile();
});

    // var point = new BMapGL.Point(116.28882, 39.72164);
    var point = getPersonPointByNationId(nation_id);
    console.log("the point", point)
    map.openInfoWindow(profile_info_window, point); //开启信息窗口
    // map.openInfoWindow(profile_info_window, point); //开启信息窗口
    // map.openInfoWindow(profile_info_window, point); //开启信息窗口
    // map.openInfoWindow(infoWindow3, point); //开启信息窗口
    // map.openInfoWindow(infoWindow3, point); //开启信息窗口
    alert("showprofile444");
    open_sns_profile(person['sns_url']);

}

function closeprofile(){
    // map.closeInfoWindow();
    alert("closing");
    close_sns_profile()
}

function showprofile3d(geoGroup) {
    nation_id = geoGroup.userData.nation_id;
    let person = geoGroup.userData;
    var sContent = `<h4 style='margin:0 0 5px 0;'>${person["nick_name"]}</h4>
    <p style='margin:0;line-height:1.5;font-size:13px;text-indent:2em'>
    ${person["profile"]}
    <a href="#" onclick="stop_talk_to_it('${nation_id}');return false;">结束聊天</a>
    </p></div>`;

    var opts = {
        width: 200,     // 信息窗口宽度200
        height: 100,     // 信息窗口高度100
        title: "", // 信息窗口标题
        offset: new BMapGL.Size(30, -50),
    }
    var infoWindow3 = new BMapGL.InfoWindow(sContent, opts);


    // 假设 geoGroup2.position 的 x 和 y 是墨卡托坐标
    const mercatorX = geoGroup.position.x;
    const mercatorY = geoGroup.position.y;
// const mercatorX = intersectedObject.position.x;
// const mercatorY = intersectedObject.position.y;

// 创建百度地图的 Point 对象
    const mercatorPoint = new BMapGL.Point(mercatorX, mercatorY);

// 将墨卡托坐标转换为经纬度坐标
    const geoCoord2 = BMapGL.Projection.convertMC2LL(mercatorPoint);

    console.log('经度:', geoCoord2.lng); // 输出经度
    console.log('纬度:', geoCoord2.lat); // 输出纬度
    let point = geoCoord2;


    map.openInfoWindow(infoWindow3, point); //开启信息窗口


    // 获取 threeLayer 中的所有 THREE.Group
    const allGroups = getAllGroups(threeLayer.scene);
    console.log(allGroups); // 输出所有 THREE.Group 实例

    var retrievedGeoGroup1 = threeLayer.scene.getObjectByName("geoGroup1");
    console.log("retrievedGeoGroup1", retrievedGeoGroup1);

}





//navigate places
var keyFrames = [
    {
        center: new BMapGL.Point(116.307092, 40.054922),
        zoom: 20,
        tilt: 50,
        heading: 0,
        percentage: 0
    },
    {
        center: new BMapGL.Point(116.307631, 40.055391),
        zoom: 21,
        tilt: 70,
        heading: 0,
        percentage: 0.1
    },
    {
        center: new BMapGL.Point(116.306858, 40.057887),
        zoom: 21,
        tilt: 70,
        heading: 0,
        percentage: 0.25
    },
    {
        center: new BMapGL.Point(116.306858, 40.057887),
        zoom: 21,
        tilt: 70,
        heading: -90,
        percentage: 0.35
    },
    {
        center: new BMapGL.Point(116.307904, 40.058118),
        zoom: 21,
        tilt: 70,
        heading: -90,
        percentage: 0.45
    },
    {
        center: new BMapGL.Point(116.307904, 40.058118),
        zoom: 21,
        tilt: 70,
        heading: -180,
        percentage: 0.55
    },
    {
        center: new BMapGL.Point(116.308902, 40.055954),
        zoom: 21,
        tilt: 70,
        heading: -180,
        percentage: 0.75
    },
    {
        center: new BMapGL.Point(116.308902, 40.055954),
        zoom: 21,
        tilt: 70,
        heading: -270,
        percentage: 0.85
    },
    {
        center: new BMapGL.Point(116.307779, 40.055754),
        zoom: 21,
        tilt: 70,
        heading: -360,
        percentage: 0.95
    },
    {
        center: new BMapGL.Point(116.307092, 40.054922),
        zoom: 20,
        tilt: 50,
        heading: -360,
        percentage: 1
    },
];

var view_opts = {
    duration: 50000,
    delay: 1500,
    interation: '2'
};

var view_animation = new BMapGL.ViewAnimation(keyFrames, view_opts);

var auto_navigate_flag=false;

function toggleNavigate(){
    if(auto_navigate_flag){
        cancelNavigate();
        auto_navigate_flag=false;
    }else{
        autoNavigate();
        auto_navigate_flag = true;
    }
}

function autoNavigate() {
    map.centerAndZoom(new BMapGL.Point(116.307092, 40.054922), 20);  // 初始化地图,设置中心点坐标和地图级别
    map.enableScrollWheelZoom(true);     // 开启鼠标滚轮缩放
    map.setTilt(50);      // 设置地图初始倾斜角
    // 定义关键帧

    displayOptions={
            indoor: false,
            poiText: true,
            poiIcon: false,
            building: true,
        }
        map.setDisplayOptions(displayOptions);


    // 监听事件
    view_animation.addEventListener('animationstart', function (e) {
        console.log('start')
    });
    view_animation.addEventListener('animationiterations', function (e) {
        console.log('onanimationiterations')
    });
    view_animation.addEventListener('animationend', function (e) {
        console.log('end');
        cancelNavigate();

    });
    // 开始播放动画
    setTimeout('map.startViewAnimation(view_animation)', 1);

}

function cancelNavigate(){
    auto_navigate_flag=false;
        displayOptions={
            indoor: false,
            poiText: false,
            poiIcon: false,
            building: false,
        }
        map.setDisplayOptions(displayOptions);
    map.cancelViewAnimation(view_animation);
    refresh();
}
