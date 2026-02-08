/**
 * Tools Handlers - 事件处理和内容渲染
 */

import ToolsEditDialog from './ToolsEditDialog.js';

const toolsHandlers = {
    currentCategory: 'tools-plugin',
    apiBaseUrl: 'http://127.0.0.1:8788/api/tools',
    editDialog: null,

    // 分页状态
    currentOffset: 0,
    pageSize: 50, // 默认值，会从配置文件读取
    hasMore: true,
    currentData: [],

    init() {
        // 确保全局 toolsEditDialog 实例存在
        if (!window.toolsEditDialog) {
            window.toolsEditDialog = new ToolsEditDialog();
        }
        this.editDialog = window.toolsEditDialog;

        // 加载配置
        this.loadConfig();

        this.bindEvents();
        // 初始加载第一个分类的内容
        this.loadCategoryContent(this.currentCategory);
    },

    async loadConfig() {
        try {
            // 从API获取系统配置
            const response = await fetch(`http://127.0.0.1:8788/api/system/config`);
            if (response.ok) {
                const config = await response.json();
                if (config.tools && config.tools.page_size) {
                    this.pageSize = config.tools.page_size;
                }
            }
        } catch (error) {
            console.log('Failed to load config, using default page size:', this.pageSize);
        }
    },

    bindEvents() {
        // 分类项点击事件
        document.querySelectorAll('.tools-category-item').forEach(item => {
            item.addEventListener('click', () => {
                const category = item.getAttribute('data-category');
                this.onCategoryClick(category);

                // 添加选中状态
                document.querySelectorAll('.tools-category-item').forEach(i => {
                    i.classList.remove('active');
                });
                item.classList.add('active');
            });
        });

        // More按钮点击事件
        const moreBtn = document.querySelector('.plugin-more-btn');
        if (moreBtn) {
            moreBtn.addEventListener('click', () => this.loadMoreTools());
        }

        // Add按钮点击事件（需要在页面中添加此按钮）
        const addBtn = document.querySelector('.tools-add-btn');
        if (addBtn) {
            addBtn.addEventListener('click', () => this.showAddDialog(this.currentCategory));
        }
    },

    onCategoryClick(category) {
        console.log('Category clicked:', category);
        this.currentCategory = category;

        // 重置分页状态
        this.currentOffset = 0;
        this.hasMore = true;
        this.currentData = [];

        this.loadCategoryContent(category);

        // 触发自定义事件
        if (typeof window.eventBus !== 'undefined') {
            window.eventBus.emit('tools:category:changed', { category });
        }
    },

    async loadCategoryContent(category, offset = 0, limit = null) {
        const pluginGrid = document.getElementById('pluginGrid');
        if (!pluginGrid) {
            console.error('Plugin grid element not found');
            return;
        }

        // 更新标题
        const titleElement = document.querySelector('.plugin-list-title');
        if (titleElement) {
            titleElement.textContent = `${this.getCategoryDisplayName(category)} List`;
        }

        // 显示加载状态（如果是首次加载）
        if (offset === 0) {
            pluginGrid.innerHTML = '<div class="loading-spinner">Loading...</div>';
        }

        try {
            let data = [];
            let endpoint = '';

            // 根据分类选择对应的API端点
            switch(category) {
                case 'tools-plugin':
                    endpoint = '/plugins';
                    break;
                case 'mcp':
                    endpoint = '/mcp';
                    break;
                case 'function':
                    endpoint = '/functions';
                    break;
                case 'computer-use':
                    endpoint = '/skills';
                    break;
                default:
                    pluginGrid.innerHTML = '<div class="empty-state">未知分类</div>';
                    return;
            }

            // 从API加载数据（只在首次加载时获取）
            if (offset === 0 || this.currentData.length === 0) {
                const response = await fetch(`${this.apiBaseUrl}${endpoint}`);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                this.currentData = await response.json();
            }

            console.log(`Loaded ${this.currentData.length} total items for ${category}`);

            // 使用分页大小
            const pageSize = limit || this.pageSize;

            // 计算要显示的数据范围
            const endIndex = offset + pageSize;
            const displayData = this.currentData.slice(0, endIndex);

            // 判断是否还有更多数据
            this.hasMore = endIndex < this.currentData.length;
            this.currentOffset = offset;

            // 渲染内容
            if (displayData && displayData.length > 0) {
                pluginGrid.innerHTML = this.renderToolCards(displayData, category);
                this.bindToolCardEvents();
            } else {
                pluginGrid.innerHTML = this.renderEmptyState(category);
            }

            // 更新More按钮状态
            this.updateMoreButton();

        } catch (error) {
            console.error('Error loading tools:', error);
            pluginGrid.innerHTML = `
                <div class="error-state">
                    <h3>加载失败</h3>
                    <p>${error.message}</p>
                    <button onclick="toolsHandlers.loadCategoryContent('${category}')" class="retry-btn">
                        重试
                    </button>
                </div>
            `;
        }
    },

    loadMoreTools() {
        if (!this.hasMore) return;

        const newOffset = this.currentOffset + this.pageSize;
        this.loadCategoryContent(this.currentCategory, newOffset);
    },

    updateMoreButton() {
        const moreBtn = document.querySelector('.plugin-more-btn');
        if (moreBtn) {
            if (this.hasMore) {
                moreBtn.style.display = 'block';
                moreBtn.disabled = false;
            } else {
                moreBtn.style.display = 'none';
            }
        }
    },

    renderToolCards(tools, category) {
        return tools.map(tool => this.renderToolCard(tool, category)).join('');
    },

    renderToolCard(tool, category) {
        const id = tool.plugin_id || tool.mcp_id || tool.function_id || tool.skill_id || '';
        const name = tool.name || 'Unnamed Tool';
        const description = tool.description || 'No description available';
        const type = this.getCategoryDisplayName(category);

        const statusLabel = tool.confirm_needed ? 'Confirm Required' : 'Active';
        const statusClass = tool.confirm_needed ? 'author-official--confirm' : 'author-official--active';

        const categoryIconMap = {
            'tools-plugin': 'extension',
            'mcp': 'dns',
            'function': 'functions',
            'computer-use': 'desktop_windows'
        };
        const iconName = categoryIconMap[category] || 'construction';

        const instructionLabel = tool.instruction || name;
        const filePath = tool.file_path || '';

        return `
            <div class="plugin-card tool-card tools-card-ref" data-id="${id}" data-category="${category}">
                <div class="tools-card-ref__top">
                    <div class="tools-card-ref__top-left">
                        <div class="tools-card-ref__icon">
                            <span class="material-icons-round">${iconName}</span>
                        </div>
                        <div class="tools-card-ref__meta">
                            <div class="tools-card-ref__title-row">
                                <h3 class="plugin-name">${name}</h3>
                                <span class="plugin-badge-connector">${type}</span>
                            </div>
                            <div class="plugin-author">
                                <span class="author-label">AI-SNS</span>
                                <span class="author-official ${statusClass}">${statusLabel}</span>
                            </div>
                        </div>
                    </div>
                </div>
                <p class="plugin-desc">${description}</p>
                ${(instructionLabel || filePath) ? `
                    <div class="tools-card-ref__codeblock">
                        <div class="tools-card-ref__codehead">
                            <span class="material-icons-round">terminal</span>
                            <span class="tools-card-ref__mono">${instructionLabel}</span>
                        </div>
                        ${filePath ? `
                            <div class="plugin-file-path tools-card-ref__codebody">
                                <span class="material-icons-round">folder</span>
                                <span class="tools-card-ref__mono">${filePath}</span>
                            </div>
                        ` : ''}
                    </div>
                ` : ''}
                <div class="plugin-actions tools-card-ref__actions">
                    <button class="plugin-test-btn tools-card-ref__btn tools-card-ref__btn--test" data-id="${id}" data-category="${category}" title="测试运行">
                        <span class="material-icons-round">play_arrow</span>
                        Test
                    </button>
                    <button class="plugin-edit-btn tools-card-ref__btn tools-card-ref__btn--edit" data-id="${id}" data-category="${category}" title="编辑">
                        <span class="material-icons-round">edit</span>
                        Edit
                    </button>
                    <button class="plugin-delete-btn tools-card-ref__btn tools-card-ref__btn--delete" data-id="${id}" data-category="${category}" title="删除">
                        <span class="material-icons-round">delete</span>
                        Delete
                    </button>
                </div>
            </div>
        `;
    },

    renderEmptyState(category) {
        const typeName = this.getCategoryDisplayName(category);
        return `
            <div class="empty-state">
                <svg viewBox="0 0 24 24" width="64" height="64" fill="none" stroke="currentColor" stroke-width="1.5">
                    <rect x="3" y="3" width="18" height="18" rx="2"/>
                    <line x1="9" y1="9" x2="15" y2="15"/>
                    <line x1="15" y1="9" x2="9" y2="15"/>
                </svg>
                <h3>暂无${typeName}</h3>
                <p>点击下方按钮创建第一个${typeName}</p>
                <button onclick="toolsHandlers.showAddDialog('${category}')" class="add-tool-btn">
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="12" y1="5" x2="12" y2="19"/>
                        <line x1="5" y1="12" x2="19" y2="12"/>
                    </svg>
                    添加${typeName}
                </button>
            </div>
        `;
    },

    bindToolCardEvents() {
        // 测试按钮
        document.querySelectorAll('.plugin-test-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.stopPropagation();
                const id = btn.getAttribute('data-id');
                const category = btn.getAttribute('data-category');
                await this.testTool(id, category, btn);
            });
        });

        // 编辑按钮
        document.querySelectorAll('.plugin-edit-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.stopPropagation();
                const id = btn.getAttribute('data-id');
                const category = btn.getAttribute('data-category');
                await this.editTool(id, category);
            });
        });

        // 删除按钮
        document.querySelectorAll('.plugin-delete-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.stopPropagation();
                const id = btn.getAttribute('data-id');
                const category = btn.getAttribute('data-category');
                await this.deleteTool(id, category);
            });
        });
    },

    async testTool(id, category, btn) {
        // 显示运行中状态
        const originalText = btn.innerHTML;
        btn.innerHTML = '<span class="spinner-small"></span> 运行中...';
        btn.disabled = true;

        try {
            let endpoint = '';
            switch(category) {
                case 'tools-plugin':
                    endpoint = `/plugins/${id}/execute`;
                    break;
                case 'mcp':
                    endpoint = `/mcp/${id}/execute`;
                    break;
                case 'function':
                    endpoint = `/functions/${id}/execute`;
                    break;
                case 'computer-use':
                    endpoint = `/skills/${id}/execute`;
                    break;
            }

            const response = await fetch(`${this.apiBaseUrl}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({})
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            // 显示结果
            this.showTestResult(result.result || result);

        } catch (error) {
            console.error('Test error:', error);
            this.showMessage('测试失败: ' + error.message, 'error');
        } finally {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    },

    showTestResult(result) {
        // 创建结果对话框
        const resultHTML = `
            <div class="modal-overlay" id="testResultDialog">
                <div class="modal-dialog test-result-dialog">
                    <div class="modal-header">
                        <h2>测试结果</h2>
                        <button class="modal-close" onclick="document.getElementById('testResultDialog').remove()">
                            <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="18" y1="6" x2="6" y2="18"/>
                                <line x1="6" y1="6" x2="18" y2="18"/>
                            </svg>
                        </button>
                    </div>
                    <div class="modal-body">
                        <pre class="test-result-pre">${JSON.stringify(result, null, 2)}</pre>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-primary" onclick="document.getElementById('testResultDialog').remove()">
                            关闭
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', resultHTML);
    },

    async editTool(id, category) {
        try {
            // 获取工具数据
            let endpoint = '';
            switch(category) {
                case 'tools-plugin':
                    endpoint = `/plugins/${id}`;
                    break;
                case 'mcp':
                    endpoint = `/mcp/${id}`;
                    break;
                case 'function':
                    endpoint = `/functions/${id}`;
                    break;
                case 'computer-use':
                    endpoint = `/skills/${id}`;
                    break;
            }

            const response = await fetch(`${this.apiBaseUrl}${endpoint}`);
            if (!response.ok) {
                throw new Error('Failed to fetch tool data');
            }

            const tool = await response.json();

            // 显示编辑对话框
            this.editDialog.show(category, tool, () => {
                // 保存成功后重新加载
                this.loadCategoryContent(category);
            });

        } catch (error) {
            console.error('Edit error:', error);
            this.showMessage('加载工具数据失败: ' + error.message, 'error');
        }
    },

    async deleteTool(id, category) {
        if (!confirm('确定要删除这个工具吗？')) return;

        try {
            let endpoint = '';
            switch(category) {
                case 'tools-plugin':
                    endpoint = `/plugins/${id}`;
                    break;
                case 'mcp':
                    endpoint = `/mcp/${id}`;
                    break;
                case 'function':
                    endpoint = `/functions/${id}`;
                    break;
                case 'computer-use':
                    endpoint = `/skills/${id}`;
                    break;
            }

            const response = await fetch(`${this.apiBaseUrl}${endpoint}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                throw new Error(`删除失败: ${response.status}`);
            }

            this.showMessage('删除成功', 'success');
            await this.loadCategoryContent(category);
        } catch (error) {
            console.error('Delete error:', error);
            this.showMessage('删除失败: ' + error.message, 'error');
        }
    },

    showAddDialog(category) {
        this.editDialog.show(category, null, () => {
            this.loadCategoryContent(category);
        });
    },

    getCategoryDisplayName(category) {
        const names = {
            'tools-plugin': 'Plugin',
            'mcp': 'MCP',
            'function': 'Function',
            'computer-use': 'Computer Use'
        };
        return names[category] || category;
    },

    getToolIcon(category) {
        const icons = {
            'tools-plugin': '<svg viewBox="0 0 24 24" width="32" height="32" fill="#10a37f"><path d="M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z"/></svg>',
            'mcp': '<svg viewBox="0 0 24 24" width="32" height="32" fill="#1a73e8"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21" stroke="currentColor" stroke-width="2"/></svg>',
            'function': '<svg viewBox="0 0 24 24" width="32" height="32" fill="#d97706"><path d="M15.6 5.29c-1.1-.1-2.07.71-2.17 1.81L13.18 10H16v2h-3l-.44 5.07c-.14 1.55-1.28 2.76-2.81 2.93-1.81.2-3.39-1.16-3.59-2.97L6 10H4V8h2.23l.21-2.93c.14-1.55 1.28-2.76 2.81-2.93 1.81-.2 3.39 1.16 3.59 2.97l.16 2.9H16V5.5c0-.83.67-1.5 1.5-1.5s1.5.67 1.5 1.5V8h2.5c.83 0 1.5.67 1.5 1.5S21.83 11 21 11h-2.5v7.5c0 .83-.67 1.5-1.5 1.5s-1.5-.67-1.5-1.5V11h-2.23l-.17 2.09z"/></svg>',
            'computer-use': '<svg viewBox="0 0 24 24" width="32" height="32" fill="#7c3aed"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="2" y1="20" x2="22" y2="20" stroke="currentColor" stroke-width="2"/></svg>'
        };
        return icons[category] || icons['tools-plugin'];
    },

    showMessage(message, type = 'info') {
        console.log(`[${type}] ${message}`);

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 16px 24px;
            background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
            color: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10000;
            animation: slideIn 0.3s ease-out;
        `;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    },

    destroy() {
        this.currentCategory = 'tools-plugin';
    }
};

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = toolsHandlers;
}

if (typeof window !== 'undefined') {
    window.toolsHandlers = toolsHandlers;
}

export default toolsHandlers;
