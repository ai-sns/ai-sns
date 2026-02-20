var route_status = "stopped";
var track;
var trackData = [];
var colorOffset = [];
var trackLine;
var movePoint;
var is_route_move_action = false;
var currentDistance = 0;
var move_duration = 600;

// 标识是否是用户主动发起的路线规划
var isUserInitiatedRoutePlanning = false;

// 坐标获取相关变量
var coordinateCaptureMode = false;
var targetInputField = null;
var lastClickPoint = null;

// 地址转坐标（Promise封装）
function geocodeAddress(address, city) {
    return new Promise((resolve, reject) => {
        new BMapGL.Geocoder().getPoint(address, point => {
            if (point) resolve(point);
            else reject(`地址解析失败: ${address}`);
        }, city);
    });
}

/**
 * 地址转坐标（Promise封装）
 * @param {string} address - 需要解析的地址
 * @param {string} [city] - 可选城市限定参数
 * @returns {Promise<BMapGL.Point>} 返回包含坐标点的Promise
 */
function geocodeAddressnew(address, city) {
    return new Promise((resolve, reject) => {
        try {
            // 创建地理编码器实例
            const geocoder = new BMapGL.Geocoder();

            // 执行地址解析
            geocoder.getPoint(
                address,
                (point) => {
                    // 成功回调处理
                    point ? resolve(point) :

                        alert(`地址解析失败: "${address}"`);
                },
                city,
                (errorCode) => {  // 百度地图错误处理回调
                    alert(`地理编码错误 [${errorCode}]: ${getGeocodeErrorMsg(errorCode)}`);
                    reject(new Error(`地理编码错误 [${errorCode}]: ${getGeocodeErrorMsg(errorCode)}`));
                }
            );
        } catch (error) {
            // 捕获同步错误（如构造函数异常）
            reject(new Error(`地理编码初始化失败: ${error.message}`));
        }
    });
}

/**
 * 百度地图错误码映射（根据官方文档扩展）
 * @param {number} code - 错误码
 * @returns {string} 可读错误信息
 */
function getGeocodeErrorMsg(code) {
    const errors = {
        1: '服务器内部错误',
        2: '请求参数非法',
        3: '权限校验失败',
        4: '配额校验失败',
        5: 'ak不存在或非法',
        101: '服务禁用',
        102: '不通过白名单或安全码不对',
        200: 'APP不存在，AK有误请检查',
        // 可根据需要添加更多错误码
    };
    return errors[code] || `未知错误 (${code})`;
}

// 初始化路线规划相关功能
function initialize_route() {
    // 添加坐标类型选择监听事件

    const positionTypeSelect = document.getElementById("position_type");
    if (positionTypeSelect) {
        positionTypeSelect.addEventListener("change", function() {
            toggleCoordinateLink();
        });
    }

    // 添加地图点击事件监听器用于坐标捕获
    map.addEventListener('click', function(e) {
        if (coordinateCaptureMode && targetInputField) {
            handleMapClick(e);
        }
    });
}
initialize_route();
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
    map.setDefaultCursor("crosshair");

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
    map.setDefaultCursor("url(http://webmap0.bdimg.com/image/api/openhand.cur) 8 8,default");

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
    map.setDefaultCursor("url(http://webmap0.bdimg.com/image/api/openhand.cur) 8 8,default");

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
function handleMapClick(e) {
    if (!coordinateCaptureMode || !targetInputField) return;

    // 将坐标填入相应输入框
    const inputElement = document.getElementById(targetInputField);
    if (inputElement) {
        // 修复坐标格式，经度在前，纬度在后
        inputElement.value = e.latlng.lng + "," + e.latlng.lat;
    }

    // 保存最后点击的点
    lastClickPoint = e.latlng;

    // 停止坐标捕获
    stopCoordinateCapture();
}

// 规划路线（异步处理）
// isUserInitiated: 是否是用户主动发起，默认为true
async function planRoute(isUserInitiated = true) {
    const start = document.getElementById("start").value.trim();
    const end = document.getElementById("end").value.trim();
    const positionType = document.getElementById("position_type").value;

    if (!start || !end) {
        showAlert("请输入起点和终点");
        return;
    }

    try {
        // 在规划新路线前清除现有路线
        stopTrack();

        let startPoint, endPoint;

        // 解析起点
        if (start.includes(",")) {
            // 起点是坐标
            const startCoords = start.split(",");
            if (startCoords.length === 2) {
                // 修复坐标解析顺序，应该是经度在前，纬度在后
                const startLng = parseFloat(startCoords[0]);
                const startLat = parseFloat(startCoords[1]);
                if (!isNaN(startLat) && !isNaN(startLng)) {
                    startPoint = new BMapGL.Point(startLng, startLat);
                } else {
                    throw new Error("起点坐标格式不正确");
                }
            }
        } else {
            // 起点是地址
            startPoint = await geocodeAddress(start, "北京市");
        }

        // 解析终点
        if (end.includes(","))  {
            // 终点是坐标
            const endCoords = end.split(",");
            if (endCoords.length === 2) {
                // 修复坐标解析顺序，应该是经度在前，纬度在后
                const endLng = parseFloat(endCoords[0]);
                const endLat = parseFloat(endCoords[1]);
                if (!isNaN(endLat) && !isNaN(endLng)) {
                    endPoint = new BMapGL.Point(endLng, endLat);
                } else {
                    throw new Error("终点坐标格式不正确");
                }
            }
        } else {
            // 终点是地址
            endPoint = await geocodeAddress(end, "北京市");
        }

        // 步骤3：使用坐标进行路线规划
        // 根据参数设置标志：标识是否是用户主动发起的路线规划
        isUserInitiatedRoutePlanning = isUserInitiated;

        // 注意：driving.search() 是异步的，成功后会触发 onSearchComplete 回调
        // 在 onSearchComplete 回调中会更新状态和UI，这里不需要立即更新
        driving.search(startPoint, endPoint);

        // 注意：不在这里更新状态和UI
        // 只有在 onSearchComplete 回调中确认路线规划成功后才更新
        // 这样可以确保在规划失败时不会错误地更新UI
    } catch (error) {
        showAlert(error.message || error); // 显示地址解析错误
    }
}

function getAllGpsPositions(routeResult) {
    var positions = [];
    positions = routeResult.getPlan(0).getRoute(0).getPath();
    console.log(positions);

    // 将路线绘制到地图上
    const pointArray = positions.map(pos => new BMapGL.Point(pos.lng, pos.lat));
    currentRoute = new BMapGL.Polyline(pointArray, {
        strokeColor: "blue",
        strokeWeight: 2,
        strokeOpacity: 0.5
    });
    map.addOverlay(currentRoute);


    track = new Track.View(map, {
        lineLayerOptions: {
            style: {
                strokeWeight: 8,
                strokeLineJoin: 'round',
                strokeLineCap: 'round'
            }
        }
    });

    for (var item of pointArray) {
        var point = item;
        var trackPoint = new Track.TrackPoint(point);
        trackData.push(trackPoint);
        var choose = [0.9, 0.5, 0.1];
        var color = choose[Math.floor(Math.random() * choose.length)];
        colorOffset.push(color);
    }
    alert(move_duration);

    trackLine = new Track.LocalTrack({
        trackPath: trackData,
        duration: move_duration,
        style: {
            sequence: true,
            marginLength: 32,
            arrowColor: '#fff',
            strokeTextureUrl: 'https://mapopen-pub-jsapi.bj.bcebos.com/jsapiGlgeo/img/down.png',
            strokeTextureWidth: 64,
            strokeTextureHeight: 32,
            traceColor: [27, 142, 236]
        },
        linearTexture: [[0, '#f45e0c'], [0.5, '#f6cd0e'], [1, '#2ad61d']],
        gradientColor: colorOffset
    });

    trackLine.on(Track.LineCodes.STATUS, (status) => {
        switch (status) {
            case Track.StatusCodes.PLAY:
                break;
            case Track.StatusCodes.RESUME:
                break;
            case Track.StatusCodes.INIT:
                break;
            case Track.StatusCodes.PAUSE:
                break;
            case Track.StatusCodes.STOP:
                break;
            case Track.StatusCodes.FINISH:
                var box = trackLine.getBBox();
                if (box) {
                    var bounds = [new BMapGL.Point(box[0], box[1]), new BMapGL.Point(box[2], box[3])];
                    map.setViewport(bounds);
                }
                break;
            default:
                break;
        }
    });

    track.addTrackLine(trackLine);
    // track.focusTrack(trackLine);
    alert(init_route_current_position.lng);
    movePointbak = new Track.GroundPoint({
        point: (typeof init_route_current_position !== 'undefined' && init_route_current_position !== null) ?
               new BMapGL.Point(init_route_current_position.lng, init_route_current_position.lat) :
               trackData[0].getPoint(),
        style: {
            url: 'http://localhost:8900/scripts/car3.png',//https://mapopen-pub-jsapi.bj.bcebos.com/jsapiGlgeo/img/car.png
            level: 18,
            scale: 1,
            size: new BMapGL.Size(16, 32),
            anchor: new BMapGL.Size(0.5, 0.5),
        }
    });

    //  movePoint = new Track.ModelPoint({ point: trackData[5].getPoint(), style:{
    //     url: 'http://localhost:8900/scripts/3d/mario6.glb',//'https://mapopen-pub-jsapi.bj.bcebos.com/jsapiGlgeo/img/bus.glb''http://localhost:8900/scripts/ybot.glb'http://localhost:8900/scripts/3d/mario3.glb,http://localhost:8900/scripts/3d/mario10.glb 15
    //     scale: 0.08,//9
    //     level: 18,
    //     rotationX: 100,//90
    //     rotationY: 180,//90
    //     rotationZ: 0//0
    // } });

    movePoint = new Track.ModelPoint({ point: trackData[5].getPoint(), style:{
        url: 'https://mapopen-pub-jsapi.bj.bcebos.com/jsapiGlgeo/img/bus.glb',//'http://localhost:8900/scripts/ybot.glb'http://localhost:8900/scripts/3d/mario3.glb,http://localhost:8900/scripts/3d/mario10.glb 15
        scale: 9,
        level: 18,
        rotationX: 90,//90
        rotationY: 90,//90
        rotationZ: 0//0
    } });


    // movePoint.setPosition(new BMapGL.Point(init_route_current_position.lng, init_route_current_position.lat));
    movePoint.addEventListener(Track.MapCodes.CLICK, (e) => {
        console.log('Track.GroundPoint.click', e);
    })
    movePoint.addEventListener(Track.MapCodes.MOUSE_OVER, (e) => {
        console.log('Track.GroundPoint.MOUSE_OVER', e);
    })
    movePoint.addEventListener(Track.MapCodes.MOUSE_OUT, (e) => {
        console.log('Track.GroundPoint.MOUSE_OUT', e);
    })

    movePoint.addEventListener(Track.PointCodes.CHANGE_POINT, (e) => {
        // alert(e.point);
        // setPersonModelPointByNationId(nation_id_me, e);
    })
    //movePoint.show(map);  // 或者 track.addMovePoint(movePoint);
    // track.addMovePoint(movePoint);
    trackLine.setMovePoint(movePoint);


    return positions;
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
    }, 10000);
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


function startTrack() {
    driving.clearResults();  // 清除路线规划结果
    trackLine.startAnimation();
}

function stopTrack() {
    try {
        // 1. 停止所有动画
        if (trackLine) {
            try {
                trackLine.stopAnimation();
            } catch (e) {
                console.warn("停止动画失败:", e);
            }
        }

        // 2. 先清除移动点（bus.glb模型）
        if (movePoint && trackLine) {
            try {
                // 从trackLine中移除movePoint
                trackLine.setMovePoint(null);
            } catch (e) {
                console.warn("移除movePoint失败:", e);
            }

            // 如果movePoint有hide方法，调用它
            if (movePoint && typeof movePoint.hide === 'function') {
                try {
                    movePoint.hide();
                } catch (e) {
                    console.warn("隐藏movePoint失败:", e);
                }
            }

            // 尝试移除movePoint的覆盖物
            if (movePoint && movePoint.Yt && map) {
                try {
                    map.removeOverlay(movePoint.Yt);
                } catch (e) {
                    console.warn("移除movePoint覆盖物失败:", e);
                }
            }
        }

        // 3. 清除轨迹点
        if (trackLine) {
            try {
                trackLine.clearTrackPoint();
            } catch (e) {
                console.warn("清除轨迹点失败:", e);
            }
        }

        // 4. 从地图上移除轨迹线
        if (trackLine && track) {
            try {
                // 从Track视图系统中移除轨迹线
                track.removeTrackLine(trackLine);
            } catch (e) {
                console.warn("移除轨迹线失败:", e);
            }

            // 强制重绘地图
            if (map) {
                try {
                    map._drawFrame(); // 强制重绘地图，确保视觉更新
                } catch (e) {
                    console.warn("重绘地图失败:", e);
                }
            }
        }

        // 5. 清除所有相关数据
        trackData = [];
        colorOffset = [];

        // 6. 清除路线规划结果
        if (driving) {
            try {
                driving.clearResults();
            } catch (e) {
                console.warn("清除路线规划结果失败:", e);
            }
        }

        // 7. 重置所有引用
        trackLine = null;
        movePoint = null;

        // 8. 检查并清除所有可能残留的折线
        if (map) {
            try {
                const overlays = map.getOverlays();
                console.log("overlays", overlays);
                for (let overlay of overlays) {
                    // 清除所有折线覆盖物
                    if (overlay instanceof BMapGL.Polyline) {
                        console.log("Polyline", overlay);
                        map.removeOverlay(overlay);
                    }
                }
            } catch (e) {
                console.warn("清除折线覆盖物失败:", e);
            }
        }

        console.log("轨迹和车辆已完全清除");
    } catch (error) {
        console.error("stopTrack执行失败:", error);
        // 即使出错也要确保清除引用
        trackLine = null;
        movePoint = null;
        trackData = [];
        colorOffset = [];
    }
}

function pauseTrack() {

    const currentPoint = movePoint.getPoint();
    // 计算偏离约50米的新位置
    // 在地球上，大约每度纬度相差111公里，所以50米约为0.00045度
    const offsetDegrees = 0.00045; // 约50米
    const offsetPoint = new BMapGL.Point(
        currentPoint.lng + offsetDegrees,
        currentPoint.lat + offsetDegrees
    );

    setPersonModelPointByNationId(nation_id_me, offsetPoint);
    alert('暂停位置:');
    alert(currentPoint);
    alert(currentPoint.lng);
    alert(currentPoint.lat);

    // 获取当前轨迹进度 (0-1)
    const progress = trackLine.process;
    alert(progress);
// 根据进度获取精确点
    console.log(trackLine);
    console.log(progress);
    const pointInfo = trackLine.getInfoByProcess(progress);
    console.log(pointInfo);
    console.log("Precise point:", pointInfo.point);
    alert("Precise point: " + pointInfo.point);

    trackLine.pauseAnimation();

    currentDistance = progress;
    const route_current_position = JSON.stringify(currentPoint);
    update_map_setting("route_current_position", route_current_position);
    update_map_setting("route", currentDistance);
    update_map_setting("current_position", route_current_position);


}

function continueTrack() {
    // trackLine.setProcess(0.1904666666666667);
    trackLine.setMovePoint(movePoint);
    trackLine.setProcess(currentDistance);
    trackLine.resumeAnimation();
}

function viewRoute() {
    // 如果存在轨迹线，将地图视图调整到轨迹线的范围
    alert("viewRoute");
    if (trackLine) {
        // 获取轨迹的边界框
        const box = trackLine.getBBox();
        if (box) {
            // 将边界框转换为百度地图的 Bounds 对象
            const bounds = [
                new BMapGL.Point(box[0], box[1]),
                new BMapGL.Point(box[2], box[3])
            ];
            map.setViewport(bounds);
        }

        // 如果有当前位置，将地图中心移动到当前位置
        if (init_route_current_position && init_route_current_position.lng && init_route_current_position.lat) {
            alert(1);
            alert(JSON.stringify(init_route_current_position));
            const currentPoint = new BMapGL.Point(init_route_current_position.lng, init_route_current_position.lat);
            map.setCenter(currentPoint);
        } else if (trackData && trackData.length > 0) {
            // 否则移动到路线起点
            alert(JSON.stringify(trackData[0].getPoint()));
            map.setCenter(trackData[0].getPoint());
            alert(2);
        }
    }else{showAlert("路线加载出错，请检查网络后刷新页面或重新指定路线。",true)}
}
