var hiddenPoints = {}; // 存储隐藏的点元素

var indexs = ['province', 'city', 'area'];

function getHTMLDOM(context) {
    console.log("context:", context);
    var index = context.belongKey ?? 'other'; // 聚合的条件
    var text = context.belongValue;
    var count = context.pointCount || 1; // 聚合中点的总数
    var i = indexs.indexOf(index);

    count === 1 && (i = 3);
    i < 0 && (i = 3);

    var div = document.createElement('div');
    div.className = 'cluster-marker';
    var content = '';
    if (context.isCluster && text) {
        if (context.type === Cluster.ClusterType.GEO_FENCE) {
            text = REGION[text].name;
        }
        content += '<span class="cluster-marker-title">' + text + '</span>';
        content += `<span class="cluster-marker-body bg${i}">` + count + '</span>';
    }
    if (context.isCluster && !text) {
        content += `<span class="cluster-marker-body-content">` + count + '</span>';
    }
    if (!context.isCluster) {
        if (context.name.substring(0, 2) == "北京") {
            content += '<span class="cluster-marker-title" style="display: none">' + context.name + '</span><img src="mapavartar.png" style="width: 36px;height: 49px">';
        } else {
            content += '<span class="cluster-marker-title" style="display: none">' + context.name + '</span><img src="mapavartar2.png" style="width: 36px;height: 49px">';
        }

    }

    div.innerHTML = content;
    return div;
}

// 获取单点的 HTML 元素
function getSinglePointHTML(context) {
    const div = document.createElement('div');
    div.className = 'single-point';
    div.id = context.nation_id;

    // 判断是否为指定类型的点并设置样式
    if (context.name.startsWith("北京")) {
        div.innerHTML = `
                <img src="mapavartar.png" style="width: 36px;height: 49px">
                <span style="display: none">${context.name}</span>
            `;
    } else {
        div.innerHTML = `
                <img src="mapavartar2.png" style="width: 36px;height: 49px">
                <span style="display: none">${context.name}</span>
            `;
    }

    // 点击事件：隐藏单点
    div.addEventListener('click', function (event) {
        event.stopPropagation(); // 阻止事件冒泡
        hiddenPoints[context.nation_id] = div; // 将点保存到隐藏点数组中
        // div.style.display = 'none'; // 隐藏点
        showprofile(context.nation_id);


    });

    return div;
}


var cluster = null;

// 添加聚合数据
function addCluster() {
    if (cluster) {
        return;
    }
    cluster = new Cluster.View(map, {
        clusterMinPoints: 2,
        clusterMaxZoom: 18,
        updateRealTime: true,
        fitViewOnClick: true,
        clusterType: [
            [3, 10, Cluster.ClusterType.GEO_FENCE, [11001, 11002]],
            [11, 11, Cluster.ClusterType.ATTR_REF, 'city'],
            [12, 12, Cluster.ClusterType.ATTR_REF, ['city', 'area']],
            [13, null, Cluster.ClusterType.DIS_PIXEL, 64]
        ],
        clusterDictionary: (type, key) => {
            if (type === Cluster.ClusterType.GEO_FENCE) {
                var properties = REGION[key];
                if (properties && properties.center) {
                    return {
                        point: properties.center,
                        region: properties.fence
                    };
                }
            } else if (type === Cluster.ClusterType.ATTR_REF) {
                var properties = DISTRICT[key];
                if (properties && properties.center) {
                    return {
                        point: properties.center,
                    };
                }
            }
            return null;
        },
        renderClusterStyle: {
            type: Cluster.ClusterRender.DOM,
            inject: (props) => {
                const count = props.pointCount;
                const container = document.createElement('div');

                // 根据聚合数量设置不同的样式
                const size = count < 10 ? 40 : count < 100 ? 50 : 60;
                const color = count < 10 ? '#1E90FF' : count < 100 ? '#FF7F50' : '#FF4500';

                Object.assign(container.style, {
                    width: `${size}px`,
                    height: `${size}px`,
                    lineHeight: `${size}px`,
                    textAlign: 'center',
                    backgroundColor: color,
                    color: 'white',
                    borderRadius: '50%',
                    fontSize: '14px',
                    boxShadow: '0 2px 5px rgba(0,0,0,0.2)',
                    border: '2px solid white'
                });

                container.innerHTML = count;
                return container;
            }
        },
        renderSingleStyle: {
            type: Cluster.ClusterRender.DOM,
            style: {
                anchors: [0, 1],
                offsetX: -20,
                offsetY: -9.5
            },
            inject: getSinglePointHTML
        }
    });
    cluster.on(Cluster.ClusterEvent.CLICK, (e) => {
        console.log('ClusterEvent.CLICK', e);
    });
    // cluster.on(Cluster.ClusterEvent.MOUSE_OVER, (e) => {
    //     console.log('ClusterEvent.MOUSEOVER', e);
    // });
    // cluster.on(Cluster.ClusterEvent.MOUSE_OUT, (e) => {
    //     console.log('ClusterEvent.MOUSEOUT', e);
    // });
    var points = Cluster.pointTransformer(personsdata, function (data) {
        return {
            point: [data.location[0], data.location[1]],
            properties: {
                name: data.nick_name,
                nation_id: data.nation_id,
            }
        }
    });
    console.log(points);
    cluster.setData(points);
    persons_loaded_flag = true;
}

// 移除聚合数据
function removeCluster() {
    cluster && cluster.destroy();
    cluster = null;
}

function showpoints() {
    addCluster();
}

// 显示所有隐藏的点
function showHiddenPoints() {
    // 遍历隐藏点数组并重新显示点
    hiddenPoints.forEach((point) => {
        point.style.display = 'block';
    });

    // 清空隐藏点记录
    hiddenPoints = {};
}

