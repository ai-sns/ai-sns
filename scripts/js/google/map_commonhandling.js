//map conmon map init and load 3d model
var info_window_type = "";
var is_3d_flag = true;
var init_address = "";
var init_position = null;
var plaza_position = null;
var clock = new THREE.Clock();
var mixers = [];
var map;
var marker;
var geocoder;
var directionsService;
var directionsRenderer;
var last_click_point;
var instruct_to_move_flag;
var person_data_me;
var model_loaded_list = {};
var nation_id_me = "";
var overlay;
var modelhouse;
var model;
var model2;
var personsdata = [];
// 配置常量提升可维护性
const FETCH_RETRIES = 3;
const INITIAL_RETRY_DELAY = 1000;
const REQUEST_TIMEOUT = 8000;

async function loadPersonsData(url, retries = FETCH_RETRIES, retryDelay = INITIAL_RETRY_DELAY) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);

    try {
        const response = await fetch(`${url}?t=${Date.now()}`, {
            signal: controller.signal,
            cache: 'no-cache'
        });
        clearTimeout(timeoutId);

        if (!response.ok) {
            throw new Error(`请求失败: ${response.status} ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        clearTimeout(timeoutId);

        if (retries > 0) {
            console.warn(`请求失败，剩余重试次数: ${retries}。将在 ${retryDelay}ms 后重试...`);
            await new Promise(resolve => setTimeout(resolve, retryDelay));
            return loadPersonsData(url, retries - 1, retryDelay * 2);
        }

        console.error('最终请求失败，错误原因:', error);
        throw error; // 向上传递错误以便调用方处理
    }
}

// 使用立即执行函数封装异步操作 loadPersonsData
(async () => {
    try {
        const dataUrl = "http://www.ai-sns.org/personsdata.json";
        const data = await loadPersonsData(dataUrl);

        console.log("成功加载人员数据:", data);
        personsdata = data;

    } catch (error) {
        console.error("人员数据加载失败，建议:",
            error.name === 'AbortError'
                ? '检查网络连接或稍后重试'
                : '联系系统管理员');
    }
})();

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

function initMap() {
    // 配置选项
    const LOADER_OPTIONS = {
        apiKey: "AIzaSyDPXsp-NFBn5AvyaYn71u4m3fgblsUjR8Y",
        version: "weekly",
    };

    // Levi’s Stadium 球场的边界坐标
    const coordinates = [
        {lng: -73.9702904, lat: 40.7634362},
        {lng: -73.9698018, lat: 40.7627095},
        {lng: -73.9693109, lat: 40.762918},
        {lng: -73.969804, lat: 40.7636465},
    ];

    const center = {lng: 116.27882, lat: 39.71164, altitude: 0};


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
        // draggingCursor: 'crosshair',
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
        alert("lastpoint:" + JSON.stringify(e.latLng.toJSON(), null, 2));
        alert("center_point:" + JSON.stringify(center_point.toJSON(), null, 2));
        distance = getDistance(last_click_point, center_point);
        alert(distance);
        // showinfo();
        // setTimeout(moveinfo, 1500);
        const domEvent = e.domEvent;
        const {left, top, width, height} = mapDiv.getBoundingClientRect();

        const x = domEvent.clientX - left;
        const y = domEvent.clientY - top;

        mousePosition.x = 2 * (x / width) - 1;
        mousePosition.y = 1 - 2 * (y / height);


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
            const gltf = await new Promise((resolve, reject) => {
                loader.load('house_red.glb', resolve, undefined, reject);
            });

            modelhouse = gltf.scene;

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
            console.log("the height:", height);
            // 获取模型包围盒

            const modelHeight = box.max.y - box.min.y;
            console.log("the modelHeight:", modelHeight);

// 根据高度调整缩放比例
            const desiredHeight = 15; // 你期望的高度
            const scale = desiredHeight / height;

            // 设置模型的缩放、旋转和位置
            // model.scale.set(scale, scale, scale);
            modelhouse.scale.set(1, 1, 1);
            modelhouse.rotation.x = (Math.PI / 15) * 0;
            modelhouse.rotation.y = (Math.PI / 15) * 1.6;
            const coordinates = {
                lng: 121.50638469117915, lat: 31.299096398606526,

            };

            const position3 = overlay.latLngAltitudeToVector3(coordinates, modelhouse.position);

            // 将模型添加到场景中
            overlay.scene.add(modelhouse);


        } catch (error) {
            console.error('Error loading model:', error); // 输出错误信息
        }
    };

    loadHouse();

    const loadModel = async () => {


        try {
            const gltf = await new Promise((resolve, reject) => {
                loader.load('tshirtgirl_0_0_0_0_1_0.glb', resolve, undefined, reject);
            });

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
            console.log("the height:", height);
            // 获取模型包围盒

            const modelHeight = box.max.y - box.min.y;
            console.log("the modelHeight:", modelHeight);

// 根据高度调整缩放比例
            const desiredHeight = 150; // 你期望的高度
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

            // 将找到的网格添加到 modelMeshes 数组中
            all_model_meshes.push(...modelMeshes_found); // 使用扩展运算符简化数组操作

            // 给模型添加点击事件
            model.traverse((child) => {
                if (child.isMesh) {
                    child.cursor = 'pointer'; // 设置鼠标光标样式
                    child.userData.isClickable = true; // 设置可点击属性
                }
            });

            // 创建动画混合器并播放动画
            const mixer = new THREE.AnimationMixer(gltf.scene);
            const action = mixer.clipAction(gltf.animations[0]);
            mixer.timeScale = 0.5;
            action.setDuration(1).play();
            mixers.push(mixer); // 将混合器添加到数组中

        } catch (error) {
            console.error('Error loading model:', error); // 输出错误信息
        }
    };

// 调用 loadModel 函数
    loadModel();
    load_aisns_building();


    const loadModel2 = async () => {
        try {
            const gltf = await new Promise((resolve, reject) => {
                loader.load('t-shirtboy2.glb', resolve, undefined, reject);
            });

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
            console.log("the height:", height);
            // 获取模型包围盒

            const modelHeight = box.max.y - box.min.y;
            console.log("the modelHeight2222:", modelHeight);

            // 根据高度调整缩放比例
            const desiredHeight = 150; // 你期望的高度
            const scale = desiredHeight / height;
            model2.scale.set(scale, scale, scale);


            // 设置模型的缩放、旋转和位置
            model2.rotation.x = Math.PI / 30;
            model2.rotation.y = Math.PI / 1.5;
            model2.position.set(130, 0, -250);

            // 将模型添加到场景中
            overlay.scene.add(model2);

            // 查找场景中的所有网格
            const modelMeshes_found = findMeshes(gltf.scene);

            // 将找到的网格添加到 modelMeshes 数组中
            all_model_meshes.push(...modelMeshes_found); // 使用扩展运算符简化数组操作

            // 给模型添加点击事件
            model2.traverse((child) => {
                if (child.isMesh) {
                    child.cursor = 'pointer'; // 设置鼠标光标样式
                    child.userData.isClickable = true; // 设置可点击属性
                }
            });

            // 创建动画混合器并播放动画
            const mixer = new THREE.AnimationMixer(gltf.scene);
            const action = mixer.clipAction(gltf.animations[0]);
            mixer.timeScale = 0.5;
            action.setDuration(10).play();
            mixers.push(mixer); // 将混合器添加到数组中

        } catch (error) {
            console.error('Error loading model:', error); // 输出错误信息
        }
    };
    loadModel2();

    overlay.onBeforeDraw = () => {

        if (mousePosition.x != 0 && mousePosition.y != 0) {
            var intersections = overlay.raycast(mousePosition, all_model_meshes, {
                recursive: false,
            });

            if (highlightedObject) {
                // highlightedObject.material.color.setHex(DEFAULT_COLOR);
                console.log("ok");
                console.log("mousepoint:", mousePosition)
            }

            if (intersections.length === 0) {
                highlightedObject = null;
                return;
            }

            highlightedObject = intersections[0].object;
            highlightedObject.material.color.setHex(HIGHLIGHT_COLOR);//暂停颜色变化
            if (highlightedObject.userData) {
                if (highlightedObject.userData.nation_id) {
                    console.log(highlightedObject.userData.nation_id);
                    console.log(highlightedObject.userData["nation_id"]);
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

function loadModel(persondata) {
    let url = persondata["avatar_3d"];
    let pos = persondata["location"];
    const coordinates = {
        lat: parseFloat(pos[1]),
        lng: parseFloat(pos[0]),
    };

    let loader = new THREE.GLTFLoader();
    loader.load(url, (gltf) => {
        model = gltf.scene;

        const ambientLight = new THREE.AmbientLight(0xffffff, 0.1);
        //overlay.scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.1);

        directionalLight.position.set(-1, -1, -1);
        // overlay.scene.add(directionalLight);

        model.name = persondata["nation_id"];
        model.userData = persondata;


        // 计算模型的包围体积
        const box = new THREE.Box3().setFromObject(model);
        const size = box.getSize(new THREE.Vector3());
        const height = size.y; // 模型的高度
        console.log("the height33:", height);
        // 获取模型包围盒

        const modelHeight = box.max.y - box.min.y;
        console.log("the modelHeight333:", modelHeight);

        // 根据高度调整缩放比例
        const desiredHeight = 150; // 你期望的高度
        let scale = desiredHeight / height;
        console.log("scale", scale);
        // scale=40;

        // 设置模型的缩放、旋转和位置
        model.scale.set(scale, scale, scale);


        // model.scale.set(40, 40, 40);
        model.rotation.x = Math.PI / 30;
        model.rotation.y = (Math.PI / 1.5);

        const position2 = overlay.latLngAltitudeToVector3(coordinates, model.position);
        console.log("position2", position2)
        console.log("model.position", model.position)
        console.log("model.positionx", model.position.x)
        console.log("model.positionz", model.position.z)

        overlay.scene.add(model); // 将模型添加到场景中
        model_loaded_list[persondata["nation_id"]] = model;


        let modelMeshes = findMeshes(gltf.scene);

        // 给模型添加点击事件
        model.traverse((child) => {
            if (child.isMesh) {
                child.cursor = 'pointer'; // 设置鼠标光标样式
                child.userData.isClickable = true; // 设置可点击属性
            }
        });

        modelMeshes.forEach(mesh => {
            mesh.userData = persondata; // 将数据集绑定到每个 Mesh 的 userData 属性
        });


        all_model_meshes.push(...modelMeshes); // 添加到全局 meshes 数组中


        let mixer = new THREE.AnimationMixer(gltf.scene);
        const action = mixer.clipAction(gltf.animations[0]);
        mixer.timeScale = 1;
        // 获取动画的总持续时间
        const duration = gltf.animations[0].duration;
        action.setDuration(duration).play();
        // action.setDuration(1).play();
        mixers.push(mixer); // 将混合器添加到数组中


    }, undefined, (error) => {
        console.error(error); // 输出错误信息
    });
    // overlay.setAnchor(coordinates);
}

function removeModel(nation_id) {


    model = model_loaded_list[nation_id];
    overlay.scene.remove(model); // 将模型添加到场景中
    delete model_loaded_list[nation_id];

}

function getLastClickPoint() {
    let point = last_click_point;
    return point;
}

function getDistance(start_point, end_point) {
    // 计算距离(返回值单位为米)
    const distance = google.maps.geometry.spherical.computeDistanceBetween(start_point, end_point);

    return distance;
}

function getCenter() {
    let point = map.getCenter();
    return point;
}


