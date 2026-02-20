//route plan
var directionDisplay;
var stepDisplay;
var markerArray = [];
var position;
var polyline = null;
var poly2 = null;
var speed = 0.000005, wait = 1;

var myPano;
var user_marker;
var route_status = "stopped";
var panoClient;
var nextPanoId;
var timerHandle = null;
var steps = []

var step = 5; // 5; // metres
var tick = 100; // milliseconds
var eol;
var k = 0;
var stepnum = 0;
var speed = "";
var lastVertex = 1;
var currentDistance = 0;
var is_route_move_action = false;
var last_p = null;

// 标识是否是用户主动发起的路线规划
var isUserInitiatedRoutePlanning = false;

// 坐标获取相关变量
var coordinateCaptureMode = false;
var targetInputField = null;

function initialize_route() {

    // Create a renderer for directions and bind it to the map.

    var rendererOptions = {
        draggable: true,
        map: map
    }
    directionsDisplay = new google.maps.DirectionsRenderer(rendererOptions);

    directionsDisplay.addListener("directions_changed", () => {
        const directions = directionsDisplay.getDirections();

        if (directions) {
            computeTotalDistance(directions);
            console.log(directions);
            handleRoute(directions);
        }
    });


    // Instantiate an info window to hold step text.
    stepDisplay = new google.maps.InfoWindow();

    polyline = new google.maps.Polyline({
        path: [],
        strokeColor: '#FF0000',
        strokeWeight: 3
    });
    poly2 = new google.maps.Polyline({
        path: [],
        strokeColor: '#FF0000',
        strokeWeight: 3
    });

    // 添加坐标类型选择监听事件
    const positionTypeSelect = document.getElementById("position_type");
    if (positionTypeSelect) {
        positionTypeSelect.addEventListener("change", function() {
            toggleCoordinateLink();
        });
    }
}

// 切换坐标链接显示/隐藏
function toggleCoordinateLink() {
    const positionType = document.getElementById("position_type").value;
    const startCoordLink = document.getElementById("start_coord_link");
    const endCoordLink = document.getElementById("end_coord_link");
    const positionTypeSelect = document.getElementById("position_type");

    if (positionType === "coordinates") {

            startCoordLink.style.display = "block";
            endCoordLink.style.display = "block";

    } else {
        startCoordLink.style.display = "none";
        endCoordLink.style.display = "none";

        // 退出坐标捕获模式
        if (coordinateCaptureMode) {
            stopCoordinateCapture();
        }
    }
}

// 开始坐标捕获
function startCoordinateCapture(targetField) {
    coordinateCaptureMode = true;
    targetInputField = targetField;

    // 改变地图光标样式
    map.setOptions({ draggableCursor: 'crosshair' });

    // 更新当前点击的链接文本
    const linkElement = document.getElementById(targetField + "_coord_link_element");
    if (linkElement) {
        linkElement.textContent = "结束坐标获取";
        linkElement.onclick = stopCoordinateCapture;
    }

    // 确保其他链接恢复为"点此获取坐标"
    const otherFields = ['start', 'end', 'home_address'];
    const currentFieldIndex = otherFields.indexOf(targetField);
    if (currentFieldIndex !== -1) {
        // 重置其他所有坐标链接
        otherFields.forEach(field => {
            if (field !== targetField) {
                const otherLinkElement = document.getElementById(field + "_coord_link_element");
                if (otherLinkElement) {
                    otherLinkElement.textContent = "点此获取坐标";
                    otherLinkElement.onclick = function() { startCoordinateCapture(field); };
                }
            }
        });
    }

    showAlert("请点击地图来指定来获取相应的坐标。");
}

// 停止坐标捕获
function stopCoordinateCapture() {
    coordinateCaptureMode = false;
    targetInputField = null;

    // 恢复地图光标样式
    map.setOptions({ draggableCursor: null });

    // 恢复链接文本和点击事件
    const startLinkElement = document.getElementById("start_coord_link_element");
    if (startLinkElement) {
        startLinkElement.textContent = "点此获取坐标";
        startLinkElement.onclick = function() { startCoordinateCapture('start'); };
    }

    const endLinkElement = document.getElementById("end_coord_link_element");
    if (endLinkElement) {
        endLinkElement.textContent = "点此获取坐标";
        endLinkElement.onclick = function() { startCoordinateCapture('end'); };
    }

    // 恢复家位置链接文本和点击事件
    const homeAddressLinkElement = document.getElementById("home_address_coord_link_element");
    if (homeAddressLinkElement) {
        homeAddressLinkElement.textContent = "点此获取坐标";
        homeAddressLinkElement.onclick = function() { startCoordinateCapture('home_address'); };
    }
}

// 重置坐标链接到初始状态
function resetCoordinateLinks() {
    coordinateCaptureMode = false;
    targetInputField = null;

    // 恢复地图光标样式
    map.setOptions({ draggableCursor: null });

    // 恢复起点链接文本和点击事件
    const startLinkElement = document.getElementById("start_coord_link_element");
    if (startLinkElement) {
        startLinkElement.textContent = "点此获取坐标";
        startLinkElement.onclick = function() { startCoordinateCapture('start'); };
    }

    // 恢复终点链接文本和点击事件
    const endLinkElement = document.getElementById("end_coord_link_element");
    if (endLinkElement) {
        endLinkElement.textContent = "点此获取坐标";
        endLinkElement.onclick = function() { startCoordinateCapture('end'); };
    }

    // 恢复家位置链接文本和点击事件
    const homeAddressLinkElement = document.getElementById("home_address_coord_link_element");
    if (homeAddressLinkElement) {
        homeAddressLinkElement.textContent = "点此获取坐标";
        homeAddressLinkElement.onclick = function() { startCoordinateCapture('home_address'); };
    }
}

// 地图点击事件处理
function handleMapClick(latLng) {
    if (!coordinateCaptureMode || !targetInputField) return;

    // 将坐标填入相应输入框
    const inputElement = document.getElementById(targetInputField);
    if (inputElement) {
        inputElement.value = latLng.lng() + "," + latLng.lat();
    }
}

function createMarker(latlng, label, html) {

    var contentString = '<b>' + label + '</b><br>' + html;

    // 将 avatar 路径转换为 _map 版本
    // 例如: images/avatars/NG2025052719071718435.png -> images/avatars/NG2025052719071718435_map.png
    var avatarPath = person_data_me.avatar;
    var lastDotIndex = avatarPath.lastIndexOf('.');
    var mapAvatarPath;
    if (lastDotIndex !== -1) {
        mapAvatarPath = avatarPath.substring(0, lastDotIndex) + '_map' + avatarPath.substring(lastDotIndex);
    } else {
        // 如果没有扩展名，直接添加 _map
        mapAvatarPath = avatarPath + '_map';
    }

    var user_marker = new google.maps.Marker({
        position: latlng,
        map: map,
        title: label,
        icon: {
            url: '/' + mapAvatarPath, // 图标图像的路径
            scaledSize: new google.maps.Size(36, 49), // 图标的缩放大小，单位为像素
            origin: new google.maps.Point(0, 0), // 图标的原点，通常为(0, 0)
            anchor: new google.maps.Point(18, 49) // 图标的锚点，通常为图标底部中心
        },
        zIndex: Math.round(latlng.lat() * -100000) << 5
    });
    user_marker.myname = label;


    google.maps.event.addListener(user_marker, 'click', function () {
        infowindow.setContent(contentString);
        infowindow.open(map, user_marker);
    });
    return user_marker;
}


// isUserInitiated: 是否是用户主动发起，默认为true
function planRoute(isUserInitiated = true) {
    // 根据参数设置标志：标识是否是用户主动发起的路线规划
    isUserInitiatedRoutePlanning = isUserInitiated;

    stopTrack(); // 清除现有路线
    calcRoute();
}

function calcRoute() {

    if (timerHandle) {
        clearTimeout(timerHandle);
    }
    if (user_marker) {
        user_marker.setMap(null);
    }
    polyline.setMap(null);
    poly2.setMap(null);
    directionsDisplay.setMap(null);
    polyline = new google.maps.Polyline({
        path: [],
        strokeColor: '#FF0000',
        strokeWeight: 3
    });
    poly2 = new google.maps.Polyline({
        path: [],
        strokeColor: '#FF0000',
        strokeWeight: 3
    });
    // Create a renderer for directions and bind it to the map.
    rendererOptions = {
        draggable: true,
        map: map
    }
    directionsDisplay = new google.maps.DirectionsRenderer(rendererOptions);

    directionsDisplay.addListener("directions_changed", () => {
        const directions = directionsDisplay.getDirections();

        if (directions) {
            computeTotalDistance(directions);
            console.log(directions);
            handleRoute(directions);
        }
    });

    var start = document.getElementById("start").value;
    var end = document.getElementById("end").value;
    var positionType = document.getElementById("position_type").value;

    // 保存原始值用于存储到数据库
    var startForStorage = start;
    var endForStorage = end;

    // 如果终点类型是坐标，则直接使用坐标

    // 解析坐标字符串 "lat,lng"
    var coords = end.split(",");
    if (coords.length === 2) {

        var endLat = parseFloat(coords[1]);
        var endLng = parseFloat(coords[0]);
        // 检查是否为有效数字
        if (!isNaN(endLat) && !isNaN(endLng)) {
            end = new google.maps.LatLng(endLat, endLng);
        }

    }


    // 检查起点是否为坐标
    var startCoords = start.split(",");
    if (startCoords.length === 2) {
        var startLat = parseFloat(startCoords[1]);
        var startLng = parseFloat(startCoords[0]);
        // 检查是否为有效数字
        if (!isNaN(startLat) && !isNaN(startLng)) {
            start = new google.maps.LatLng(startLat, startLng);
        }
    }

    var travelMode = google.maps.DirectionsTravelMode.DRIVING

    var request = {
        origin: start,
        destination: end,
        travelMode: travelMode
    };

    // Route the directions and pass the response to a
    // function to create markers for each step.
    directionsService.route(request, function (response, status) {
        if (status == google.maps.DirectionsStatus.OK) {
            let directions = response;
            directionsDisplay.setDirections(directions);

            // 保存起点和终点到后端
            update_map_setting("route_start", startForStorage);
            update_map_setting("route_end", endForStorage);

            // 路线规划成功后，更新状态为playing
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
            showAlert("路线规划失败: " + status);
        }
    });
}


function handleRoute(directions) {

    if (timerHandle) {
        clearTimeout(timerHandle);
    }
    if (user_marker) {
        user_marker.setMap(null);
    }
    polyline.setMap(null);
    poly2.setMap(null);
    // directionsDisplay.setMap(null);

    polyline = new google.maps.Polyline({
        path: [],
        strokeColor: '#FF0000',
        strokeWeight: 3
    });
    poly2 = new google.maps.Polyline({
        path: [],
        strokeColor: '#FF0000',
        strokeWeight: 3
    });

    var bounds = new google.maps.LatLngBounds();
    var route = directions.routes[0];
    startLocation = {};
    endLocation = {};

    // For each route, display summary information.
    var path = directions.routes[0].overview_path;
    var legs = directions.routes[0].legs;
    for (i = 0; i < legs.length; i++) {
        if (i == 0) {
            startLocation.latlng = legs[i].start_location;
            startLocation.address = legs[i].start_address;
            // user_marker = google.maps.Marker({map:map,position: startLocation.latlng});
            if (init_route_current_position) {
                // 创建经纬度对象，假设已经有latitude和longitude变量
                const latitude = init_route_current_position.lat; // 示例纬度
                const longitude = init_route_current_position.lng; // 示例经度
                // 创建google.maps.LatLng对象来表示地图上的一个位置
                const latlng = new google.maps.LatLng(latitude, longitude);
                user_marker = createMarker(latlng, "start", legs[i].start_address, "green");
            } else {
                user_marker = createMarker(legs[i].start_location, "start", legs[i].start_address, "green");
            }

        }
        endLocation.latlng = legs[i].end_location;
        console.log("endLocation.latlng:", endLocation.latlng);
        endLocation.address = legs[i].end_address;
        var steps = legs[i].steps;
        for (j = 0; j < steps.length; j++) {
            var nextSegment = steps[j].path;
            for (k = 0; k < nextSegment.length; k++) {
                polyline.getPath().push(nextSegment[k]);
                bounds.extend(nextSegment[k]);


            }
        }
    }

    polyline.setMap(map);
    map.fitBounds(bounds);
}


//animation functions
function updatePoly(d) {
    // Spawn a new polyline every 20 vertices, because updating a 100-vertex poly is too slow
    if (poly2.getPath().getLength() > 20) {
        poly2 = new google.maps.Polyline([polyline.getPath().getAt(lastVertex - 1)]);
    }

    if (polyline.GetIndexAtDistance(d) < lastVertex + 2) {
        if (poly2.getPath().getLength() > 1) {
            poly2.getPath().removeAt(poly2.getPath().getLength() - 1)
        }
        poly2.getPath().insertAt(poly2.getPath().getLength(), polyline.GetPointAtDistance(d));
    } else {
        poly2.getPath().insertAt(poly2.getPath().getLength(), endLocation.latlng);
    }
}


function animatePoly(d) {
    if (d > eol) {
        console.log("endLocation.latlng", endLocation.latlng.lat());
        map.panTo(endLocation.latlng);
        user_marker.setPosition(endLocation.latlng);
        return;
    }
    var p = polyline.GetPointAtDistance(d);
    last_p = p;
    // setPersonModelPointByNationId(nation_id_me, p);
    console.log("middle point", p.lat());
    // map.panTo(p);
    user_marker.setPosition(p);
    updatePoly(d);
    timerHandle = setTimeout("animatePoly(" + (d + step) + ")", tick);
    currentDistance = d + step;
    const route_current_position = JSON.stringify(p);
    const current_position = route_current_position;
    update_map_setting("route_current_position", route_current_position);
    update_map_setting("route", currentDistance);
    update_map_setting("current_position", route_current_position);
}


function startAnimation() {

    eol = polyline.Distance();
    if (init_route_current_position) {
        map.setCenter(init_route_current_position);
    } else {
        map.setCenter(polyline.getPath().getAt(0));
    }


    poly2 = new google.maps.Polyline({
        path: [polyline.getPath().getAt(0)],
        strokeColor: "#FF0000",
        strokeWeight: 10
    });


    setTimeout(function () {
        animatePoly(init_route_distance); // 传递变量到animatePoly函数
    }, 2000); // 延迟时间保持不变
    // display

}


function viewRoute() {
alert("1viewroute");
    eol = polyline.Distance();
    alert(0);
    alert(eol);
    if(polyline){
    if (init_route_current_position && Object.keys(init_route_current_position).length > 0) {
        alert(init_route_current_position);
        const str = JSON.stringify(init_route_current_position);
        alert(str);
        alert(11);
        map.setCenter(init_route_current_position);
    } else {
        alert(22);
        map.setCenter(polyline.getPath().getAt(0));
    }}else{showAlert("路线加载出错，请检查网络后刷新页面或重新指定路线。",true)}
}

// 切换轨迹的函数
function route_move_action_from_python(){
    // 根据currentDistance的值决定调用startTrack还是continueTrack
    if (currentDistance === 0) {
        startTrack();
    } else {
        continueTrack();
    }

    // 10秒后调用pauseTrack
    setTimeout(() => {
        pauseTrack();
    }, 11000);
}

function toggleTrack() {
    const span = document.getElementById('route_opr');
    const icon = document.getElementById('track_icon');

    switch (route_status) {
        case 'stopped':
            startTrack();
            span.textContent = '暂停漫游'; // 更新文本
            icon.className = 'fas fa-circle-pause'; // 更新图标为暂停
            route_status = 'playing'; // 更新状态
            break;
        case 'playing':
            pauseTrack();
            span.textContent = '继续漫游'; // 更新文本
            icon.className = 'fas fa-circle-play'; // 更新图标为播放
            route_status = 'paused'; // 更新状态
            break;
        case 'paused':
            continueTrack();
            span.textContent = '暂停漫游'; // 更新文本
            icon.className = 'fas fa-circle-pause'; // 更新图标为暂停
            route_status = 'playing'; // 更新状态
            break;
        default:
            console.error('未知的路由状态:', route_status);
    }
    update_map_setting("route_status", route_status);
}

// 轨迹模拟
function startTrack() {

    startAnimation();
}

// 暂停动画，并显示当前地理位置点
function pauseTrack() {

    if (timerHandle) {
        clearTimeout(timerHandle);
    }

    // 计算偏离约50米的新位置
    // 在地球上，大约每度纬度相差111公里，所以50米约为0.00045度
    const offsetDegrees = 0.00045; // 约50米
    const offsetPoint = new google.maps.LatLng(
        last_p.lat() + offsetDegrees,
        last_p.lng() + offsetDegrees
    );

    setPersonModelPointByNationId(nation_id_me, offsetPoint);

}

// 继续动画
function continueTrack() {
    d = currentDistance;
    timerHandle = setTimeout("animatePoly(" + d + ")", tick);
}

// 清除路线
function stopTrack() {
    try {
        if (timerHandle) {
            clearTimeout(timerHandle);
            timerHandle = null;
        }

        if (user_marker) {
            try {
                user_marker.setMap(null);
            } catch (e) {
                console.warn("移除user_marker失败:", e);
            }
            user_marker = null;
        }

        if (polyline) {
            try {
                polyline.setMap(null);
            } catch (e) {
                console.warn("移除polyline失败:", e);
            }
        }

        if (poly2) {
            try {
                poly2.setMap(null);
            } catch (e) {
                console.warn("移除poly2失败:", e);
            }
        }

        if (directionsDisplay) {
            try {
                directionsDisplay.setMap(null);
            } catch (e) {
                console.warn("移除directionsDisplay失败:", e);
            }
        }

        console.log("路线已完全清除");

        // 注意：不在这里更新菜单项的勾选标记
        // stopTrack() 可能被多个地方调用（如planRoute准备规划新路线时）
        // 只有在确认切换到随机路线时才更新勾选标记（在setRouteRandom的回调中处理）
    } catch (error) {
        console.error("stopTrack执行失败:", error);
        // 即使出错也要确保清除引用
        timerHandle = null;
        user_marker = null;
    }
}

function computeTotalDistance(result) {
    let total = 0;
    const myroute = result.routes[0];

    if (!myroute) {
        return;
    }

    for (let i = 0; i < myroute.legs.length; i++) {
        total += myroute.legs[i].distance.value;
    }

    total = total / 1000;

alert("总距离");
alert(total);

}


