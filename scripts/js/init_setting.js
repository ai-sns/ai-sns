//todo 优化调整顺序
// 初始化设置

// 定义一个函数，根据set_route_flag的值设置相应的✓
function initRouteDisplay() {

    const randomRouteItem = document.getElementById("random_route");
    const specifiedRouteItem = document.getElementById("specified_route");
    if (randomRouteItem && specifiedRouteItem) {
        if (route_status === "stopped") {
            // 随机路线状态，给随机路线添加✓
            if (!randomRouteItem.textContent.includes('✓')) {
                randomRouteItem.textContent += ' ✓';
            }
            // 确保指定路线没有✓
            specifiedRouteItem.textContent = specifiedRouteItem.textContent.replace(' ✓', '');
        } else {
            // 指定路线状态，给指定路线添加✓
            if (!specifiedRouteItem.textContent.includes('✓')) {
                specifiedRouteItem.textContent += ' ✓';
            }
            // 确保随机路线没有✓
            randomRouteItem.textContent = randomRouteItem.textContent.replace(' ✓', '');
        }
    }
}

showHistory();
// 定义一个异步函数，用于检查并显示积分
async function checkAndShowPoints() {
    // 检查是否已加载人员数据
    if (!persons_loaded_flag) {
        // 定义数据URL
        const host = (typeof base_url !== 'undefined' && base_url) ? base_url : (window.__AI_SNS_SERVER__ || '');
        const dataUrl = `${host}/personsdata.json`;

        try {
            // 加载人员数据
            const data = await loadPersonsData(dataUrl);
            console.log("成功加载人员数据:", data);

            // 显示加载成功的提示
            showAlert(`Person data loaded.`);

            // 存储加载的数据
            personsdata = data;

            // 显示积分
            showpoints();
        } catch (error) {
            console.error("加载人员数据时发生错误:", error);
            showAlert(`Error loading person data: ${error.message}`);
        }
    }
}

// 设置一个延迟调用checkAndShowPoints函数
setTimeout(checkAndShowPoints, 10000);

function set_shortcut_key() {
    // 为地址输入框添加键盘事件监听
    document.getElementById('home_address').addEventListener('keydown', handleKeyEvent.bind(null, updateHomePosition, closeHomePositionSetting));

    // 为起点输入框添加键盘事件监听
    document.getElementById('start').addEventListener('keydown', handleKeyEvent.bind(null, planRoute, closeRouteSetting));

    // 为终点输入框添加键盘事件监听
    document.getElementById('end').addEventListener('keydown', handleKeyEvent.bind(null, planRoute, closeRouteSetting));
}
// 通用键盘事件处理函数
function handleKeyEvent(action, closeAction, event) {
    if (event.key === 'Enter') {
        event.preventDefault(); // 阻止默认表单提交行为
        action(); // 执行对应操作
    } else if (event.key === 'Escape') {
        event.preventDefault(); // 阻止默认行为
        closeAction(); // 关闭对应面板
    }
}

// 页面加载完成后初始化路线显示状态
//initRouteDisplay();
// 初始化键盘快捷键
set_shortcut_key();
// 初始化路线规划功能

setTimeout(() => {
  // 判断 mapManager 是否存在，且具有 init 方法
  if (window.mapManager && typeof window.mapManager.init === 'function') {
    window.mapManager.init();
  } else {
    console.warn('mapManager 或 init 方法不存在，跳过初始化');
  }
}, 1000);


// 初始化
