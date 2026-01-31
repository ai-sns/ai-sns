/**
 * Home Handlers - 事件处理
 */

import InitializationWizard from './InitializationWizard.js';

const homeHandlers = {
    init() {
        this.bindEvents();
    },

    bindEvents() {
        // 绑定设置按钮事件
        document.querySelectorAll('.setting-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const action = btn.dataset.action;
                switch (action) {
                    case 'initialization':
                        this.showInitializationModal();
                        break;
                    case 'help':
                        this.showHelpModal();
                        break;
                }
            });
        });
    },

    showInitializationModal() {
        InitializationWizard.show();
    },

    showHelpModal() {
        if (typeof Modal === 'undefined') {
            console.error('Modal component not loaded');
            return;
        }

        Modal.show({
            title: '帮助',
            content: `
                <div class="help-modal">
                    <h4>快捷键</h4>
                    <ul class="help-list">
                        <li><kbd>Ctrl/Cmd + B</kbd> 折叠/展开侧边栏</li>
                        <li><kbd>Ctrl/Cmd + K</kbd> 搜索</li>
                        <li><kbd>Ctrl/Cmd + ,</kbd> 设置</li>
                        <li><kbd>Ctrl/Cmd + 1-6</kbd> 快速导航</li>
                    </ul>
                    <h4>功能模块</h4>
                    <ul class="help-list">
                        <li><strong>SNS</strong> - 地图社交探索</li>
                        <li><strong>Agent</strong> - AI Agent对话</li>
                        <li><strong>KM</strong> - 知识库管理</li>
                        <li><strong>Tools</strong> - 插件工具</li>
                        <li><strong>Web</strong> - LLM在线服务</li>
                        <li><strong>Home</strong> - 首页设置</li>
                    </ul>
                </div>
            `,
            showCancel: false,
            confirmText: '关闭'
        });
    },

    destroy() {
        // 清理事件监听器
    }
};

export default homeHandlers;
