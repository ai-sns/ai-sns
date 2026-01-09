const { app, BrowserWindow, ipcMain, Menu, Tray, dialog, shell } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

// Windows 10 + 无边框窗口：禁用 GPU 硬件加速（可选，根据需要启用）
// app.disableHardwareAcceleration();

let mainWindow = null;
let mapWindow = null;

// Azure OpenAI 配置已移至后端 API Server（api_server.py）
// 配置从数据库或环境变量读取
// const AZURE_OPENAI_CONFIG = {
//     baseUrl: 'https://api.chatanywhere.tech/v1',
//     apiKey: 'sk-SVCuk9EAqrgUEvvh31PKxVIr1fZhwt5boDB2Hexw8vs2Bl26',
//     model: 'gpt-4o-mini'
// };
let tray = null;
let pythonProcess = null;
let isQuitting = false;

// API服务器配置
const API_HOST = '127.0.0.1';  // 明确使用 IPv4，避免 IPv6 解析问题
const API_PORT = 8788;
const API_BASE_URL = `http://${API_HOST}:${API_PORT}`;

// 开发模式检测
const isDev = process.argv.includes('--dev') || process.env.NODE_ENV === 'development';

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        minWidth: 1000,
        minHeight: 700,
        icon: path.join(__dirname, '../images/logowithe.png'),
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js'),
            webSecurity: false,  // 禁用跨域安全策略，允许加载本地服务器地图
            // 确保输入框可用
            enableBlinkFeatures: 'KeyboardFocusableScrollers'
        },
        // 无边框窗口，使用自定义标题栏
        frame: false,
        // macOS 专用设置
        trafficLightPosition: { x: 16, y: 16 },
        // 启用窗口透明效果
        transparent: false,
        backgroundColor: '#f5f5f5',
        // 启用窗口阴影
        hasShadow: true,
        show: false,
        // Windows 焦点修复
        skipTaskbar: false,
        focusable: true
    });

    // 移除应用菜单
    Menu.setApplicationMenu(null);

    // 加载主页面
    mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'));

    // 窗口准备好后显示
    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
        mainWindow.focus();
        mainWindow.webContents.focus();

        if (isDev) {
            console.log('开发模式：打开开发者工具');
            mainWindow.webContents.openDevTools({
                mode: 'right' // 在右侧打开开发者工具
            });
        }
    });

    // 窗口关闭事件处理（最小化到托盘）
    mainWindow.on('close', (event) => {
        if (!isQuitting) {
            event.preventDefault();
            mainWindow.hide();
            if (tray) {
                tray.displayBalloon({
                    title: 'AI-SNS',
                    content: '应用已最小化到托盘，点击托盘图标可恢复窗口'
                });
            }
        }
    });

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

function createMapWindow() {
    mapWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        minWidth: 800,
        minHeight: 600,
        icon: path.join(__dirname, '../images/logowithe.png'),
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js'),
            webSecurity: true
        },
        frame: true,
        backgroundColor: '#f5f5f5',
        show: false
    });

    // 加载地图页面
    mapWindow.loadURL('http://localhost:8788/scripts/map.html');

    // 窗口准备好后显示
    mapWindow.once('ready-to-show', () => {
        mapWindow.show();
        mapWindow.focus();

        if (isDev) {
            mapWindow.webContents.openDevTools();
        }
    });

    mapWindow.on('closed', () => {
        mapWindow = null;
    });
}
function createTray() {
    const iconPath = path.join(__dirname, '../images/logowithe.png');
    tray = new Tray(iconPath);

    const contextMenu = Menu.buildFromTemplate([
        {
            label: '显示',
            click: () => {
                if (mainWindow) {
                    mainWindow.show();
                    mainWindow.focus();
                }
            }
        },
        {
            label: '隐藏',
            click: () => {
                if (mainWindow) {
                    mainWindow.hide();
                }
            }
        },
        {
            label: '地图',
            click: () => {
                createMapWindow();
            }
        },
        { type: 'separator' },
        {
            label: '退出',
            click: () => {
                isQuitting = true;
                app.quit();
            }
        }
    ]);

    tray.setToolTip('AI-SNS - AI Agent Social Network');
    tray.setContextMenu(contextMenu);

    tray.on('click', () => {
        if (mainWindow) {
            if (mainWindow.isVisible()) {
                mainWindow.hide();
            } else {
                mainWindow.show();
                mainWindow.focus();
            }
        }
    });
}

// IPC通信处理
ipcMain.handle('get-api-url', () => {
    return API_BASE_URL;
});

ipcMain.handle('get-app-path', () => {
    return app.getAppPath();
});

ipcMain.handle('show-open-dialog', async (event, options) => {
    const result = await dialog.showOpenDialog(mainWindow, options);
    return result;
});

ipcMain.handle('show-save-dialog', async (event, options) => {
    const result = await dialog.showSaveDialog(mainWindow, options);
    return result;
});

ipcMain.handle('show-message-box', async (event, options) => {
    const result = await dialog.showMessageBox(mainWindow, options);
    return result;
});

ipcMain.on('set-title', (event, title) => {
    if (mainWindow) {
        mainWindow.setTitle(title);
    }
});

// 地图窗口控制 IPC
ipcMain.on('open-map-window', () => {
    createMapWindow();
});

ipcMain.on('close-map-window', () => {
    if (mapWindow) {
        mapWindow.close();
    }
});

ipcMain.on('maximize-map-window', () => {
    if (mapWindow) {
        if (mapWindow.isMaximized()) {
            mapWindow.unmaximize();
        } else {
            mapWindow.maximize();
        }
    }
});

ipcMain.on('minimize-map-window', () => {
    if (mapWindow) {
        mapWindow.minimize();
    }
});

// 地图操作 IPC
ipcMain.on('map-command', (event, data) => {
    if (mapWindow) {
        mapWindow.webContents.send('map-command', data);
    }
});

// 地图配置 IPC
ipcMain.handle('load-map-setting', async () => {
    // TODO: 从配置文件或数据库加载地图设置
    return {
        mapType: 'baidu',
        center: { lng: 116.3974, lat: 39.9093 },
        zoom: 13,
        homePosition: null,
        route: null
    };
});

ipcMain.handle('save-map-setting', async (event, setting) => {
    // TODO: 保存地图设置到配置文件或数据库
    console.log('Saving map setting:', setting);
    return true;
});

// 地图聊天 IPC
ipcMain.on('map-chat-message', (event, data) => {
    if (mapWindow) {
        mapWindow.webContents.send('map-chat-message', data);
    }
});

// 打开链接 IPC
ipcMain.on('open-url', (event, url) => {
    shell.openExternal(url);
});

// 窗口控制 IPC
ipcMain.on('window-minimize', () => {
    if (mainWindow) {
        mainWindow.minimize();
    }
});

ipcMain.on('window-maximize', () => {
    if (mainWindow) {
        if (mainWindow.isMaximized()) {
            mainWindow.unmaximize();
        } else {
            mainWindow.maximize();
        }
    }
});

ipcMain.on('window-close', () => {
    if (mainWindow) {
        mainWindow.close();
    }
});

ipcMain.handle('window-is-maximized', () => {
    return mainWindow ? mainWindow.isMaximized() : false;
});

ipcMain.on('minimize-to-tray', () => {
    if (mainWindow) {
        mainWindow.hide();
    }
});

ipcMain.on('quit-app', () => {
    isQuitting = true;
    app.quit();
});

// 修复 Windows 10 无边框窗口输入框焦点问题
ipcMain.on('fix-input-focus', () => {
    if (mainWindow) {
        // 模拟最小化再还原，强制触发 Windows 焦点事件
        mainWindow.minimize();
        setTimeout(() => {
            mainWindow.restore();
            mainWindow.focus();
            mainWindow.webContents.focus();
        }, 50);
    }
});

// Azure OpenAI 流式聊天（通过后端 API Server）
ipcMain.on('chat-stream-start', async (event, { messages, requestId }) => {
    try {
        const http = require('http');

        const requestBody = JSON.stringify({
            messages: messages,
            temperature: 1.0,
            max_tokens: 4096
        });

        console.log(`Sending chat request to backend: ${API_BASE_URL}/api/chat/stream`);

        const options = {
            hostname: API_HOST,
            port: API_PORT,
            path: '/api/chat/stream',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'text/event-stream',
                'Content-Length': Buffer.byteLength(requestBody)
            }
        };

        const req = http.request(options, (res) => {
            let buffer = '';

            console.log(`Response status: ${res.statusCode}`);
            console.log(`Response headers:`, res.headers);

            // 检查 HTTP 状态码
            if (res.statusCode !== 200) {
                let errorBody = '';
                res.on('data', (chunk) => {
                    errorBody += chunk.toString();
                });
                res.on('end', () => {
                    console.error(`API Error Response: ${errorBody}`);
                    event.sender.send('chat-stream-error', {
                        requestId,
                        error: `HTTP ${res.statusCode}: ${errorBody}`
                    });
                });
                return;
            }

            // 处理 SSE 流
            res.on('data', (chunk) => {
                const chunkStr = chunk.toString();
                buffer += chunkStr;

                // 处理 SSE 数据
                const lines = buffer.split('\n');
                buffer = lines.pop() || ''; // 保留未完成的行

                for (const line of lines) {
                    const trimmedLine = line.trim();

                    // SSE 格式: event: message\ndata: {...}
                    if (trimmedLine.startsWith('event:')) {
                        // 跳过 event 行
                        continue;
                    }

                    if (trimmedLine.startsWith('data:')) {
                        const data = trimmedLine.slice(5).trim();

                        try {
                            const parsed = JSON.parse(data);

                            // 处理消息内容
                            if (parsed.content) {
                                console.log(`Stream content: ${parsed.content}`);
                                event.sender.send('chat-stream-data', { requestId, content: parsed.content });
                            }

                            // 处理完成状态
                            if (parsed.status === 'completed') {
                                console.log('Stream completed');
                                event.sender.send('chat-stream-end', { requestId });
                                return;
                            }

                            // 处理错误
                            if (parsed.error) {
                                console.error(`Stream error: ${parsed.error}`);
                                event.sender.send('chat-stream-error', { requestId, error: parsed.error });
                                return;
                            }
                        } catch (e) {
                            console.log(`Parse error for line: ${trimmedLine}, error: ${e.message}`);
                        }
                    }
                }
            });

            res.on('end', () => {
                console.log('Stream connection closed');
                // 处理剩余的 buffer
                if (buffer.trim()) {
                    const lines = buffer.split('\n');
                    for (const line of lines) {
                        const trimmedLine = line.trim();
                        if (trimmedLine.startsWith('data:')) {
                            const data = trimmedLine.slice(5).trim();
                            try {
                                const parsed = JSON.parse(data);
                                if (parsed.content) {
                                    event.sender.send('chat-stream-data', { requestId, content: parsed.content });
                                }
                            } catch (e) {}
                        }
                    }
                }
                event.sender.send('chat-stream-end', { requestId });
            });

            res.on('error', (error) => {
                console.error(`Response error: ${error.message}`);
                event.sender.send('chat-stream-error', { requestId, error: error.message });
            });
        });

        req.on('error', (error) => {
            console.error(`Request error: ${error.message}`);
            event.sender.send('chat-stream-error', { requestId, error: error.message });
        });

        req.write(requestBody);
        req.end();

    } catch (error) {
        console.error(`Chat stream start error: ${error.message}`);
        event.sender.send('chat-stream-error', { requestId, error: error.message });
    }
});

// Windows 焦点修复：窗口获得焦点时确保 webContents 也获得焦点
app.on('browser-window-focus', () => {
    const win = BrowserWindow.getFocusedWindow();
    if (win) {
        win.webContents.focus();
    }
});

// 应用生命周期
app.whenReady().then(() => {
    createWindow();
    createTray();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        } else if (mainWindow) {
            mainWindow.show();
        }
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('before-quit', () => {
    isQuitting = true;
    // 清理Python进程
    if (pythonProcess) {
        pythonProcess.kill();
    }
});

// 错误处理
process.on('uncaughtException', (error) => {
    console.error('Uncaught Exception:', error);
    dialog.showErrorBox('错误', `发生未捕获的异常: ${error.message}`);
});
