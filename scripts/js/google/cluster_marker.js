
    //handle cluster marker
    var markerCluster;
    var hiddenMarkers = {};
    var markers;

    function showpoints() {
        // 2. 随机生成1000个坐标点

        const markersData = personsdata;


        // 3. 创建标记对象并添加到地图
        const iconSize = new google.maps.Size(36, 49); // 图标的实际尺寸
        markers = markersData.map(data => {
            const marker = new google.maps.Marker({
                position: {
                    lng: data.location[0],
                    lat: data.location[1]
                },
                map: map,
                title: data.nick_name, // 设置标记的名称
                nation_id: data.nation_id,
                icon: {
                    url: "mapavartar.png", // 自定义图标URL
                    scaledSize: iconSize // 设置图标的缩放大小
                }
            });

            // 为每个标记添加点击事件
            marker.addListener('click', () => {
                alert(`坐标: (${data.location[0]}, ${data.location[1]})\n名称: ${data.nick_name}`);
                hiddenMarkers[data.nation_id] = marker;
                showprofile(data.nation_id);
                // hideMarker(marker); // 隐藏标记并将其移入隐藏列表
            });
            console.log("marker:", marker);

            return marker;
        });

        // 4. 使用标记聚类器（可选）
        markerCluster = new MarkerClusterer(map, markers, {
            // imagePath: 'https://developers.google.com/maps/documentation/javascript/examples/markerclusterer/m'
            imagePath: './m'
            // 组合参数m1-m5：the actual url   https://developers.google.com/maps/documentation/javascript/examples/markerclusterer/m1.png
        });
        console.log("markers", markers);
        persons_loaded_flag = true;
    }

    function getMarkerByNationId(nationId) {
        return markers.find(marker => marker.nation_id === nationId) || null;
    }

    function hideMarker(marker) {
        marker.setVisible(false); // 隐藏标记

    }
