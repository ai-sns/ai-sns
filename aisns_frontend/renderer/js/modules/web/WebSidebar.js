/**
 * Web Sidebar - sidebar rendering
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
                    // Filter and sort LLM data
                    this.llmData = response.data
                        .filter(item => item.type === 'LLM' && !item.is_delete)
                        .sort((a, b) => {
                            const posA = a.position !== null && a.position !== undefined ? a.position : 999;
                            const posB = b.position !== null && b.position !== undefined ? b.position : 999;
                            return posA - posB;
                        });

                    // Filter and sort Tool data
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
                    <span class="web-section-title">${window.escHtml(window.tt('web.sidebar.llmOnline'))}</span>
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
                        <input type="text" placeholder="${window.escAttr(window.tt('web.sidebar.searchPlaceholder'))}" class="web-search-input" id="llmSearchInput">
                    </div>
                    <div class="web-action-buttons">
                        <button class="web-action-btn" id="addLLMBtn">
                            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M12 5v14M5 12h14"/>
                            </svg>
                            <span>${window.escHtml(window.tt('web.sidebar.add'))}</span>
                        </button>
                        <button class="web-action-btn" id="manageLLMBtn">
                            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                                <circle cx="12" cy="12" r="3"/>
                                <path d="M12 1v6m0 6v6M1 12h6m6 0h6"/>
                            </svg>
                            <span>${window.escHtml(window.tt('web.sidebar.manage'))}</span>
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
                    <span class="web-section-title">${window.escHtml(window.tt('web.sidebar.aiToolsOnline'))}</span>
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
                        <input type="text" placeholder="${window.escAttr(window.tt('web.sidebar.searchPlaceholder'))}" class="web-search-input" id="toolSearchInput">
                    </div>
                    <div class="web-action-buttons">
                        <button class="web-action-btn" id="addToolBtn">
                            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M12 5v14M5 12h14"/>
                            </svg>
                            <span>${window.escHtml(window.tt('web.sidebar.add'))}</span>
                        </button>
                        <button class="web-action-btn" id="manageToolBtn">
                            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                                <circle cx="12" cy="12" r="3"/>
                                <path d="M12 1v6m0 6v6M1 12h6m6 0h6"/>
                            </svg>
                            <span>${window.escHtml(window.tt('web.sidebar.manage'))}</span>
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
            return `<div class="web-empty-message">${window.escHtml(window.tt('web.sidebar.emptyLlm'))}</div>`;
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
            return `<div class="web-empty-message">${window.escHtml(window.tt('web.sidebar.emptyTools'))}</div>`;
        }
        return filteredData.map(tool => `
            <div class="web-icon-item" data-url="${tool.url || ''}" data-name="${tool.name}" title="${tool.name}">
                ${this.getIcon(tool.filename, tool.name)}
                <span class="web-icon-label">${tool.name}</span>
            </div>
        `).join('');
    },

    getIcon(filename, name) {
        return `<div class="web-icon-fallback">${name.charAt(0).toUpperCase()}</div>`;
    },

    // Search
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

    // Manage dialog
    showManageDialog(type) {
        const data = type === 'LLM' ? this.llmData : this.toolData;
        const title = type === 'LLM' ? 'Manage LLM Services' : 'Manage AI Tools';

        // Hide BrowserView to prevent it from covering the dialog
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

        // Remove old dialog
        const oldDialog = document.getElementById('webManageDialog');
        if (oldDialog) oldDialog.remove();

        // Insert new dialog
        document.body.insertAdjacentHTML('beforeend', dialogHTML);

        // Init drag & drop
        this.initDragAndDrop(type);

        // Bind button events
        this.bindManageDialogEvents(type);
    },

    bindManageDialogEvents(type) {
        const dialog = document.getElementById('webManageDialog');
        if (!dialog) return;

        // Event delegation for all button clicks
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
            // Get dialog type
            const list = dialog.querySelector('#webManageList');
            const type = list ? list.dataset.type : null;

            // Remove dialog
            dialog.remove();

            // Restore BrowserView
            if (window.electronAPI && window.electronAPI.showBrowserView) {
                window.electronAPI.showBrowserView();
            }

            // Refresh sidebar (using current in-memory data)
            if (type === 'LLM') {
                this.refreshLLMIcons();
            } else if (type === 'Tool') {
                this.refreshToolIcons();
            }

            console.log('[WebSidebar] Dialog closed, sidebar refreshed');
        }
    },

    // Edit
    async editItem(itemId, type) {
        const data = type === 'LLM' ? this.llmData : this.toolData;
        const item = data.find(i => i.id === itemId);
        if (!item) return;

        // No need to hide BrowserView again; manage dialog already did it

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
                            <input type="hidden" id="editTitle" value="${item.title || ''}">
                            <div class="web-edit-form-group">
                                <label>URL *</label>
                                <input type="text" id="editUrl" value="${item.url || ''}" required>
                            </div>
                            <div class="web-edit-form-group">
                                <label>Description</label>
                                <textarea id="editDescription" rows="3">${item.description || ''}</textarea>
                            </div>
                            <input type="hidden" id="editFilename" value="${item.filename || ''}">
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

        // Bind edit dialog events
        this.bindEditDialogEvents(itemId, type);
    },

    bindEditDialogEvents(itemId, type) {
        const dialog = document.getElementById('webEditDialog');
        if (!dialog) return;

        // Event delegation for all button clicks
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

                // Update in-memory data
                const data = type === 'LLM' ? this.llmData : this.toolData;
                const item = data.find(i => i.id === itemId);
                if (item) {
                    item.name = name;
                    item.title = title;
                    item.url = url;
                    item.description = description;
                    item.filename = filename;
                }

                // Close edit dialog
                this.closeEditDialog();

                // Re-render manage dialog to show updates
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

    // Delete
    async deleteItem(itemId, type) {
        const data = type === 'LLM' ? this.llmData : this.toolData;
        const item = (data || []).find(i => parseInt(i.id) === parseInt(itemId));
        const itemName = item && item.name ? `"${item.name}"` : 'this item';
        const dialogTitle = type === 'LLM' ? 'Delete LLM Service' : 'Delete AI Tool';

        const confirmed = await (async () => {
            try {
                if (window.Toast && typeof window.Toast.confirm === 'function') {
                    return await window.Toast.confirm(`Delete ${itemName}?`, {
                        title: dialogTitle,
                        confirmText: 'Delete',
                        cancelText: 'Cancel',
                        type: 'warning'
                    });
                }

                if (window.Modal && typeof window.Modal.show === 'function') {
                    return await new Promise((resolve) => {
                        window.Modal.show({
                            title: dialogTitle,
                            content: `<p>Delete ${itemName}?</p>`,
                            confirmText: 'Delete',
                            cancelText: 'Cancel',
                            onConfirm: () => {
                                resolve(true);
                                return true;
                            },
                            onCancel: () => {
                                resolve(false);
                                return true;
                            }
                        });
                    });
                }
            } catch (err) {
                console.error('[WebSidebar] Failed to show delete confirmation dialog:', err);
            }

            // Fail-closed: when no confirmation UI is available, do not delete.
            return false;
        })();

        if (!confirmed) return;

        try {
            const response = await window.api.delete(`/api/system/web-mng/${itemId}`);

            if (response && response.success) {
                console.log('[WebSidebar] Item deleted successfully');

                // Remove item from in-memory data
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

                // Re-render manage dialog to show updates
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

    // Drag-and-drop sorting
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

        // Use different position ranges to avoid conflicts
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

                // Update in-memory data only; do not reload
                // Update positions for the corresponding type
                if (type === 'LLM') {
                    updates.forEach(update => {
                        const item = this.llmData.find(i => i.id === update.id);
                        if (item) {
                            item.position = update.position;
                        }
                    });
                    // Re-sort
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
                    // Re-sort
                    this.toolData.sort((a, b) => {
                        const posA = a.position !== null && a.position !== undefined ? a.position : 999;
                        const posB = b.position !== null && b.position !== undefined ? b.position : 999;
                        return posA - posB;
                    });
                }

                // Do not reload/refresh/reopen dialogs
                // User can keep dragging to adjust
                console.log('[WebSidebar] Local data updated, ready for next drag');
            }
        } catch (error) {
            console.error('[WebSidebar] Failed to update positions:', error);
            console.error('[WebSidebar] Error details:', error.message);
            alert('Failed to update positions. Please try again.');
        }
    },

    // Add dialog
    showAddDialog(type) {
        const title = type === 'LLM' ? 'Add LLM Service' : 'Add AI Tool';

        // Hide BrowserView to prevent it from covering the dialog
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
                                <label>Name *</label>
                                <input type="text" id="addName" placeholder="e.g., ChatGPT" required>
                            </div>
                            <div class="web-edit-form-group">
                                <label>URL *</label>
                                <input type="url" id="addUrl" placeholder="https://..." required>
                            </div>
                            <div class="web-edit-form-group">
                                <label>Description</label>
                                <textarea id="addDescription" rows="3"></textarea>
                            </div>
                            <input type="hidden" id="addFilename" value="openai.png">
                        </div>
                    </div>
                    <div class="web-edit-dialog-footer">
                        <button class="web-edit-dialog-btn web-edit-dialog-btn-cancel" data-action="cancel-add">Cancel</button>
                        <button class="web-edit-dialog-btn web-edit-dialog-btn-save" data-action="save-add" data-type="${type}">Add</button>
                    </div>
                </div>
            </div>
        `;

        // Remove old dialog
        const oldDialog = document.getElementById('webAddDialog');
        if (oldDialog) oldDialog.remove();

        // Insert new dialog
        document.body.insertAdjacentHTML('beforeend', dialogHTML);

        // Bind button events
        this.bindAddDialogEvents(type);
    },

    bindAddDialogEvents(type) {
        const dialog = document.getElementById('webAddDialog');
        if (!dialog) return;

        // Event delegation for all button clicks
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

            // Restore BrowserView
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

        const basePosition = type === 'LLM' ? 0 : 1000;
        const data = type === 'LLM' ? this.llmData : this.toolData;
        const maxPosition = (data || []).reduce((max, item) => {
            const p = item && item.position !== null && item.position !== undefined ? Number(item.position) : NaN;
            if (!Number.isFinite(p)) return max;
            return Math.max(max, p);
        }, basePosition - 1);
        const position = Math.max(maxPosition, basePosition - 1) + 1;

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
                filename,
                position
            });

            if (response && response.success) {
                console.log('[WebSidebar] Item added successfully');

                // Reload data
                await this.loadData();

                // Refresh sidebar
                const sidebar = document.getElementById('sidebar-web');
                if (sidebar) {
                    sidebar.innerHTML = this.render();
                }

                // Close dialog (BrowserView will be restored automatically)
                this.closeAddDialog();

                // Show success message
                alert(`${type} service added successfully`);
            }
        } catch (error) {
            console.error('[WebSidebar] Failed to add item:', error);
            alert('Failed to add item. Please try again.');
        }
    }
};

export default WebSidebar;
