/**
 * SNS Module - Event Handlers
 * SNS事件处理和初始化
 */

import snsState from './snsState.js';
import snsApi from './snsApi.js';
import { SNSAvatarDialog } from './SNSAvatarDialog.js';
import { SNSProfessionDialog } from './SNSProfessionDialog.js';
import { SNSSocialRoleDialog } from './SNSSocialRoleDialog.js';
import { SNSMapConfigDialog } from './SNSMapConfigDialog.js';

export default {
    resolve(urlOrPath) {
        try {
            if (typeof window !== 'undefined' && typeof window.resolveAgentServerUrl === 'function') {
                return window.resolveAgentServerUrl(urlOrPath);
            }
        } catch (e) {
        }
        return urlOrPath;
    },

    getMapIframeTargetOrigin() {
        try {
            const iframe = document.querySelector('#mapContainer iframe');
            const src = iframe ? iframe.getAttribute('src') : '';
            if (src) {
                const u = new URL(src, window.location && window.location.href ? window.location.href : undefined);
                return u.origin;
            }
        } catch (e) {
        }
        const agentBase = (window.appConfig && window.appConfig.agent_server) ? String(window.appConfig.agent_server) : '';
        try {
            if (agentBase) {
                return new URL(agentBase).origin;
            }
        } catch (e) {
        }
        return '*';
    },

    safePostMessageToMap(iframe, message, preferredOrigin = '*') {
        if (!iframe || !iframe.contentWindow) return false;
        let origin = preferredOrigin || '*';

        try {
            // If the iframe is blocked or has opaque origin, prefer '*' to avoid mismatches.
            // Accessing contentWindow.location may throw due to cross-origin restrictions.
            const loc = iframe.contentWindow.location;
            if (loc && typeof loc.origin === 'string' && loc.origin === 'null') {
                origin = '*';
            }
        } catch (e) {
            origin = '*';
        }

        try {
            iframe.contentWindow.postMessage(message, origin);
            return true;
        } catch (e) {
            try {
                // Last resort
                iframe.contentWindow.postMessage(message, '*');
                return true;
            } catch (e2) {
                return false;
            }
        }
    },
    /**
     * 初始化SNS页面
     */
    init() {
        console.log('SNS 页面控制器初始化');
        this.loadBaiduMap();
        this.loadSNSData();
        this.initSNSPanelResizer();
        this.initSNSStatusTabs();
        this.initSNSContextMenu();
        this.initSNSStatusTabReloadMenu();
        this.initSNSSearch();
        this.initSNSToolbar();
        this.initSNSSettingsPanel();
        this.initConfigButtons();
        this.initSNSActionBar();
        this.initMapReloadListener();
        this.initSNSUpdateListener();
    },

    initSNSStatusTabReloadMenu() {
        const statusTabs = document.getElementById('statusTabs');
        const statusTabContent = document.getElementById('statusTabContent');
        if (!statusTabs || !statusTabContent) return;

        if (this._snsTabReloadMenuInitialized) return;
        this._snsTabReloadMenuInitialized = true;

        const existingMenu = document.getElementById('snsTabReloadContextMenu');
        const menu = existingMenu || (() => {
            const el = document.createElement('div');
            el.id = 'snsTabReloadContextMenu';
            el.className = 'status-context-menu compact';
            el.innerHTML = `
                <button type="button" class="context-menu-item" data-action="reload">
                    <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <polyline points="23 4 23 10 17 10"></polyline>
                        <polyline points="1 20 1 14 7 14"></polyline>
                        <path d="M3.51 9a9 9 0 0 1 14.13-3.36L23 10"></path>
                        <path d="M20.49 15a9 9 0 0 1-14.13 3.36L1 14"></path>
                    </svg>
                    <span>刷新</span>
                </button>
                <button type="button" class="context-menu-item" data-action="open-browser">
                    <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                        <polyline points="15 3 21 3 21 9"/>
                        <line x1="10" y1="14" x2="21" y2="3"/>
                    </svg>
                    <span>Open in Browser</span>
                </button>
                <button type="button" class="context-menu-item" data-action="copy-url">
                    <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                    </svg>
                    <span>Copy URL</span>
                </button>
            `;
            document.body.appendChild(el);
            return el;
        })();

        let currentTabKey = null;
        let removeObserver = null;

        const hideMenu = () => {
            menu.style.display = 'none';
            menu.dataset.tab = '';
            currentTabKey = null;
            if (removeObserver) {
                removeObserver.disconnect();
                removeObserver = null;
            }
        };

        const getCurrentIframeUrl = () => {
            if (!isCurrentTargetAlive()) return '';
            const pane = statusTabContent.querySelector(`.tab-pane[data-tab="${currentTabKey}"]`);
            const iframe = pane ? pane.querySelector('iframe') : null;
            const src = iframe && iframe.src ? String(iframe.src) : '';
            if (!src) return '';
            try {
                const u = new URL(src);
                u.searchParams.delete('_ts');
                return u.toString();
            } catch (e) {
                return src;
            }
        };

        const copyTextToClipboard = async (text) => {
            if (!text) return false;

            try {
                if (window.electronAPI && typeof window.electronAPI.writeClipboardText === 'function') {
                    const res = await window.electronAPI.writeClipboardText(text);
                    if (res && res.success) return true;
                }
            } catch (e) {
            }

            try {
                if (navigator.clipboard && typeof navigator.clipboard.writeText === 'function') {
                    await navigator.clipboard.writeText(text);
                    return true;
                }
            } catch (e) {
            }

            try {
                const textarea = document.createElement('textarea');
                textarea.value = text;
                textarea.setAttribute('readonly', '');
                textarea.style.position = 'fixed';
                textarea.style.left = '-9999px';
                textarea.style.top = '-9999px';
                document.body.appendChild(textarea);
                textarea.focus();
                textarea.select();
                textarea.setSelectionRange(0, textarea.value.length);
                const ok = document.execCommand('copy');
                textarea.remove();
                return !!ok;
            } catch (e) {
                return false;
            }
        };

        const isCurrentTargetAlive = () => {
            if (!currentTabKey) return false;
            const tabBtn = statusTabs.querySelector(`.status-tab[data-tab="${currentTabKey}"]`);
            const pane = statusTabContent.querySelector(`.tab-pane[data-tab="${currentTabKey}"]`);
            return !!(tabBtn && pane);
        };

        const reloadCurrentIframe = () => {
            if (!isCurrentTargetAlive()) {
                hideMenu();
                return;
            }

            const pane = statusTabContent.querySelector(`.tab-pane[data-tab="${currentTabKey}"]`);
            const iframe = pane ? pane.querySelector('iframe') : null;
            if (iframe && iframe.src) {
                try {
                    if (iframe.contentWindow && iframe.contentWindow.location && typeof iframe.contentWindow.location.reload === 'function') {
                        iframe.contentWindow.location.reload();
                        return;
                    }
                } catch (e) {
                    // ignore and fallback to src reload
                }

                try {
                    const u = new URL(iframe.src);
                    u.searchParams.set('_ts', String(Date.now()));
                    iframe.src = u.toString();
                } catch (e) {
                    const sep = iframe.src.includes('?') ? '&' : '?';
                    iframe.src = `${iframe.src}${sep}_ts=${Date.now()}`;
                }
            }
        };

        const showMenuAt = (x, y) => {
            menu.style.display = 'block';
            const menuWidth = menu.offsetWidth || 140;
            const menuHeight = menu.offsetHeight || 38;
            const viewportWidth = window.innerWidth;
            const viewportHeight = window.innerHeight;
            let left = x;
            let top = y;
            if (left + menuWidth > viewportWidth) left = viewportWidth - menuWidth - 10;
            if (top + menuHeight > viewportHeight) top = viewportHeight - menuHeight - 10;
            menu.style.left = left + 'px';
            menu.style.top = top + 'px';
        };

        document.addEventListener('click', (e) => {
            if (!menu.contains(e.target)) hideMenu();
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') hideMenu();
        });

        window.addEventListener('blur', hideMenu);
        window.addEventListener('resize', hideMenu);
        window.addEventListener('scroll', hideMenu, true);

        menu.addEventListener('click', (e) => {
            const item = e.target.closest('.context-menu-item');
            if (!item) return;
            const action = item.dataset.action;
            if (action === 'reload') {
                reloadCurrentIframe();
            } else if (action === 'open-browser') {
                const url = getCurrentIframeUrl();
                if (url) {
                    if (window.electronAPI && window.electronAPI.openUrl) {
                        window.electronAPI.openUrl(url);
                    } else {
                        window.open(url, '_blank');
                    }
                }
            } else if (action === 'copy-url') {
                const url = getCurrentIframeUrl();
                if (url) {
                    copyTextToClipboard(url).then((ok) => {
                        if (ok) console.log('URL copied to clipboard');
                    });
                }
            }
            hideMenu();
        });

        statusTabs.addEventListener('contextmenu', (e) => {
            const tabBtn = e.target.closest('.status-tab');
            if (!tabBtn) return;
            if (e.target.closest('.tab-close-btn')) return;

            const tabKey = tabBtn.dataset.tab;
            if (tabKey !== 'profile' && tabKey !== 'placeIntro') return;

            e.preventDefault();
            e.stopPropagation();

            currentTabKey = tabKey;
            menu.dataset.tab = tabKey;
            showMenuAt(e.clientX, e.clientY);

            if (removeObserver) {
                removeObserver.disconnect();
                removeObserver = null;
            }
            removeObserver = new MutationObserver(() => {
                if (!isCurrentTargetAlive()) hideMenu();
            });
            removeObserver.observe(document.body, { childList: true, subtree: true });
        });

        document.addEventListener('click', (e) => {
            if (e.target.closest('#statusTabs .tab-close-btn')) {
                hideMenu();
            }
        });
    },

    /**
     * 销毁SNS页面
     */
    destroy() {
        // 清理事件监听器
        this.cleanupMapListeners();

        // 移除 SNS 更新监听器
        if (this.snsUpdateListener) {
            window.removeEventListener('websocket-message', this.snsUpdateListener);
        }
    },

    /**
     * 初始化顶部工具栏收缩功能
     */
    initSNSToolbar() {
        const toolbar = document.getElementById('snsToolbar');
        const collapseBtn = document.getElementById('toolbarCollapseBtn');
        const expandBtn = document.getElementById('toolbarExpandBtn');
        const mapArea = document.querySelector('.sns-map-area');

        if (!toolbar || !collapseBtn || !expandBtn || !mapArea) return;

        // 从 localStorage 恢复状态
        const savedCollapsed = localStorage.getItem('snsToolbarCollapsed') === 'true';
        if (savedCollapsed) {
            toolbar.classList.add('collapsed');
            mapArea.classList.add('toolbar-hidden');
        }

        // 收起工具栏
        collapseBtn.addEventListener('click', () => {
            toolbar.classList.add('collapsed');
            mapArea.classList.add('toolbar-hidden');
            localStorage.setItem('snsToolbarCollapsed', 'true');
        });

        // 展开工具栏
        expandBtn.addEventListener('click', () => {
            toolbar.classList.remove('collapsed');
            mapArea.classList.remove('toolbar-hidden');
            localStorage.setItem('snsToolbarCollapsed', 'false');
        });
    },

    /**
     * 初始化右侧设置面板收缩功能
     */
    initSNSSettingsPanel() {
        const panel = document.getElementById('mapSettingsPanel');
        const collapseBtn = document.getElementById('settingsCollapseBtn');
        const expandBtn = document.getElementById('settingsExpandBtn');
        const mapArea = document.querySelector('.sns-map-area');

        if (!panel || !collapseBtn || !expandBtn || !mapArea) return;

        // 从 localStorage 恢复状态
        const savedCollapsed = localStorage.getItem('snsSettingsPanelCollapsed') === 'true';
        if (savedCollapsed) {
            panel.classList.add('collapsed');
            mapArea.classList.add('settings-hidden');
        }

        // 收起设置面板
        collapseBtn.addEventListener('click', () => {
            panel.classList.add('collapsed');
            mapArea.classList.add('settings-hidden');
            localStorage.setItem('snsSettingsPanelCollapsed', 'true');
        });

        // 展开设置面板
        expandBtn.addEventListener('click', () => {
            panel.classList.remove('collapsed');
            mapArea.classList.remove('settings-hidden');
            localStorage.setItem('snsSettingsPanelCollapsed', 'false');
        });

        // Add configuration buttons
        this.initConfigButtons();
    },

    /**
     * Initialize configuration buttons
     */
    initConfigButtons() {
        // Avatar configuration button
        const avatarBtn = document.getElementById('snsAvatarConfigBtn');
        if (avatarBtn) {
            avatarBtn.addEventListener('click', async () => {
                const dialog = new SNSAvatarDialog();
                await dialog.show();
            });
        }

        // Profession configuration button
        const professionBtn = document.getElementById('snsProfessionConfigBtn');
        if (professionBtn) {
            professionBtn.addEventListener('click', async () => {
                const dialog = new SNSProfessionDialog();
                await dialog.show();
            });
        }

        // Social role configuration button
        const socialRoleBtn = document.getElementById('snsSocialRoleConfigBtn');
        if (socialRoleBtn) {
            socialRoleBtn.addEventListener('click', async () => {
                const dialog = new SNSSocialRoleDialog();
                await dialog.show();
            });
        }

        // Map configuration button
        const mapConfigBtn = document.getElementById('snsMapConfigBtn');
        if (mapConfigBtn) {
            mapConfigBtn.addEventListener('click', async () => {
                const dialog = new SNSMapConfigDialog();
                await dialog.show();
            });
        }
    },

    /**
     * 初始化地图重新加载监听器
     */
    initMapReloadListener() {
        window.addEventListener('reloadMap', () => {
            console.log('Received reloadMap event - reloading map');
            this.loadBaiduMap();
        });
    },

    /**
     * 初始化底部动作栏
     */
    initSNSActionBar() {
        const actionBar = document.querySelector('.map-action-bar');
        if (!actionBar) return;

        const state1 = document.getElementById('actionBarState1');
        const state2 = document.getElementById('actionBarState2');
        const controlBtn = document.getElementById('controlBtn');
        const computerBtn = document.getElementById('computerBtn');
        const appsMenuBtn = document.getElementById('appsMenuBtn');
        const mapMenuBtn = document.getElementById('mapMenuBtn');
        const appsDropdown = document.getElementById('appsDropdown');
        const mapDropdown = document.getElementById('mapDropdown');

        // Toggle between state 1 and state 2
        const switchToState2 = () => {
            if (state1 && state2) {
                state1.style.display = 'none';
                state2.style.display = 'block';
            }

            // Enter control mode => backend human_take_over = true
            const activeToggle = actionBar.querySelector('.toggle-btn.active');
            const mode = activeToggle ? activeToggle.dataset.mode : 'ai';
            const humanTalkType = mode === 'ai' ? 0 : 1;
            snsApi.setHumanControlState(true, humanTalkType);
        };

        const switchToState1 = () => {
            if (state1 && state2) {
                state1.style.display = 'flex';
                state2.style.display = 'none';
            }

            // Exit control mode => backend human_take_over = false
            snsApi.setHumanControlState(false, null);
        };

        // Control button click - switch to state 2
        if (controlBtn) {
            controlBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                switchToState2();
            });
        }

        // Computer button click - switch back to state 1
        if (computerBtn) {
            computerBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                switchToState1();
            });
        }

        // Apps menu dropdown toggle
        if (appsMenuBtn && appsDropdown) {
            appsMenuBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                const isVisible = appsDropdown.style.display === 'block';
                appsDropdown.style.display = isVisible ? 'none' : 'block';
                if (mapDropdown) mapDropdown.style.display = 'none';
            });
        }

        // Map menu dropdown toggle
        if (mapMenuBtn && mapDropdown) {
            mapMenuBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                const isVisible = mapDropdown.style.display === 'block';
                mapDropdown.style.display = isVisible ? 'none' : 'block';
                if (appsDropdown) appsDropdown.style.display = 'none';
            });
        }

        // Close dropdowns when clicking outside
        document.addEventListener('click', () => {
            if (appsDropdown) appsDropdown.style.display = 'none';
            if (mapDropdown) mapDropdown.style.display = 'none';
        });

        // Toggle buttons in control mode
        const toggleBtns = actionBar.querySelectorAll('.toggle-btn');
        toggleBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                toggleBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');

                // Sync backend talk type when toggled
                const mode = btn.dataset.mode || 'ai';
                const humanTalkType = mode === 'ai' ? 0 : 1;
                // Keep take over aligned with current UI state
                const inControlState = state2 && state2.style.display !== 'none';
                snsApi.setHumanControlState(!!inControlState, humanTalkType);
            });
        });

        // 动作按钮点击事件
        actionBar.addEventListener('click', (e) => {
            const btn = e.target.closest('.action-btn, .dropdown-item');
            if (!btn) return;

            const action = btn.dataset.action;
            if (!action) return;

            // 更新激活状态
            const allBtns = actionBar.querySelectorAll('.action-btn');
            allBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Close dropdowns after selection
            if (appsDropdown) appsDropdown.style.display = 'none';
            if (mapDropdown) mapDropdown.style.display = 'none';

            // 处理不同的动作
            console.log('SNS Action:', action);

            // 建立 action 到 map.html 按钮 data-title 的映射
            const actionToTitleMap = {
                'home': 'home',
                'square': 'plaza',
                'ai': 'AI',
                'move': 'move',
                'board': 'activity'
            };

            // 如果是 home, square, ai, move, board 这些动作，向 map iframe 发送消息
            const mapActions = ['home', 'square', 'ai', 'move', 'board'];
            if (mapActions.includes(action)) {
                const iframe = document.querySelector('#mapContainer iframe');
                if (iframe && iframe.contentWindow) {
                    const message = {
                        type: 'mapButtonAction',
                        action: actionToTitleMap[action]  // 转换为对应的 data-title
                    };
                    try {
                        iframe.contentWindow.postMessage(message, this.getMapIframeTargetOrigin());
                        console.log('Sent mapButtonAction to iframe:', message);
                    } catch (error) {
                        console.error('Failed to send message to iframe:', error);
                    }
                } else {
                    console.warn('Map iframe not found or not ready');
                }
            }
        });

        // Start 按钮
        const startBtn = document.getElementById('snsStartBtn');
        if (startBtn) {
            startBtn.addEventListener('click', async () => {
                const isRunning = startBtn.classList.contains('running');
                const buttonText = startBtn.textContent.trim();

                if (!isRunning && buttonText === 'Start') {
                    // 启动引擎
                    startBtn.disabled = true;
                    startBtn.innerHTML = `<svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><circle cx="12" cy="12" r="10" opacity="0.3"/></svg><span>Starting...</span>`;

                    try {
                        const result = await snsApi.startEngine();

                        if (result.success) {
                            startBtn.classList.add('running');
                            startBtn.innerHTML = `<svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg><span>Pause</span>`;
                            this.showToast('AI社交引擎已启动', 'success');
                        } else {
                            startBtn.innerHTML = `<svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M8 5v14l11-7z"/></svg><span>Start</span>`;
                            this.showToast(`启动失败: ${result.message}`, 'error');
                        }
                    } catch (error) {
                        console.error('启动引擎失败:', error);
                        startBtn.innerHTML = `<svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M8 5v14l11-7z"/></svg><span>Start</span>`;
                        this.showToast(`启动失败: ${error.message}`, 'error');
                    } finally {
                        startBtn.disabled = false;
                    }
                } else if (isRunning && buttonText === 'Pause') {
                    // 暂停引擎
                    startBtn.disabled = true;
                    startBtn.innerHTML = `<svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><circle cx="12" cy="12" r="10" opacity="0.3"/></svg><span>Pausing...</span>`;

                    try {
                        const result = await snsApi.pauseEngine();

                        if (result.success) {
                            startBtn.classList.remove('running');
                            startBtn.innerHTML = `<svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M8 5v14l11-7z"/></svg><span>Resume</span>`;
                            this.showToast('AI社交引擎已暂停', 'success');
                        } else {
                            startBtn.innerHTML = `<svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg><span>Pause</span>`;
                            this.showToast(`暂停失败: ${result.message}`, 'error');
                        }
                    } catch (error) {
                        console.error('暂停引擎失败:', error);
                        startBtn.innerHTML = `<svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg><span>Pause</span>`;
                        this.showToast(`暂停失败: ${error.message}`, 'error');
                    } finally {
                        startBtn.disabled = false;
                    }
                } else if (!isRunning && buttonText === 'Resume') {
                    // 恢复引擎
                    startBtn.disabled = true;
                    startBtn.innerHTML = `<svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><circle cx="12" cy="12" r="10" opacity="0.3"/></svg><span>Resuming...</span>`;

                    try {
                        const result = await snsApi.resumeEngine();

                        if (result.success) {
                            startBtn.classList.add('running');
                            startBtn.innerHTML = `<svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg><span>Pause</span>`;
                            this.showToast('AI社交引擎已恢复', 'success');
                        } else {
                            startBtn.innerHTML = `<svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M8 5v14l11-7z"/></svg><span>Resume</span>`;
                            this.showToast(`恢复失败: ${result.message}`, 'error');
                        }
                    } catch (error) {
                        console.error('恢复引擎失败:', error);
                        startBtn.innerHTML = `<svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M8 5v14l11-7z"/></svg><span>Resume</span>`;
                        this.showToast(`恢复失败: ${error.message}`, 'error');
                    } finally {
                        startBtn.disabled = false;
                    }
                }
            });
        }

        // Control Send 按钮
        const sendBtn = actionBar.querySelector('.control-send-btn');
        const inputField = actionBar.querySelector('.control-input');
        if (sendBtn && inputField) {
            const handleSend = async () => {
                const message = inputField.value.trim();
                if (!message) return;

                // 获取当前模式
                const activeToggle = actionBar.querySelector('.toggle-btn.active');
                const mode = activeToggle ? activeToggle.dataset.mode : 'ai';

                // 清空输入框
                inputField.value = '';

                try {
                    // Forward to backend AISocialEngine.human_message_received
                    // Ensure backend state matches UI at send time
                    const humanTalkType = mode === 'ai' ? 0 : 1;
                    await snsApi.setHumanControlState(true, humanTalkType);
                    const result = await snsApi.sendHumanMessage(message);

                    if (!result.success) {
                        this.showToast(`错误: ${result.message || '未知错误'}`, 'error');
                    }
                } catch (error) {
                    console.error('发送消息失败:', error);
                    this.showToast(`发送失败: ${error.message}`, 'error');
                }
            };

            sendBtn.addEventListener('click', handleSend);
            inputField.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    handleSend();
                }
            });
        }
    },

    /**
     * 初始化右侧面板收缩功能
     */
    initSNSPanelResizer() {
        const resizer = document.getElementById('snsPanelResizer');
        const collapseBtn = document.getElementById('snsPanelCollapseBtn');
        const statusPanel = document.getElementById('snsStatusPanel');

        if (!resizer || !collapseBtn || !statusPanel) return;

        // 从 localStorage 恢复面板状态
        const savedCollapsed = localStorage.getItem('snsPanelCollapsed') === 'true';
        if (savedCollapsed) {
            resizer.classList.add('collapsed');
            statusPanel.classList.add('collapsed');
        }

        // 折叠/展开按钮点击事件
        collapseBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const isCollapsed = statusPanel.classList.toggle('collapsed');
            resizer.classList.toggle('collapsed', isCollapsed);
            localStorage.setItem('snsPanelCollapsed', isCollapsed);
        });

        // 拖拽调整面板宽度
        let isResizing = false;
        let startX = 0;
        let startWidth = 0;

        resizer.addEventListener('mousedown', (e) => {
            if (e.target === collapseBtn || collapseBtn.contains(e.target)) return;
            if (statusPanel.classList.contains('collapsed')) return;

            isResizing = true;
            startX = e.clientX;
            startWidth = statusPanel.offsetWidth;
            resizer.classList.add('resizing');
            document.body.style.cursor = 'col-resize';
            document.body.style.userSelect = 'none';

            // 禁用 iframe 的鼠标事件，防止拖动时卡顿
            const iframes = document.querySelectorAll('iframe');
            iframes.forEach(iframe => {
                iframe.style.pointerEvents = 'none';
            });

            e.preventDefault();
        });

        document.addEventListener('mousemove', (e) => {
            if (!isResizing) return;

            // 向左拖拽增加宽度,向右拖拽减少宽度
            const deltaX = startX - e.clientX;
            const minPanelWidth = 200;
            const minMapWidth = 0;
            const layout = document.querySelector('.sns-page-layout');
            const layoutWidth = layout ? layout.getBoundingClientRect().width : window.innerWidth;
            const resizerWidth = resizer.getBoundingClientRect().width || 8;
            const maxPanelWidth = Math.max(minPanelWidth, Math.floor(layoutWidth - resizerWidth - minMapWidth));
            let newWidth = Math.max(minPanelWidth, Math.min(maxPanelWidth, startWidth + deltaX));
            if (newWidth > maxPanelWidth - 1) newWidth = maxPanelWidth;
            statusPanel.style.width = `${newWidth}px`;
        });

        document.addEventListener('mouseup', () => {
            if (isResizing) {
                isResizing = false;
                resizer.classList.remove('resizing');
                document.body.style.cursor = '';
                document.body.style.userSelect = '';

                // 恢复 iframe 的鼠标事件
                const iframes = document.querySelectorAll('iframe');
                iframes.forEach(iframe => {
                    iframe.style.pointerEvents = '';
                });
            }
        });
    },

    /**
     * 初始化状态页签切换
     */
    initSNSStatusTabs() {
        const tabsContainer = document.getElementById('statusTabs');
        const tabContent = document.getElementById('statusTabContent');

        if (!tabsContainer || !tabContent) return;

        // 存储每个页签的滚动位置
        const scrollPositions = {};

        const getActiveTab = () => {
            const activeBtn = tabsContainer.querySelector('.status-tab.active');
            return activeBtn ? activeBtn.dataset.tab : null;
        };

        const saveScrollPosition = (tab) => {
            if (!tab) return;
            scrollPositions[tab] = tabContent.scrollTop;
        };

        const restoreScrollPosition = (tab) => {
            if (!tab) return;
            const pos = scrollPositions[tab];
            tabContent.scrollTop = typeof pos === 'number' ? pos : 0;
        };

        const ensureTabButtonVisible = (tabBtn) => {
            if (!tabBtn) return;
            const containerRect = tabsContainer.getBoundingClientRect();
            const btnRect = tabBtn.getBoundingClientRect();

            // Only adjust horizontal scroll of the tabs bar; do not trigger vertical scroll.
            if (btnRect.left < containerRect.left) {
                tabsContainer.scrollLeft -= (containerRect.left - btnRect.left) + 16;
            } else if (btnRect.right > containerRect.right) {
                tabsContainer.scrollLeft += (btnRect.right - containerRect.right) + 16;
            }
        };

        // 页签切换事件
        tabsContainer.addEventListener('click', (e) => {
            const tabBtn = e.target.closest('.status-tab');
            if (!tabBtn) return;

            const targetTab = tabBtn.dataset.tab;
            if (!targetTab) return;

            // 保存当前激活页签的滚动位置
            const currentTab = getActiveTab();
            saveScrollPosition(currentTab);

            // 更新按钮激活状态
            tabsContainer.querySelectorAll('.status-tab').forEach(btn => {
                btn.classList.toggle('active', btn === tabBtn);
            });

            // 切换内容面板
            tabContent.querySelectorAll('.tab-pane').forEach(pane => {
                pane.classList.toggle('active', pane.dataset.tab === targetTab);
            });

            // 恢复目标页签的滚动位置
            requestAnimationFrame(() => {
                restoreScrollPosition(targetTab);
            });

            // 只调整页签按钮容器的横向滚动，不影响内容区域
            ensureTabButtonVisible(tabBtn);
        });

        // 检测滚动状态并添加渐变提示
        const updateScrollIndicators = () => {
            const scrollLeft = tabsContainer.scrollLeft;
            const scrollWidth = tabsContainer.scrollWidth;
            const clientWidth = tabsContainer.clientWidth;
            const maxScroll = scrollWidth - clientWidth;

            // 添加或移除滚动指示类
            if (scrollLeft > 5) {
                tabsContainer.classList.add('can-scroll-left');
            } else {
                tabsContainer.classList.remove('can-scroll-left');
            }

            if (scrollLeft < maxScroll - 5) {
                tabsContainer.classList.add('can-scroll-right');
            } else {
                tabsContainer.classList.remove('can-scroll-right');
            }
        };

        // 监听滚动事件
        tabsContainer.addEventListener('scroll', updateScrollIndicators);

        // 监听窗口大小变化
        const resizeObserver = new ResizeObserver(updateScrollIndicators);
        resizeObserver.observe(tabsContainer);

        // 初始检查
        setTimeout(updateScrollIndicators, 100);
    },

    /**
     * 初始化右键菜单
     */
    initSNSContextMenu() {
        const tabContent = document.getElementById('statusTabContent');
        const contextMenu = document.getElementById('statusContextMenu');
        const searchBar = document.getElementById('statusSearchBar');
        const searchInput = document.getElementById('statusSearchInput');

        if (!tabContent || !contextMenu) return;

        // 阻止默认右键菜单
        tabContent.addEventListener('contextmenu', (e) => {
            e.preventDefault();

            // 显示自定义右键菜单
            contextMenu.style.display = 'block';

            // 计算菜单位置
            const menuWidth = 180;
            const menuHeight = 120;
            const viewportWidth = window.innerWidth;
            const viewportHeight = window.innerHeight;

            let x = e.clientX;
            let y = e.clientY;

            // 防止菜单超出视口
            if (x + menuWidth > viewportWidth) {
                x = viewportWidth - menuWidth - 10;
            }
            if (y + menuHeight > viewportHeight) {
                y = viewportHeight - menuHeight - 10;
            }

            contextMenu.style.left = x + 'px';
            contextMenu.style.top = y + 'px';
        });

        // 点击其他地方关闭菜单
        document.addEventListener('click', (e) => {
            if (!contextMenu.contains(e.target)) {
                contextMenu.style.display = 'none';
            }
        });

        // 菜单项点击事件
        contextMenu.addEventListener('click', (e) => {
            const menuItem = e.target.closest('.context-menu-item');
            if (!menuItem) return;

            const action = menuItem.dataset.action;
            const activePane = tabContent.querySelector('.tab-pane.active');

            switch (action) {
                case 'copy':
                    // 复制选中的文本
                    const selectedText = window.getSelection().toString();
                    if (selectedText) {
                        navigator.clipboard.writeText(selectedText).then(() => {
                            console.log('文本已复制到剪贴板');
                        }).catch(err => {
                            console.error('复制失败:', err);
                        });
                    }
                    break;

                case 'selectAll':
                    // 选中当前页签的所有文本
                    if (activePane) {
                        const range = document.createRange();
                        range.selectNodeContents(activePane);
                        const selection = window.getSelection();
                        selection.removeAllRanges();
                        selection.addRange(range);
                    }
                    break;

                case 'search':
                    // 显示搜索栏
                    if (searchBar) {
                        searchBar.style.display = 'flex';
                        // 聚焦到搜索框
                        setTimeout(() => {
                            if (searchInput) {
                                searchInput.focus();
                                // 如果有选中的文本，自动填充到搜索框
                                const selectedText = window.getSelection().toString();
                                if (selectedText) {
                                    searchInput.value = selectedText;
                                    // 触发搜索
                                    const event = new Event('input', { bubbles: true });
                                    searchInput.dispatchEvent(event);
                                }
                            }
                        }, 100);
                    }
                    break;
            }

            // 关闭菜单
            contextMenu.style.display = 'none';
        });

        // ESC 键关闭菜单
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                contextMenu.style.display = 'none';
            }
        });
    },

    /**
     * 初始化状态面板搜索功能
     */
    initSNSSearch() {
        const searchInput = document.getElementById('statusSearchInput');
        const searchClear = document.getElementById('statusSearchClear');
        const searchResultsInfo = document.getElementById('searchResultsInfo');
        const searchResultsText = document.getElementById('searchResultsText');
        const searchPrevBtn = document.getElementById('searchPrevBtn');
        const searchNextBtn = document.getElementById('searchNextBtn');
        const tabContent = document.getElementById('statusTabContent');

        if (!searchInput || !tabContent) return;

        let currentMatches = [];
        let currentMatchIndex = -1;

        // 高亮搜索结果
        const highlightMatches = (searchText) => {
            // 清除之前的高亮
            this.clearSearchHighlights();

            if (!searchText.trim()) {
                searchResultsInfo.style.display = 'none';
                return;
            }

            // 获取当前激活的页签
            const activePane = tabContent.querySelector('.tab-pane.active');
            if (!activePane) return;

            // 搜索文本内容
            const textNodes = this.getTextNodes(activePane);
            currentMatches = [];

            const searchLower = searchText.toLowerCase();

            textNodes.forEach(node => {
                const text = node.textContent;
                const textLower = text.toLowerCase();
                let index = 0;

                while ((index = textLower.indexOf(searchLower, index)) !== -1) {
                    // 创建高亮标记
                    const range = document.createRange();
                    range.setStart(node, index);
                    range.setEnd(node, index + searchText.length);

                    const mark = document.createElement('mark');
                    mark.className = 'search-highlight';
                    mark.textContent = text.substring(index, index + searchText.length);

                    range.deleteContents();
                    range.insertNode(mark);

                    currentMatches.push(mark);
                    index += searchText.length;

                    // 更新节点引用（因为DOM已改变）
                    node = mark.nextSibling;
                    if (!node || node.nodeType !== Node.TEXT_NODE) break;
                }
            });

            // 更新搜索结果信息
            if (currentMatches.length > 0) {
                searchResultsInfo.style.display = 'flex';
                searchResultsText.textContent = `找到 ${currentMatches.length} 个结果`;
                currentMatchIndex = 0;
                this.scrollToMatch(currentMatchIndex);
            } else {
                searchResultsInfo.style.display = 'flex';
                searchResultsText.textContent = '未找到结果';
                currentMatchIndex = -1;
            }
        };

        // 获取所有文本节点
        this.getTextNodes = (element) => {
            const textNodes = [];
            const walker = document.createTreeWalker(
                element,
                NodeFilter.SHOW_TEXT,
                {
                    acceptNode: (node) => {
                        // 跳过空白节点和已高亮的节点
                        if (!node.textContent.trim() || node.parentElement.tagName === 'MARK') {
                            return NodeFilter.FILTER_REJECT;
                        }
                        return NodeFilter.FILTER_ACCEPT;
                    }
                }
            );

            let node;
            while (node = walker.nextNode()) {
                textNodes.push(node);
            }
            return textNodes;
        };

        // 清除搜索高亮
        this.clearSearchHighlights = () => {
            const highlights = tabContent.querySelectorAll('.search-highlight');
            highlights.forEach(mark => {
                const parent = mark.parentNode;
                parent.replaceChild(document.createTextNode(mark.textContent), mark);
                parent.normalize(); // 合并相邻的文本节点
            });
            currentMatches = [];
            currentMatchIndex = -1;
        };

        // 滚动到指定匹配项
        this.scrollToMatch = (index) => {
            if (index < 0 || index >= currentMatches.length) return;

            // 移除之前的当前高亮
            currentMatches.forEach(mark => mark.classList.remove('search-highlight-current'));

            // 添加当前高亮
            const currentMark = currentMatches[index];
            currentMark.classList.add('search-highlight-current');

            // 滚动到视图
            currentMark.scrollIntoView({
                behavior: 'smooth',
                block: 'center'
            });

            // 更新结果文本
            searchResultsText.textContent = `${index + 1} / ${currentMatches.length}`;
        };

        // 搜索输入事件
        let searchTimeout;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                highlightMatches(e.target.value);
            }, 300); // 防抖
        });

        // 清除按钮 - 清除搜索并关闭搜索栏
        searchClear.addEventListener('click', () => {
            searchInput.value = '';
            this.clearSearchHighlights();
            searchResultsInfo.style.display = 'none';
            // 隐藏搜索栏
            const searchBar = document.getElementById('statusSearchBar');
            if (searchBar) {
                searchBar.style.display = 'none';
            }
        });

        // 上一个结果
        searchPrevBtn.addEventListener('click', () => {
            if (currentMatches.length === 0) return;
            currentMatchIndex = (currentMatchIndex - 1 + currentMatches.length) % currentMatches.length;
            this.scrollToMatch(currentMatchIndex);
        });

        // 下一个结果
        searchNextBtn.addEventListener('click', () => {
            if (currentMatches.length === 0) return;
            currentMatchIndex = (currentMatchIndex + 1) % currentMatches.length;
            this.scrollToMatch(currentMatchIndex);
        });

        // 快捷键支持
        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                if (e.shiftKey) {
                    searchPrevBtn.click();
                } else {
                    searchNextBtn.click();
                }
            } else if (e.key === 'Escape') {
                searchClear.click();
            }
        });

        // 页签切换时清除搜索
        const tabsContainer = document.getElementById('statusTabs');
        if (tabsContainer) {
            tabsContainer.addEventListener('click', (e) => {
                if (e.target.closest('.status-tab')) {
                    // 延迟清除，等待页签切换完成
                    setTimeout(() => {
                        if (searchInput.value) {
                            highlightMatches(searchInput.value);
                        }
                    }, 100);
                }
            });
        }
    },

    /**
     * 加载百度地图
     */
    async loadBaiduMap() {
        const mapContainer = document.getElementById('mapContainer');
        if (!mapContainer) {
            console.error('地图容器未找到');
            return;
        }

        const normalizeHttpBaseUrl = (raw) => {
            const v = String(raw || '').trim();
            if (!v) return '';
            const withScheme = /^https?:\/\//i.test(v) ? v : `http://${v}`;
            return withScheme.endsWith('/') ? withScheme.slice(0, -1) : withScheme;
        };

        const getAgentServerBaseUrl = () => {
            const v = (window.appConfig && window.appConfig.agent_server)
                || (window.api && window.api.baseUrl)
                || '';
            return normalizeHttpBaseUrl(v);
        };

        const getAiSnsServerBaseUrl = () => {
            const v = (window.appConfig && window.appConfig.ai_sns_server) || '';
            return normalizeHttpBaseUrl(v);
        };

        console.log('加载地图');

        // 立即显示地图内容，不显示加载动画
        const placeholder = mapContainer.querySelector('.map-placeholder');
        if (placeholder) {
            placeholder.remove();
        }

        // 检查地图是否已经加载过
        const existingIframe = mapContainer.querySelector('iframe');
        if (existingIframe) {
            console.log('地图已加载，直接显示');
            return;
        }

        const agentBaseUrl = getAgentServerBaseUrl();
        const aiSnsBaseUrl = getAiSnsServerBaseUrl();

        const qs = new URLSearchParams();
        if (agentBaseUrl) {
            qs.set('agent_server', agentBaseUrl);
        }
        if (aiSnsBaseUrl) {
            qs.set('ai_sns_server', aiSnsBaseUrl);
        }

        // 获取地图配置
        let mapUrl = agentBaseUrl ? `${agentBaseUrl}/scripts/map.html?${qs.toString()}` : ''; // 默认百度地图
        try {
            const response = await fetch(agentBaseUrl ? `${agentBaseUrl}/api/sns/map-config` : '/api/sns/map-config');
            const result = await response.json();

            console.log('Map config API response:', result);

            if (result.success && result.data) {
                const mapType = String(result.data.map_type).trim();
                console.log('Map type:', mapType);

                if (mapType === '0') {
                    mapUrl = agentBaseUrl ? `${agentBaseUrl}/scripts/googlemap3d.html?${qs.toString()}` : '';
                    console.log('Loading Google Map');
                } else {
                    console.log('Loading Baidu Map');
                }
            }
        } catch (error) {
            console.error('Failed to fetch map config:', error);
        }

        console.log('Final map URL:', mapUrl);

        // 创建 iframe 加载地图页面
        const iframe = document.createElement('iframe');
        iframe.src = mapUrl;
        iframe.style.transform = 'scale(0.8)';
        iframe.style.transformOrigin = '0 0';
        iframe.style.width = '125%';//because scale(0.8)
        iframe.style.height = '125%';
        iframe.style.border = 'none';
        iframe.style.display = 'block';
        iframe.style.backgroundColor = 'white';
        iframe.style.minHeight = '500px';
        iframe.style.zIndex = '1';

        mapContainer.appendChild(iframe);

        // 等待 iframe 加载完成后建立通信
        iframe.onload = () => {
            console.log('地图页面加载完成');

            let targetOrigin = '*';
            try {
                targetOrigin = new URL(mapUrl).origin;
            } catch (e) {
            }

            // 向 iframe 发送初始数据
            const initialData = {
                type: 'init',
                data: {
                    message: 'Hello from AI-SNS Electron App!',
                    timestamp: Date.now()
                }
            };

            try {
                this.safePostMessageToMap(iframe, initialData, targetOrigin);
                console.log('已发送初始化消息');
            } catch (error) {
                console.error('发送消息到地图页面失败:', error);
            }
        };

        // 监听 iframe 加载失败
        iframe.onerror = () => {
            console.error('地图页面加载失败');
            this.showMapError(mapContainer);
        };

        // 监听来自 iframe 的消息
        const handleMessage = (event) => {
            // If we have a reference to the iframe, ensure message is from it.
            try {
                if (iframe && iframe.contentWindow && event.source !== iframe.contentWindow) {
                    return;
                }
            } catch (e) {
            }

            let expectedOrigin = '';
            try {
                expectedOrigin = new URL(mapUrl).origin;
            } catch (e) {
            }

            if (!expectedOrigin || event.origin === expectedOrigin) {
                const data = event.data;
                console.log('收到地图页面消息:', data);

                switch (data.type) {
                    case 'received':
                        console.log('地图页面已确认收到消息:', data.data);
                        break;
                    case 'locationUpdate':
                        this.handleLocationUpdate(data.data);
                        break;
                    case 'mapClick':
                        this.handleMapClick(data.data);
                        break;
                    case 'markerAdd':
                        this.handleMarkerAdd(data.data);
                        break;
                    case 'openDialog':
                        this.handleOpenDialog(data.dialogType);
                        break;
                    case 'togglePanels':
                        this.handleTogglePanels(data.action);
                        break;
                    case 'openSNSProfile':
                        this.handleOpenSNSProfile(data.url);
                        break;
                    case 'openPlaceWebAddress':
                        this.handleOpenPlaceWebAddress(data.url);
                        break;
                    case 'closeSNSProfile':
                        this.handleCloseSNSProfile();
                        break;
                    default:
                        console.log('未知消息类型:', data.type);
                }
            }
        };

        window.addEventListener('message', handleMessage);
        iframe._messageListener = handleMessage;
    },

    /**
     * 显示地图加载错误
     */
    showMapError(mapContainer) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'map-placeholder';
        errorDiv.style.zIndex = '10';

        const agentServer = (window.appConfig && window.appConfig.agent_server)
            || (window.api && window.api.baseUrl)
            || '';
        errorDiv.innerHTML = `
            <div class="map-placeholder-icon">
                <svg viewBox="0 0 24 24" width="48" height="48" fill="currentColor">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93z"/>
                </svg>
            </div>
            <p class="map-placeholder-text">地图加载失败</p>
            <p class="map-placeholder-desc">请检查地图服务器是否运行${agentServer ? `在 ${agentServer}` : ''}</p>
            <button class="map-retry-btn" id="mapRetryBtn">重试</button>
        `;
        mapContainer.appendChild(errorDiv);

        // 绑定重试按钮
        const retryBtn = errorDiv.querySelector('#mapRetryBtn');
        if (retryBtn) {
            retryBtn.addEventListener('click', () => this.tryLoadMap());
        }
    },

    /**
     * 重试加载地图
     */
    tryLoadMap() {
        const mapContainer = document.getElementById('mapContainer');
        if (!mapContainer) return;

        console.log('尝试重新加载地图');

        // 移除现有的iframe
        const existingIframe = mapContainer.querySelector('iframe');
        if (existingIframe) {
            if (existingIframe._messageListener) {
                window.removeEventListener('message', existingIframe._messageListener);
            }
            existingIframe.remove();
        }

        // 移除现有的错误提示
        const existingErrorDiv = mapContainer.querySelector('.map-placeholder');
        if (existingErrorDiv) {
            existingErrorDiv.remove();
        }

        // 创建新的加载动画
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'map-placeholder';
        loadingDiv.innerHTML = `
            <div class="map-placeholder-icon">
                <svg viewBox="0 0 24 24" width="48" height="48" fill="currentColor">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93z"/>
                </svg>
            </div>
            <p class="map-placeholder-text">正在加载地图...</p>
            <div class="map-placeholder-loader">
                <div class="loader-dot"></div>
                <div class="loader-dot"></div>
                <div class="loader-dot"></div>
            </div>
        `;
        mapContainer.appendChild(loadingDiv);

        // 延迟调用loadBaiduMap
        setTimeout(() => {
            this.loadBaiduMap();
        }, 500);
    },

    /**
     * 处理位置更新
     */
    handleLocationUpdate(data) {
        console.log('位置更新:', data);
        const lngElement = document.querySelector('.status-row.sub span[class="value"]');
        const latElement = document.querySelectorAll('.status-row.sub span[class="value"]')[1];
        if (lngElement && data.lng) {
            lngElement.textContent = `: ${data.lng}`;
        }
        if (latElement && data.lat) {
            latElement.textContent = `: ${data.lat}`;
        }
    },

    /**
     * 处理地图点击事件
     */
    handleMapClick(data) {
        console.log('地图点击:', data);
    },

    /**
     * 处理添加标记事件
     */
    handleMarkerAdd(data) {
        console.log('添加标记:', data);
    },

    /**
     * 向地图页面发送消息
     */
    sendMessageToMap(type, data) {
        const iframe = document.querySelector('#mapContainer iframe');
        if (iframe && iframe.contentWindow) {
            const message = {
                type: type,
                data: data
            };
            iframe.contentWindow.postMessage(message, this.getMapIframeTargetOrigin());
        }
    },

    /**
     * 加载SNS数据
     */
    loadSNSData() {
        // 模拟加载SNS数据
        const updateValue = (id, value) => {
            const el = document.getElementById(id);
            if (el) el.textContent = value;
        };

        updateValue('onlineNodes', Math.floor(Math.random() * 100) + 50);
        updateValue('activeUsers', Math.floor(Math.random() * 500) + 100);
        updateValue('messageCount', Math.floor(Math.random() * 10000) + 1000);
    },

    /**
     * 清理地图监听器
     */
    cleanupMapListeners() {
        const iframe = document.querySelector('#mapContainer iframe');
        if (iframe && iframe._messageListener) {
            window.removeEventListener('message', iframe._messageListener);
        }
    },

    /**
     * 显示Toast消息
     */
    showToast(message, type = 'success') {
        // 创建toast元素
        const toast = document.createElement('div');
        toast.className = `sns-toast sns-toast-${type}`;
        toast.textContent = message;

        // 根据类型选择背景色
        let backgroundColor;
        switch (type) {
            case 'error':
                backgroundColor = '#f44336';
                break;
            case 'info':
                backgroundColor = '#2196f3';
                break;
            case 'success':
            default:
                backgroundColor = '#4caf50';
                break;
        }

        // 添加样式
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${backgroundColor};
            color: white;
            padding: 16px 24px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10000;
            max-width: 400px;
            word-wrap: break-word;
            animation: slideIn 0.3s ease-out;
        `;

        document.body.appendChild(toast);

        // 3秒后自动移除
        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 3000);
    },

    /**
     * 初始化SNS更新监听器（使用全局 WebSocket 事件）
     */
    initSNSUpdateListener() {
        // 监听全局 WebSocket 消息事件
        this.snsUpdateListener = (event) => {
            const message = event.detail;
            if (message.type === 'sns_update') {
                console.log('SNS update received:', message);
                this.handleSNSUpdate(message);
            }
        };

        window.addEventListener('websocket-message', this.snsUpdateListener);
        console.log('SNS update listener initialized');
    },

    /**
     * 处理SNS更新消息
     */
    handleSNSUpdate(data) {
        console.log('Handling SNS update:', data);
        const { tab, content, section } = data;

        if (tab === 'think') {
            console.log('Updating Think tab with content:', content);
            this.updateThinkTab(content);
        } else if (tab === 'process') {
            console.log('Updating Process tab with content:', content, 'section:', section);
            this.updateProcessTab(content, section);
        } else if (tab === 'resource') {
            console.log('Updating Resource tab with content:', content);
            this.updateResourceTab(content);
        }
    },

    /**
     * 更新Think页签内容
     */
    updateThinkTab(content) {
        console.log('updateThinkTab called with content:', content);
        // 找到Think页签的内容区域
        const thinkPane = document.querySelector('.tab-pane[data-tab="think"]');
        console.log('Think pane found:', thinkPane);
        if (!thinkPane) return;

        // 找到Thinking Log部分
        let thinkingLogSection = thinkPane.querySelector('.status-section:nth-child(2) .status-rows');
        console.log('Thinking log section found:', thinkingLogSection);
        if (!thinkingLogSection) return;

        // 创建新的内容元素
        const contentDiv = document.createElement('div');
        contentDiv.className = 'thinking-log-entry';
        contentDiv.style.cssText = `
            white-space: pre-wrap;
            font-family: monospace;
            font-size: 12px;
            line-height: 1.5;
            padding: 8px;
            background: rgba(26, 115, 232, 0.05);
            border-left: 3px solid #1a73e8;
            margin-bottom: 8px;
            border-radius: 4px;
        `;
        contentDiv.textContent = content;

        // 如果是第一条内容，清除"N/A"
        if (thinkingLogSection.querySelector('.na')) {
            thinkingLogSection.innerHTML = '';
        }

        // 添加新内容
        thinkingLogSection.appendChild(contentDiv);

        // 滚动到底部
        thinkingLogSection.scrollTop = thinkingLogSection.scrollHeight;
        thinkingLogSection.scrollTop = thinkingLogSection.scrollHeight;
    },

    /**
     * 更新Process页签内容
     */
    updateProcessTab(content, section = null) {
        console.log('updateProcessTab called with content:', content, 'section:', section);
        // 找到Process页签的内容区域
        const processPane = document.querySelector('.tab-pane[data-tab="process"]');
        console.log('Process pane found:', processPane);
        if (!processPane) return;

        // 如果指定了 section，检查是否需要拆分
        if (section === 'ongoing') {
            // 检查内容是否包含 Current Status
            if (content.includes('📊 Current Status')) {
                console.log('Content contains Current Status, parsing...');
                // 需要拆分内容
                const lines = content.split('\n');
                let currentStatusContent = '';
                let onGoingContent = '';
                let currentSection = '';

                for (const line of lines) {
                    if (line.includes('📊 Current Status')) {
                        currentSection = 'status';
                        continue;
                    } else if (line.includes('⏳ On Going')) {
                        currentSection = 'ongoing';
                        continue;
                    }

                    // 跳过分隔线
                    if (line.includes('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')) {
                        continue;
                    }

                    if (currentSection === 'status') {
                        currentStatusContent += line + '\n';
                    } else if (currentSection === 'ongoing') {
                        onGoingContent += line + '\n';
                    }
                }

                // 更新两个部分
                if (currentStatusContent.trim()) {
                    this.updateCurrentStatusSection(processPane, currentStatusContent.trim());
                }
                if (onGoingContent.trim()) {
                    this.updateOnGoingSection(processPane, onGoingContent.trim());
                }
            } else {
                // 只有 On Going 内容
                this.updateOnGoingSection(processPane, content);
            }
            return;
        } else if (section === 'history') {
            this.updateHistorySection(processPane, content);
            return;
        } else if (section === 'status') {
            this.updateCurrentStatusSection(processPane, content);
            return;
        }

        // 否则，解析内容并更新三个部分
        const lines = content.split('\n');
        let currentStatusContent = '';
        let onGoingContent = '';
        let processHistoryContent = '';
        let currentSection = '';

        for (const line of lines) {
            if (line.includes('📊 Current Status')) {
                currentSection = 'status';
                continue;
            } else if (line.includes('⏳ On Going')) {
                currentSection = 'ongoing';
                continue;
            } else if (line.includes('📜 Process history')) {
                currentSection = 'history';
                continue;
            }

            // 跳过分隔线
            if (line.includes('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')) {
                continue;
            }

            if (currentSection === 'status') {
                currentStatusContent += line + '\n';
            } else if (currentSection === 'ongoing') {
                onGoingContent += line + '\n';
            } else if (currentSection === 'history') {
                processHistoryContent += line + '\n';
            }
        }

        // 更新各个部分
        if (currentStatusContent.trim()) {
            this.updateCurrentStatusSection(processPane, currentStatusContent.trim());
        }

        if (onGoingContent.trim()) {
            this.updateOnGoingSection(processPane, onGoingContent.trim());
        }

        if (processHistoryContent.trim()) {
            this.updateHistorySection(processPane, processHistoryContent.trim());
        }
    },

    /**
     * 更新 Current Status 部分
     */
    updateCurrentStatusSection(processPane, content) {
        const statusSection = processPane.querySelector('.status-section:nth-child(1) .status-rows');
        if (!statusSection) {
            console.warn('Current Status section not found');
            return;
        }

        // 清空现有内容
        statusSection.innerHTML = '';

        // 解析内容并创建状态行
        const lines = content.split('\n');
        for (const line of lines) {
            if (!line.trim()) continue;

            // 创建状态行元素
            const statusRow = document.createElement('div');
            statusRow.className = 'status-row';

            // 检查是否是子行（Location的lng/lat）
            if (line.trim().startsWith('├─') || line.trim().startsWith('└─')) {
                statusRow.classList.add('sub');
                // 移除树形符号
                const cleanLine = line.replace(/[├└]─\s*/, '').trim();
                const parts = cleanLine.split(':');
                if (parts.length === 2) {
                    const label = document.createElement('span');
                    label.textContent = parts[0].trim();
                    const value = document.createElement('span');
                    value.className = 'value';
                    value.textContent = ': ' + parts[1].trim();
                    statusRow.appendChild(label);
                    statusRow.appendChild(value);
                }
            } else {
                // 普通状态行
                const parts = line.split(':');
                if (parts.length >= 2) {
                    const label = document.createElement('span');
                    label.textContent = parts[0].trim();
                    const value = document.createElement('span');
                    value.className = 'value';
                    value.textContent = ': ' + parts.slice(1).join(':').trim();
                    statusRow.appendChild(label);
                    statusRow.appendChild(value);
                } else {
                    // 只有标签没有值的行（如 📍 Location）
                    const label = document.createElement('span');
                    label.textContent = line.trim();
                    statusRow.appendChild(label);
                }
            }

            statusSection.appendChild(statusRow);
        }

        console.log('Current Status section updated');
    },

    /**
     * 更新 On Going 部分
     */
    updateOnGoingSection(processPane, content) {
        const onGoingSection = processPane.querySelector('.status-section:nth-child(2) .status-rows');
        if (!onGoingSection) {
            console.warn('On Going section not found');
            return;
        }

        if (onGoingSection.querySelector('.na')) {
            onGoingSection.innerHTML = '';
        }

        const onGoingDiv = document.createElement('div');
        onGoingDiv.style.cssText = `
            white-space: pre-wrap;
            font-family: monospace;
            font-size: 12px;
            line-height: 1.5;
        `;
        onGoingDiv.textContent = content;
        onGoingSection.innerHTML = '';
        onGoingSection.appendChild(onGoingDiv);
        console.log('On Going section updated');
    },

    /**
     * 更新 Process History 部分
     */
    updateHistorySection(processPane, content) {
        const historySection = processPane.querySelector('.status-section:nth-child(3) .status-rows');
        if (!historySection) {
            console.warn('History section not found');
            return;
        }

        if (historySection.querySelector('.na')) {
            historySection.innerHTML = '';
        }

        const historyDiv = document.createElement('div');
        historyDiv.style.cssText = `
            white-space: pre-wrap;
            font-family: monospace;
            font-size: 12px;
            line-height: 1.5;
        `;
        historyDiv.textContent = content;
        historySection.innerHTML = '';
        historySection.appendChild(historyDiv);
        console.log('History section updated');
    },

    /**
     * 更新 Resource 页签内容
     */
    updateResourceTab(content) {
        console.log('updateResourceTab called with content:', content);
        // 找到Resource页签的内容区域
        const resourcePane = document.querySelector('.tab-pane[data-tab="resource"]');
        console.log('Resource pane found:', resourcePane);
        if (!resourcePane) return;

        // 找到第一个 status-section（Resource Overview）
        const resourceSection = resourcePane.querySelector('.status-section:nth-child(1) .status-rows');
        console.log('Resource section found:', resourceSection);
        if (!resourceSection) return;

        // 清除 N/A 标记
        if (resourceSection.querySelector('.na')) {
            resourceSection.innerHTML = '';
        }

        // 创建内容元素
        const contentDiv = document.createElement('div');
        contentDiv.style.cssText = `
            white-space: pre-wrap;
            font-family: monospace;
            font-size: 12px;
            line-height: 1.5;
        `;
        contentDiv.textContent = content;

        // 更新内容
        resourceSection.innerHTML = '';
        resourceSection.appendChild(contentDiv);
        console.log('Resource tab updated successfully');
    },

    /**
     * 处理来自 map.html 的打开对话框请求
     */
    async handleOpenDialog(dialogType) {
        console.log('handleOpenDialog called with dialogType:', dialogType);

        try {
            let dialog;
            switch (dialogType) {
                case 'avatar':
                    dialog = new SNSAvatarDialog();
                    break;
                case 'profession':
                    dialog = new SNSProfessionDialog();
                    break;
                case 'socialRole':
                    dialog = new SNSSocialRoleDialog();
                    break;
                case 'mapConfig':
                    dialog = new SNSMapConfigDialog();
                    break;
                default:
                    console.warn('Unknown dialog type:', dialogType);
                    return;
            }

            if (dialog) {
                await dialog.show();
                console.log('Dialog opened successfully:', dialogType);
            }
        } catch (error) {
            console.error('Error opening dialog:', dialogType, error);
            this.showToast(`打开对话框失败: ${error.message}`, 'error');
        }
    },

    /**
     * 处理来自 map.html 的面板折叠/展开请求
     */
    handleTogglePanels(action) {
        console.log('handleTogglePanels called with action:', action);

        // 获取侧边栏相关元素（二级侧边栏）
        const secondarySidebar = document.getElementById('secondarySidebar');
        const sidebarResizer = document.getElementById('sidebarResizer');
        const mainContent = document.getElementById('mainContent');

        // 获取 SNS 页面右侧面板相关元素
        const statusPanel = document.getElementById('snsStatusPanel');
        const panelResizer = document.getElementById('snsPanelResizer');

        if (!secondarySidebar || !sidebarResizer || !mainContent) {
            console.warn('Sidebar elements not found');
            return;
        }

        if (action === 'collapse') {
            // 折叠侧边栏
            secondarySidebar.classList.add('collapsed');
            sidebarResizer.classList.add('collapsed');
            mainContent.classList.add('sidebar-collapsed');

            console.log('Sidebar collapsed');
        } else if (action === 'expand') {
            // 展开侧边栏
            secondarySidebar.classList.remove('collapsed');
            sidebarResizer.classList.remove('collapsed');
            mainContent.classList.remove('sidebar-collapsed');

            console.log('Sidebar expanded');
        }

        // 处理右侧状态面板（仅在 SNS 页面时）
        if (statusPanel && panelResizer) {
            if (action === 'collapse') {
                // 折叠右侧面板
                statusPanel.classList.add('collapsed');
                panelResizer.classList.add('collapsed');
                localStorage.setItem('snsPanelCollapsed', 'true');
                console.log('SNS panel collapsed');
            } else if (action === 'expand') {
                // 展开右侧面板
                statusPanel.classList.remove('collapsed');
                panelResizer.classList.remove('collapsed');
                localStorage.setItem('snsPanelCollapsed', 'false');
                console.log('SNS panel expanded');
            }
        }
    },

    /**
     * 处理打开 SNS Profile 页签请求
     */
    handleOpenSNSProfile(url) {
        console.log('handleOpenSNSProfile called with url:', url);

        // URL 规范化处理
        if (!url || typeof url !== 'string') {
            console.error('Invalid URL provided:', url);
            return;
        }

        // 去除首尾空格
        url = url.trim();

        // 检查是否有协议头
        if (!url.match(/^https?:\/\//i)) {
            // 判断是否是本地地址
            if (url.startsWith('localhost') || url.startsWith('127.0.0.1') || url.startsWith('192.168.')) {
                url = 'http://' + url;
                console.log('Added http:// to local URL:', url);
            } else if (url.startsWith('//')) {
                // 协议相对 URL
                url = 'https:' + url;
                console.log('Added https: to protocol-relative URL:', url);
            } else if (url.startsWith('/')) {
                // 相对路径，使用当前服务器
                url = this.resolve(url);
                console.log('Converted relative path to absolute URL:', url);
            } else {
                // 默认添加 https://
                url = 'https://' + url;
                console.log('Added https:// to URL:', url);
            }
        }

        // 验证 URL 格式
        try {
            new URL(url);
        } catch (e) {
            console.error('Invalid URL format after normalization:', url, e);
            this.showToast('无效的 URL 格式: ' + url, 'error');
            return;
        }

        const statusTabs = document.getElementById('statusTabs');
        const statusTabContent = document.getElementById('statusTabContent');

        if (!statusTabs || !statusTabContent) {
            console.warn('Status tabs container not found');
            return;
        }

        // 检查是否已存在 Profile 页签
        let profileTab = statusTabs.querySelector('.status-tab[data-tab="profile"]');
        let profilePane = statusTabContent.querySelector('.tab-pane[data-tab="profile"]');

        if (!profileTab) {
            // 创建 Profile 页签按钮
            profileTab = document.createElement('button');
            profileTab.className = 'status-tab';
            profileTab.dataset.tab = 'profile';
            profileTab.innerHTML = `Profile <span class="tab-close-btn" title="关闭">×</span>`;
            statusTabs.appendChild(profileTab);

            // 绑定关闭按钮事件
            const closeBtn = profileTab.querySelector('.tab-close-btn');
            closeBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.handleCloseSNSProfile();
            });
        }

        if (!profilePane) {
            // 创建 Profile 页签内容
            profilePane = document.createElement('div');
            profilePane.className = 'tab-pane';
            profilePane.dataset.tab = 'profile';
            profilePane.innerHTML = `
                <div class="profile-webview-container">
                    <iframe src="${url}" class="profile-webview" frameborder="0"></iframe>
                </div>
            `;
            statusTabContent.appendChild(profilePane);
        } else {
            // 更新现有 iframe 的 URL
            const iframe = profilePane.querySelector('.profile-webview');
            if (iframe) {
                iframe.src = url;
            }
        }

        // 切换到 Profile 页签
        statusTabs.querySelectorAll('.status-tab').forEach(btn => {
            btn.classList.toggle('active', btn === profileTab);
        });

        statusTabContent.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.toggle('active', pane === profilePane);
        });

        // 自动滚动到 Profile 页签（确保可见）
        if (profileTab) {
            profileTab.scrollIntoView({
                behavior: 'smooth',
                block: 'nearest',
                inline: 'center'
            });
        }

        console.log('SNS Profile tab opened with URL:', url);
    },

    /**
     * 处理关闭 SNS Profile 页签请求
     */
    handleCloseSNSProfile() {
        console.log('handleCloseSNSProfile called');

        const statusTabs = document.getElementById('statusTabs');
        const statusTabContent = document.getElementById('statusTabContent');

        if (!statusTabs || !statusTabContent) {
            console.warn('Status tabs container not found');
            return;
        }

        // 查找并移除 Profile 页签
        const profileTab = statusTabs.querySelector('.status-tab[data-tab="profile"]');
        const profilePane = statusTabContent.querySelector('.tab-pane[data-tab="profile"]');

        if (profileTab) {
            profileTab.remove();
        }

        if (profilePane) {
            profilePane.remove();
        }

        // 切换到第一个页签（Process）
        const firstTab = statusTabs.querySelector('.status-tab');
        const firstPane = statusTabContent.querySelector('.tab-pane');

        if (firstTab && firstPane) {
            firstTab.classList.add('active');
            firstPane.classList.add('active');
        }

        console.log('SNS Profile tab closed');
    }

    ,

    /**
     * 处理打开 Place intro 页签请求
     */
    handleOpenPlaceWebAddress(url) {
        console.log('handleOpenPlaceWebAddress called with url:', url);

        // URL 规范化处理
        if (!url || typeof url !== 'string') {
            console.error('Invalid URL provided:', url);
            return;
        }

        // 去除首尾空格
        url = url.trim();

        // 检查是否有协议头
        if (!url.match(/^https?:\/\//i)) {
            // 判断是否是本地地址
            if (url.startsWith('localhost') || url.startsWith('127.0.0.1') || url.startsWith('192.168.')) {
                url = 'http://' + url;
                console.log('Added http:// to local URL:', url);
            } else if (url.startsWith('//')) {
                // 协议相对 URL
                url = 'https:' + url;
                console.log('Added https: to protocol-relative URL:', url);
            } else if (url.startsWith('/')) {
                // 相对路径，使用当前服务器
                url = this.resolve(url);
                console.log('Converted relative path to absolute URL:', url);
            } else {
                // 默认添加 https://
                url = 'https://' + url;
                console.log('Added https:// to URL:', url);
            }
        }

        // 验证 URL 格式
        try {
            new URL(url);
        } catch (e) {
            console.error('Invalid URL format after normalization:', url, e);
            this.showToast('无效的 URL 格式: ' + url, 'error');
            return;
        }

        const statusTabs = document.getElementById('statusTabs');
        const statusTabContent = document.getElementById('statusTabContent');

        if (!statusTabs || !statusTabContent) {
            console.warn('Status tabs container not found');
            return;
        }

        // 检查是否已存在 Place intro 页签
        let placeTab = statusTabs.querySelector('.status-tab[data-tab="placeIntro"]');
        let placePane = statusTabContent.querySelector('.tab-pane[data-tab="placeIntro"]');

        if (!placeTab) {
            // 创建 Place intro 页签按钮
            placeTab = document.createElement('button');
            placeTab.className = 'status-tab';
            placeTab.dataset.tab = 'placeIntro';
            placeTab.innerHTML = `Place intro <span class="tab-close-btn" title="关闭">×</span>`;
            statusTabs.appendChild(placeTab);

            // 绑定关闭按钮事件
            const closeBtn = placeTab.querySelector('.tab-close-btn');
            closeBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                if (placeTab) placeTab.remove();
                if (placePane) placePane.remove();

                // 切换到第一个页签（Process）
                const firstTab = statusTabs.querySelector('.status-tab');
                const firstPane = statusTabContent.querySelector('.tab-pane');
                if (firstTab && firstPane) {
                    firstTab.classList.add('active');
                    firstPane.classList.add('active');
                }
            });
        }

        if (!placePane) {
            // 创建 Place intro 页签内容
            placePane = document.createElement('div');
            placePane.className = 'tab-pane';
            placePane.dataset.tab = 'placeIntro';
            placePane.innerHTML = `
                <div class="profile-webview-container">
                    <iframe src="${url}" class="profile-webview" frameborder="0"></iframe>
                </div>
            `;
            statusTabContent.appendChild(placePane);
        } else {
            // 更新现有 iframe 的 URL
            const iframe = placePane.querySelector('.profile-webview');
            if (iframe) {
                iframe.src = url;
            }
        }

        // 切换到 Place intro 页签
        statusTabs.querySelectorAll('.status-tab').forEach(btn => {
            btn.classList.toggle('active', btn === placeTab);
        });

        statusTabContent.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.toggle('active', pane === placePane);
        });

        // 自动滚动到 Place intro 页签（确保可见）
        if (placeTab) {
            placeTab.scrollIntoView({
                behavior: 'smooth',
                block: 'nearest',
                inline: 'center'
            });
        }

        console.log('Place intro tab opened with URL:', url);
    }
};
