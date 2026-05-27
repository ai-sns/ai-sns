/**
 * Tools Edit Dialog - tool edit dialog
 * Supports creating and editing Plugin, MCP, Function, Skill
 */

class ToolsEditDialog {
    constructor() {
        const normalizeHttpBaseUrl = (raw) => {
            const v = String(raw || '').trim();
            if (!v) return '';
            const withScheme = /^https?:\/\//i.test(v) ? v : `http://${v}`;
            return withScheme.endsWith('/') ? withScheme.slice(0, -1) : withScheme;
        };

        const base = normalizeHttpBaseUrl(
            (window.appConfig && window.appConfig.agent_server)
            || (window.api && window.api.baseUrl)
            || ''
        );

        this.apiBaseUrl = base ? `${base}/api/tools` : '/api/tools';
        this.currentTool = null;
        this.currentCategory = null;
        this.onSaveCallback = null;
    }

    /**
     * Show dialog
     * @param {string} category - tools-plugin/mcp/function/computer-use
     * @param {object|null} tool - tool to edit; null means create new
     * @param {function} onSave - callback after successful save
     */
    show(category, tool = null, onSave = null) {
        this.currentCategory = category;
        this.currentTool = tool;
        this.onSaveCallback = onSave;

        const isEdit = tool !== null;
        const title = isEdit ? `Edit ${this.getCategoryName(category)}` : `Add ${this.getCategoryName(category)}`;

        const dialogHTML = `
            <div class="modal-overlay" id="toolEditDialog">
                <div class="modal-dialog tool-edit-dialog">
                    <div class="modal-header">
                        <h2>${title}</h2>
                        <button class="modal-close" onclick="toolsEditDialog.close()">
                            <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="18" y1="6" x2="6" y2="18"/>
                                <line x1="6" y1="6" x2="18" y2="18"/>
                            </svg>
                        </button>
                    </div>
                    <div class="modal-body">
                        <form id="toolEditForm" class="tool-edit-form">
                            ${this.renderFormFields(category, tool)}
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" onclick="toolsEditDialog.close()">
                            Cancel
                        </button>
                        <button type="button" class="btn btn-primary" onclick="toolsEditDialog.save()">
                            ${isEdit ? 'Save' : 'Create'}
                        </button>
                    </div>
                </div>
            </div>
        `;

        // Remove existing dialog
        const existing = document.getElementById('toolEditDialog');
        if (existing) {
            existing.remove();
        }

        // Insert new dialog
        document.body.insertAdjacentHTML('beforeend', dialogHTML);

        // If edit mode, populate data
        if (isEdit) {
            this.fillFormData(tool);
        }

        // Wire up MCP-specific behaviors (Load Tools button)
        if (category === 'mcp') {
            this.bindLoadMcpToolsButton();
        }
    }

    /**
     * Bind the "Load Tools" button next to the Tools textarea in the MCP form.
     * - In edit mode (existing mcp_id): probes the MCP server via the same
     *   /api/tools/mcp/{id}/execute endpoint that powers the MCP List "Test"
     *   button, then writes the comma-joined tool name list into the textarea.
     * - In create mode (no mcp_id yet): button is disabled and a hint is shown
     *   asking the user to save first; the textarea remains manually editable.
     */
    bindLoadMcpToolsButton() {
        const btn = document.getElementById('loadMcpToolsBtn');
        const hint = document.getElementById('loadMcpToolsHint');
        const detailEl = document.getElementById('mcpDetail');
        if (!btn || !detailEl) return;

        const mcpId = this.currentTool && this.currentTool.mcp_id;
        if (!mcpId) {
            btn.disabled = true;
            if (hint) {
                hint.textContent = 'Save the MCP first, then reopen Edit to load tools.';
            }
            return;
        }

        btn.addEventListener('click', async () => {
            const originalText = btn.innerHTML;
            btn.innerHTML = '<span class="spinner-small"></span> Loading...';
            btn.disabled = true;
            if (hint) hint.textContent = '';

            try {
                const response = await fetch(`${this.apiBaseUrl}/mcp/${encodeURIComponent(mcpId)}/execute`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({})
                });
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                const tools = this.extractMcpToolNames(data);
                if (!tools.length) {
                    if (hint) hint.textContent = 'No tools reported by the MCP server.';
                    return;
                }
                detailEl.value = tools.join(', ');
                if (hint) hint.textContent = `Loaded ${tools.length} tool(s).`;
            } catch (error) {
                console.error('Load MCP tools error:', error);
                this.showMessage('Failed to load tools: ' + error.message, 'error');
                if (hint) hint.textContent = 'Failed to load tools.';
            } finally {
                btn.innerHTML = originalText;
                btn.disabled = false;
            }
        });
    }

    /**
     * Extract tool names from the /mcp/{id}/execute response.
     * Expected shape: { success, result: { connection: { tools: [{ name, description }, ...] } } }
     */
    extractMcpToolNames(data) {
        try {
            const result = data && data.result ? data.result : null;
            const connection = result && result.connection ? result.connection : null;
            const tools = connection && Array.isArray(connection.tools) ? connection.tools : [];
            return tools
                .map(t => (t && t.name ? String(t.name).trim() : ''))
                .filter(Boolean);
        } catch (e) {
            return [];
        }
    }

    renderFormFields(category, tool) {
        const baseFields = `
            <div class="tool-edit-section">
                <h4>Basic</h4>
                <div class="form-group">
                    <label for="toolName">Name *</label>
                    <input type="text" id="toolName" name="name" class="form-control" required placeholder="Enter tool name">
                </div>
                <div class="form-group">
                    <label for="toolDescription">Description</label>
                    <textarea id="toolDescription" name="description" class="form-control" rows="2" placeholder="Enter tool description"></textarea>
                </div>
                <div class="form-group">
                    <label for="toolInstruction">Instructions</label>
                    <textarea id="toolInstruction" name="instruction" class="form-control" rows="3" placeholder="Describe how the AI should use this tool"></textarea>
                </div>
            </div>
        `;

        let specificFields = '';
        let configTitle = 'Configuration';

        switch(category) {
            case 'tools-plugin':
                configTitle = 'Plugin Configuration';
                specificFields = `
                    <div class="form-group">
                        <label for="pluginType">Plugin Type</label>
                        <select id="pluginType" name="used_in_sns" class="form-control">
                            <option value="false">Agent</option>
                            <option value="true">SNS</option>
                        </select>
                    </div>
                `;
                break;

            case 'mcp':
                configTitle = 'MCP Server Configuration';
                specificFields = `
                    <div class="form-group">
                        <label for="mcpType">MCP Type</label>
                        <select id="mcpType" name="mcp_type" class="form-control">
                            <option value="stdio">stdio</option>
                            <option value="sse">SSE</option>
                            <option value="streamable-http">Streamable HTTP</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="filePath">Server File Path / Endpoint URL *</label>
                        <input type="text" id="filePath" name="file_path" class="form-control" required placeholder="/path/to/mcp_server.py or http://127.0.0.1:3088/sse or http://127.0.0.1:3089/mcp">
                        <small class="form-text">For stdio use a local script path or a command (e.g. npx); for SSE/Streamable HTTP use an HTTP URL.</small>
                    </div>
                    <div class="form-group">
                        <label for="parameter">Launch Parameters (JSON)</label>
                        <textarea id="parameter" name="parameter" class="form-control code-editor" rows="4" placeholder='{"args": ["-y", "@org/pkg"], "env": {"KEY": "VALUE"}}'></textarea>
                    </div>
                    <div class="form-group">
                        <label for="requirement">Requirements</label>
                        <textarea id="requirement" name="requirement" class="form-control" rows="2" placeholder="mcp==1.0.0&#10;other-package==2.0.0"></textarea>
                    </div>
                    <div class="form-group">
                        <label for="mcpDetail">Tools</label>
                        <textarea id="mcpDetail" name="detail" class="form-control" rows="2" placeholder="MCP tool list (comma-separated). Click 'Load Tools' to auto-fill."></textarea>
                        <div style="margin-top: 8px; display: flex; align-items: center; gap: 8px;">
                            <button type="button" id="loadMcpToolsBtn" class="btn btn-secondary">Load Tools</button>
                            <small id="loadMcpToolsHint" class="form-text" style="margin: 0;"></small>
                        </div>
                    </div>
                `;
                break;

            case 'function':
                configTitle = 'Function Configuration';
                specificFields = `
                    <div class="form-group">
                        <label for="functionType">Language</label>
                        <select id="functionType" name="function_type" class="form-control">
                            <option value="python">Python</option>
                            <option value="javascript">JavaScript</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="filePath">Script File Path *</label>
                        <input type="text" id="filePath" name="file_path" class="form-control" required placeholder="/path/to/function.py">
                        <small class="form-text">Path to the function script file</small>
                    </div>
                    <div class="form-group">
                        <label for="parameter">Function Arguments (JSON)</label>
                        <textarea id="parameter" name="parameter" class="form-control code-editor" rows="5" placeholder='{"param1": {"type": "string", "description": "Parameter description"}}'></textarea>
                        <small class="form-text">Define parameters accepted by the function</small>
                    </div>
                `;
                break;

            case 'computer-use':
                configTitle = 'Skill Configuration';
                specificFields = `
                    <div class="form-group">
                        <label for="skillType">Skill Type</label>
                        <select id="skillType" name="skill_type" class="form-control">
                            <option value="screenshot">Screenshot</option>
                            <option value="mouse_click">Mouse Click</option>
                            <option value="keyboard_input">Keyboard Input</option>
                            <option value="custom">Custom Script</option>
                        </select>
                    </div>
                    <div class="form-group" id="filePathGroup">
                        <label for="filePath">Script File Path</label>
                        <input type="text" id="filePath" name="file_path" class="form-control" placeholder="/path/to/skill.py">
                        <small class="form-text">Custom script path (only required for Custom)</small>
                    </div>
                    <div class="form-group">
                        <label for="parameter">Execution Parameters (JSON)</label>
                        <textarea id="parameter" name="parameter" class="form-control code-editor" rows="5" placeholder='{"x": 100, "y": 200}'></textarea>
                        <small class="form-text">Provide parameters based on the selected skill type</small>
                    </div>
                `;
                break;
        }

        const configSection = `
            <div class="tool-edit-section">
                <h4>${configTitle}</h4>
                ${specificFields}
            </div>
        `;

        const confirmField = `
            <div class="tool-edit-section">
                <h4>Safety</h4>
                <div class="form-group">
                    <div class="form-check">
                        <input type="checkbox" id="confirmNeeded" name="confirm_needed" class="form-check-input" checked>
                        <label for="confirmNeeded" class="form-check-label">
                            Confirmation required before execution <small class="text-muted">(recommended for safety)</small>
                        </label>
                    </div>
                </div>
            </div>
        `;

        // Plugin editor is intentionally minimal.
        if (category === 'tools-plugin') {
            return baseFields + configSection;
        }

        return baseFields + configSection + confirmField;
    }

    fillFormData(tool) {
        // Fill form data
        Object.keys(tool).forEach(key => {
            const input = document.querySelector(`[name="${key}"]`);
            if (input) {
                if (input.type === 'checkbox') {
                    input.checked = tool[key];
                } else {
                    if (key === 'used_in_sns') {
                        input.value = tool[key] ? 'true' : 'false';
                    } else {
                        input.value = tool[key] || '';
                    }
                }
            }
        });
    }

    async save() {
        const form = document.getElementById('toolEditForm');
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        // Collect form data
        const formData = new FormData(form);
        const data = {};

        formData.forEach((value, key) => {
            if (key === 'confirm_needed') {
                data[key] = document.getElementById('confirmNeeded').checked;
            } else if (key === 'used_in_sns') {
                data[key] = String(value).toLowerCase() === 'true';
            } else {
                data[key] = value;
            }
        });

        try {
            const isEdit = this.currentTool !== null;
            let endpoint, method;

            // Determine endpoint by category
            switch(this.currentCategory) {
                case 'tools-plugin':
                    endpoint = isEdit ? `/plugins/${this.currentTool.plugin_id}` : '/plugins';
                    break;
                case 'mcp':
                    endpoint = isEdit ? `/mcp/${this.currentTool.mcp_id}` : '/mcp';
                    break;
                case 'function':
                    endpoint = isEdit ? `/functions/${this.currentTool.function_id}` : '/functions';
                    break;
                case 'computer-use':
                    endpoint = isEdit ? `/skills/${this.currentTool.skill_id}` : '/skills';
                    break;
                default:
                    throw new Error(`Unknown tool category: ${this.currentCategory}`);
            }

            method = isEdit ? 'PUT' : 'POST';

            // Send request
            const response = await fetch(`${this.apiBaseUrl}${endpoint}`, {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            // Show success message
            this.showMessage(isEdit ? 'Saved successfully' : 'Created successfully', 'success');

            // Close dialog
            this.close();

            // Invoke callback
            if (this.onSaveCallback) {
                this.onSaveCallback(result);
            }
        } catch (error) {
            console.error('Save error:', error);
            this.showMessage('Save failed: ' + error.message, 'error');
        }
    }

    close() {
        const dialog = document.getElementById('toolEditDialog');
        if (dialog) {
            dialog.remove();
        }
    }

    getCategoryName(category) {
        const names = {
            'tools-plugin': 'Plugin',
            'mcp': 'MCP',
            'function': 'Function',
            'computer-use': 'Computer Use'
        };
        return names[category] || category;
    }

    showMessage(message, type = 'info') {
        console.log(`[${type}] ${message}`);

        try {
            if (typeof window !== 'undefined' && window.Toast && typeof window.Toast.show === 'function') {
                window.Toast.show(String(message), String(type || 'info'), 3000);
                return;
            }
        } catch (e) {
        }

        // Create temporary toast
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
            z-index: 2000000;
            animation: slideIn 0.3s ease-out;
        `;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}

// Create global instance
window.toolsEditDialog = new ToolsEditDialog();

export default ToolsEditDialog;
