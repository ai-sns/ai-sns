/**
 * SNS Profession Selection Dialog
 */

export class SNSProfessionDialog {
    constructor() {
        this.dialog = null;
        this.selectedProfession = null;
        this.currentMoney = 0;
        this.selectedTradeOption = null;
        this.messageContent = '';
        this.selectedTool = null;
        this.selectedMcpToolName = '';
        this.mcpToolsCache = new Map();
        this._pendingMcpToolName = '';
        this.availableTools = [];
    }

    async show() {
        // Load current configuration
        await this.loadCurrentConfig();

        // Create dialog HTML
        const dialogHTML = `
            <div class="modal-overlay" id="snsProfessionDialog">
                <div class="modal-dialog" style="max-width: 600px;">
                    <div class="modal-header">
                        <h3>职业选择</h3>
                        <button class="modal-close" onclick="document.getElementById('snsProfessionDialog').remove()">&times;</button>
                    </div>
                    <div class="modal-body">
                        <div class="profession-config-container">
                            <!-- Current Balance -->
                            <div class="balance-display">
                                <h4>当前资金: <span id="currentBalance">${this.currentMoney.toFixed(2)}</span>元</h4>
                            </div>

                            <!-- Professions with Cost -->
                            <div class="profession-section">
                                <h4>需要开办费的职业</h4>
                                <div class="profession-list" id="professionListCost">
                                    <div class="loading">加载中...</div>
                                </div>
                            </div>

                            <!-- Professions without Cost -->
                            <div class="profession-section">
                                <h4>其他职业选项</h4>
                                <div class="profession-list" id="professionListFree">
                                    <div class="loading">加载中...</div>
                                </div>
                            </div>

                            <!-- Trade Handling Section -->
                            <div class="trade-section">
                                <h4>交易时的发货方</h4>
                                <div class="trade-options">
                                    <label class="trade-option">
                                        <input type="radio" name="tradeOption" value="message">
                                        <span>发送消息</span>
                                    </label>
                                    <label class="trade-option">
                                        <input type="radio" name="tradeOption" value="tool">
                                        <span>调用工具</span>
                                    </label>
                                </div>
                                
                                <!-- Message Input (shown when 'send message' is selected) -->
                                <div class="message-input-container" id="messageInputContainer" style="display: none;">
                                    <label for="messageContent">消息内容:</label>
                                    <textarea id="messageContent" placeholder="请输入要发送的消息内容..." rows="3" style="width: 100%; margin-top: 5px;"></textarea>
                                </div>
                                
                                <!-- Tool Selection (shown when 'call tool' is selected) -->
                                <div class="tool-selection-container" id="toolSelectionContainer" style="display: none;">
                                    <label for="toolSelect">选择工具:</label>
                                    <select id="toolSelect" style="width: 100%; margin-top: 5px; padding: 5px;">
                                        <option value="">请选择工具...</option>
                                    </select>

                                    <div class="mcp-tool-selection-container" id="mcpToolSelectionContainer" style="display: none; margin-top: 10px;">
                                        <label for="mcpToolSelect">选择 MCP 内部工具:</label>
                                        <select id="mcpToolSelect" style="width: 100%; margin-top: 5px; padding: 5px;">
                                            <option value="">请选择 MCP 工具...</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-secondary" onclick="document.getElementById('snsProfessionDialog').remove()">取消</button>
                        <button class="btn btn-primary" id="saveProfessionBtn">确定</button>
                    </div>
                </div>
            </div>
        `;

        // Add to DOM
        document.body.insertAdjacentHTML('beforeend', dialogHTML);
        this.dialog = document.getElementById('snsProfessionDialog');

        // Load professions
        await this.loadProfessions();
        
        // Load available tools
        await this.loadTools();

        // Load existing saved user config and apply to UI
        await this.loadExistingUserConfig();

        // Setup event listeners
        this.setupEventListeners();
    }

    async loadCurrentConfig() {
        try {
            const response = await fetch('http://localhost:8788/api/sns/user-stats');
            const stats = await response.json();
            this.currentMoney = stats.money || 0;
        } catch (error) {
            console.error('Error loading current config:', error);
            this.currentMoney = 0;
        }
    }

    async loadExistingUserConfig() {
        try {
            const resp = await fetch('http://localhost:8788/api/sns/user-info');
            const result = await resp.json();

            if (!result || !result.success || !result.data) {
                return;
            }

            const data = result.data;

            if (typeof data.money === 'number') {
                this.currentMoney = data.money;
                const balanceEl = document.getElementById('currentBalance');
                if (balanceEl) {
                    balanceEl.textContent = this.currentMoney.toFixed(2);
                }
            }

            if (data.profession) {
                this.selectedProfession = data.profession;
                const radio = document.querySelector(`input[name="profession"][value="${CSS.escape(data.profession)}"]`);
                if (radio && !radio.disabled) {
                    radio.checked = true;
                }
            }

            if (data.handle_after_trade) {
                const option = data.handle_after_trade;
                const tradeRadio = document.querySelector(`input[name="tradeOption"][value="${CSS.escape(option)}"]`);
                if (tradeRadio) {
                    tradeRadio.checked = true;
                }

                this.onTradeOptionChange(option);

                if (option === 'message') {
                    this.messageContent = data.handle_content || '';
                    const messageEl = document.getElementById('messageContent');
                    if (messageEl) {
                        messageEl.value = this.messageContent;
                    }
                } else if (option === 'tool') {
                    const raw = data.handle_content || '';
                    // Backward compatible: old data might store only id (e.g. PLxxxx)
                    this.selectedTool = raw.includes(':') ? raw : raw;
                    const toolEl = document.getElementById('toolSelect');
                    const mcpToolEl = document.getElementById('mcpToolSelect');
                    if (toolEl) {
                        if (raw.includes(':')) {
                            if (raw.startsWith('mcp:')) {
                                const parts = raw.split(':');
                                const mcpId = parts[1] || '';
                                const toolName = parts[2] || '';
                                toolEl.value = mcpId ? `mcp:${mcpId}` : '';
                                this.selectedMcpToolName = '';
                                this._pendingMcpToolName = toolName;
                                await this.onToolSelectionChange(toolEl.value);
                                if (mcpToolEl && toolName) {
                                    mcpToolEl.value = toolName;
                                    this.selectedMcpToolName = toolName;
                                    this.updateSelectedToolValue();
                                }
                            } else {
                                toolEl.value = raw;
                                await this.onToolSelectionChange(raw);
                            }
                        } else {
                            // Try to match any option with suffix :<id>
                            const match = Array.from(toolEl.options).find(opt => opt.value && opt.value.endsWith(`:${raw}`));
                            if (match) {
                                toolEl.value = match.value;
                                this.selectedTool = match.value;
                                await this.onToolSelectionChange(match.value);
                            } else {
                                toolEl.value = '';
                                await this.onToolSelectionChange('');
                            }
                        }
                    }
                }
            }
        } catch (error) {
            console.error('Error loading existing user config:', error);
        }
    }

    async loadProfessions() {
        try {
            const response = await fetch('http://localhost:8788/api/sns/professions');
            const professions = await response.json();

            const costList = document.getElementById('professionListCost');
            const freeList = document.getElementById('professionListFree');

            costList.innerHTML = '';
            freeList.innerHTML = '';

            professions.forEach(profession => {
                const item = document.createElement('div');
                item.className = 'profession-item';
                item.dataset.name = profession.name;
                item.dataset.cost = profession.cost || 0;

                const costText = profession.cost ? `(*需要${profession.cost}元开办费)` : '';
                const disabled = profession.cost && profession.cost > this.currentMoney ? 'disabled' : '';

                item.innerHTML = `
                    <label class="profession-label ${disabled}">
                        <input type="radio" name="profession" value="${profession.name}" ${disabled}>
                        <span>${profession.name} ${costText}</span>
                    </label>
                `;

                if (profession.cost) {
                    costList.appendChild(item);
                } else {
                    freeList.appendChild(item);
                }
            });
        } catch (error) {
            console.error('Error loading professions:', error);
            document.getElementById('professionListCost').innerHTML = '<div class="error">加载失败</div>';
            document.getElementById('professionListFree').innerHTML = '<div class="error">加载失败</div>';
        }
    }

    setupEventListeners() {
        // Save button
        document.getElementById('saveProfessionBtn').addEventListener('click', () => {
            this.saveConfiguration();
        });

        // Radio button change
        document.querySelectorAll('input[name="profession"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.selectedProfession = e.target.value;
            });
        });
        
        // Trade option change
        document.querySelectorAll('input[name="tradeOption"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.onTradeOptionChange(e.target.value);
            });
        });
        
        // Message content change
        const messageContent = document.getElementById('messageContent');
        if (messageContent) {
            messageContent.addEventListener('input', (e) => {
                this.messageContent = e.target.value;
            });
        }
        
        // Tool selection change
        const toolSelect = document.getElementById('toolSelect');
        if (toolSelect) {
            toolSelect.addEventListener('change', (e) => {
                this.onToolSelectionChange(e.target.value);
            });
        }

        const mcpToolSelect = document.getElementById('mcpToolSelect');
        if (mcpToolSelect) {
            mcpToolSelect.addEventListener('change', (e) => {
                this.selectedMcpToolName = e.target.value;
                this.updateSelectedToolValue();
            });
        }
    }

    async onToolSelectionChange(value) {
        const mcpContainer = document.getElementById('mcpToolSelectionContainer');
        const mcpSelect = document.getElementById('mcpToolSelect');

        this.selectedMcpToolName = '';

        if (mcpContainer) {
            mcpContainer.style.display = 'none';
        }

        if (mcpSelect) {
            mcpSelect.innerHTML = '<option value="">请选择 MCP 工具...</option>';
        }

        if (value && value.startsWith('mcp:')) {
            const parts = value.split(':');
            const mcpId = parts[1] || '';
            if (mcpId) {
                if (mcpContainer) {
                    mcpContainer.style.display = 'block';
                }
                await this.loadMcpToolsIntoSelect(mcpId);
                if (mcpSelect && this._pendingMcpToolName) {
                    const pending = this._pendingMcpToolName;
                    this._pendingMcpToolName = '';
                    const exists = Array.from(mcpSelect.options).some(opt => opt.value === pending);
                    if (exists) {
                        mcpSelect.value = pending;
                        this.selectedMcpToolName = pending;
                    }
                }
            }
        }

        this.selectedTool = value || '';
        this.updateSelectedToolValue();
    }

    updateSelectedToolValue() {
        const base = this.selectedTool || '';
        if (base.startsWith('mcp:')) {
            const parts = base.split(':');
            const mcpId = parts[1] || '';
            if (mcpId && this.selectedMcpToolName) {
                this.selectedTool = `mcp:${mcpId}:${this.selectedMcpToolName}`;
                return;
            }
            this.selectedTool = base;
        }
    }

    async loadMcpToolsIntoSelect(mcpId) {
        const mcpSelect = document.getElementById('mcpToolSelect');
        if (!mcpSelect) return;

        if (this.mcpToolsCache.has(mcpId)) {
            const cached = this.mcpToolsCache.get(mcpId);
            this.populateMcpToolSelect(cached);
            return;
        }

        try {
            const resp = await fetch(`http://localhost:8788/api/tools/mcp/${encodeURIComponent(mcpId)}/execute`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({})
            });
            const data = await resp.json();
            const tools = this.extractMcpToolsFromExecuteResponse(data);
            this.mcpToolsCache.set(mcpId, tools);
            this.populateMcpToolSelect(tools);
        } catch (e) {
            console.error('Error loading MCP tools:', e);
            this.populateMcpToolSelect([]);
        }
    }

    extractMcpToolsFromExecuteResponse(data) {
        try {
            // Expected: { success: true, result: { connection: { tools: [...] } } }
            const result = data && data.result ? data.result : null;
            const connection = result && result.connection ? result.connection : null;
            const tools = connection && Array.isArray(connection.tools) ? connection.tools : [];
            return tools
                .map(t => ({ name: t && t.name ? String(t.name) : '', description: t && t.description ? String(t.description) : '' }))
                .filter(t => t.name);
        } catch {
            return [];
        }
    }

    populateMcpToolSelect(tools) {
        const mcpSelect = document.getElementById('mcpToolSelect');
        if (!mcpSelect) return;
        mcpSelect.innerHTML = '<option value="">请选择 MCP 工具...</option>';
        (tools || []).forEach(t => {
            const opt = document.createElement('option');
            opt.value = t.name;
            opt.textContent = t.description ? `${t.name} - ${t.description}` : t.name;
            mcpSelect.appendChild(opt);
        });
    }

    async saveConfiguration() {
        if (!this.selectedProfession) {
            alert('请选择一个职业');
            return;
        }

        // Validate trade option if selected
        if (this.selectedTradeOption === 'message' && !this.messageContent.trim()) {
            alert('请输入消息内容');
            return;
        }
        
        if (this.selectedTradeOption === 'tool' && !this.selectedTool) {
            alert('请选择一个工具');
            return;
        }

        if (this.selectedTradeOption === 'tool' && this.selectedTool && !this.selectedTool.includes(':')) {
            alert('工具配置格式错误，请重新选择工具');
            return;
        }

        if (
            this.selectedTradeOption === 'tool' &&
            this.selectedTool &&
            this.selectedTool.startsWith('mcp:')
        ) {
            const parts = this.selectedTool.split(':');
            if (parts.length < 3) {
                alert('请选择 MCP 内部工具');
                return;
            }
        }

        try {
            const configData = {
                profession: this.selectedProfession,
                handle_after_trade: this.selectedTradeOption || '',
                handle_content: this.selectedTradeOption === 'message' ? this.messageContent : this.selectedTool || ''
            };

            const response = await fetch('http://localhost:8788/api/sns/user-info', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(configData)
            });

            const result = await response.json();
            if (result.success) {
                const deducted = result.data && typeof result.data.deducted === 'number' ? result.data.deducted : 0;
                const newMoney = result.data && typeof result.data.money === 'number' ? result.data.money : null;
                if (typeof newMoney === 'number') {
                    this.currentMoney = newMoney;
                }

                alert('职业设置成功！' + (deducted > 0 ? `已扣除${deducted}元开办费。` : ''));
                this.dialog.remove();
            } else {
                alert('保存失败：' + (result.message || '未知错误'));
            }
        } catch (error) {
            console.error('Error saving profession:', error);
            alert('保存失败：' + error.message);
        }
    }
    
    getProfessionCost(professionName) {
        const professionCosts = {
            '医生': 800,
            '出租车司机': 1000,
            '食品商贩': 800
        };
        return professionCosts[professionName] || 0;
    }
    
    onTradeOptionChange(option) {
        this.selectedTradeOption = option;
        
        // Hide both containers first
        document.getElementById('messageInputContainer').style.display = 'none';
        document.getElementById('toolSelectionContainer').style.display = 'none';
        
        // Show relevant container
        if (option === 'message') {
            document.getElementById('messageInputContainer').style.display = 'block';
        } else if (option === 'tool') {
            document.getElementById('toolSelectionContainer').style.display = 'block';
        }
    }
    
    async loadTools() {
        try {
            // Fetch all tool types from the tools API
            const [pluginsResponse, mcpsResponse, functionsResponse, skillsResponse] = await Promise.all([
                fetch('http://localhost:8788/api/tools/plugins'),
                fetch('http://localhost:8788/api/tools/mcp'),
                fetch('http://localhost:8788/api/tools/functions'),
                fetch('http://localhost:8788/api/tools/skills')
            ]);
            
            const plugins = await pluginsResponse.json();
            const mcps = await mcpsResponse.json();
            const functions = await functionsResponse.json();
            const skills = await skillsResponse.json();
            
            this.availableTools = [
                ...plugins.map(tool => ({ ...tool, type: 'plugin', id: tool.plugin_id })),
                ...mcps.map(tool => ({ ...tool, type: 'mcp', id: tool.mcp_id })),
                ...functions.map(tool => ({ ...tool, type: 'function', id: tool.function_id })),
                ...skills.map(tool => ({ ...tool, type: 'skill', id: tool.skill_id }))
            ];
            
            this.populateToolSelect();
        } catch (error) {
            console.error('Error loading tools:', error);
        }
    }
    
    populateToolSelect() {
        const toolSelect = document.getElementById('toolSelect');
        if (!toolSelect) return;
        
        // Clear existing options except the first one
        toolSelect.innerHTML = '<option value="">请选择工具...</option>';
        
        // Group tools by type
        const toolsByType = {
            '插件工具': this.availableTools.filter(tool => tool.type === 'plugin'),
            'MCP工具': this.availableTools.filter(tool => tool.type === 'mcp'),
            '函数工具': this.availableTools.filter(tool => tool.type === 'function'),
            '技能工具': this.availableTools.filter(tool => tool.type === 'skill')
        };
        
        // Create option groups
        Object.entries(toolsByType).forEach(([typeName, tools]) => {
            if (tools.length > 0) {
                const optgroup = document.createElement('optgroup');
                optgroup.label = typeName;
                
                tools.forEach(tool => {
                    const option = document.createElement('option');
                    option.value = `${tool.type}:${tool.id}`;
                    option.textContent = `${tool.name} - ${tool.description || '无描述'}`;
                    optgroup.appendChild(option);
                });
                
                toolSelect.appendChild(optgroup);
            }
        });
    }
}
