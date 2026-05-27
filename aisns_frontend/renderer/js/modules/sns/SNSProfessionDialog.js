/**
 * SNS Profession Selection Dialog
 */

export class SNSProfessionDialog {
    constructor() {
        this.dialog = null;
        this.selectedProfession = null;
        this.otherProfession = '';
        this.restrictedOtherValues = new Set(['doctor', 'restaurateur']);
        this.currentMoney = 0;
        this.selectedTradeOption = null;
        this.messageContent = '';
        this.selectedTool = null;
        this.selectedMcpToolName = '';
        this.mcpToolsCache = new Map();
        this._pendingMcpToolName = '';
        this.availableTools = [];
        this.autoCloseTimer = null;
        this.goodsOrServiceDescription = '';
        this.goodsOrServicePrice = '';
        this.serviceFieldsDirty = false;
        this.professionServiceDefaults = new Map();
        this.isRemoteAgent = false;
    }

    static REMOTE_DELIVERY_TOOL_VALUE = 'remote:remote_agent_delivery_tool';
    static REMOTE_DELIVERY_TOOL_LABEL = 'Remote Agent Delivery Tool';

    applyServiceDefaultsIfNeeded() {
        if (this.serviceFieldsDirty) {
            return;
        }

        const defaults = this.professionServiceDefaults.get(this.selectedProfession);
        if (!defaults) {
            return;
        }

        const descInput = this._q('#goodsOrServiceDescription');
        const priceInput = this._q('#goodsOrServicePrice');

        const currentDesc = (this.goodsOrServiceDescription || '').trim();
        const currentPrice = (this.goodsOrServicePrice || '').trim();

        const nextDesc = (defaults.description || '').trim();
        const nextPrice = (defaults.price || '').trim();

        if (!currentDesc && nextDesc) {
            this.goodsOrServiceDescription = nextDesc;
            if (descInput) {
                descInput.value = nextDesc;
            }
        }

        if (!currentPrice && nextPrice) {
            this.goodsOrServicePrice = nextPrice;
            if (priceInput) {
                priceInput.value = nextPrice;
            }
        }
    }

    updateOtherProfessionUI() {
        const container = this._q('#otherProfessionContainer');
        const input = this._q('#otherProfessionInput');
        if (!container) return;

        const show = this.selectedProfession === 'Other';
        container.style.display = show ? 'block' : 'none';
        if (!show) {
            this.setOtherProfessionHelper();
            return;
        }

        if (input) {
            input.value = this.otherProfession || '';
        }
    }

    setOtherProfessionHelper(message = '') {
        const helper = this._q('#otherProfessionHelper');
        if (!helper) {
            return;
        }
        helper.textContent = message;
        helper.style.display = message ? 'block' : 'none';
    }

    clearInlineMessage() {
        const alertBox = this._q('#snsProfessionAlert');
        if (alertBox) {
            alertBox.style.display = 'none';
            alertBox.textContent = '';
            alertBox.classList.remove('inline-alert-error', 'inline-alert-success');
        }
        if (this.autoCloseTimer) {
            clearTimeout(this.autoCloseTimer);
            this.autoCloseTimer = null;
        }
    }

    showInlineMessage(message, type = 'error') {
        const alertBox = this._q('#snsProfessionAlert');
        if (!alertBox) {
            return;
        }
        if (this.autoCloseTimer) {
            clearTimeout(this.autoCloseTimer);
            this.autoCloseTimer = null;
        }

        alertBox.textContent = message;
        alertBox.classList.remove('inline-alert-error', 'inline-alert-success');
        alertBox.classList.add(type === 'success' ? 'inline-alert-success' : 'inline-alert-error');
        alertBox.style.display = 'block';

        this.scrollToBottom();
    }

    scrollToBottom() {
        if (!this._isDialogAlive()) {
            return;
        }

        const alertBox = this._q('#snsProfessionAlert');
        const modalBody = this._q('.modal-body');

        requestAnimationFrame(() => {
            try {
                if (modalBody && modalBody.scrollHeight > modalBody.clientHeight) {
                    modalBody.scrollTop = modalBody.scrollHeight;
                }
                if (alertBox && typeof alertBox.scrollIntoView === 'function') {
                    alertBox.scrollIntoView({ block: 'end' });
                }
            } catch (e) {
            }
        });
    }

    _isDialogAlive() {
        return !!(this.dialog && typeof document !== 'undefined' && document.body && document.body.contains(this.dialog));
    }

    _q(selector) {
        return this.dialog ? this.dialog.querySelector(selector) : null;
    }

    _qa(selector) {
        return this.dialog ? Array.from(this.dialog.querySelectorAll(selector)) : [];
    }

    resolve(urlOrPath) {
        try {
            if (typeof window !== 'undefined' && typeof window.resolveAgentServerUrl === 'function') {
                return window.resolveAgentServerUrl(urlOrPath);
            }
        } catch (e) {
        }
        return urlOrPath;
    }

    async show() {
        // Load current configuration
        await this.loadCurrentConfig();

        const existing = document.getElementById('snsProfessionDialog');
        if (existing) {
            try {
                existing.remove();
            } catch (e) {
            }
        }

        // Create dialog HTML
        const dialogHTML = `
            <div class="modal-overlay sns-profession-dialog-overlay" id="snsProfessionDialog">
                <div class="modal-dialog sns-profession-dialog" style="max-width: 600px;">
                    <div class="modal-header">
                        <h3>Profession</h3>
                        <button class="modal-close" onclick="document.getElementById('snsProfessionDialog').remove()">&times;</button>
                    </div>
                    <div class="modal-body">
                        <div class="profession-config-container">
                            <!-- Current Balance -->
                            <div class="balance-display">
                                <h4>Current balance: <span id="currentBalance">${this.currentMoney.toFixed(2)}</span></h4>
                            </div>

                            <!-- Professions with Cost -->
                            <div class="profession-section">
                                <h4>Professions requiring setup fee</h4>
                                <div class="profession-list" id="professionListCost">
                                    <div class="loading">Loading...</div>
                                </div>
                            </div>

                            <!-- Professions without Cost -->
                            <div class="profession-section">
                                <h4>Professions without setup fee</h4>
                                <div class="profession-list" id="professionListFree">
                                    <div class="loading">Loading...</div>
                                </div>
                            </div>

                            <div class="other-profession-container" id="otherProfessionContainer" style="display: none;">
                                <label for="otherProfessionInput">Other profession<span class="required-asterisk">*</span></label>
                                <input type="text" id="otherProfessionInput" class="form-control" placeholder="Enter your profession" />
                                <div class="other-profession-helper" id="otherProfessionHelper" aria-live="polite"></div>
                            </div>

                            <!-- Service Details -->
                            <div class="profession-section">
                                <h4>Service Details</h4>
                                <div class="form-group">
                                    <label for="goodsOrServiceDescription">Goods or service description</label>
                                    <textarea id="goodsOrServiceDescription" class="form-control" placeholder="Describe the goods or service you provide..." rows="3"></textarea>
                                </div>

                                <div class="form-group" style="margin-bottom: 0;">
                                    <label for="goodsOrServicePrice">Goods or service price</label>
                                    <input type="text" id="goodsOrServicePrice" class="form-control" placeholder="Enter a price" />
                                </div>
                            </div>

                            <!-- Trade Handling Section -->
                            <div class="profession-section">
                                <h4>Sender in trade</h4>
                                <div class="trade-options">
                                    <label class="profession-label">
                                        <input type="radio" name="tradeOption" value="message">
                                        <span>Send message</span>
                                    </label>
                                    <label class="profession-label">
                                        <input type="radio" name="tradeOption" value="tool">
                                        <span>Call tool</span>
                                    </label>
                                </div>
                                
                                <!-- Message Input (shown when 'send message' is selected) -->
                                <div class="message-input-container" id="messageInputContainer" style="display: none;">
                                    <div class="form-group" style="margin-bottom: 0;">
                                        <label for="messageContent">Message content<span class="required-asterisk">*</span></label>
                                        <textarea id="messageContent" class="form-control" placeholder="Enter the message to send..." rows="3"></textarea>
                                    </div>
                                </div>
                                
                                <!-- Tool Selection (shown when 'call tool' is selected) -->
                                <div class="tool-selection-container" id="toolSelectionContainer" style="display: none;">
                                    <div class="form-group">
                                        <label for="toolSelect">Select tool</label>
                                        <select id="toolSelect" class="form-control">
                                            <option value="">Select a tool...</option>
                                        </select>
                                    </div>

                                    <div class="mcp-tool-selection-container" id="mcpToolSelectionContainer" style="display: none;">
                                        <div class="form-group" style="margin-bottom: 0;">
                                            <label for="mcpToolSelect">Select MCP internal tool</label>
                                            <select id="mcpToolSelect" class="form-control">
                                                <option value="">Select an MCP tool...</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="dialog-inline-alert" id="snsProfessionAlert" style="display: none;"></div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-secondary" onclick="document.getElementById('snsProfessionDialog').remove()">Cancel</button>
                        <button class="btn btn-primary" id="saveProfessionBtn">Ok</button>
                    </div>
                </div>
            </div>
        `;

        // Add to DOM
        document.body.insertAdjacentHTML('beforeend', dialogHTML);
        this.dialog = document.getElementById('snsProfessionDialog');

        if (!this._isDialogAlive()) return;

        this.setOtherProfessionHelper();
        this.clearInlineMessage();

        // Load professions
        await this.loadProfessions();

        if (!this._isDialogAlive()) return;

        // Setup event listeners early so profession changes are responsive even if tools are still loading
        this.setupEventListeners();

        // Load available tools
        await this.loadTools();

        if (!this._isDialogAlive()) return;

        // Load existing saved user config and apply to UI
        await this.loadExistingUserConfig();

        if (!this._isDialogAlive()) return;

        // Ensure defaults are applied after existing values are loaded
        this.applyServiceDefaultsIfNeeded();
    }

    async loadCurrentConfig() {
        try {
            const response = await fetch(this.resolve('/api/sns/user-stats'));
            const stats = await response.json();
            this.currentMoney = stats.money || 0;
        } catch (error) {
            console.error('Error loading current config:', error);
            this.currentMoney = 0;
        }

        // Detect agent_type early so loadTools can branch for remote agents
        try {
            const resp = await fetch(this.resolve('/api/sns/user-info'));
            const result = await resp.json();
            const agentType = result && result.success && result.data
                ? String(result.data.agent_type || 'local').trim().toLowerCase()
                : 'local';
            this.isRemoteAgent = (agentType === 'remote');
        } catch (e) {
            this.isRemoteAgent = false;
        }
    }

    async loadExistingUserConfig() {
        try {
            const resp = await fetch(this.resolve('/api/sns/user-info'));
            const result = await resp.json();

            if (!this._isDialogAlive()) {
                return;
            }

            if (!result || !result.success || !result.data) {
                return;
            }

            const data = result.data;

            this.goodsOrServiceDescription = data.goods_or_service_description || '';
            this.goodsOrServicePrice = data.goods_or_service_price || '';
            this.serviceFieldsDirty = false;

            const descInput = this._q('#goodsOrServiceDescription');
            if (descInput) {
                descInput.value = this.goodsOrServiceDescription;
            }
            const priceInput = this._q('#goodsOrServicePrice');
            if (priceInput) {
                priceInput.value = this.goodsOrServicePrice;
            }

            if (typeof data.money === 'number') {
                this.currentMoney = data.money;
                const balanceEl = this._q('#currentBalance');
                if (balanceEl) {
                    balanceEl.textContent = this.currentMoney.toFixed(2);
                }
            }

            if (data.profession) {
                const storedProfession = String(data.profession);
                const radio = this._q(`input[name="profession"][value="${CSS.escape(storedProfession)}"]`);
                if (radio) {
                    this.selectedProfession = storedProfession;
                    radio.checked = true;
                    this.otherProfession = '';
                    this.updateOtherProfessionUI();
                    this.applyServiceDefaultsIfNeeded();
                } else {
                    const otherRadio = this._q('input[name="profession"][value="Other"]');
                    if (otherRadio && !otherRadio.disabled) {
                        otherRadio.checked = true;
                    }
                    this.selectedProfession = 'Other';
                    this.otherProfession = storedProfession;
                    const otherInput = this._q('#otherProfessionInput');
                    if (otherInput) {
                        otherInput.value = this.otherProfession;
                    }
                    this.updateOtherProfessionUI();
                    this.applyServiceDefaultsIfNeeded();
                }
            } else {
                this.selectedProfession = null;
                this.otherProfession = '';
                this.updateOtherProfessionUI();
                this.applyServiceDefaultsIfNeeded();
            }

            if (data.handle_after_trade) {
                const option = data.handle_after_trade;
                const tradeRadio = this._q(`input[name="tradeOption"][value="${CSS.escape(option)}"]`);
                if (tradeRadio) {
                    tradeRadio.checked = true;
                }

                this.onTradeOptionChange(option);

                if (option === 'message') {
                    this.messageContent = data.handle_content || '';
                    const messageEl = this._q('#messageContent');
                    if (messageEl) {
                        messageEl.value = this.messageContent;
                    }
                } else if (option === 'tool') {
                    const raw = data.handle_content || '';
                    const toolEl = this._q('#toolSelect');
                    const mcpToolEl = this._q('#mcpToolSelect');
                    // Helper: check if an option value exists in the toolSelect dropdown
                    const hasToolOption = (val) => !!(toolEl && val && Array.from(toolEl.options).some(opt => opt.value === val));
                    // Reset to default ("Select a tool...") and clear in-memory selection
                    const resetToolSelection = async () => {
                        this.selectedTool = '';
                        this.selectedMcpToolName = '';
                        this._pendingMcpToolName = '';
                        if (toolEl) {
                            toolEl.value = '';
                        }
                        await this.onToolSelectionChange('');
                    };

                    if (toolEl) {
                        if (raw.includes(':')) {
                            if (raw.startsWith('mcp:')) {
                                const parts = raw.split(':');
                                const mcpId = parts[1] || '';
                                const toolName = parts[2] || '';
                                const mcpOptionValue = mcpId ? `mcp:${mcpId}` : '';
                                if (mcpOptionValue && hasToolOption(mcpOptionValue)) {
                                    this.selectedTool = raw;
                                    toolEl.value = mcpOptionValue;
                                    this.selectedMcpToolName = '';
                                    this._pendingMcpToolName = toolName;
                                    await this.onToolSelectionChange(mcpOptionValue);
                                    if (mcpToolEl && toolName) {
                                        const mcpToolExists = Array.from(mcpToolEl.options).some(opt => opt.value === toolName);
                                        if (mcpToolExists) {
                                            mcpToolEl.value = toolName;
                                            this.selectedMcpToolName = toolName;
                                            this.updateSelectedToolValue();
                                        } else {
                                            // Saved MCP internal tool no longer exists; clear sub-selection
                                            mcpToolEl.value = '';
                                            this.selectedMcpToolName = '';
                                            this.updateSelectedToolValue();
                                        }
                                    }
                                } else {
                                    await resetToolSelection();
                                }
                            } else {
                                if (hasToolOption(raw)) {
                                    this.selectedTool = raw;
                                    toolEl.value = raw;
                                    await this.onToolSelectionChange(raw);
                                } else {
                                    await resetToolSelection();
                                }
                            }
                        } else {
                            // Backward compatible: old data might store only id (e.g. PLxxxx)
                            // Try to match any option with suffix :<id>
                            const match = Array.from(toolEl.options).find(opt => opt.value && opt.value.endsWith(`:${raw}`));
                            if (match) {
                                toolEl.value = match.value;
                                this.selectedTool = match.value;
                                await this.onToolSelectionChange(match.value);
                            } else {
                                await resetToolSelection();
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
            const response = await fetch(this.resolve('/api/sns/professions'));
            const professions = await response.json();

            const costList = this._q('#professionListCost');
            const freeList = this._q('#professionListFree');

            if (!costList || !freeList) {
                return;
            }

            costList.innerHTML = '';
            freeList.innerHTML = '';

            this.professionServiceDefaults.clear();
            professions.forEach(profession => {
                if (profession && profession.name) {
                    const desc = profession.service_description ? String(profession.service_description) : '';
                    const price = profession.service_price ? String(profession.service_price) : '';
                    if (desc || price) {
                        this.professionServiceDefaults.set(String(profession.name), { description: desc, price: price });
                    }
                }
            });

            professions.forEach(profession => {
                const item = document.createElement('div');
                item.className = 'profession-item';
                item.dataset.name = profession.name;
                item.dataset.cost = profession.cost || 0;

                const costText = profession.cost ? `(setup fee: ${profession.cost})` : '';
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
            const costList = this._q('#professionListCost');
            const freeList = this._q('#professionListFree');
            if (costList) costList.innerHTML = '<div class="error">Load failed</div>';
            if (freeList) freeList.innerHTML = '<div class="error">Load failed</div>';
        }
    }

    setupEventListeners() {
        // Save button
        const saveBtn = this._q('#saveProfessionBtn');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => {
                this.saveConfiguration();
            });
        }

        // Radio button change
        this._qa('input[name="profession"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.selectedProfession = e.target.value;
                if (this.selectedProfession !== 'Other') {
                    this.setOtherProfessionHelper();
                }
                this.updateOtherProfessionUI();
                this.applyServiceDefaultsIfNeeded();
                this.clearInlineMessage();
            });
        });

        const goodsOrServiceDescription = this._q('#goodsOrServiceDescription');
        if (goodsOrServiceDescription) {
            goodsOrServiceDescription.addEventListener('input', (e) => {
                this.goodsOrServiceDescription = e.target.value;
                this.serviceFieldsDirty = true;
                this.clearInlineMessage();
            });
        }

        const goodsOrServicePrice = this._q('#goodsOrServicePrice');
        if (goodsOrServicePrice) {
            goodsOrServicePrice.addEventListener('input', (e) => {
                this.goodsOrServicePrice = e.target.value;
                this.serviceFieldsDirty = true;
                this.clearInlineMessage();
            });
        }

        const otherProfessionInput = this._q('#otherProfessionInput');
        if (otherProfessionInput) {
            otherProfessionInput.addEventListener('input', (e) => {
                this.otherProfession = e.target.value;
                this.setOtherProfessionHelper();
                this.clearInlineMessage();
            });
        }

        // Trade option change
        this._qa('input[name="tradeOption"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.onTradeOptionChange(e.target.value);
                this.clearInlineMessage();
            });
        });

        // Message content change
        const messageContent = this._q('#messageContent');
        if (messageContent) {
            messageContent.addEventListener('input', (e) => {
                this.messageContent = e.target.value;
                this.clearInlineMessage();
            });
        }

        // Tool selection change
        const toolSelect = this._q('#toolSelect');
        if (toolSelect) {
            toolSelect.addEventListener('change', (e) => {
                this.onToolSelectionChange(e.target.value);
                this.clearInlineMessage();
            });
        }

        const mcpToolSelect = this._q('#mcpToolSelect');
        if (mcpToolSelect) {
            mcpToolSelect.addEventListener('change', (e) => {
                this.selectedMcpToolName = e.target.value;
                this.updateSelectedToolValue();
                this.clearInlineMessage();
            });
        }
    }

    async onToolSelectionChange(value) {
        const mcpContainer = this._q('#mcpToolSelectionContainer');
        const mcpSelect = this._q('#mcpToolSelect');

        this.selectedMcpToolName = '';

        if (mcpContainer) {
            mcpContainer.style.display = 'none';
        }

        if (mcpSelect) {
            mcpSelect.innerHTML = '<option value="">Select an MCP tool...</option>';
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
        const mcpSelect = this._q('#mcpToolSelect');
        if (!mcpSelect) return;

        if (this.mcpToolsCache.has(mcpId)) {
            const cached = this.mcpToolsCache.get(mcpId);
            this.populateMcpToolSelect(cached);
            return;
        }

        // Read tool names directly from the MCP record's `detail` field
        // (populated via the "Load Tools" button on the MCP edit dialog).
        // No live probing of the MCP server is performed here.
        const mcpRecord = (this.availableTools || []).find(
            t => t && t.type === 'mcp' && String(t.id) === String(mcpId)
        );
        const tools = this.parseMcpDetailField(mcpRecord && mcpRecord.detail);
        this.mcpToolsCache.set(mcpId, tools);
        this.populateMcpToolSelect(tools);
    }

    /**
     * Parse the MCP `detail` field into a list of tool descriptors.
     * The field is expected to be a comma-separated list of tool names,
     * e.g. "get_weather, get_current_time". Returns an array of {name}.
     */
    parseMcpDetailField(detail) {
        if (!detail || typeof detail !== 'string') return [];
        return detail
            .split(',')
            .map(s => s.trim())
            .filter(Boolean)
            .map(name => ({ name, description: '' }));
    }

    populateMcpToolSelect(tools) {
        const mcpSelect = this._q('#mcpToolSelect');
        if (!mcpSelect) return;
        mcpSelect.innerHTML = '<option value="">Select an MCP tool...</option>';
        (tools || []).forEach(t => {
            const opt = document.createElement('option');
            opt.value = t.name;
            // Show only the tool name; description is intentionally omitted to keep the list compact
            opt.textContent = t.name;
            mcpSelect.appendChild(opt);
        });
    }

    async saveConfiguration() {
        this.clearInlineMessage();

        if (!this.selectedProfession) {
            this.showInlineMessage('Please select a profession.');
            return;
        }

        if (this.selectedProfession === 'Other') {
            const otherText = (this.otherProfession || '').trim();
            if (!otherText) {
                this.showInlineMessage('Please enter your profession.');
                return;
            }

            if (this.restrictedOtherValues.has(otherText.toLowerCase())) {
                this.setOtherProfessionHelper('Please select this profession from the list instead of typing it.');
                const otherInput = this._q('#otherProfessionInput');
                if (otherInput) {
                    otherInput.focus();
                }
                return;
            }
        }

        // Validate trade option if selected
        if (this.selectedTradeOption === 'message' && !this.messageContent.trim()) {
            this.showInlineMessage('Please enter message content.');
            return;
        }

        if (this.selectedTradeOption === 'tool' && !this.selectedTool) {
            this.showInlineMessage('Please select a tool.');
            return;
        }

        if (this.selectedTradeOption === 'tool' && this.selectedTool && !this.selectedTool.includes(':')) {
            this.showInlineMessage('Invalid tool configuration. Please re-select a tool.');
            return;
        }

        if (
            this.selectedTradeOption === 'tool' &&
            this.selectedTool &&
            this.selectedTool.startsWith('mcp:')
        ) {
            const parts = this.selectedTool.split(':');
            if (parts.length < 3) {
                this.showInlineMessage('Please select an MCP internal tool.');
                return;
            }
        }

        try {
            const professionToSave = this.selectedProfession === 'Other'
                ? (this.otherProfession || '').trim()
                : this.selectedProfession;

            const configData = {
                profession: professionToSave,
                handle_after_trade: this.selectedTradeOption || '',
                handle_content: this.selectedTradeOption === 'message' ? this.messageContent : this.selectedTool || '',
                goods_or_service_description: (this.goodsOrServiceDescription || '').trim(),
                goods_or_service_price: (this.goodsOrServicePrice || '').trim()
            };

            const response = await fetch(this.resolve('/api/sns/user-info'), {
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

                try {
                    window.dispatchEvent(new CustomEvent('sns-user-info-updated', {
                        detail: {
                            profession: professionToSave
                        }
                    }));
                } catch (e) {
                }

                this.showInlineMessage('Profession saved successfully.' + (deducted > 0 ? ` Setup fee deducted: ${deducted}.` : ''), 'success');
                this.autoCloseTimer = setTimeout(() => {
                    if (this._isDialogAlive()) {
                        this.dialog.remove();
                    }
                }, 1200);
            } else {
                this.showInlineMessage('Save failed: ' + (result.message || 'Unknown error'));
            }
        } catch (error) {
            console.error('Error saving profession:', error);
            this.showInlineMessage('Save failed: ' + error.message);
        }
    }

    getProfessionCost(professionName) {
        const professionCosts = {
            'Doctor': 800,
            'Restaurateur': 800
        };
        return professionCosts[professionName] || 0;
    }

    onTradeOptionChange(option) {
        this.selectedTradeOption = option;

        // Hide both containers first
        const messageContainer = this._q('#messageInputContainer');
        const toolContainer = this._q('#toolSelectionContainer');
        if (messageContainer) messageContainer.style.display = 'none';
        if (toolContainer) toolContainer.style.display = 'none';

        // Show relevant container
        if (option === 'message') {
            if (messageContainer) messageContainer.style.display = 'block';
        } else if (option === 'tool') {
            if (toolContainer) toolContainer.style.display = 'block';
        }
    }

    async loadTools() {
        // Remote agents are restricted to a single fixed delivery tool.
        // Skip fetching MCP/Skill lists in that case.
        if (this.isRemoteAgent) {
            this.availableTools = [];
            this.populateToolSelect();
            return;
        }

        try {
            // Fetch MCP tools and DocSkills (same source as Agent module)
            const [mcpsResponse, docSkillsResponse] = await Promise.all([
                fetch(this.resolve('/api/tools/mcp')),
                fetch(this.resolve('/api/skills/list'))
            ]);

            const mcps = await mcpsResponse.json();
            const docSkillsPayload = await docSkillsResponse.json();
            const docSkills = docSkillsPayload?.data || [];

            this.availableTools = [
                ...mcps.map(tool => ({ ...tool, type: 'mcp', id: tool.mcp_id })),
                ...docSkills.map(tool => ({ ...tool, type: 'skill', id: tool.skill_key }))
            ];

            this.populateToolSelect();
        } catch (error) {
            console.error('Error loading tools:', error);
        }
    }

    populateToolSelect() {
        const toolSelect = this._q('#toolSelect');
        if (!toolSelect) return;

        // Remote agent: only one fixed option is available
        if (this.isRemoteAgent) {
            toolSelect.innerHTML = '';
            const option = document.createElement('option');
            option.value = SNSProfessionDialog.REMOTE_DELIVERY_TOOL_VALUE;
            option.textContent = SNSProfessionDialog.REMOTE_DELIVERY_TOOL_LABEL;
            toolSelect.appendChild(option);
            // Auto-select since there is only one option
            toolSelect.value = SNSProfessionDialog.REMOTE_DELIVERY_TOOL_VALUE;
            this.selectedTool = SNSProfessionDialog.REMOTE_DELIVERY_TOOL_VALUE;
            // Hide the MCP sub-selection container if present
            const mcpContainer = this._q('#mcpToolSelectionContainer');
            if (mcpContainer) mcpContainer.style.display = 'none';
            return;
        }

        // Clear existing options except the first one
        toolSelect.innerHTML = '<option value="">Select a tool...</option>';

        // Group tools by type (MCP and Skill only)
        const toolsByType = {
            'MCP tools': this.availableTools.filter(tool => tool.type === 'mcp'),
            'Skill tools': this.availableTools.filter(tool => tool.type === 'skill')
        };

        // Create option groups. Show only the tool name (description omitted to keep the list compact)
        Object.entries(toolsByType).forEach(([typeName, tools]) => {
            if (tools.length > 0) {
                const optgroup = document.createElement('optgroup');
                optgroup.label = typeName;

                tools.forEach(tool => {
                    const option = document.createElement('option');
                    option.value = `${tool.type}:${tool.id}`;
                    option.textContent = tool.name || tool.id || '';
                    optgroup.appendChild(option);
                });

                toolSelect.appendChild(optgroup);
            }
        });
    }
}
