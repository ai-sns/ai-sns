// ModelManagementPage.js - LLM Model Configuration Management
const ModelManagementPage = {
    resolve(urlOrPath) {
        try {
            if (typeof window !== 'undefined' && typeof window.resolveAgentServerUrl === 'function') {
                return window.resolveAgentServerUrl(urlOrPath);
            }
        } catch (e) {
        }
        return urlOrPath;
    },
    notify(message, type = 'info') {
        const msg = String(message ?? '');
        const t = String(type || 'info');
        try {
            if (typeof window !== 'undefined' && typeof window.showNotification === 'function') {
                window.showNotification(msg, t);
                return;
            }
        } catch (e) {
        }
        try {
            if (typeof window !== 'undefined' && window.Toast && typeof window.Toast.show === 'function') {
                window.Toast.show(msg, t, 4000);
                return;
            }
        } catch (e) {
        }
        try {
            alert(msg);
        } catch (e) {
        }
    },
    showTestResultDialog(payload, rawResponse = null) {
        const data = payload && typeof payload === 'object' ? payload : {};
        const status = String(data.status || 'error');
        const latency = data.latency_ms != null ? String(data.latency_ms) : '';
        const reply = data.reply != null ? String(data.reply) : '';
        const baseUrl = data.base_url != null ? String(data.base_url) : '';
        const model = data.model != null ? String(data.model) : '';

        const overlayId = 'llmTestConnectionResultModal';
        try {
            const existing = document.getElementById(overlayId);
            if (existing) existing.remove();
        } catch (e) {
        }

        const safeReply = String(reply || '').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        const contentHtml = `
            <div class="llm-test-result" style="display:flex; flex-direction:column; gap:10px;">
                <div><b>Status:</b> ${status}</div>
                ${model ? `<div><b>Model:</b> ${model}</div>` : ''}
                ${baseUrl ? `<div><b>Base URL:</b> ${baseUrl}</div>` : ''}
                ${latency ? `<div><b>Latency:</b> ${latency} ms</div>` : ''}
                ${safeReply ? `<div><b>Reply:</b><div class="llm-test-result__reply" style="margin-top:6px; padding:10px; border:1px solid var(--border-color); border-radius:8px; white-space:pre-wrap;">${safeReply}</div></div>` : ''}
            </div>
        `;

        const html = `
            <div class="modal-overlay modal-overlay--top" id="${overlayId}" style="z-index: 1000010;">
                <div class="modal-dialog" style="max-width: 720px;">
                    <div class="modal-header">
                        <h3>Test connection</h3>
                        <button class="modal-close" type="button" data-close="1">×</button>
                    </div>
                    <div class="modal-body">
                        ${contentHtml}
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-primary" type="button" data-close="1">OK</button>
                    </div>
                </div>
            </div>
        `;
        try {
            document.body.insertAdjacentHTML('beforeend', html);
            const el = document.getElementById(overlayId);
            if (el) {
                el.addEventListener('click', (e) => {
                    const t = e.target;
                    if (!t) return;
                    if (t.id === overlayId) {
                        try { el.remove(); } catch (e) {}
                        return;
                    }
                    if (t.closest && t.closest('[data-close]')) {
                        try { el.remove(); } catch (e) {}
                    }
                });
                return;
            }
        } catch (e) {
        }

        const fallbackMsg = safeReply
            ? `Reply: ${safeReply}${latency ? `\nLatency: ${latency} ms` : ''}`
            : (rawResponse && rawResponse.error ? String(rawResponse.error) : 'No response');
        this.notify(fallbackMsg, status === 'success' ? 'success' : 'error');
    },
    state: {
        models: [],
        selectedModel: null,
        editMode: false,
        providers: [
            { value: 'openai', label: 'OpenAI' },
            { value: 'claude', label: 'Claude (Anthropic)' },
            { value: 'gemini', label: 'Gemini (Google)' },
            { value: 'custom', label: 'OpenAI-like (Custom)' }
        ]
    },

    async init() {
        await this.loadModels();
        this.bindEvents();
        this.bindSidebarClickHandler();
    },

    async loadModels() {
        try {
            const response = await fetch(this.resolve('/api/agent/llm-configs'));
            const result = await response.json();
            if (result.success) {
                this.state.models = result.data;
                this.render();
            }
        } catch (error) {
            console.error('Failed to load models:', error);
            window.showNotification?.('Failed to load model configurations', 'error');
        }
    },

    render() {
        const mainContent = document.getElementById('mainContent');
        if (!mainContent) return;

        // Create or get the model management page container
        let pageContainer = mainContent.querySelector('.model-management-page-container');

        if (!pageContainer) {
            // Create the page container for the first time
            pageContainer = document.createElement('div');
            pageContainer.className = 'model-management-page-container page-container';
            mainContent.appendChild(pageContainer);
        }

        // Hide other pages and only show the model management page
        mainContent.querySelectorAll('.page-container').forEach(page => {
            page.style.display = 'none';
        });
        pageContainer.style.display = 'block';

        // Render content
        pageContainer.innerHTML = `
            <div class="model-management-page">
                ${this.renderHeader()}
                ${this.renderModelsList()}
            </div>
        `;

        this.bindPageEvents();
    },

    renderHeader() {
        return `
            <div class="page-header">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <h2>LLM</h2>
                </div>
                <div class="header-actions">
                    <button class="btn btn-primary" id="addModelBtn">
                        <span>+</span> New LLM
                    </button>
                </div>
            </div>
        `;
    },

    renderModelsList() {
        if (!this.state.models.length) {
            return '<div class="empty-state">No model configurations yet. Click "New LLM" to get started.</div>';
        }

        const modelsHtml = this.state.models.map(model => this.renderModelCard(model)).join('');

        return `
            <div class="models-container">
                <div class="models-list">
                    ${modelsHtml}
                </div>
            </div>
        `;
    },

    renderModelCard(model) {
        const providerLabel = this.state.providers.find(p => p.value === model.provider)?.label || model.provider;
        const modelId = model.model_name || 'N/A';
        const apiEndpoint = model.api_endpoint || 'N/A';
        const hasModelId = !!(model.model_name && String(model.model_name).trim());
        const hasApiEndpoint = !!(model.api_endpoint && String(model.api_endpoint).trim());

        return `
            <div class="model-card" data-id="${model.config_id}">
                <div class="mgmt-card__top">
                    <div class="mgmt-card__top-left">
                        <div class="mgmt-card__icon" aria-hidden="true">
                            <span class="material-icons-round">hub</span>
                        </div>
                        <div class="mgmt-card__meta">
                            <div class="mgmt-card__title-row">
                                <h3 class="model-name">${model.name}</h3>
                            </div>
                            <div class="mgmt-card__badges">
                                <span class="mgmt-pill mgmt-pill--provider">${String(providerLabel).toUpperCase()}</span>
                                ${model.is_default ? '<span class="mgmt-pill mgmt-pill--default">DEFAULT</span>' : ''}
                            </div>
                        </div>
                    </div>
                    <div class="model-actions mgmt-card__actions">
                        <button class="btn-icon" type="button" data-action="test" data-id="${model.config_id}" title="Test connection">
                            <span class="material-icons-round">play_arrow</span>
                        </button>
                        <button class="btn-icon" type="button" data-action="edit" data-id="${model.config_id}" title="Edit">
                            <span class="material-icons-round">edit</span>
                        </button>
                        <button class="btn-icon" type="button" data-action="delete" data-id="${model.config_id}" title="Delete">
                            <span class="material-icons-round">delete</span>
                        </button>
                    </div>
                </div>
                <div class="model-card-body mgmt-card__body">
                    <div class="mgmt-field">
                        <div class="mgmt-field__label">MODEL ID</div>
                        <div class="mgmt-field__value ${hasModelId ? '' : 'is-empty'}">${modelId}</div>
                    </div>
                    <div class="mgmt-field">
                        <div class="mgmt-field__label">API ENDPOINT</div>
                        <div class="mgmt-field__value ${hasApiEndpoint ? '' : 'is-empty'}">${apiEndpoint}</div>
                    </div>
                    ${model.description ? `<div class="model-description">${model.description}</div>` : ''}
                </div>
            </div>
        `;
    },

    bindPageEvents() {
        document.getElementById('addModelBtn')?.addEventListener('click', () => {
            this.showModelDialog();
        });

        const container = document.querySelector('.model-management-page-container');
        if (container && !container.__modelActionsBound) {
            container.__modelActionsBound = true;
            container.addEventListener('click', (e) => {
                const btn = e.target && e.target.closest ? e.target.closest('[data-action]') : null;
                if (!btn) return;
                const action = btn.dataset.action;
                const id = btn.dataset.id;
                if (!action || !id) return;

                switch (action) {
                    case 'edit':
                        this.editModel(id);
                        break;
                    case 'delete':
                        this.deleteModel(id);
                        break;
                    case 'test':
                        this.testConnection(id, null, btn);
                        break;
                }
            });
        }
    },

    showModelDialog(model = null) {
        const isEdit = !!model;
        const title = isEdit ? 'Edit Model' : 'Add Model';

        const modalHtml = `
            <div class="modal-overlay" id="modelModal">
                <div class="modal-dialog" style="max-width: 600px;">
                    <div class="modal-header">
                        <h3>${title}</h3>
                        <button class="modal-close" id="closeModal">×</button>
                    </div>
                    <div class="modal-body">
                        ${this.renderModelForm(model)}
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-secondary" id="cancelBtn">Cancel</button>
                        <button class="btn btn-primary" id="saveBtn">Save</button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);

        const modal = document.getElementById('modelModal');

        // Tab switching
        modal.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const tab = btn.dataset.tab;
                modal.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                modal.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                btn.classList.add('active');
                modal.querySelector(`[data-tab-content="${tab}"]`).classList.add('active');
            });
        });

        // Modal close
        modal.querySelector('#closeModal').addEventListener('click', () => modal.remove());
        modal.querySelector('#cancelBtn').addEventListener('click', () => modal.remove());

        // Save button
        modal.querySelector('#saveBtn').addEventListener('click', async () => {
            const formData = this.getFormData(modal);
            const success = isEdit
                ? await this.updateModel(model.config_id, formData)
                : await this.createModel(formData);

            if (success) {
                modal.remove();
                await this.loadModels();
            }
        });

        // Test connection button
        modal.querySelector('.test-connection-btn')?.addEventListener('click', async () => {
            const formData = this.getFormData(modal);
            const btn = modal.querySelector('.test-connection-btn');
            await this.testConnection(null, {
                api_endpoint: formData.api_endpoint,
                api_key: formData.api_key,
                model_name: formData.model_name,
                provider: formData.provider
            }, btn);
        });
    },

    renderModelForm(model = null) {
        return `
            <form id="modelForm" class="model-form">
                <div class="form-tabs">
                    <button type="button" class="tab-btn active" data-tab="basic">Basic</button>
                </div>

                <!-- Basic Config -->
                <div class="tab-content active" data-tab-content="basic">
                    <div class="dialog-section">
                        <h4>Basic</h4>
                        <div class="form-group">
                            <label>Display Name *</label>
                            <input type="text" name="name" class="form-control"
                                   value="${model?.name || ''}" required placeholder="e.g. GPT-4o Production">
                        </div>

                        <div class="form-group">
                            <label>Provider *</label>
                            <select name="provider" class="form-control" required>
                                ${this.state.providers.map(p => `
                                    <option value="${p.value}" ${model?.provider === p.value ? 'selected' : ''}>
                                        ${p.label}
                                    </option>
                                `).join('')}
                            </select>
                        </div>

                        <div class="form-group">
                            <label>Model ID *</label>
                            <input type="text" name="model_name" class="form-control"
                                   value="${model?.model_name || ''}"
                                   placeholder="e.g. gpt-4o, claude-3-5-sonnet-20240620" required>
                        </div>
                        
                        <div class="form-group">
                            <label>Description</label>
                            <textarea name="description" class="form-control" rows="2" placeholder="Optional: describe the model's purpose or characteristics">${model?.description || ''}</textarea>
                        </div>
                    </div>

                    <div class="dialog-section">
                        <h4>Connection</h4>
                        <div class="form-group">
                            <label>API Endpoint (Base URL) *</label>
                            <input type="url" name="api_endpoint" class="form-control"
                                   value="${model?.api_endpoint || ''}"
                                   placeholder="e.g. https://api.openai.com/v1/chat/completions" required>
                        </div>

                        <div class="form-group">
                            <label>API Key *</label>
                            <div class="input-with-buttons">
                                <input type="password" name="api_key" class="form-control"
                                       value="${model?.api_key || ''}"
                                       placeholder="sk-..." required>
                                <button type="button" class="btn btn-secondary test-connection-btn">
                                    <span class="material-icons-round" aria-hidden="true">play_arrow</span>
                                    <span>Test connection</span>
                                </button>
                            </div>
                        </div>
                    </div>

                    <div class="dialog-section">
                        <h4>Status</h4>
                        <div class="checkbox-group">
                            <label class="checkbox-label">
                                <input type="checkbox" name="is_default" ${model?.is_default ? 'checked' : ''}>
                                Set as default
                            </label>
                        </div>
                    </div>
                </div>
            </form>
        `;
    },

    getFormData(modal) {
        const form = modal.querySelector('#modelForm');
        const formData = new FormData(form);
        const data = {};

        for (const [key, value] of formData.entries()) {
            if (key === 'is_default') {
                data[key] = form.querySelector(`[name="${key}"]`).checked;
            } else {
                data[key] = value;
            }
        }

        // is_active is no longer user-editable; configurations are always enabled.
        data.is_active = true;

        return data;
    },

    async createModel(data) {
        try {
            const response = await fetch(this.resolve('/api/agent/llm-configs'), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            const result = await response.json();

            if (result.success) {
                window.showNotification?.('Model created', 'success');
                // Notify main UI to refresh model options
                if (window.agentHandlers && window.agentHandlers.loadModelOptions) {
                    window.agentHandlers.loadModelOptions();
                }
                return true;
            } else {
                window.showNotification?.('Create failed: ' + (result.error || 'Unknown error'), 'error');
                return false;
            }
        } catch (error) {
            window.showNotification?.('Create failed: ' + error.message, 'error');
            return false;
        }
    },

    async updateModel(configId, data) {
        try {
            const response = await fetch(this.resolve(`/api/agent/llm-configs/${configId}`), {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            const result = await response.json();

            if (result.success) {
                window.showNotification?.('Model updated', 'success');
                // Notify main UI to refresh model options
                if (window.agentHandlers && window.agentHandlers.loadModelOptions) {
                    window.agentHandlers.loadModelOptions();
                }
                return true;
            } else {
                window.showNotification?.('Update failed: ' + (result.error || 'Unknown error'), 'error');
                return false;
            }
        } catch (error) {
            window.showNotification?.('Update failed: ' + error.message, 'error');
            return false;
        }
    },

    editModel(configId) {
        const model = this.state.models.find(m => m.config_id === configId);
        if (model) {
            this.showModelDialog(model);
        }
    },

    async deleteModel(configId) {
        const confirmed = await (async () => {
            try {
                if (window.Toast && typeof window.Toast.confirm === 'function') {
                    return await window.Toast.confirm('Delete this model configuration?', {
                        title: 'Delete Model',
                        confirmText: 'Delete',
                        cancelText: 'Cancel',
                        type: 'warning'
                    });
                }

                if (window.Modal && typeof window.Modal.show === 'function') {
                    return await new Promise((resolve) => {
                        window.Modal.show({
                            title: 'Delete Model',
                            content: '<p>Delete this model configuration?</p>',
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
            } catch (e) {
                console.error('Failed to show delete model confirmation dialog:', e);
            }
            return false;
        })();

        if (!confirmed) return;

        try {
            const response = await fetch(this.resolve(`/api/agent/llm-configs/${configId}`), {
                method: 'DELETE'
            });
            const result = await response.json();

            if (result.success) {
                window.showNotification?.('Model deleted', 'success');
                await this.loadModels();
                // Notify main UI to refresh model options
                if (window.agentHandlers && window.agentHandlers.loadModelOptions) {
                    window.agentHandlers.loadModelOptions();
                }
            } else {
                window.showNotification?.('Delete failed', 'error');
            }
        } catch (error) {
            window.showNotification?.('Delete failed: ' + error.message, 'error');
        }
    },

    async testConnection(configId, data = null, btnEl = null) {
        let payload = data;
        if (!payload) {
            const model = this.state.models.find(m => m.config_id === configId);
            if (!model) return;
            payload = {
                api_endpoint: model.api_endpoint,
                api_key: model.api_key,
                model_name: model.model_name,
                provider: model.provider
            };
        }

        try {
            if (btnEl) {
                try { btnEl.disabled = true; } catch (e) {}
            }
            this.notify('Testing connection...', 'info');
            const response = await fetch(this.resolve('/api/agent/llm-configs/test'), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const result = await response.json();
            if (result && result.success && result.data && String(result.data.status || '').toLowerCase() === 'success') {
                this.notify('Connection test succeeded', 'success');
                this.showTestResultDialog(result.data, result);
                return;
            }
            const errMsg = (result && (result.error || (result.data && result.data.message))) ? String(result.error || result.data.message) : 'Unknown error';
            this.notify('Connection test failed: ' + errMsg, 'error');
        } catch (error) {
            this.notify('Connection test failed: ' + error.message, 'error');
        } finally {
            if (btnEl) {
                try { btnEl.disabled = false; } catch (e) {}
            }
        }
    },

    async exportModels() {
        try {
            const response = await fetch(this.resolve('/api/agent/llm-configs/export/all'));
            const result = await response.json();

            if (result.success) {
                const dataStr = JSON.stringify(result.data, null, 2);
                const blob = new Blob([dataStr], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `llm-configs-${Date.now()}.json`;
                a.click();
                URL.revokeObjectURL(url);

                window.showNotification?.('Exported successfully', 'success');
            }
        } catch (error) {
            window.showNotification?.('Export failed: ' + error.message, 'error');
        }
    },

    showImportDialog() {
        const modalHtml = `
            <div class="modal-overlay" id="importModal">
                <div class="modal-dialog">
                    <div class="modal-header">
                        <h3>Import model configurations</h3>
                        <button class="modal-close" id="closeImportModal">×</button>
                    </div>
                    <div class="modal-body">
                        <div class="import-dialog">
                            <p>Select a configuration file to import (JSON)</p>
                            <input type="file" id="importFileInput" accept=".json">
                            <div class="import-preview" id="importPreview"></div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-secondary" id="cancelImportBtn">Cancel</button>
                        <button class="btn btn-primary" id="confirmImportBtn">Confirm</button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);

        const modal = document.getElementById('importModal');

        // File preview
        modal.querySelector('#importFileInput').addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (file) {
                try {
                    const text = await file.text();
                    const configs = JSON.parse(text);
                    const preview = modal.querySelector('#importPreview');
                    preview.innerHTML = `<p>Will import ${configs.length} configuration(s)</p>`;
                } catch (error) {
                    const preview = modal.querySelector('#importPreview');
                    preview.innerHTML = `<p class="error">Invalid file format</p>`;
                }
            }
        });

        // Modal close
        modal.querySelector('#closeImportModal').addEventListener('click', () => modal.remove());
        modal.querySelector('#cancelImportBtn').addEventListener('click', () => modal.remove());

        // Confirm import
        modal.querySelector('#confirmImportBtn').addEventListener('click', async () => {
            const file = modal.querySelector('#importFileInput').files[0];
            if (!file) {
                window.showNotification?.('Please select a file', 'warning');
                return;
            }

            try {
                const text = await file.text();
                const configs = JSON.parse(text);

                const response = await fetch(this.resolve('/api/agent/llm-configs/import'), {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(configs)
                });
                const result = await response.json();

                if (result.success) {
                    window.showNotification?.(`Imported ${result.data.created} configuration(s)`, 'success');
                    modal.remove();
                    await this.loadModels();
                } else {
                    window.showNotification?.('Import failed', 'error');
                }
            } catch (error) {
                window.showNotification?.('Import failed: ' + error.message, 'error');
            }
        });
    },

    bindEvents() {
        // This is called once on init
    },

    /**
     * Bind sidebar click handler - go back when clicking agent or chat list
     */
    bindSidebarClickHandler() {
        // Use event delegation to listen for sidebar clicks
        document.addEventListener('click', (e) => {
            // Check whether an agent item or chat list item was clicked
            const agentItem = e.target.closest('.agent-item[data-agent-id]');
            const chatItem = e.target.closest('.tree-item[data-conversation-id]');

            if (agentItem || chatItem) {
                // If the management page is open, close it
                const mgmtPage = document.querySelector('.model-management-page-container');
                if (mgmtPage && mgmtPage.style.display !== 'none') {
                    this.destroy();
                }
            }
        }, true); // Use capture phase to ensure it runs first
    },

    /**
     * Destroy page - called when switching to other pages
     */
    destroy() {
        const mainContent = document.getElementById('mainContent');
        if (!mainContent) return;

        // Hide model management page
        const pageContainer = mainContent.querySelector('.model-management-page-container');
        if (pageContainer) {
            pageContainer.style.display = 'none';
        }

        // Show Agent main page
        const agentPage = mainContent.querySelector('#page-agent, .agent-page-layout');
        if (agentPage) {
            agentPage.style.display = '';
        }
    }
};

export default ModelManagementPage;
