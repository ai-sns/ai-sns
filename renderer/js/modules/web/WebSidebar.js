/**
 * Web Sidebar - 侧边栏渲染
 */

const WebSidebar = {
    llmData: [],
    toolData: [],
    llmExpanded: true,
    toolExpanded: false,
    llmSearchText: '',
    toolSearchText: '',

    async init() {
        await this.loadData();
    },

    async loadData() {
        try {
            console.log('[WebSidebar] Loading data from API...');
            if (window.api) {
                const response = await window.api.get('/api/system/web-mng');
                console.log('[WebSidebar] API response:', response);
                if (response && response.data) {
                    // 过滤并排序LLM数据
                    this.llmData = response.data
                        .filter(item => item.type === 'LLM' && !item.is_delete)
                        .sort((a, b) => {
                            const posA = a.position !== null && a.position !== undefined ? a.position : 999;
                            const posB = b.position !== null && b.position !== undefined ? b.position : 999;
                            return posA - posB;
                        });
                    
                    // 过滤并排序Tool数据
                    this.toolData = response.data
                        .filter(item => item.type === 'Tool' && !item.is_delete)
                        .sort((a, b) => {
                            const posA = a.position !== null && a.position !== undefined ? a.position : 999;
                            const posB = b.position !== null && b.position !== undefined ? b.position : 999;
                            return posA - posB;
                        });
                    
                    console.log('[WebSidebar] Loaded LLM items:', this.llmData.length);
                    console.log('[WebSidebar] Loaded Tool items:', this.toolData.length);
                } else {
                    console.warn('[WebSidebar] No data in response');
                }
            } else {
                console.error('[WebSidebar] window.api not available');
            }
        } catch (error) {
            console.error('[WebSidebar] Failed to load web data:', error);
        }
    },

    getFilteredLLMData() {
        if (!this.llmSearchText) return this.llmData;
        const searchLower = this.llmSearchText.toLowerCase();
        return this.llmData.filter(item => 
            item.name.toLowerCase().includes(searchLower) ||
            (item.title && item.title.toLowerCase().includes(searchLower)) ||
            (item.description && item.description.toLowerCase().includes(searchLower))
        );
    },

    getFilteredToolData() {
        if (!this.toolSearchText) return this.toolData;
        const searchLower = this.toolSearchText.toLowerCase();
        return this.toolData.filter(item => 
            item.name.toLowerCase().includes(searchLower) ||
            (item.title && item.title.toLowerCase().includes(searchLower)) ||
            (item.description && item.description.toLowerCase().includes(searchLower))
        );
    },

    render() {
        return `
            <div class="web-sidebar-content">
                ${this.renderLLMSection()}
                ${this.renderToolSection()}
            </div>
        `;
    },

    renderLLMSection() {
        return `
            <div class="web-section ${this.llmExpanded ? 'expanded' : 'collapsed'}" data-type="llm">
                <div class="web-section-header" data-section="llm">
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"/>
                        <path d="M2 12h20"/>
                        <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
                    </svg>
                    <span class="web-section-title">LLM Online</span>
                    <svg class="web-section-chevron" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="6 9 12 15 18 9"/>
                    </svg>
                </div>
                <div class="web-section-content">
                    <div class="web-search-box">
                        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="11" cy="11" r="8"/>
                            <path d="m21 21-4.35-4.35"/>
                        </svg>
                        <input type="text" placeholder="Search..." class="web-search-input" id="llmSearchInput">
                    </div>
                    <div class="web-action-buttons">
                        <button class="web-action-btn" id="addLLMBtn">
                            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M12 5v14M5 12h14"/>
                            </svg>
                            <span>Add</span>
                        </button>
                        <button class="web-action-btn" id="manageLLMBtn">
                            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                                <circle cx="12" cy="12" r="3"/>
                                <path d="M12 1v6m0 6v6M1 12h6m6 0h6"/>
                            </svg>
                            <span>Manage</span>
                        </button>
                    </div>
                    <div class="web-icon-grid">
                        ${this.renderLLMIcons()}
                    </div>
                </div>
            </div>
        `;
    },

    renderToolSection() {
        return `
            <div class="web-section ${this.toolExpanded ? 'expanded' : 'collapsed'}" data-type="tool">
                <div class="web-section-header" data-section="tool">
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
                    </svg>
                    <span class="web-section-title">AI Tools Online</span>
                    <svg class="web-section-chevron" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="6 9 12 15 18 9"/>
                    </svg>
                </div>
                <div class="web-section-content">
                    <div class="web-search-box">
                        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="11" cy="11" r="8"/>
                            <path d="m21 21-4.35-4.35"/>
                        </svg>
                        <input type="text" placeholder="Search..." class="web-search-input" id="toolSearchInput">
                    </div>
                    <div class="web-action-buttons">
                        <button class="web-action-btn" id="addToolBtn">
                            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M12 5v14M5 12h14"/>
                            </svg>
                            <span>Add</span>
                        </button>
                        <button class="web-action-btn" id="manageToolBtn">
                            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                                <circle cx="12" cy="12" r="3"/>
                                <path d="M12 1v6m0 6v6M1 12h6m6 0h6"/>
                            </svg>
                            <span>Manage</span>
                        </button>
                    </div>
                    <div class="web-icon-grid">
                        ${this.renderToolIcons()}
                    </div>
                </div>
            </div>
        `;
    },

    renderLLMIcons() {
        const filteredData = this.getFilteredLLMData();
        if (filteredData.length === 0) {
            return '<div class="web-empty-message">No LLM services available</div>';
        }
        return filteredData.map(llm => `
            <div class="web-icon-item" data-url="${llm.url || ''}" data-name="${llm.name}" title="${llm.name}">
                ${this.getIcon(llm.filename, llm.name)}
                <span class="web-icon-label">${llm.name}</span>
            </div>
        `).join('');
    },

    renderToolIcons() {
        const filteredData = this.getFilteredToolData();
        if (filteredData.length === 0) {
            return '<div class="web-empty-message">No AI tools available</div>';
        }
        return filteredData.map(tool => `
            <div class="web-icon-item" data-url="${tool.url || ''}" data-name="${tool.name}" title="${tool.name}">
                ${this.getIcon(tool.filename, tool.name)}
                <span class="web-icon-label">${tool.name}</span>
            </div>
        `).join('');
    },

    getIcon(filename, name) {
        if (filename && filename !== 'openai.png') {
            // Use backend server URL for images
            const path = `/resource/images/${filename}`;
            const imageUrl = (typeof window !== 'undefined' && typeof window.resolveAgentServerUrl === 'function')
                ? window.resolveAgentServerUrl(path)
                : path;
            return `<img src="${imageUrl}" alt="${name}" class="web-icon-img" onerror="this.style.display='none';this.nextElementSibling.style.display='flex';">
                    <div class="web-icon-fallback" style="display:none;">${name.charAt(0).toUpperCase()}</div>`;
        }
        return `<div class="web-icon-fallback">${name.charAt(0).toUpperCase()}</div>`;
    },

    // 搜索功能
    handleLLMSearch(searchText) {
        this.llmSearchText = searchText;
        this.refreshLLMIcons();
    },

    handleToolSearch(searchText) {
        this.toolSearchText = searchText;
        this.refreshToolIcons();
    },

    refreshLLMIcons() {
        const container = document.querySelector('.web-section[data-type="llm"] .web-icon-grid');
        if (container) {
            container.innerHTML = this.renderLLMIcons();
        }
    },

    refreshToolIcons() {
        const container = document.querySelector('.web-section[data-type="tool"] .web-icon-grid');
        if (container) {
            container.innerHTML = this.renderToolIcons();
        }
    },

    // 管理对话框
    showManageDialog(type) {
        const data = type === 'LLM' ? this.llmData : this.toolData;
        const title = type === 'LLM' ? 'Manage LLM Services' : 'Manage AI Tools';
        
        // 隐藏 BrowserView 以防止遮挡对话框
        if (window.electronAPI && window.electronAPI.hideBrowserView) {
            window.electronAPI.hideBrowserView();
        }
        
        const dialogHTML = `
            <div class="web-manage-dialog-overlay" id="webManageDialog">
                <div class="web-manage-dialog">
                    <div class="web-manage-dialog-header">
                        <h3>${title}</h3>
                        <button class="web-manage-dialog-close" data-action="close-manage">
                            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M18 6L6 18M6 6l12 12"/>
                            </svg>
                        </button>
                    </div>
                    <div class="web-manage-dialog-content">
                        <div class="web-manage-list" id="webManageList" data-type="${type}">
                            ${this.renderManageItems(data, type)}
                        </div>
                    </div>
                </div>
            </div>
        `;

        // 移除旧对话框
        const oldDialog = document.getElementById('webManageDialog');
        if (oldDialog) oldDialog.remove();

        // 添加新对话框
        document.body.insertAdjacentHTML('beforeend', dialogHTML);

        // 初始化拖拽
        this.initDragAndDrop(type);

        // 绑定按钮事件
        this.bindManageDialogEvents(type);
    },

    bindManageDialogEvents(type) {
        const dialog = document.getElementById('webManageDialog');
        if (!dialog) return;

        // 事件委托处理所有按钮点击
        dialog.addEventListener('click', (e) => {
            const button = e.target.closest('button');
            if (!button) return;

            const action = button.dataset.action;
            const itemId = parseInt(button.dataset.id);
            const itemType = button.dataset.type;

            switch (action) {
                case 'close-manage':
                    this.closeManageDialog();
                    break;
                case 'edit':
                    this.editItem(itemId, itemType);
                    break;
                case 'delete':
                    this.deleteItem(itemId, itemType);
                    break;
            }
        });
    },

    renderManageItems(data, type) {
        if (data.length === 0) {
            return '<div class="web-empty-message">No items available</div>';
        }

        return data.map((item, index) => `
            <div class="web-manage-item" draggable="true" data-id="${item.id}" data-position="${item.position || index}">
                <div class="web-manage-item-drag">
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M9 5h2M9 12h2M9 19h2M15 5h2M15 12h2M15 19h2"/>
                    </svg>
                </div>
                <div class="web-manage-item-icon">
                    ${this.getIcon(item.filename, item.name)}
                </div>
                <div class="web-manage-item-info">
                    <div class="web-manage-item-name">${item.name}</div>
                    <div class="web-manage-item-url">${item.url || ''}</div>
                </div>
                <div class="web-manage-item-actions">
                    <button class="web-manage-item-btn" data-action="edit" data-id="${item.id}" data-type="${type}" title="Edit">
                        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                        </svg>
                    </button>
                    <button class="web-manage-item-btn web-manage-item-btn-delete" data-action="delete" data-id="${item.id}" data-type="${type}" title="Delete">
                        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                        </svg>
                    </button>
                </div>
            </div>
        `).join('');
    },

    closeManageDialog() {
        const dialog = document.getElementById('webManageDialog');
        if (dialog) {
            // 获取对话框类型
            const list = dialog.querySelector('#webManageList');
            const type = list ? list.dataset.type : null;
            
            // 移除对话框
            dialog.remove();
            
            // 恢复显示 BrowserView
            if (window.electronAPI && window.electronAPI.showBrowserView) {
                window.electronAPI.showBrowserView();
            }
            
            // 刷新侧边栏显示（使用当前内存中的数据）
            if (type === 'LLM') {
                this.refreshLLMIcons();
            } else if (type === 'Tool') {
                this.refreshToolIcons();
            }
            
            console.log('[WebSidebar] Dialog closed, sidebar refreshed');
        }
    },

    // 编辑功能
    async editItem(itemId, type) {
        const data = type === 'LLM' ? this.llmData : this.toolData;
        const item = data.find(i => i.id === itemId);
        if (!item) return;

        // 不需要再次隐藏 BrowserView，因为管理对话框已经隐藏了它
        
        const editHTML = `
            <div class="web-edit-dialog-overlay" id="webEditDialog">
                <div class="web-edit-dialog">
                    <div class="web-edit-dialog-header">
                        <h3>Edit ${type}</h3>
                        <button class="web-edit-dialog-close" data-action="close-edit">
                            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M18 6L6 18M6 6l12 12"/>
                            </svg>
                        </button>
                    </div>
                    <div class="web-edit-dialog-content">
                        <div class="web-edit-form">
                            <div class="web-edit-form-group">
                                <label>Name *</label>
                                <input type="text" id="editName" value="${item.name || ''}" required>
                            </div>
                            <div class="web-edit-form-group">
                                <label>Title</label>
                                <input type="text" id="editTitle" value="${item.title || ''}">
                            </div>
                            <div class="web-edit-form-group">
                                <label>URL *</label>
                                <input type="text" id="editUrl" value="${item.url || ''}" required>
                            </div>
                            <div class="web-edit-form-group">
                                <label>Description</label>
                                <textarea id="editDescription" rows="3">${item.description || ''}</textarea>
                            </div>
                            <div class="web-edit-form-group">
                                <label>Icon Filename</label>
                                <input type="text" id="editFilename" value="${item.filename || ''}" placeholder="e.g., icon.png">
                            </div>
                        </div>
                    </div>
                    <div class="web-edit-dialog-footer">
                        <button class="web-edit-dialog-btn web-edit-dialog-btn-cancel" data-action="cancel-edit">Cancel</button>
                        <button class="web-edit-dialog-btn web-edit-dialog-btn-save" data-action="save-edit" data-id="${itemId}" data-type="${type}">Save</button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', editHTML);

        // 绑定编辑对话框事件
        this.bindEditDialogEvents(itemId, type);
    },

    bindEditDialogEvents(itemId, type) {
        const dialog = document.getElementById('webEditDialog');
        if (!dialog) return;

        // 事件委托处理所有按钮点击
        dialog.addEventListener('click', (e) => {
            const button = e.target.closest('button');
            if (!button) return;

            const action = button.dataset.action;

            switch (action) {
                case 'close-edit':
                case 'cancel-edit':
                    this.closeEditDialog();
                    break;
                case 'save-edit':
                    const saveItemId = parseInt(button.dataset.id);
                    const saveType = button.dataset.type;
                    this.saveEdit(saveItemId, saveType);
                    break;
            }
        });
    },

    closeEditDialog() {
        const dialog = document.getElementById('webEditDialog');
        if (dialog) dialog.remove();
    },

    async saveEdit(itemId, type) {
        const name = document.getElementById('editName').value.trim();
        const title = document.getElementById('editTitle').value.trim();
        const url = document.getElementById('editUrl').value.trim();
        const description = document.getElementById('editDescription').value.trim();
        const filename = document.getElementById('editFilename').value.trim();

        if (!name || !url) {
            alert('Name and URL are required!');
            return;
        }

        try {
            const response = await window.api.put(`/api/system/web-mng/${itemId}`, {
                name,
                title,
                url,
                description,
                filename,
                type
            });

            if (response && response.success) {
                console.log('[WebSidebar] Item updated successfully');
                
                // 更新内存中的数据
                const data = type === 'LLM' ? this.llmData : this.toolData;
                const item = data.find(i => i.id === itemId);
                if (item) {
                    item.name = name;
                    item.title = title;
                    item.url = url;
                    item.description = description;
                    item.filename = filename;
                }
                
                // 关闭编辑对话框
                this.closeEditDialog();
                
                // 重新渲染管理对话框以显示更新
                const list = document.getElementById('webManageList');
                if (list) {
                    list.innerHTML = this.renderManageItems(data, type);
                }
                
                console.log('[WebSidebar] Item updated in dialog');
            }
        } catch (error) {
            console.error('[WebSidebar] Failed to update item:', error);
            alert('Failed to update item. Please try again.');
        }
    },

    // 删除功能
    async deleteItem(itemId, type) {
        if (!confirm('Are you sure you want to delete this item?')) {
            return;
        }

        try {
            const response = await window.api.delete(`/api/system/web-mng/${itemId}`);

            if (response && response.success) {
                console.log('[WebSidebar] Item deleted successfully');
                
                // 从内存中的数据移除该项
                if (type === 'LLM') {
                    const index = this.llmData.findIndex(i => i.id === itemId);
                    if (index !== -1) {
                        this.llmData.splice(index, 1);
                    }
                } else {
                    const index = this.toolData.findIndex(i => i.id === itemId);
                    if (index !== -1) {
                        this.toolData.splice(index, 1);
                    }
                }
                
                // 重新渲染管理对话框以显示更新
                const data = type === 'LLM' ? this.llmData : this.toolData;
                const list = document.getElementById('webManageList');
                if (list) {
                    list.innerHTML = this.renderManageItems(data, type);
                }
                
                console.log('[WebSidebar] Item removed from dialog');
            }
        } catch (error) {
            console.error('[WebSidebar] Failed to delete item:', error);
            alert('Failed to delete item. Please try again.');
        }
    },

    // 拖拽排序功能
    initDragAndDrop(type) {
        const list = document.getElementById('webManageList');
        if (!list) return;

        let draggedElement = null;

        list.addEventListener('dragstart', (e) => {
            if (e.target.classList.contains('web-manage-item')) {
                draggedElement = e.target;
                e.target.classList.add('dragging');
            }
        });

        list.addEventListener('dragend', (e) => {
            if (e.target.classList.contains('web-manage-item')) {
                e.target.classList.remove('dragging');
                draggedElement = null;
            }
        });

        list.addEventListener('dragover', (e) => {
            e.preventDefault();
            const afterElement = this.getDragAfterElement(list, e.clientY);
            const dragging = document.querySelector('.dragging');
            
            if (afterElement == null) {
                list.appendChild(dragging);
            } else {
                list.insertBefore(dragging, afterElement);
            }
        });

        list.addEventListener('drop', async (e) => {
            e.preventDefault();
            await this.updatePositions(type);
        });
    },

    getDragAfterElement(container, y) {
        const draggableElements = [...container.querySelectorAll('.web-manage-item:not(.dragging)')];

        return draggableElements.reduce((closest, child) => {
            const box = child.getBoundingClientRect();
            const offset = y - box.top - box.height / 2;

            if (offset < 0 && offset > closest.offset) {
                return { offset: offset, element: child };
            } else {
                return closest;
            }
        }, { offset: Number.NEGATIVE_INFINITY }).element;
    },

    async updatePositions(type) {
        const list = document.getElementById('webManageList');
        const items = [...list.querySelectorAll('.web-manage-item')];
        
        // 使用不同的 position 范围避免冲突
        // LLM: 0-999, Tool: 1000-1999
        const basePosition = type === 'LLM' ? 0 : 1000;
        
        const updates = items.map((item, index) => ({
            id: parseInt(item.dataset.id),
            position: basePosition + index
        }));

        console.log('[WebSidebar] Sending reorder request for', type);
        console.log('[WebSidebar] Updates:', JSON.stringify(updates, null, 2));

        try {
            const response = await window.api.put('/api/system/web-mng/reorder', updates);

            if (response && response.success) {
                console.log('[WebSidebar] Positions updated successfully');
                
                // 只更新内存中的数据，不重新加载
                // 更新对应类型的数据的 position
                if (type === 'LLM') {
                    updates.forEach(update => {
                        const item = this.llmData.find(i => i.id === update.id);
                        if (item) {
                            item.position = update.position;
                        }
                    });
                    // 重新排序
                    this.llmData.sort((a, b) => {
                        const posA = a.position !== null && a.position !== undefined ? a.position : 999;
                        const posB = b.position !== null && b.position !== undefined ? b.position : 999;
                        return posA - posB;
                    });
                } else {
                    updates.forEach(update => {
                        const item = this.toolData.find(i => i.id === update.id);
                        if (item) {
                            item.position = update.position;
                        }
                    });
                    // 重新排序
                    this.toolData.sort((a, b) => {
                        const posA = a.position !== null && a.position !== undefined ? a.position : 999;
                        const posB = b.position !== null && b.position !== undefined ? b.position : 999;
                        return posA - posB;
                    });
                }
                
                // 不重新加载，不刷新侧边栏，不重新打开对话框
                // 用户可以继续拖拽调整
                console.log('[WebSidebar] Local data updated, ready for next drag');
            }
        } catch (error) {
            console.error('[WebSidebar] Failed to update positions:', error);
            console.error('[WebSidebar] Error details:', error.message);
            alert('Failed to update positions. Please try again.');
        }
    },

    // Add对话框
    showAddDialog(type) {
        const title = type === 'LLM' ? 'Add LLM Service' : 'Add AI Tool';
        
        // 隐藏 BrowserView 以防止遮挡对话框
        if (window.electronAPI && window.electronAPI.hideBrowserView) {
            window.electronAPI.hideBrowserView();
        }
        
        const dialogHTML = `
            <div class="web-manage-dialog-overlay" id="webAddDialog">
                <div class="web-edit-dialog">
                    <div class="web-edit-dialog-header">
                        <h3>${title}</h3>
                        <button class="web-edit-dialog-close" data-action="close-add">
                            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M18 6L6 18M6 6l12 12"/>
                            </svg>
                        </button>
                    </div>
                    <div class="web-edit-dialog-content">
                        <div class="web-edit-form">
                            <div class="web-edit-form-group">
                                <label>Service Name *</label>
                                <input type="text" id="addName" placeholder="e.g., ChatGPT" required>
                            </div>
                            <div class="web-edit-form-group">
                                <label>Service URL *</label>
                                <input type="url" id="addUrl" placeholder="https://..." required>
                            </div>
                            <div class="web-edit-form-group">
                                <label>Description (Optional)</label>
                                <textarea id="addDescription" rows="3"></textarea>
                            </div>
                            <div class="web-edit-form-group">
                                <label>Icon Filename</label>
                                <input type="text" id="addFilename" value="openai.png" placeholder="e.g., icon.png">
                            </div>
                        </div>
                    </div>
                    <div class="web-edit-dialog-footer">
                        <button class="web-edit-dialog-btn web-edit-dialog-btn-cancel" data-action="cancel-add">Cancel</button>
                        <button class="web-edit-dialog-btn web-edit-dialog-btn-save" data-action="save-add" data-type="${type}">Add</button>
                    </div>
                </div>
            </div>
        `;

        // 移除旧对话框
        const oldDialog = document.getElementById('webAddDialog');
        if (oldDialog) oldDialog.remove();

        // 添加新对话框
        document.body.insertAdjacentHTML('beforeend', dialogHTML);

        // 绑定按钮事件
        this.bindAddDialogEvents(type);
    },

    bindAddDialogEvents(type) {
        const dialog = document.getElementById('webAddDialog');
        if (!dialog) return;

        // 事件委托处理所有按钮点击
        dialog.addEventListener('click', (e) => {
            const button = e.target.closest('button');
            if (!button) return;

            const action = button.dataset.action;

            switch (action) {
                case 'close-add':
                case 'cancel-add':
                    this.closeAddDialog();
                    break;
                case 'save-add':
                    const saveType = button.dataset.type;
                    this.saveAdd(saveType);
                    break;
            }
        });
    },

    closeAddDialog() {
        const dialog = document.getElementById('webAddDialog');
        if (dialog) {
            dialog.remove();
            
            // 恢复显示 BrowserView
            if (window.electronAPI && window.electronAPI.showBrowserView) {
                window.electronAPI.showBrowserView();
            }
            
            console.log('[WebSidebar] Add dialog closed, BrowserView restored');
        }
    },

    async saveAdd(type) {
        const name = document.getElementById('addName').value.trim();
        const url = document.getElementById('addUrl').value.trim();
        const description = document.getElementById('addDescription').value.trim();
        const filename = document.getElementById('addFilename').value.trim();

        if (!name || !url) {
            alert('Name and URL are required!');
            return;
        }

        try {
            const response = await window.api.post('/api/system/web-mng', {
                name,
                url,
                type,
                description,
                filename
            });

            if (response && response.success) {
                console.log('[WebSidebar] Item added successfully');
                
                // 重新加载数据
                await this.loadData();
                
                // 刷新sidebar
                const sidebar = document.getElementById('sidebar-web');
                if (sidebar) {
                    sidebar.innerHTML = this.render();
                }
                
                // 关闭对话框（会自动恢复BrowserView）
                this.closeAddDialog();
                
                // 显示成功消息
                alert(`${type} service added successfully`);
            }
        } catch (error) {
            console.error('[WebSidebar] Failed to add item:', error);
            alert('Failed to add item. Please try again.');
        }
    }
};

export default WebSidebar;
