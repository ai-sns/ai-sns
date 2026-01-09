//page ui menu
var current_screen_type = "AI";

// 定义按钮点击事件处理函数映射
const buttonActions = {
    plaza: function () {
        goPlaza();
    },
    home: function () {
        initPos();
    },
    AI: function () {
        findHim();
    },
    move: function (btn) {
        toggleButtonActive(btn); // 仅对自身的active状态进行切换
        set_move_status();
    },
    activity: function (btn) {
        info_window_type = "";
        const isActive = btn.classList.contains('active');
        if (isActive) {
            btn.classList.remove('active');
            hideHistory();
            return;
        } else {
            btn.classList.add('active');
        }
        btn = document.getElementById("message_btn");
        btn.classList.remove('active');
        btn = document.getElementById("system_info_btn");
        btn.classList.remove('active');
        info_title = document.getElementById("info_title");
        if (info_title.textContent == "Notification" || info_title.textContent == "Chat message" || info_title.textContent == "All message") {
            info_title.textContent = "All message";
        } else {
            info_title.textContent = "旅程信息";
        }

        document.getElementById("info").style.display = "block";
        document.getElementById("info_chat").style.display = "none";
    }
};

// 切换按钮的active状态
function toggleButtonActive(btn) {
    btn.classList.toggle('active');
}

// 处理按钮点击事件的函数
function handleButtonClick(event) {
    const btn = event.target.closest('.map-btn');
    if (btn) {
        const btnTitle = btn.dataset.title;

        // 处理plaza, home和AI按钮的互斥状态
        if (['plaza', 'home', 'AI'].includes(btnTitle)) {
            document.querySelector('.map-btn.active')?.classList.remove('active');
            btn.classList.add('active');
            buttonActions[btnTitle]();
        } else if (['move', 'activity'].includes(btnTitle)) {
            buttonActions[btnTitle](btn);
        }
    }
}

// 事件委托：为 .bottom-left-buttons 容器添加点击事件
document.querySelector('.bottom-left-buttons').addEventListener('click', handleButtonClick);


document.querySelectorAll('.menu-section').forEach(section => {
    section.addEventListener('click', function (e) {
        const item = e.target.closest('.menu-item');
        if (item && !item.classList.contains('active')) {
            const activeItem = section.querySelector('.menu-item.active');
            activeItem && activeItem.classList.remove('active');
            item.classList.add('active');
        }
    });
});

// 右侧菜单收起/展开功能
const rightMenuToggle = document.querySelector('.right-menu .menu-toggle');
const rightMenu = document.querySelector('.right-menu');

rightMenuToggle.addEventListener('click', function () {
    rightMenu.classList.toggle('collapsed');

    // 切换图标方向
    const icon = this.querySelector('i');
    icon.classList.toggle('fa-angle-double-right');
    icon.classList.toggle('fa-angle-double-left');
});

// 顶部菜单栏收起/展开功能
const topBarToggle = document.querySelector('.top-bar-toggle');
const topBar = document.querySelector('.top-bar');

topBarToggle.addEventListener('click', function () {
    topBar.classList.toggle('collapsed');

    // 切换图标方向
    const icon = this.querySelector('i');
    icon.classList.toggle('fa-angle-double-up');
    icon.classList.toggle('fa-angle-double-down');
});

// 显示自定义确认对话框
function showConfirmDialog(title, message, onConfirm, onCancel) {
    document.getElementById("dialogTitle").innerText = title; // 设置标题
    document.getElementById("dialogMessage").innerText = message; // 设置消息
    document.getElementById("confirmDialog").style.display = "flex"; // 显示对话框

    // 确认按钮事件
    document.getElementById("confirmButton").onclick = function () {
        onConfirm(); // 调用确认回调
        closeDialog();
    };

    // 取消按钮事件
    document.getElementById("cancelButton").onclick = function () {
        onCancel(); // 调用取消回调
        closeDialog();
    };
}

// 关闭对话框的函数
function closeDialog() {
    document.getElementById("confirmDialog").style.display = "none"; // 隐藏对话框
}

function initPos() {
    current_screen_type = "home";
    set_map_center(home_position?.lng, home_position?.lat);
    // 隐藏plaza相关的菜单项
    menu_div = document.getElementById('menu-plaza-top');
    menu_div.style.display = 'none';
    menu_div = document.getElementById('menu-plaza-middle');
    menu_div.style.display = 'none';
    menu_div = document.getElementById('menu-plaza');
    menu_div.style.display = 'none';

    // 显示AI相关的菜单项
    menu_div = document.getElementById('menu-ai-top');
    menu_div.style.display = 'block';
    menu_div = document.getElementById('menu-ai-middle');
    menu_div.style.display = 'block';
    menu_div = document.getElementById('menu-ai');
    menu_div.style.display = 'block';

    // 隐藏其他菜单项
    menu_div = document.getElementById('menu-home');
    menu_div.style.display = 'none';

    // 设置右侧菜单宽度为180px
    const rightMenu = document.querySelector('.right-menu');
    if (rightMenu) {
        rightMenu.style.width = '180px';
    }

    stop_plaza_message();
    aimodel_status.setVisible(true);
}

// 菜单项文本最大长度
const MAX_MENU_ITEM_LENGTH = 30;

// 从网络获取新闻数据并更新菜单项
async function fetchAndCreateMenuItems() {
    try {
        const response = await fetch('http://www.ai-sns.org/news.json');
        const data = await response.json();

        // 更新置顶信息菜单项 (menu-plaza-top)
        const topMenu = document.getElementById('menu-plaza-top');
        if (topMenu) {
            // 清除原有的菜单项（除了标题）
            const titleElement = topMenu.querySelector('.menu-title');
            topMenu.innerHTML = '';
            if (titleElement) {
                topMenu.appendChild(titleElement);
            }

            // 添加新的菜单项
            data.top.forEach((item, index) => {
                const menuItem = document.createElement('div');
                menuItem.className = 'menu-item';
                menuItem.innerHTML = `<span onclick="open_url('${item.url}')" title="${item.title}">${index + 1}. ${item.title}</span>`;
                topMenu.appendChild(menuItem);
            });
        }

        // 更新热点信息菜单项 (menu-plaza-middle)
        const middleMenu = document.getElementById('menu-plaza-middle');
        if (middleMenu) {
            // 清除原有的菜单项（除了标题）
            const titleElement = middleMenu.querySelector('.menu-title');
            middleMenu.innerHTML = '';
            if (titleElement) {
                middleMenu.appendChild(titleElement);
            }

            // 添加新的菜单项
            data.hot.forEach((item, index) => {
                const menuItem = document.createElement('div');
                menuItem.className = 'menu-item';
                menuItem.innerHTML = `<span onclick="open_url('${item.url}')" title="${item.title}">${index + 1}. ${item.title}</span>`;
                middleMenu.appendChild(menuItem);
            });
        }

        // 更新最新信息菜单项 (menu-plaza)
        const plazaMenu = document.getElementById('menu-plaza');
        if (plazaMenu) {
            // 清除原有的菜单项（除了标题）
            const titleElement = plazaMenu.querySelector('.menu-title');
            plazaMenu.innerHTML = '';
            if (titleElement) {
                plazaMenu.appendChild(titleElement);
            }

            // 添加新的菜单项
            data.latest.forEach((item, index) => {
                const menuItem = document.createElement('div');
                menuItem.className = 'menu-item';
                menuItem.innerHTML = `<span onclick="open_url('${item.url}')" title="${item.title}">${index + 1}. ${item.title}</span>`;
                plazaMenu.appendChild(menuItem);
            });
        }
    } catch (error) {
        console.error('获取新闻数据失败:', error);
    }
}

function goPlaza() {
    if (current_screen_type != "plaza") {
        play_plaza_message();
    }
    current_screen_type = "plaza";
    if (plaza_position) {
        set_map_center(plaza_position?.lng, plaza_position?.lat, [0, 0], [17, 20]);
    } else {
        set_map_center(building_position[0], building_position[1]), [0, 0], [17, 20];
    }

    // 获取并创建菜单项
    fetchAndCreateMenuItems();

    // 显示plaza相关的菜单项
    menu_div = document.getElementById('menu-plaza-top');
    menu_div.style.display = 'block';
    menu_div = document.getElementById('menu-plaza-middle');
    menu_div.style.display = 'block';
    menu_div = document.getElementById('menu-plaza');
    menu_div.style.display = 'block';

    // 隐藏AI相关的菜单项
    menu_div = document.getElementById('menu-ai-top');
    menu_div.style.display = 'none';
    menu_div = document.getElementById('menu-ai-middle');
    menu_div.style.display = 'none';
    menu_div = document.getElementById('menu-ai');
    menu_div.style.display = 'none';

    // 隐藏其他菜单项
    menu_div = document.getElementById('menu-home');
    menu_div.style.display = 'none';

    // 设置右侧菜单宽度为240px
    const rightMenu = document.querySelector('.right-menu');
    if (rightMenu) {
        rightMenu.style.width = '240px';
    }

    aimodel_status.setVisible(false);
    close_info_list();
}

function check_place(address, lng, lat) {
    set_map_center(lng, lat, [0, 0], [17, 19]);
    msg = address + "\n" + lng + "," + lat;
    alert(msg)
}

function findHim() {

    current_screen_type = "AI";

    let user_current_point;
    if (typeof nation_id_me !== 'undefined' && nation_id_me) {
        user_current_point = getPersonPointByNationId(nation_id_me);
    } else {
        console.error("nation_id_me 未定义或无效");
        user_current_point = new BMapGL.Point(116.397428, 39.90923); // 返回默认位置
    }

    // 自动兼容百度 (属性) 和谷歌 (方法)
    const lng = typeof user_current_point.lng === 'function'
        ? user_current_point.lng()
        : user_current_point.lng;

    const lat = typeof user_current_point.lat === 'function'
        ? user_current_point.lat()
        : user_current_point.lat;

    set_map_center(lng, lat);

    // 隐藏plaza相关的菜单项
    menu_div = document.getElementById('menu-plaza-top');
    menu_div.style.display = 'none';
    menu_div = document.getElementById('menu-plaza-middle');
    menu_div.style.display = 'none';
    menu_div = document.getElementById('menu-plaza');
    menu_div.style.display = 'none';

    // 显示AI相关的菜单项
    menu_div = document.getElementById('menu-ai-top');
    menu_div.style.display = 'block';
    menu_div = document.getElementById('menu-ai-middle');
    menu_div.style.display = 'block';
    menu_div = document.getElementById('menu-ai');
    menu_div.style.display = 'block';

    // 隐藏其他菜单项
    menu_div = document.getElementById('menu-home');
    menu_div.style.display = 'none';

    // 设置右侧菜单宽度为180px
    const rightMenu = document.querySelector('.right-menu');
    if (rightMenu) {
        rightMenu.style.width = '180px';
    }

    stop_plaza_message();
    aimodel_status.setVisible(true);
}

function hideHistory() {
    document.getElementById("info").style.display = "none";
}

function showHistory() {
    info_window_type = "";
    btn = document.getElementById("process_btn");
    btn.classList.add('active');
    btn = document.getElementById("system_info_btn");
    btn.classList.remove('active');
    btn = document.getElementById("message_btn");
    btn.classList.remove('active');
    info_title = document.getElementById("info_title");
    info_title.textContent = lt("All message", "全部信息");
    document.getElementById("info").style.display = "block";
}

function clear_chat_history() {
    const infoList = document.getElementById('info_list');
    while (infoList.firstChild) {
        infoList.removeChild(infoList.firstChild); // 移除第一个子节点，直到没有子节点为止
    }
}

function clear_chat_list() {
    const infoList = document.getElementById('info_list_chat');
    while (infoList.firstChild) {
        infoList.removeChild(infoList.firstChild); // 移除第一个子节点，直到没有子节点为止
    }
}

function show_inform_message_in_info_list() {
    info_window_type = "2";
    btn = document.getElementById("system_info_btn");
    const isActive = btn.classList.contains('active');
    if (isActive) {
        btn.classList.remove('active');
        hideHistory();
        return;
    } else {
        btn.classList.add('active');
    }
    btn = document.getElementById("message_btn");
    btn.classList.remove('active');
    btn = document.getElementById("process_btn");
    btn.classList.remove('active');
    info_title = document.getElementById("info_title");
    info_title.textContent = lt("Notification", "通知信息");
    document.getElementById("info").style.display = "block";
}

function show_talk_message_in_info_list() {
    info_window_type = "3";
    btn = document.getElementById("message_btn");
    const isActive = btn.classList.contains('active');
    if (isActive) {
        btn.classList.remove('active');
        hideHistory();
        return;
    } else {
        btn.classList.add('active');
    }
    btn = document.getElementById("system_info_btn");
    btn.classList.remove('active');
    btn = document.getElementById("process_btn");
    btn.classList.remove('active');
    info_title = document.getElementById("info_title");
    info_title.textContent = lt("Chat message", "聊天信息");
    document.getElementById("info").style.display = "block";
}

function close_info_list() {

    info_window_type = "";
    hideHistory();
    btn = document.getElementById("message_btn");
    btn.classList.remove('active');
    btn = document.getElementById("system_info_btn");
    btn.classList.remove('active');
    btn = document.getElementById("process_btn");
    btn.classList.remove('active');

}

function close_info_list_chat() {

    document.getElementById("info_chat").style.display = "none";

}

function addMessageToBoard(message) {
    // 获取信息列表的引用
    const infoList = document.getElementById('info_list');

    // 创建新的列表项
    const newListItem = document.createElement('li');

    // 设置新列表项的类名
    newListItem.className = 'info_list_li';

    // 设置列表项的文本内容
    // newListItem.textContent = message;

    newListItem.innerHTML = message;
    // 将新项插入到列表的最上方
    infoList.insertBefore(newListItem, infoList.firstChild);
}

function appendMessageToBoard(message) {
    // 获取信息列表的引用
    const infoList = document.getElementById('info_list');

    // 创建新的列表项
    const newListItem = document.createElement('li');

    // 设置新列表项的类名
    newListItem.className = 'info_list_li';

    // 设置列表项的文本内容
    // newListItem.textContent = message;

    newListItem.innerHTML = message;
    // 将新项插入到列表的最上方
    // infoList.insertBefore(newListItem, infoList.firstChild);
    infoList.append(newListItem);

}

function appendMessageToBoardChat(message) {

    close_info_list()

    document.getElementById('info_chat').style.display = "block";
    const infoListChat = document.getElementById('info_list_chat');


    // 创建新的列表项
    const newListItem = document.createElement('li');

    // 设置新列表项的类名
    newListItem.className = 'info_list_li';

    // 设置列表项的文本内容
    // newListItem.textContent = message;
    newListItem.innerHTML = message;

    // 将新项插入到列表的最上方
    // infoListChat.insertBefore(newListItem, infoList.firstChild);
    infoListChat.append(newListItem);


}

// 获取信息列表元素
const infoList = document.getElementById('info_list');
const infoListChat = document.getElementById('info_list_chat');

// 监听滚动事件，当滚动接近底部时加载更多数据
infoList.addEventListener('scroll', function () {
    // 设置一个阈值，以便在接近底部时加载更多
    const threshold = 5; // 5px阈值

    // 检查是否滚动接近底部
    if (infoList.scrollTop + infoList.clientHeight >= infoList.scrollHeight - threshold) {
        loadMoreItems(false);
    }
});

infoListChat.addEventListener('scroll', function () {
    // 设置一个阈值，以便在接近底部时加载更多
    const threshold = 5; // 5px阈值

    // 检查是否滚动接近底部
    if (infoListChat.scrollTop + infoListChat.clientHeight >= infoListChat.scrollHeight - threshold) {
        loadMoreItemsChat(false);
    }
});




function setHomePosition() {
    msgdiv = document.getElementById("sethomeposition");
    msgdiv.style.display = "inline";

    // 聚焦到地址输入框
    const addressInput = document.getElementById('home_address');
    addressInput.focus();

    // 确保坐标链接的点击事件正确绑定
    const coordLinkElement = document.getElementById("home_address_coord_link_element");
    if (coordLinkElement) {
        coordLinkElement.textContent = "点此获取坐标";
        coordLinkElement.onclick = function() { startCoordinateCapture('home_address'); };
    }
}

function updateHomePosition() {
    // 获取输入框的值
    const addressInput = document.getElementById('home_address');
    const scaleInput = document.getElementById('home_scale');
    const rotationInput = document.getElementById('home_rotation');

    const address = addressInput.value;
    const scale = scaleInput.value;
    const rotation = rotationInput.value;

    // 如果地址是坐标格式，解析坐标
    let homePosition = {};
    if (address && address.includes(',')) {
        // 假设坐标格式是 "lng,lat" 或 "lng,lat,altitude"
        const coords = address.split(',');
        homePosition.lng = parseFloat(coords[0]);
        homePosition.lat = parseFloat(coords[1]);
        homePosition.altitude = coords[2] ? parseFloat(coords[2]) : 0;
    } else {
        return false;
    }

    // 设置缩放比例，默认为20
    homePosition.scale = scale ? parseFloat(scale) : 20;

    // 更新到Python后端
    update_map_setting("home_position", JSON.stringify(homePosition));

    // 处理旋转
    let rotationValues = { x: 0, y: 0, z: 0 };
    if (rotation) {
        const rotations = rotation.split(',');
        rotationValues.x = parseFloat(rotations[0]) || 0;
        rotationValues.y = parseFloat(rotations[1]) || 0;
        rotationValues.z = parseFloat(rotations[2]) || 0;

        update_map_setting("positionx", rotationValues.x);
        update_map_setting("positiony", rotationValues.y);
        update_map_setting("positionz", rotationValues.z);
    }

    // 关闭设置面板
    closeHomePositionSetting();

    // 显示提示
    showAlert("家位置设置成功");

    // 更新house_red.glb模型参数
    updateHouseModel(homePosition, homePosition.scale, rotationValues);
}


function closeHomePositionSetting() {
    msgdiv = document.getElementById("sethomeposition");
    msgdiv.style.display = "none";

    // 重置坐标链接状态
    resetCoordinateLinks();
}

function setRoute() {
    // 注意：即使当前已经是指定路线(route_status === "playing")，也要继续执行函数
    // 以便正确设置UI元素的状态

    msgdiv = document.getElementById("setroute");
    msgdiv.style.display = "inline";

    // 获取起点和终点输入框
    const startInput = document.getElementById('start');
    const endInput = document.getElementById('end');
    // 获取position_type下拉框
    const positionTypeSelect = document.getElementById('position_type');
    // 获取坐标链接元素
    const startCoordLink = document.getElementById("start_coord_link");
    const endCoordLink = document.getElementById("end_coord_link");

    // 根据set_route_flag状态设置输入框和按钮
    if (route_status === "playing") {
        // 如果已经是指定路线状态
        // 设置输入框为只读状态
        startInput.setAttribute('readonly', 'readonly');
        endInput.setAttribute('readonly', 'readonly');

        // 隐藏确定按钮，显示查看和重设按钮
        const buttons = msgdiv.getElementsByTagName('button');
        for (let i = 0; i < buttons.length; i++) {
            const button = buttons[i];
            const buttonText = button.textContent.trim();
            if (buttonText === '确定') {
                button.style.display = 'none';
            } else if (buttonText === '查看' || buttonText === '重设') {
                button.style.display = 'inline';
            }
        }

        // 隐藏position_type下拉框
        if (positionTypeSelect) {
            positionTypeSelect.style.display = 'none';
        }

        // 当position_type下拉框隐藏时，坐标链接也应该隐藏
        if (startCoordLink) {
            startCoordLink.style.display = 'none';
        }
        if (endCoordLink) {
            endCoordLink.style.display = 'none';
        }

        showAlert("当前已经是指定路线");
    } else {
        // 如果不是指定路线状态
        // 移除只读属性（确保输入框可编辑）
        startInput.removeAttribute('readonly');
        endInput.removeAttribute('readonly');

        // 显示确定按钮，隐藏查看和重设按钮
        const buttons = msgdiv.getElementsByTagName('button');
        for (let i = 0; i < buttons.length; i++) {
            const button = buttons[i];
            const buttonText = button.textContent.trim();
            if (buttonText === '确定') {
                button.style.display = 'inline';
            } else if (buttonText === '查看' || buttonText === '重设') {
                button.style.display = 'none';
            }
        }

        // 显示position_type下拉框
        if (positionTypeSelect) {
            positionTypeSelect.style.display = 'inline-block';
        }

        // 根据position_type的值决定是否显示坐标链接
        const positionType = document.getElementById("position_type").value;
        if (positionType === "coordinates") {
            if (startCoordLink) {
                startCoordLink.style.display = 'block';
            }
            if (endCoordLink) {
                endCoordLink.style.display = 'block';
            }
        } else {
            if (startCoordLink) {
                startCoordLink.style.display = 'none';
            }
            if (endCoordLink) {
                endCoordLink.style.display = 'none';
            }
        }
    }

    startInput.focus();

    // 注意：不在这里更新菜单项的勾选标记
    // 只有在planRoute()成功规划路线后才添加✓标记
}

function setRouteRandom() {
    // 检查当前是否已经是随机路线
    if (route_status === "stopped") {
        showAlert("当前已经是随机路线");
        return;
    }

    // 询问用户是否确认设置为随机路线
    showConfirmDialog("路线设置确认", "是否要将路线设置为随机路线？", function() {
        try {
            // 清除现有路线
            stopTrack();

            // 更新状态标识
            route_status = "stopped";

            // 将route_status更新同步到Python后端
            update_map_setting("route_status", route_status);

            // 清除后端数据库中的所有路线相关数据
            update_map_setting("route_start", "");
            update_map_setting("route_end", "");
            update_map_setting("route_current_position", "");
            update_map_setting("route", "");

            // 重置路线设置面板的UI状态
            const msgdiv = document.getElementById("setroute");
            if (msgdiv) {
                // 关闭设置面板
                msgdiv.style.display = "none";

                // 重置输入框状态
                const startInput = document.getElementById('start');
                const endInput = document.getElementById('end');
                if (startInput) startInput.removeAttribute('readonly');
                if (endInput) endInput.removeAttribute('readonly');

                // 重置按钮显示状态
                const buttons = msgdiv.getElementsByTagName('button');
                for (let i = 0; i < buttons.length; i++) {
                    const button = buttons[i];
                    const buttonText = button.textContent.trim();
                    if (buttonText === '确定') {
                        button.style.display = 'inline-block';
                    } else if (buttonText === '查看' || buttonText === '重设') {
                        button.style.display = 'none';
                    }
                }

                // 显示position_type下拉框
                const positionTypeSelect = document.getElementById("position_type");
                if (positionTypeSelect) {
                    positionTypeSelect.style.display = 'inline-block';
                }
            }

            // 重置坐标链接状态
            resetCoordinateLinks();

            // 只有在所有操作成功后才更新菜单项的勾选标记
            const randomRouteItem = document.getElementById("random_route");
            const specifiedRouteItem = document.getElementById("specified_route");

            if (randomRouteItem && specifiedRouteItem) {
                // 移除指定路线的勾选标记
                specifiedRouteItem.textContent = specifiedRouteItem.textContent.replace(' ✓', '');
                // 添加勾选标记到随机路线
                if (!randomRouteItem.textContent.includes('✓')) {
                    randomRouteItem.textContent += ' ✓';
                }
            }

            showAlert("已设置为随机路线");
        } catch (error) {
            // 如果操作失败，显示错误信息但不更新UI
            showAlert("设置随机路线失败: " + error.message);
            console.error("设置随机路线失败:", error);
        }
    }, function() {
        // 用户点击取消，不需要执行任何操作
        return;
    });
}



function closeRouteSetting() {
    //route_status = "stopped";
    msgdiv = document.getElementById("setroute");
    msgdiv.style.display = "none";

    // 重置坐标链接到初始状态
    resetCoordinateLinks();
}

// 重设路线函数
function resetRoute() {
    // 获取起点和终点输入框
    const startInput = document.getElementById('start');
    const endInput = document.getElementById('end');
    const msgdiv = document.getElementById("setroute");
    // 获取position_type下拉框
    const positionTypeSelect = document.getElementById('position_type');
    // 获取坐标链接元素
    const startCoordLink = document.getElementById("start_coord_link");
    const endCoordLink = document.getElementById("end_coord_link");

    // 移除只读属性
    startInput.removeAttribute('readonly');
    endInput.removeAttribute('readonly');

    // 显示确定按钮，隐藏查看和重设按钮
    const buttons = msgdiv.getElementsByTagName('button');
    for (let i = 0; i < buttons.length; i++) {
        const button = buttons[i];
        const buttonText = button.textContent.trim();
        if (buttonText === '确定') {
            button.style.display = 'inline-block';
        } else if (buttonText === '查看' || buttonText === '重设') {
            button.style.display = 'none';
        }
    }

    // 显示position_type下拉框
    if (positionTypeSelect) {
        positionTypeSelect.style.display = 'inline-block';
    }

    // 根据position_type的值决定是否显示坐标链接
    const positionType = document.getElementById("position_type").value;
    if (positionType === "coordinates") {
        if (startCoordLink) {
            startCoordLink.style.display = 'block';
        }
        if (endCoordLink) {
            endCoordLink.style.display = 'block';
        }
    } else {
        if (startCoordLink) {
            startCoordLink.style.display = 'none';
        }
        if (endCoordLink) {
            endCoordLink.style.display = 'none';
        }
    }

    // 清空输入框内容
    startInput.value = '';
    endInput.value = '';

    // 聚焦到起点输入框
    startInput.focus();
}


