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
        this.agentPrompt = '';
        this.autoCloseTimer = null;
        this.goodsOrServiceDescription = '';
        this.goodsOrServicePrice = '';
        this.serviceFieldsDirty = false;
        this.professionServiceDefaults = new Map();
    }

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

                            <!-- Service Offering -->
                            <div class="profession-section">
                                <h4>Service Offering</h4>
                                <div class="form-group">
                                    <label for="goodsOrServiceDescription">Description</label>
                                    <textarea id="goodsOrServiceDescription" class="form-control" placeholder="Describe the service you provide..." rows="3"></textarea>
                                </div>

                                <div class="form-group" style="margin-bottom: 0;">
                                    <label for="goodsOrServicePrice">Pricing</label>
                                    <input type="text" id="goodsOrServicePrice" class="form-control" placeholder="Enter a price" />
                                </div>
                            </div>

                            <!-- Trade Handling Section -->
                            <div class="profession-section">
                                <h4>Delivery Type</h4>
                                <div class="trade-options">
                                    <label class="profession-label">
                                        <input type="radio" name="tradeOption" value="message">
                                        <span>Fixed Message</span>
                                    </label>
                                    <label class="profession-label">
                                        <input type="radio" name="tradeOption" value="agent">
                                        <span>Agent Response</span>
                                    </label>
                                </div>
                                
                                <!-- Message Input (shown when 'send message' is selected) -->
                                <div class="message-input-container" id="messageInputContainer" style="display: none;">
                                    <div class="form-group" style="margin-bottom: 0;">
                                        <label for="messageContent">Message content<span class="required-asterisk">*</span></label>
                                        <textarea id="messageContent" class="form-control" placeholder="Enter the message to send..." rows="3"></textarea>
                                    </div>
                                </div>
                                
                                <!-- Agent Prompt Input (shown when 'send by agent' is selected) -->
                                <div class="message-input-container" id="agentPromptInputContainer" style="display: none;">
                                    <div class="form-group" style="margin-bottom: 0;">
                                        <label for="agentPrompt">Prompt<span class="required-asterisk">*</span></label>
                                        <textarea id="agentPrompt" class="form-control" placeholder="Enter the prompt for llm" rows="3"></textarea>
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

        // Setup event listeners
        this.setupEventListeners();

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
                } else if (option === 'agent') {
                    this.agentPrompt = data.handle_content || '';
                    const promptEl = this._q('#agentPrompt');
                    if (promptEl) {
                        promptEl.value = this.agentPrompt;
                    }
                }
            }

            // After hydrating UI from saved data, enforce the fixed-payload
            // lock for professions whose delivery is hard-coded. This must
            // run last so the lock supersedes any saved handle_after_trade
            // / handle_content for those professions.
            this.applyTradeLockForProfession();
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
                this.applyTradeLockForProfession();
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

        // Agent prompt change
        const agentPrompt = this._q('#agentPrompt');
        if (agentPrompt) {
            agentPrompt.addEventListener('input', (e) => {
                this.agentPrompt = e.target.value;
                this.clearInlineMessage();
            });
        }
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

        if (this.selectedTradeOption === 'agent' && !this.agentPrompt.trim()) {
            this.showInlineMessage('Please enter the prompt.');
            return;
        }

        try {
            const professionToSave = this.selectedProfession === 'Other'
                ? (this.otherProfession || '').trim()
                : this.selectedProfession;
            const fixedDeliveryProfessions = new Set(['Doctor', 'Restaurateur']);
            const fixedDeliveryMessage = 'Service Or Goods Is Provided.';
            const isFixedDeliveryProfession = fixedDeliveryProfessions.has(professionToSave);
            const handleAfterTrade = isFixedDeliveryProfession
                ? 'message'
                : this.selectedTradeOption || '';
            const handleContent = isFixedDeliveryProfession
                ? fixedDeliveryMessage
                : (this.selectedTradeOption === 'message' ? this.messageContent : this.agentPrompt || '');

            const configData = {
                profession: professionToSave,
                handle_after_trade: handleAfterTrade,
                handle_content: handleContent,
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
        const agentPromptContainer = this._q('#agentPromptInputContainer');
        if (messageContainer) messageContainer.style.display = 'none';
        if (agentPromptContainer) agentPromptContainer.style.display = 'none';

        // Show relevant container
        if (option === 'message') {
            if (messageContainer) messageContainer.style.display = 'block';
        } else if (option === 'agent') {
            if (agentPromptContainer) agentPromptContainer.style.display = 'block';
        }
    }

    /**
     * For professions whose delivery payload is fixed (Doctor / Restaurateur),
     * lock the "Delivery Type" section: force "Fixed Message" with a fixed
     * acknowledgement content, and make the whole region read-only.
     * Called whenever the selected profession changes.
     */
    applyTradeLockForProfession() {
        const FIXED_MESSAGE = 'Service Or Goods Is Provided.';
        const lockedProfessions = new Set(['Doctor', 'Restaurateur']);
        const isLocked = lockedProfessions.has(this.selectedProfession);

        const messageRadio = this._q('input[name="tradeOption"][value="message"]');
        const agentRadio = this._q('input[name="tradeOption"][value="agent"]');
        const messageEl = this._q('#messageContent');
        const agentPromptContainer = this._q('#agentPromptInputContainer');

        if (isLocked) {
            // Force selection to "message" using the native radio state
            // machine. Some browsers ignore programmatic `.checked = true`
            // on a radio that is about to be disabled (or that is part of
            // a group with another currently-checked element). Calling
            // `.click()` on a fully-enabled radio is the most reliable
            // way to flip the group's checked state, then we disable both
            // radios to make the choice read-only.
            if (agentRadio) {
                agentRadio.disabled = false;
                agentRadio.checked = false;
            }
            if (messageRadio) {
                messageRadio.disabled = false;
                if (!messageRadio.checked) {
                    messageRadio.click();
                }
                // Defensive: ensure checked even if click() was no-op
                // (e.g. element not in layout for some reason).
                messageRadio.checked = true;
            }
            // Disable AFTER the checked state has been committed so the
            // browser preserves it visually on the disabled control.
            if (messageRadio) messageRadio.disabled = true;
            if (agentRadio) agentRadio.disabled = true;

            this.selectedTradeOption = 'message';
            this.messageContent = FIXED_MESSAGE;
            if (messageEl) {
                messageEl.value = FIXED_MESSAGE;
                messageEl.readOnly = true;
                messageEl.setAttribute('aria-disabled', 'true');
            }
            // Make sure UI shows the message container and hides the agent prompt
            this.onTradeOptionChange('message');
            if (agentPromptContainer) {
                agentPromptContainer.style.display = 'none';
            }
            // Clear any stale agent prompt while locked so it is not saved.
            this.agentPrompt = '';
            const promptElLocked = this._q('#agentPrompt');
            if (promptElLocked) {
                promptElLocked.value = '';
            }
        } else {
            // Unlock: restore editability for non-fixed professions
            if (messageRadio) messageRadio.disabled = false;
            if (agentRadio) agentRadio.disabled = false;
            if (messageEl) {
                if (messageEl.readOnly) {
                    messageEl.readOnly = false;
                    messageEl.removeAttribute('aria-disabled');
                    // If the message field still holds the fixed acknowledgement
                    // (auto-filled while previously locked), clear it so the
                    // user can type a new one.
                    if (messageEl.value === FIXED_MESSAGE) {
                        messageEl.value = '';
                        this.messageContent = '';
                    }
                }
            }
        }
    }

}
