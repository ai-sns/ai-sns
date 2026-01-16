/**
 * Router - 路由管理
 * 负责页面导航和模块加载
 */

class Router {
    constructor() {
        this.currentPage = null;
        this.modules = {};
        this.initialized = false;
    }

    /**
     * 注册模块
     * @param {string} name - 模块名称
     * @param {Object} module - 模块对象
     */
    register(name, module) {
        if (!module.renderPage || !module.renderSidebar || !module.init) {
            console.error(`Module '${name}' missing required methods`);
            return false;
        }
        this.modules[name] = module;
        return true;
    }

    /**
     * 导航到指定页面
     * @param {string} page - 页面名称
     */
    async navigateTo(page) {
        if (this.currentPage === page) {
            console.log(`Already on page '${page}'`);
            return;
        }

        if (!this.modules[page]) {
            console.error(`Module '${page}' not found`);
            return;
        }

        console.log(`Navigating to: ${page}`);

        // 隐藏Agent管理页面（如果打开的话）
        const modelMgmtPage = document.querySelector('.model-management-page-container');
        const roleMgmtPage = document.querySelector('.role-management-page-container');
        if (modelMgmtPage) {
            modelMgmtPage.style.display = 'none';
        }
        if (roleMgmtPage) {
            roleMgmtPage.style.display = 'none';
        }

        // 隐藏当前页面（保持状态，不调用destroy）
        if (this.currentPage) {
            const currentPageElement = document.getElementById(`page-${this.currentPage}`);
            if (currentPageElement) {
                currentPageElement.classList.add('hidden');
            }

            // 注意：不再调用 destroy() 方法，以保持模块状态
            // 如果需要清理，应该监听应用退出事件，而不是页面切换
        }

        this.currentPage = page;

        // 更新导航栏状态
        document.querySelectorAll('.nav-icon-item').forEach(item => {
            item.classList.toggle('active', item.dataset.page === page);
        });

        // 渲染侧边栏（等待异步完成）
        await this.renderSidebar(page);

        // 渲染或显示主内容区
        this.renderOrShowMainContent(page);

        // 触发导航事件
        if (window.eventBus) {
            window.eventBus.emit('page:changed', { from: this.currentPage, to: page });
        }
    }

    /**
     * 渲染侧边栏（保持状态版本）
     * @param {string} page - 页面名称
     */
    async renderSidebar(page) {
        const sidebarContainer = document.getElementById('secondarySidebar');
        if (!sidebarContainer) return;

        const module = this.modules[page];
        if (!module) return;

        try {
            // 隐藏所有侧边栏容器
            const allSidebars = sidebarContainer.querySelectorAll('.sidebar-page-container');
            allSidebars.forEach(sb => sb.classList.add('hidden'));

            // 检查该页面的侧边栏容器是否已存在
            let pageSidebar = sidebarContainer.querySelector(`#sidebar-${page}`);

            if (!pageSidebar) {
                // 首次渲染：创建新的侧边栏容器
                pageSidebar = document.createElement('div');
                pageSidebar.id = `sidebar-${page}`;
                pageSidebar.className = 'sidebar-page-container';

                const sidebarContent = module.renderSidebar();
                pageSidebar.innerHTML = sidebarContent;
                sidebarContainer.appendChild(pageSidebar);

                // 特殊处理：Agent页面需要异步初始化
                if (page === 'agent' && window.AgentSidebar && typeof window.AgentSidebar.init === 'function') {
                    console.log('[Router] 初始化Agent侧边栏...');
                    await window.AgentSidebar.init();
                }

                pageSidebar.dataset.initialized = 'true';
                console.log(`[Router] 侧边栏首次渲染: ${page}`);
            } else {
                // 已存在：直接显示
                pageSidebar.classList.remove('hidden');
                console.log(`[Router] 侧边栏恢复显示（保持状态）: ${page}`);

                // 特殊处理：Agent页面恢复时，确保UI状态与agentState同步
                if (page === 'agent' && window.agentState && window.AgentSidebar) {
                    const currentAgentId = window.agentState.currentAgentId;
                    if (currentAgentId) {
                        console.log(`[Router] 恢复Agent选中状态: ${currentAgentId}`);
                        // 确保UI上的选中状态正确
                        setTimeout(() => {
                            // 移除所有active class
                            document.querySelectorAll('.agent-item').forEach(item => {
                                item.classList.remove('active');
                            });
                            // 添加当前agent的active class
                            const currentAgentItem = document.querySelector(`.agent-item[data-agent-id="${currentAgentId}"]`);
                            if (currentAgentItem) {
                                currentAgentItem.classList.add('active');
                            }
                            // 确保当前agent的section是展开的
                            const currentAgentSection = document.querySelector(`.agent-section-container[data-agent-id="${currentAgentId}"]`);
                            if (currentAgentSection) {
                                currentAgentSection.style.display = 'block';
                            }
                        }, 50);
                    }
                }
            }
        } catch (error) {
            console.error(`Error rendering sidebar for '${page}':`, error);
            // 创建错误提示容器
            const errorSidebar = document.createElement('div');
            errorSidebar.id = `sidebar-${page}`;
            errorSidebar.className = 'sidebar-page-container';
            errorSidebar.innerHTML = '<p style="padding: 20px; color: #999;">侧边栏加载失败</p>';
            sidebarContainer.appendChild(errorSidebar);
        }
    }

    /**
     * 渲染或显示主内容区
     * @param {string} page - 页面名称
     */
    renderOrShowMainContent(page) {
        const mainContent = document.getElementById('mainContent');
        if (!mainContent) return;

        const module = this.modules[page];
        if (!module) return;

        // 检查页面是否已渲染
        let pageElement = document.getElementById(`page-${page}`);

        if (!pageElement) {
            // 页面未渲染，创建新的页面容器
            pageElement = document.createElement('div');
            pageElement.id = `page-${page}`;
            pageElement.className = 'page-container';

            try {
                const pageContent = module.renderPage();
                pageElement.innerHTML = pageContent;
                mainContent.appendChild(pageElement);

                // 初始化模块
                if (module.init) {
                    module.init();
                }
                pageElement.dataset.initialized = 'true';
            } catch (error) {
                console.error(`Error rendering page '${page}':`, error);
                pageElement.innerHTML = '<p style="padding: 20px; color: #999;">页面加载失败</p>';
            }
        } else {
            // 页面已渲染，直接显示（保持所有状态）
            pageElement.classList.remove('hidden');
            // 清除可能被管理页面设置的 display: none 样式
            pageElement.style.display = '';
            console.log(`[Router] 页面恢复显示（保持状态）: ${page}`);
        }
    }

    /**
     * 获取当前页面
     * @returns {string|null}
     */
    getCurrentPage() {
        return this.currentPage;
    }

    /**
     * 重新加载当前页面
     */
    reload() {
        if (!this.currentPage) return;

        const pageElement = document.getElementById(`page-${this.currentPage}`);
        if (pageElement) {
            pageElement.remove();
        }

        const page = this.currentPage;
        this.currentPage = null;
        this.navigateTo(page);
    }
}

// 导出单例
const router = new Router();
window.router = router;