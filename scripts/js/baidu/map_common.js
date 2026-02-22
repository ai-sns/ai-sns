// todo
// Delay initializing the map center until current_position is set
function initializeMapCenter() {
    var centerPoint;
    // Prefer global current_position if present and has valid lng/lat
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

// If current_position already exists, initialize immediately; otherwise wait
if (typeof window.current_position !== 'undefined' && window.current_position !== null) {
    initializeMapCenter();
} else {
    // Delay execution until current_position is set (set in interact_python)
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

            // Get the route plan
            const plan = result.getPlan(0);
            if (plan) {
                alert("距离时长");
                distance = plan.getDistance(true); // 获取距离，true表示返回数值
                duration = plan.getDuration(true); // 获取时间，true表示返回数值
                alert(distance);
                alert(duration);

                // Convert distance to a float and compute move_duration
                // First extract numeric value from strings like "35.5km"
                var distanceValue = parseFloat(String(distance).replace(/[^\d\.]/g, ''));
                if (!isNaN(distanceValue)) {
                    move_duration = distanceValue / 0.05;
                }
            }

            gpsPositions = getAllGpsPositions(result);
            console.log("规划成功，坐标数:", gpsPositions.length);

            const start = document.getElementById("start").value.trim();
            const end = document.getElementById("end").value.trim();

            // Save start/end to backend
            update_map_setting("route_start", start);
            update_map_setting("route_end", end);

            // Update route status to playing
            route_status = "playing";
            update_map_setting("route_status", route_status);

            // Only user-initiated route planning resets progress/current position
            // Auto planning (e.g. on page load) keeps previous progress
            if (isUserInitiatedRoutePlanning) {
                update_map_setting("route_current_position", "");
                update_map_setting("route", "");
                // Reset flag
                isUserInitiatedRoutePlanning = false;
            }

            // Get start/end input elements
            const startInput = document.getElementById('start');
            const endInput = document.getElementById('end');
            const msgdiv = document.getElementById("setroute");
            const positionTypeSelect = document.getElementById("position_type");
            const startCoordLink = document.getElementById("start_coord_link");
            const endCoordLink = document.getElementById("end_coord_link");

            // Make inputs read-only
            if (startInput) startInput.setAttribute('readonly', 'readonly');
            if (endInput) endInput.setAttribute('readonly', 'readonly');

            // Show view/reset buttons, hide confirm button
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

            // Hide position_type select and coordinate links
            if (positionTypeSelect) positionTypeSelect.style.display = 'none';
            if (startCoordLink) startCoordLink.style.display = 'none';
            if (endCoordLink) endCoordLink.style.display = 'none';

            // Only update menu checkmarks after route planning succeeds
            const randomRouteItem = document.getElementById("random_route");
            const specifiedRouteItem = document.getElementById("specified_route");
            if (randomRouteItem && specifiedRouteItem) {
                // Remove ✓ from random route
                randomRouteItem.textContent = randomRouteItem.textContent.replace(' ✓', '');
                // Add ✓ to specified route
                if (!specifiedRouteItem.textContent.includes('✓')) {
                    specifiedRouteItem.textContent += ' ✓';
                }
            }
        } else {
            // Route planning failed; do not update status or UI
            alert("路线规划失败，状态码: " + driving.getStatus());
        }
    }
});


const FETCH_RETRIES = 30;
const INITIAL_RETRY_DELAY = 1000;
const REQUEST_TIMEOUT = 80000;

async function loadPersonsData(url, retries = FETCH_RETRIES, retryDelay = INITIAL_RETRY_DELAY) {
    // Validate input parameters
    if (typeof url !== 'string' || !url.trim()) {
        throw new Error('无效的URL参数');
    }

    // Inner function that performs the request
    async function fetchData(retriesLeft, delay) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);

        try {
            console.log(`剩余重试次数: ${retriesLeft}`);

            // Add random query param to avoid caching
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

            // Try parsing JSON response
            const data = await response.json();
            // showAlert(`Request succeeded, response data: ${data}`);
            return data;

        } catch (error) {
            clearTimeout(timeoutId);

            // Check whether it is a timeout error
            if (error.name === 'AbortError') {
                console.error('请求超时被取消');
                showAlert('请求超时被取消');
                throw new Error('请求超时');
            }

            // Retry logic
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

// Wrap async operation loadPersonsData
async function load_persons_data_and_show() {
    const resolvedBaseUrl = (typeof API_BASE_URL !== 'undefined' && API_BASE_URL)
        ? API_BASE_URL
        : ((typeof window !== 'undefined' && window.__AGENT_SERVER__) ? window.__AGENT_SERVER__ : '');
    const normalizedBaseUrl = (resolvedBaseUrl || '').replace(/\/+$/, '');
    const dataUrl = `${normalizedBaseUrl}/api/get_people_list/`;
    const nation_id = nation_id_me;
    try {
        const data = await loadPersonsData(dataUrl); // Load person data
        console.log("成功加载人员数据:", data);
        showAlert(`用户数据已加载成功。`);

        // Filter out items whose nation_id equals the input value
        personsdata = data.filter(person => person.nation_id !== nation_id);

        // Show updated data points
        showpoints();
    } catch (error) {
        console.error("人员数据加载失败，建议:",
            error.name === 'AbortError'
                ? '检查网络连接或稍后重试'
                : '联系系统管理员');
    }
}

// Initialize 3D view
var view = new mapvgl.View({map: map});
var threeLayer = new mapvgl.ThreeLayer({notUpdateSize: false});
view.addLayer(threeLayer);

// Test threeLayer click event
// threeLayer.addEventListener('click', function(e) {
//     console.log('threeLayer click event triggered!', e);
// });

// Add lights
var lights = [];
lights[0] = new THREE.PointLight(0xffffff, 1, 0);
lights[0].position.set(0, -1000, 1000);
threeLayer.scene.add(lights[0]);

// Animation loop
var clock = new THREE.Clock();
var mixers = []; // Stores animation mixers
var meshes = []; // Stores all Mesh instances
var geoGroups = []; // Stores all THREE.Group instances
var person_gltfLoader = new mapvgl.THREELoader.GLTFLoader();

/**
 * Parse model parameters from filename
 * Filename format: EnglishName_xRot_yRot_zRot_altitude_scale_animationIndex.glb
 * Example: ctboyblue_0_0_0_0_1_0.glb
 * @param {string} filename - filename
 * @returns {object|null} Parsed params; returns null if parsing fails
 */
function parseModelFilename(filename) {
    // Strip path and keep only the filename
    const baseName = filename.split('/').pop().split('\\').pop();
    // Strip extension
    const nameWithoutExt = baseName.replace(/\.[^/.]+$/, '');

    // Match: starts with letters, followed by underscore-separated numbers
    const match = nameWithoutExt.match(/^[a-zA-Z]+(.*)$/);
    if (!match || !match[1]) {
        return null;
    }

    // Parse underscore-separated numeric params after the letter prefix
    const paramString = match[1];
    const params = paramString.split('_').filter(s => s !== '');

    if (params.length < 6) {
        console.warn(`文件名参数不足6个: ${filename}, 找到 ${params.length} 个参数`);
        return null;
    }

    // Parse scale parameter (5th number, index 4)
    // If it starts with 0, treat as decimal, e.g. 05 => 0.5
    let scaleMultiplier = 1;
    const scaleParam = params[4];
    if (scaleParam.startsWith('0') && scaleParam.length > 1) {
        // Starts with 0: convert to decimal
        scaleMultiplier = parseFloat('0.' + scaleParam.substring(1));
        scaleMultiplier = scaleMultiplier*10;
    } else {
        scaleMultiplier = parseFloat(scaleParam);
    }

    return {
        rotationX: parseFloat(params[0]) || 0,      // 1st number: X rotation (degrees)
        rotationY: parseFloat(params[1]) || 0,      // 2nd number: Y rotation (degrees)
        rotationZ: parseFloat(params[2]) || 0,      // 3rd number: Z rotation (degrees)
        altitude: parseFloat(params[3]) || 0,       // 4th number: altitude
        scaleMultiplier: scaleMultiplier,     // 5th number: scale multiplier (Baidu is ~1.8x smaller than Google)
        animationIndex: parseInt(params[5]) || 0    // 6th number: animation index
    };
}

/**
 * Check whether URL is a web URL
 * @param {string} url - URL string
 * @returns {boolean} True if it's a web URL
 */
function isWebUrl(url) {
    return url.startsWith('http://') || url.startsWith('https://') || url.startsWith('//');
}

// GLTF model loader
function loadModel(persondata) {
    let url = persondata["avatar_3d"];
    let pos = persondata["location"];
    let llPoint = new BMapGL.Point(pos[0], pos[1]);
    console.log("llPoint", llPoint);
    const mcpoint = BMapGL.Projection.convertLL2MC(llPoint);
    console.log("mcpoint", mcpoint)

    // Parse filename params
    let modelParams = null;

    // If not a web URL, add directory prefix and parse filename params
    if (!isWebUrl(url)) {
        // Parse params from filename
        modelParams = parseModelFilename(url);
        if (modelParams) {
            console.log(`解析到模型参数:`, modelParams);
        }
        // Add directory prefix
        url = '/scripts/avatar3d/' + url;
        console.log(`模型完整路径: ${url}`);
    }

    person_gltfLoader.load(url, function (obj) {
        let model = obj.scene;
        model.rotateX(90 / 180 * Math.PI); // Rotate model

        // Compute model bounding box
        const box = new THREE.Box3().setFromObject(model);
        const size = box.getSize(new THREE.Vector3());
        const height = size.y; // Model height
        alert(height);
        console.log("the height33:", height);
        // Get model bounding box

        const modelHeight = box.max.y - box.min.y;
        console.log("the modelHeight333:", modelHeight);

        // Adjust scale based on height
        const desiredHeight = 150; // Desired height
        let scale = desiredHeight / height;


        // If filename params exist, apply scale multiplier
        if (modelParams && modelParams.scaleMultiplier) {
            scale = scale * modelParams.scaleMultiplier;
            console.log(`应用缩放乘数 ${modelParams.scaleMultiplier}, 最终缩放比例: ${scale}`);
        } else {
            console.log("scale", scale);
        }


        // Set model scale/rotation/position
        model.scale.set(scale, scale, scale);

        let geoGroup = new THREE.Group();
        geoGroup.add(model);

        // Position model and account for altitude
        let altitude = 0;
        if (modelParams && modelParams.altitude) {
            altitude = modelParams.altitude;
            console.log(`应用海拔高度: ${altitude}`);
        }
        geoGroup.position.set(mcpoint.lng, mcpoint.lat, altitude);

        // Set rotation
        if (modelParams) {
            // Use rotation params parsed from filename (convert to radians)
            // Note: in Baidu map the model has already been rotated 90 degrees (rotateX(90 / 180 * Math.PI))
            model.rotation.x += THREE.MathUtils.degToRad(modelParams.rotationX) - Math.PI / 30;
            model.rotation.y = THREE.MathUtils.degToRad(modelParams.rotationY);
            model.rotation.z = THREE.MathUtils.degToRad(modelParams.rotationZ);
            console.log(`应用旋转: x=${modelParams.rotationX}°, y=${modelParams.rotationY}°, z=${modelParams.rotationZ}°`);
        } else {
            // Default rotation: tilt the head slightly upward
            model.rotation.x -= Math.PI / 30;
        }

        console.log("mcpoint.lng", mcpoint.lng);
        console.log("mcpoint.lat", mcpoint.lat);
        geoGroup.name = persondata["nation_id"];
        geoGroup.userData = persondata;
        threeLayer.add(geoGroup);
        geoGroups.push(geoGroup); // Add geoGroup to array

        // Process animations
        if (obj.animations && obj.animations.length > 0) {
            let mixer = new THREE.AnimationMixer(obj.scene);

            // Determine which animation index to play
            let animIndex = 0;
            if (modelParams && modelParams.animationIndex !== undefined) {
                animIndex = modelParams.animationIndex;
                // Ensure index is within bounds
                if (animIndex >= obj.animations.length) {
                    console.warn(`动画索引 ${animIndex} 超出范围，使用索引 0`);
                    animIndex = 0;
                }
            }

            const action = mixer.clipAction(obj.animations[animIndex]);
            mixer.timeScale = 0.5;
            const duration = obj.animations[animIndex].duration || 1;
            action.setDuration(duration).play();
            mixers.push(mixer); // Add mixer to array
            console.log(`模型动画已启动, 播放动画索引: ${animIndex}`);
        }

        let modelMeshes = findMeshes(model); // Find all Mesh
        modelMeshes.forEach(mesh => {
            mesh.userData = persondata; // Bind dataset to each Mesh.userData
        });
        meshes.push(...modelMeshes); // Add to global meshes array
    });
}

function removeModel(nation_id) {
    const groupIndex = geoGroups.findIndex(group => group.name === nation_id);

    if (groupIndex !== -1) {
        // Remove geoGroup from threeLayer
        threeLayer.remove(geoGroups[groupIndex]);
        // Remove geoGroup from geoGroups array
        geoGroups.splice(groupIndex, 1);
    }

    //  currentModel = threeLayer.scene.getObjectByName(nation_id);
    //
    // threeLayer.remove(currentModel);

    // If you want to hide the model (instead of deleting)
    // currentModel.visible = false;
}

// Find all Mesh
function findMeshes(object) {
    const meshes = [];
    object.traverse((child) => {
        if (child.isMesh) {
            meshes.push(child);
        }
    });
    return meshes;
}

// Click event handling
var raycaster = new THREE.Raycaster();
var mouse = new THREE.Vector2();
var currentModel = null;

map.addEventListener('click', function (e) {
    mouse.x = (e.x / window.innerWidth) * 2 - 1;
    mouse.y = -(e.y / window.innerHeight) * 2 + 1;
    raycaster.setFromCamera(mouse, threeLayer.camera);

    // Use the collected Mesh objects for hit-testing
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

        setPersonModelPointByNationId(nation_id_me, e.latlng);
        setPersonPointByNationId(nation_id_me, e.latlng.lng, e.latlng.lat);

        service = getServiceForUser();
        if (service !== null) {
            const userConfirmed = confirm("此处有相应的应用服务，要继续吗？");
            if (userConfirmed) {
                alert("您选择了确定！");
                open_place_web_address(service.address);
            } else {
                return;
            }

        }

        // map.setDefaultCursor("url(http://webmap0.bdimg.com/image/api/openhand.cur) 8 8,default");
        // instruct_to_move_flag = false;
        map.cancelViewAnimation(animation);

    }
});
// Listen for zoom events
map.addEventListener("zoomend", function () {
    // Get current zoom level
    var currentZoom = map.getZoom();

    // Log current zoom level
    // alert("Current zoom level: " + currentZoom);
    console.log("Current zoom level: " + currentZoom);

    // You can add additional logic here, e.g. update data based on zoom level
});

function getAllGroups(scene) {
    const groups = [];
    scene.traverse((object) => {
        if (object.isGroup) { // Check whether it's a THREE.Group
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
    // If threeLayer is not defined, return early
    if (typeof threeLayer === 'undefined' || !threeLayer.scene) {
        console.warn('threeLayer not initialized, cannot update model');
        return;
    }

    // Debug: list all objects in the scene
    console.log('Scene objects:');
    threeLayer.scene.traverse(function(object) {
        console.log('Object name:', object.name, 'Type:', object.type);
    });

    // Find houseModel Group in the scene (note: this is a Group, not the model itself)
    let houseModelGroup = threeLayer.scene.getObjectByName('houseModel');

    // If not found by name, try alternative search
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

        // Convert coordinates (same approach as reference code)
        const llPoint = new BMapGL.Point(position.lng, position.lat);
        const mercatorPoint = BMapGL.Projection.convertLL2MC(llPoint);
        console.log("mercatorPoint", mercatorPoint);

        // Update Group position (model is inside Group; Group position is the model map position)
        houseModelGroup.position.set(mercatorPoint.lng, mercatorPoint.lat, 0);

        // Ensure Group is visible
        houseModelGroup.visible = true;

        // Update scale of the model inside the Group
        if (houseModelGroup.children.length > 0) {
            const model = houseModelGroup.children[0];
            model.scale.set(scale, scale, scale);

            // Update model rotation (keep the original Math.PI / 2 offset)
            model.rotation.x = (rotation.x || 0) + Math.PI / 2;
            model.rotation.y = rotation.y || 0;
            model.rotation.z = rotation.z || 0;

            // Ensure model is visible
            model.visible = true;
        }

        // Re-render
        threeLayer.render();

        console.log('House model updated:', {
            position: {lng: position.lng, lat: position.lat},
            mercator: {lng: mercatorPoint.lng, lat: mercatorPoint.lat},
            scale: scale,
            rotation: rotation
        });

        // Debug: check whether model is within viewport
        const mapCenter = map.getCenter();
        const mapZoom = map.getZoom();
        console.log('Map center:', mapCenter, 'Zoom:', mapZoom);
        console.log('Model position:', mercatorPoint);

        // Compute distance between model and map center
        const centerMercator = BMapGL.Projection.convertLL2MC(new BMapGL.Point(mapCenter.lng, mapCenter.lat));
        const distance = Math.sqrt(
            Math.pow(mercatorPoint.lng - centerMercator.lng, 2) +
            Math.pow(mercatorPoint.lat - centerMercator.lat, 2)
        );
        console.log('Distance from center (mercator units):', distance);

        // Check model bounds
        const box = new THREE.Box3().setFromObject(houseModelGroup);
        console.log('Model bounding box:', box);

        // Check model matrix
        console.log('Model matrix:', houseModelGroup.matrix);
    } else {
        console.warn('未找到houseModel模型Group');

        // List all objects for confirmation
        console.log('All objects in scene:');
        threeLayer.scene.traverse(function(object) {
            console.log('Name:', object.name, 'Type:', object.type);
        });
    }
}

function queryAddress() {
    // Create geocoder instance
    var address = document.getElementById("address").value;
    var myGeo = new BMapGL.Geocoder();
    if (marker) {
        map.removeOverlay(marker);
    }
    // Show geocoding result on the map and adjust viewport
    myGeo.getPoint(address, function (point) {
        if (point) {
            map.centerAndZoom(point, 16);
            marker = new BMapGL.Marker(point);
            map.addOverlay(marker);
            init_address = address;
            home_position = point;
        } else {
            alert('Address not resolved!');
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
        // Set map container cursor to crosshair
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


    // Use setTimeout to delay opening the second info window by 1.5s
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


// Flag variable indicating whether an info window is currently being shown
let showing_info_flag = false;

function send_chat_msg(lng, lat, msg,send_person_name="") {
    // Check whether an info window is currently being shown
    if (showing_info_flag) {
        console.log("信息窗口仍在显示。请稍后...");

        // Retry later
        setTimeout(() => send_chat_msg(lng, lat, msg,send_person_name), 1000);
        return; // If showing, exit
    }

    // Set flag to true to indicate an info window is being shown
    showing_info_flag = true;

    // Create map coordinate point
    var point = new BMapGL.Point(lng, lat);


    let opts = {
    width: 200,     // 信息窗口宽度200
    height: 100,     // 信息窗口高度100
    title: send_person_name, // 信息窗口标题
    offset: new BMapGL.Size(30, -50),
}

let infoWindow_chat = new BMapGL.InfoWindow(msg, opts);  // 创建信息窗口对象




    // Open info window
    map.openInfoWindow(infoWindow_chat, point);

    // Set timer to close the info window and reset the flag
    setTimeout(function () {
        map.closeInfoWindow(); // close info window
        showing_info_flag = false; // reset flag
    }, 3000);

    // Debug output
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
    // Listen for InfoWindow close event
profile_info_window.addEventListener("close", function() {
    // Code to run when the InfoWindow is closed
    alert(1);
    closeprofile();
});

    // var point = new BMapGL.Point(116.28882, 39.72164);
    var point = getPersonPointByNationId(nation_id);
    console.log("the point", point)
    map.openInfoWindow(profile_info_window, point); // Open InfoWindow
    // map.openInfoWindow(profile_info_window, point); // Open InfoWindow
    // map.openInfoWindow(profile_info_window, point); // Open InfoWindow
    // map.openInfoWindow(infoWindow3, point); // Open InfoWindow
    // map.openInfoWindow(infoWindow3, point); // Open InfoWindow
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


    // Assume geoGroup.position x/y are Mercator coordinates
    const mercatorX = geoGroup.position.x;
    const mercatorY = geoGroup.position.y;
// const mercatorX = intersectedObject.position.x;
// const mercatorY = intersectedObject.position.y;

// Create a Baidu Map Point object
    const mercatorPoint = new BMapGL.Point(mercatorX, mercatorY);

// Convert Mercator coordinates to lat/lng
    const geoCoord2 = BMapGL.Projection.convertMC2LL(mercatorPoint);

    console.log('Longitude:', geoCoord2.lng); // Output longitude
    console.log('Latitude:', geoCoord2.lat); // Output latitude
    let point = geoCoord2;


    map.openInfoWindow(infoWindow3, point); // Open InfoWindow


    // Get all THREE.Group instances in threeLayer
    const allGroups = getAllGroups(threeLayer.scene);
    console.log(allGroups); // Output all THREE.Group instances

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
    map.centerAndZoom(new BMapGL.Point(116.307092, 40.054922), 20);  // Initialize map: center + zoom level
    map.enableScrollWheelZoom(true);     // Enable mouse wheel zoom
    map.setTilt(50);      // Set initial tilt
    // Define keyframes

    displayOptions={
            indoor: false,
            poiText: true,
            poiIcon: false,
            building: true,
        }
        map.setDisplayOptions(displayOptions);


    // Bind events
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
    // Start animation
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
