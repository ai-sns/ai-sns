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
                this.selectedTool = e.target.value;
            });
        }
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
                alert('职业设置成功！' + (this.selectedProfession && this.getProfessionCost(this.selectedProfession) > 0 ? `已扣除${this.getProfessionCost(this.selectedProfession)}元开办费。` : ''));
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
                    option.value = tool.id;
                    option.textContent = `${tool.name} - ${tool.description || '无描述'}`;
                    optgroup.appendChild(option);
                });
                
                toolSelect.appendChild(optgroup);
            }
        });
    }
}
