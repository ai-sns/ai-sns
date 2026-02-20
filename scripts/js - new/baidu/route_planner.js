var route_status = "stopped";
var track;
var trackData = [];
var colorOffset = [];
var trackLine;
var movePoint;
var is_route_move_action = false;
var currentDistance = 0;
var move_duration = 600;

// Flag: whether the route planning is initiated by the user
var isUserInitiatedRoutePlanning = false;

// Coordinate capture related variables
var coordinateCaptureMode = false;
var targetInputField = null;
var lastClickPoint = null;

// Geocode address to coordinate (Promise wrapper)
function geocodeAddress(address, city) {
    return new Promise((resolve, reject) => {
        new BMapGL.Geocoder().getPoint(address, point => {
            if (point) resolve(point);
            else reject(`地址解析失败: ${address}`);
        }, city);
    });
}

/**
 * Geocode address to coordinate (Promise wrapper)
 * @param {string} address - address to resolve
 * @param {string} [city] - optional city constraint
 * @returns {Promise<BMapGL.Point>} Promise that resolves to a coordinate point
 */
function geocodeAddressnew(address, city) {
    return new Promise((resolve, reject) => {
        try {
            // Create geocoder instance
            const geocoder = new BMapGL.Geocoder();

            // Execute geocoding
            geocoder.getPoint(
                address,
                (point) => {
                    // Success callback
                    point ? resolve(point) :

                        alert(`地址解析失败: "${address}"`);
                },
                city,
                (errorCode) => {  // Baidu map error callback
                    alert(`地理编码错误 [${errorCode}]: ${getGeocodeErrorMsg(errorCode)}`);
                    reject(new Error(`地理编码错误 [${errorCode}]: ${getGeocodeErrorMsg(errorCode)}`));
                }
            );
        } catch (error) {
            // Catch sync errors (e.g. constructor exceptions)
            reject(new Error(`地理编码初始化失败: ${error.message}`));
        }
    });
}

/**
 * Baidu map error code mapping (extend per official docs)
 * @param {number} code - error code
 * @returns {string} human-readable message
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
        // Add more codes as needed
    };
    return errors[code] || `未知错误 (${code})`;
}

// Initialize route planning related features
function initialize_route() {
    // Bind position type selector

    const positionTypeSelect = document.getElementById("position_type");
    if (positionTypeSelect) {
        positionTypeSelect.addEventListener("change", function() {
            toggleCoordinateLink();
        });
    }

    // Bind map click for coordinate capture
    map.addEventListener('click', function(e) {
        if (coordinateCaptureMode && targetInputField) {
            handleMapClick(e);
        }
    });
}
initialize_route();
// Toggle coordinate link show/hide
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

        // Exit coordinate capture mode
        if (coordinateCaptureMode) {
            stopCoordinateCapture();
        }
    }
}

// Start coordinate capture
function startCoordinateCapture(targetField) {
    coordinateCaptureMode = true;
    targetInputField = targetField;

    // Change map cursor
    map.setDefaultCursor("crosshair");

    // Update link text for current field
    const linkElement = document.getElementById(targetField + "_coord_link_element");
    if (linkElement) {
        linkElement.textContent = "结束坐标获取";
        linkElement.onclick = stopCoordinateCapture;
    }

    // Ensure other links reset to the initial "get coordinates" text
    const otherFields = ['start', 'end', 'home_address'];
    const currentFieldIndex = otherFields.indexOf(targetField);
    if (currentFieldIndex !== -1) {
        // Reset all other coordinate links
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

// Stop coordinate capture
function stopCoordinateCapture() {
    coordinateCaptureMode = false;
    targetInputField = null;

    // Restore map cursor
    map.setDefaultCursor("url(http://webmap0.bdimg.com/image/api/openhand.cur) 8 8,default");

    // Restore link text and click handler
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

    // Restore home position link text and click handler
    const homeAddressLinkElement = document.getElementById("home_address_coord_link_element");
    if (homeAddressLinkElement) {
        homeAddressLinkElement.textContent = "点此获取坐标";
        homeAddressLinkElement.onclick = function() { startCoordinateCapture('home_address'); };
    }
}

// Reset coordinate links to initial state
function resetCoordinateLinks() {
    coordinateCaptureMode = false;
    targetInputField = null;

    // Restore map cursor
    map.setDefaultCursor("url(http://webmap0.bdimg.com/image/api/openhand.cur) 8 8,default");

    // Restore start link text and click handler
    const startLinkElement = document.getElementById("start_coord_link_element");
    if (startLinkElement) {
        startLinkElement.textContent = "点此获取坐标";
        startLinkElement.onclick = function() { startCoordinateCapture('start'); };
    }

    // Restore end link text and click handler
    const endLinkElement = document.getElementById("end_coord_link_element");
    if (endLinkElement) {
        endLinkElement.textContent = "点此获取坐标";
        endLinkElement.onclick = function() { startCoordinateCapture('end'); };
    }

    // Restore home position link text and click handler
    const homeAddressLinkElement = document.getElementById("home_address_coord_link_element");
    if (homeAddressLinkElement) {
        homeAddressLinkElement.textContent = "点此获取坐标";
        homeAddressLinkElement.onclick = function() { startCoordinateCapture('home_address'); };
    }
}

// Map click handler
function handleMapClick(e) {
    if (!coordinateCaptureMode || !targetInputField) return;

    // Fill coordinates into target input
    const inputElement = document.getElementById(targetInputField);
    if (inputElement) {
        // Ensure format: lng first, lat second
        inputElement.value = e.latlng.lng + "," + e.latlng.lat;
    }

    // Save last clicked point
    lastClickPoint = e.latlng;

    // Stop coordinate capture
    stopCoordinateCapture();
}

// Plan route (async)
// isUserInitiated: whether initiated by user (default true)
async function planRoute(isUserInitiated = true) {
    const start = document.getElementById("start").value.trim();
    const end = document.getElementById("end").value.trim();
    const positionType = document.getElementById("position_type").value;

    if (!start || !end) {
        showAlert("请输入起点和终点");
        return;
    }

    try {
        // Clear existing route before planning a new one
        stopTrack();

        let startPoint, endPoint;

        // Parse start point
        if (start.includes(",")) {
            // Start is coordinates
            const startCoords = start.split(",");
            if (startCoords.length === 2) {
                // Ensure parse order: lng first, lat second
                const startLng = parseFloat(startCoords[0]);
                const startLat = parseFloat(startCoords[1]);
                if (!isNaN(startLat) && !isNaN(startLng)) {
                    startPoint = new BMapGL.Point(startLng, startLat);
                } else {
                    throw new Error("起点坐标格式不正确");
                }
            }
        } else {
            // Start is address
            startPoint = await geocodeAddress(start, "北京市");
        }

        // Parse end point
        if (end.includes(","))  {
            // End is coordinates
            const endCoords = end.split(",");
            if (endCoords.length === 2) {
                // Ensure parse order: lng first, lat second
                const endLng = parseFloat(endCoords[0]);
                const endLat = parseFloat(endCoords[1]);
                if (!isNaN(endLat) && !isNaN(endLng)) {
                    endPoint = new BMapGL.Point(endLng, endLat);
                } else {
                    throw new Error("终点坐标格式不正确");
                }
            }
        } else {
            // End is address
            endPoint = await geocodeAddress(end, "北京市");
        }

        // Step 3: plan route using coordinates
        // Set flag based on parameter: whether user initiated
        isUserInitiatedRoutePlanning = isUserInitiated;

        // Note: driving.search() is async; success triggers onSearchComplete
        // State/UI will be updated in onSearchComplete; no immediate update needed here
        driving.search(startPoint, endPoint);

        // Note: do not update state/UI here
        // Only update after confirming success in onSearchComplete
        // This avoids incorrect UI updates when planning fails
    } catch (error) {
        showAlert(error.message || error); // Display geocoding error
    }
}

function getAllGpsPositions(routeResult) {
    var positions = [];
    positions = routeResult.getPlan(0).getRoute(0).getPath();
    console.log(positions);

    // Draw route on the map
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
    //movePoint.show(map);  // Or track.addMovePoint(movePoint);
    // track.addMovePoint(movePoint);
    trackLine.setMovePoint(movePoint);


    return positions;
}


// Toggle track from python side
function route_move_action_from_python(){
    // Decide startTrack vs continueTrack based on currentDistance
    if (currentDistance === 0) {
        startTrack();
    } else {
        continueTrack();
    }

    // Call pauseTrack after 10 seconds
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
            span.textContent = '暂停漫游'; // Update text
            icon.className = 'fas fa-circle-pause'; // Update icon: pause
            route_status = 'playing'; // Update state
            break;
        case 'playing':
            pauseTrack();
            span.textContent = '继续漫游'; // Update text
            icon.className = 'fas fa-circle-play'; // Update icon: play
            route_status = 'paused'; // Update state
            break;
        case 'paused':
            continueTrack();
            span.textContent = '暂停漫游'; // Update text
            icon.className = 'fas fa-circle-pause'; // Update icon: pause
            route_status = 'playing'; // Update state
            break;
        default:
            console.error('未知的路由状态:', route_status);
    }
    update_map_setting("route_status", route_status);
}


function startTrack() {
    driving.clearResults();  // Clear route planning results
    trackLine.startAnimation();
}

function stopTrack() {
    try {
        // 1. Stop all animations
        if (trackLine) {
            try {
                trackLine.stopAnimation();
            } catch (e) {
                console.warn("停止动画失败:", e);
            }
        }

        // 2. Remove move point first (bus.glb model)
        if (movePoint && trackLine) {
            try {
                // Remove movePoint from trackLine
                trackLine.setMovePoint(null);
            } catch (e) {
                console.warn("移除movePoint失败:", e);
            }

            // If movePoint has hide(), call it
            if (movePoint && typeof movePoint.hide === 'function') {
                try {
                    movePoint.hide();
                } catch (e) {
                    console.warn("隐藏movePoint失败:", e);
                }
            }

            // Try removing movePoint overlay
            if (movePoint && movePoint.Yt && map) {
                try {
                    map.removeOverlay(movePoint.Yt);
                } catch (e) {
                    console.warn("移除movePoint覆盖物失败:", e);
                }
            }
        }

        // 3. Clear track points
        if (trackLine) {
            try {
                trackLine.clearTrackPoint();
            } catch (e) {
                console.warn("清除轨迹点失败:", e);
            }
        }

        // 4. Remove track line from map
        if (trackLine && track) {
            try {
                // Remove track line from Track view system
                track.removeTrackLine(trackLine);
            } catch (e) {
                console.warn("移除轨迹线失败:", e);
            }

            // Force redraw map
            if (map) {
                try {
                    map._drawFrame(); // Force redraw to ensure visual update
                } catch (e) {
                    console.warn("重绘地图失败:", e);
                }
            }
        }

        // 5. Clear related data
        trackData = [];
        colorOffset = [];

        // 6. Clear route planning results
        if (driving) {
            try {
                driving.clearResults();
            } catch (e) {
                console.warn("清除路线规划结果失败:", e);
            }
        }

        // 7. Reset references
        trackLine = null;
        movePoint = null;

        // 8. Check and remove any leftover polylines
        if (map) {
            try {
                const overlays = map.getOverlays();
                console.log("overlays", overlays);
                for (let overlay of overlays) {
                    // Remove all polyline overlays
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
        // Ensure references are cleared even on error
        trackLine = null;
        movePoint = null;
        trackData = [];
        colorOffset = [];
    }
}

function pauseTrack() {

    const currentPoint = movePoint.getPoint();
    // Compute an offset position about 50 meters away
    // On Earth, ~1 degree latitude is ~111km, so 50m is about 0.00045 degrees
    const offsetDegrees = 0.00045; // About 50 meters
    const offsetPoint = new BMapGL.Point(
        currentPoint.lng + offsetDegrees,
        currentPoint.lat + offsetDegrees
    );

    setPersonModelPointByNationId(nation_id_me, offsetPoint);
    alert('暂停位置:');
    alert(currentPoint);
    alert(currentPoint.lng);
    alert(currentPoint.lat);

    // Get current track progress (0-1)
    const progress = trackLine.process;
    alert(progress);
// Get precise point by progress
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
    // If a track line exists, fit the map viewport to it
    alert("viewRoute");
    if (trackLine) {
        // Get track bounding box
        const box = trackLine.getBBox();
        if (box) {
            // Convert bbox to Baidu map Bounds
            const bounds = [
                new BMapGL.Point(box[0], box[1]),
                new BMapGL.Point(box[2], box[3])
            ];
            map.setViewport(bounds);
        }

        // If current position exists, move map center to it
        if (init_route_current_position && init_route_current_position.lng && init_route_current_position.lat) {
            alert(1);
            alert(JSON.stringify(init_route_current_position));
            const currentPoint = new BMapGL.Point(init_route_current_position.lng, init_route_current_position.lat);
            map.setCenter(currentPoint);
        } else if (trackData && trackData.length > 0) {
            // Otherwise move to route start
            alert(JSON.stringify(trackData[0].getPoint()));
            map.setCenter(trackData[0].getPoint());
            alert(2);
        }
    }else{showAlert("路线加载出错，请检查网络后刷新页面或重新指定路线。",true)}
}
