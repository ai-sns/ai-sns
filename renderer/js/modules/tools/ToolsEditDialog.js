/**
 * Tools Edit Dialog - 工具编辑对话框
 * 支持 Plugin, MCP, Function, Skill 的创建和编辑
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
     * 显示对话框
     * @param {string} category - tools-plugin/mcp/function/computer-use
     * @param {object|null} tool - 要编辑的工具，null表示新建
     * @param {function} onSave - 保存成功后的回调
     */
    show(category, tool = null, onSave = null) {
        this.currentCategory = category;
        this.currentTool = tool;
        this.onSaveCallback = onSave;

        const isEdit = tool !== null;
        const title = isEdit ? `编辑 ${this.getCategoryName(category)}` : `添加 ${this.getCategoryName(category)}`;

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
                            取消
                        </button>
                        <button type="button" class="btn btn-primary" onclick="toolsEditDialog.save()">
                            ${isEdit ? '保存' : '创建'}
                        </button>
                    </div>
                </div>
            </div>
        `;

        // 移除已存在的对话框
        const existing = document.getElementById('toolEditDialog');
        if (existing) {
            existing.remove();
        }

        // 添加新对话框
        document.body.insertAdjacentHTML('beforeend', dialogHTML);

        // 如果是编辑模式，填充数据
        if (isEdit) {
            this.fillFormData(tool);
        }
    }

    renderFormFields(category, tool) {
        const baseFields = `
            <div class="form-group">
                <label for="toolName">名称 *</label>
                <input type="text" id="toolName" name="name" class="form-control" required placeholder="输入工具名称">
            </div>
            <div class="form-group">
                <label for="toolDescription">描述</label>
                <textarea id="toolDescription" name="description" class="form-control" rows="3" placeholder="输入工具描述"></textarea>
            </div>
            <div class="form-group">
                <label for="toolInstruction">使用说明</label>
                <textarea id="toolInstruction" name="instruction" class="form-control" rows="4" placeholder="输入使用说明，告诉AI如何使用这个工具"></textarea>
            </div>
        `;

        let specificFields = '';

        switch(category) {
            case 'tools-plugin':
                specificFields = `
                    <div class="form-group">
                        <label for="pluginType">插件类型</label>
                        <select id="pluginType" name="plugin_type" class="form-control">
                            <option value="tool">通用工具</option>
                            <option value="api">API接口</option>
                            <option value="data">数据处理</option>
                            <option value="ai">AI模型</option>
                            <option value="custom">自定义</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="filePath">文件路径</label>
                        <input type="text" id="filePath" name="file_path" class="form-control" placeholder="/path/to/plugin.py">
                        <small class="form-text">Python或JavaScript文件路径</small>
                    </div>
                    <div class="form-group">
                        <label for="runtimeMain">运行代码 (Python)</label>
                        <textarea id="runtimeMain" name="runtime_main" class="form-control code-editor" rows="10" placeholder="import sys&#10;import json&#10;&#10;# 从stdin读取参数&#10;params = json.loads(sys.stdin.read())&#10;&#10;# 处理逻辑&#10;result = {'output': 'Hello'}&#10;&#10;# 输出结果&#10;print(json.dumps(result))"></textarea>
                        <small class="form-text">留空则使用文件路径执行</small>
                    </div>
                    <div class="form-group">
                        <label for="parameter">参数配置 (JSON)</label>
                        <textarea id="parameter" name="parameter" class="form-control code-editor" rows="5" placeholder='{"arg1": "value1", "arg2": "value2"}'></textarea>
                    </div>
                `;
                break;

            case 'mcp':
                specificFields = `
                    <div class="form-group">
                        <label for="mcpType">MCP类型</label>
                        <select id="mcpType" name="mcp_type" class="form-control">
                            <option value="stdio">stdio</option>
                            <option value="sse">SSE</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="filePath">服务器文件路径 *</label>
                        <input type="text" id="filePath" name="file_path" class="form-control" required placeholder="/path/to/mcp_server.py">
                        <small class="form-text">MCP服务器脚本路径</small>
                    </div>
                    <div class="form-group">
                        <label for="parameter">启动参数 (JSON)</label>
                        <textarea id="parameter" name="parameter" class="form-control code-editor" rows="4" placeholder='{"arg": "value"}'></textarea>
                    </div>
                    <div class="form-group">
                        <label for="requirement">依赖要求</label>
                        <textarea id="requirement" name="requirement" class="form-control" rows="3" placeholder="mcp==1.0.0&#10;other-package==2.0.0"></textarea>
                    </div>
                `;
                break;

            case 'function':
                specificFields = `
                    <div class="form-group">
                        <label for="functionType">函数类型</label>
                        <select id="functionType" name="function_type" class="form-control">
                            <option value="python">Python</option>
                            <option value="javascript">JavaScript</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="filePath">函数文件路径 *</label>
                        <input type="text" id="filePath" name="file_path" class="form-control" required placeholder="/path/to/function.py">
                        <small class="form-text">函数脚本文件路径</small>
                    </div>
                    <div class="form-group">
                        <label for="parameter">函数参数 (JSON)</label>
                        <textarea id="parameter" name="parameter" class="form-control code-editor" rows="5" placeholder='{"param1": {"type": "string", "description": "参数说明"}}'></textarea>
                        <small class="form-text">定义函数接受的参数</small>
                    </div>
                `;
                break;

            case 'computer-use':
                specificFields = `
                    <div class="form-group">
                        <label for="skillType">技能类型</label>
                        <select id="skillType" name="skill_type" class="form-control">
                            <option value="screenshot">屏幕截图</option>
                            <option value="mouse_click">鼠标点击</option>
                            <option value="keyboard_input">键盘输入</option>
                            <option value="custom">自定义脚本</option>
                        </select>
                    </div>
                    <div class="form-group" id="filePathGroup">
                        <label for="filePath">脚本文件路径</label>
                        <input type="text" id="filePath" name="file_path" class="form-control" placeholder="/path/to/skill.py">
                        <small class="form-text">自定义脚本路径（仅自定义类型需要）</small>
                    </div>
                    <div class="form-group">
                        <label for="parameter">执行参数 (JSON)</label>
                        <textarea id="parameter" name="parameter" class="form-control code-editor" rows="5" placeholder='{"x": 100, "y": 200}'></textarea>
                        <small class="form-text">根据技能类型提供对应参数</small>
                    </div>
                `;
                break;
        }

        const confirmField = `
            <div class="form-group">
                <div class="form-check">
                    <input type="checkbox" id="confirmNeeded" name="confirm_needed" class="form-check-input" checked>
                    <label for="confirmNeeded" class="form-check-label">
                        执行前需要确认 <small class="text-muted">(建议开启以增加安全性)</small>
                    </label>
                </div>
            </div>
        `;

        return baseFields + specificFields + confirmField;
    }

    fillFormData(tool) {
        // 填充表单数据
        Object.keys(tool).forEach(key => {
            const input = document.querySelector(`[name="${key}"]`);
            if (input) {
                if (input.type === 'checkbox') {
                    input.checked = tool[key];
                } else {
                    input.value = tool[key] || '';
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

        // 收集表单数据
        const formData = new FormData(form);
        const data = {};

        formData.forEach((value, key) => {
            if (key === 'confirm_needed') {
                data[key] = document.getElementById('confirmNeeded').checked;
            } else {
                data[key] = value;
            }
        });

        try {
            const isEdit = this.currentTool !== null;
            let endpoint, method;

            // 根据类别确定端点
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
                    throw new Error(`未知的工具类别: ${this.currentCategory}`);
            }

            method = isEdit ? 'PUT' : 'POST';

            // 发送请求
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

            // 显示成功消息
            this.showMessage(isEdit ? '保存成功' : '创建成功', 'success');

            // 关闭对话框
            this.close();

            // 调用回调函数
            if (this.onSaveCallback) {
                this.onSaveCallback(result);
            }
        } catch (error) {
            console.error('Save error:', error);
            this.showMessage('保存失败: ' + error.message, 'error');
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

        // 创建临时提示
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
    }
}

// 创建全局实例
window.toolsEditDialog = new ToolsEditDialog();

// 添加样式
const style = document.createElement('style');
style.textContent = `
    .tool-edit-dialog {
        max-width: 800px;
        max-height: 90vh;
        overflow-y: auto;
    }

    .tool-edit-form {
        display: flex;
        flex-direction: column;
        gap: 20px;
    }

    .form-group {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .form-group label {
        font-weight: 600;
        font-size: 14px;
        color: #374151;
    }

    .form-control {
        padding: 10px 12px;
        border: 1px solid #d1d5db;
        border-radius: 6px;
        font-size: 14px;
        font-family: inherit;
        transition: all 0.2s;
    }

    .form-control:focus {
        outline: none;
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }

    .form-control.code-editor {
        font-family: 'Courier New', monospace;
        font-size: 13px;
        background: #f9fafb;
    }

    .form-text {
        font-size: 12px;
        color: #6b7280;
        margin-top: 4px;
    }

    .form-check {
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .form-check-input {
        width: 18px;
        height: 18px;
        cursor: pointer;
    }

    .form-check-label {
        cursor: pointer;
        font-size: 14px;
        color: #374151;
    }

    .text-muted {
        color: #9ca3af;
    }

    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }

    body.theme-dark .form-group label {
        color: #f3f4f6;
    }

    body.theme-dark .form-control {
        background: #1f2937;
        border-color: #374151;
        color: #f3f4f6;
    }

    body.theme-dark .form-control.code-editor {
        background: #111827;
    }

    body.theme-dark .form-text {
        color: #9ca3af;
    }

    body.theme-dark .form-check-label {
        color: #f3f4f6;
    }
`;
document.head.appendChild(style);

export default ToolsEditDialog;
