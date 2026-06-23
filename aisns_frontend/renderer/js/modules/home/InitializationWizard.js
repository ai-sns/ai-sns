// Prefix under which all Initialization Setup wizard strings live in the
// language JSON files (renderer/lang/{en,zh}.json), which are the single
// source of truth. Consumed by InitializationWizard.t().
const INIT_WIZARD_I18N_PREFIX = 'home.init_wizard';

const InitializationWizard = {
    modal: null,
    step: 0,
    avatar3dItems: [],
    captcha: {
        id: '',
        objectUrl: ''
    },
    captchaRequestSeq: 0,
    // Currently selected wizard UI language ('en' or 'zh').
    // Initialized from window.appConfig.language on first show().
    currentLang: 'en',
    state: {
        id: null,
        status: 0,
        name: '',
        avatar: '',
        password: '',
        confirm_password: '',
        profile: '',
        llm: 'OpenAI',
        llm_server: 'https://api.openai.com/v1/chat/completions',
        api_key: '',
        avatar3d: '',
        account: '',
        account_password: '',
        sns_url: '',
        map: 'Google',
        map_api_key: '',
        map_id: ''
    },

    // Resolve a localized label (sub-key under home.init_wizard) for the
    // current wizard language, reading from the language JSON via the global
    // i18n module. Falls back to English JSON, then to the raw key.
    t(key) {
        const fullKey = `${INIT_WIZARD_I18N_PREFIX}.${key}`;
        if (window.i18n && typeof window.i18n.ltFor === 'function') {
            const lang = (this.currentLang === 'zh') ? 'zh' : 'en';
            const val = window.i18n.ltFor(lang, fullKey, '');
            if (val) {
                return val;
            }
            const en = window.i18n.ltFor('en', fullKey, '');
            if (en) {
                return en;
            }
        }
        return key;
    },

    // Persist the chosen UI language to system config (system_cfg) and sync
    // the in-memory app config so the rest of the app (and a re-opened wizard)
    // reflects it immediately. Safe to call repeatedly; failures are non-fatal.
    async persistLanguage(lang) {
        const chosen = (String(lang || '').toLowerCase() === 'zh') ? 'zh' : 'en';
        try {
            if (window.api && typeof window.api.put === 'function') {
                await window.api.put('/api/system/config', { language: chosen });
            }
            if (!window.appConfig || typeof window.appConfig !== 'object') {
                window.appConfig = {};
            }
            window.appConfig.language = chosen;
            try {
                window.dispatchEvent(new CustomEvent('app-config-updated', {
                    detail: { language: chosen }
                }));
            } catch (_) {}
        } catch (e) {
            console.warn('[InitializationWizard] persistLanguage failed:', e);
        }
    },

    // Pick the initial wizard language from window.appConfig.language.
    resolveInitialLang() {
        try {
            const v = (window.appConfig && window.appConfig.language)
                ? String(window.appConfig.language).toLowerCase()
                : '';
            return v === 'zh' ? 'zh' : 'en';
        } catch (_) {
            return 'en';
        }
    },

    // Render the language selector that lives in the modal footer's
    // bottom-left corner. Returns an HTML string ready to be injected.
    renderLanguageSelectorHtml() {
        const lang = this.currentLang === 'zh' ? 'zh' : 'en';
        return `
            <div class="init-wizard-lang-selector" style="display:flex;align-items:center;gap:8px;margin-right:auto;">
                <label for="initWizardLangSelect" style="margin:0;font-size:12px;opacity:0.85;">${this.escapeHtml(this.t('languageLabel'))}</label>
                <select id="initWizardLangSelect" class="form-input" style="height:30px;padding:2px 8px;font-size:12px;min-width:120px;">
                    <option value="en" ${lang === 'en' ? 'selected' : ''}>English</option>
                    <option value="zh" ${lang === 'zh' ? 'selected' : ''}>中文</option>
                </select>
            </div>
        `;
    },

    // Insert (or refresh) the language selector inside the modal footer.
    // Uses margin-right:auto on the selector to push action buttons to the
    // right edge while the selector sits in the bottom-left corner.
    mountLanguageSelector() {
        if (!this.modal || !this.modal.element) {
            return;
        }
        const footer = this.modal.element.querySelector('.modal-footer');
        if (!footer) {
            return;
        }

        const existing = footer.querySelector('.init-wizard-lang-selector');
        if (existing) {
            existing.remove();
        }

        const wrapper = document.createElement('div');
        wrapper.innerHTML = this.renderLanguageSelectorHtml().trim();
        const node = wrapper.firstElementChild;
        if (!node) {
            return;
        }
        footer.insertBefore(node, footer.firstChild);

        const select = node.querySelector('#initWizardLangSelect');
        if (select) {
            select.addEventListener('change', async (e) => {
                const next = String(e.target.value || 'en').toLowerCase() === 'zh' ? 'zh' : 'en';
                select.disabled = true;
                // Preserve user input on the current step before re-rendering.
                this.collectFormValues();
                // Load the target language dictionary from JSON before
                // re-rendering so all labels resolve correctly.
                if (window.i18n && typeof window.i18n.ensureLang === 'function') {
                    try {
                        await window.i18n.ensureLang(next);
                    } catch (_) {}
                }
                this.currentLang = next;
                // Persist the language choice to system config immediately, so
                // that closing the wizard before completing initialization does
                // not lose the selection (it is restored on next open).
                await this.persistLanguage(next);
                this.updateModal();
            });
        }
    },

    sanitizeTestMessage(message) {
        if (window.Toast && typeof window.Toast.sanitizeMessage === 'function') {
            return window.Toast.sanitizeMessage(message);
        }
        let text = (message || '').toString().trim();
        text = text.replace(/\bsk-proj-[A-Za-z0-9_\-*]{12,}\b/g, (v) => `${v.slice(0, 6)}...${v.slice(-4)}`);
        text = text.replace(/\bsk-svcac[A-Za-z0-9_\-*]{12,}\b/g, (v) => `${v.slice(0, 6)}...${v.slice(-4)}`);
        text = text.replace(/\bsk-[A-Za-z0-9_\-*]{12,}\b/g, (v) => `${v.slice(0, 6)}...${v.slice(-4)}`);
        text = text.replace(/[ \t\r\n]+/g, ' ').trim();
        return text.length > 420 ? `${text.slice(0, 420).trim()}...` : text;
    },

    setInlineTestResult(type, message) {
        if (!this.modal || !this.modal.element) {
            return;
        }
        const root = this.modal.element.querySelector('#initWizard');
        if (!root) {
            return;
        }
        const el = root.querySelector('#initInlineTestResult');
        if (!el) {
            return;
        }
        const text = this.sanitizeTestMessage(message);
        if (!text) {
            el.style.display = 'none';
            el.textContent = '';
            return;
        }
        el.style.display = 'block';
        el.textContent = text;
        el.style.maxWidth = '100%';
        el.style.overflowWrap = 'anywhere';
        el.style.whiteSpace = 'pre-wrap';

        const ok = type === 'success';
        el.style.borderColor = ok ? 'rgba(46, 204, 113, 0.65)' : 'rgba(231, 76, 60, 0.65)';
        el.style.background = ok ? 'rgba(46, 204, 113, 0.08)' : 'rgba(231, 76, 60, 0.08)';
        el.style.color = ok ? 'rgba(46, 204, 113, 0.95)' : 'rgba(231, 76, 60, 0.95)';
    },

    setTestingState(kind, isTesting) {
        if (!this.modal || !this.modal.element) {
            return;
        }
        const root = this.modal.element.querySelector('#initWizard');
        if (!root) {
            return;
        }

        const map = {
            llm: { btn: '#initTestLlmBtn', indicator: '#initLlmTestingIndicator' },
            xmpp: { btn: '#initTestXmppBtn', indicator: '#initXmppTestingIndicator' }
        };
        const cfg = map[kind];
        if (!cfg) {
            return;
        }

        const btn = root.querySelector(cfg.btn);
        const indicator = root.querySelector(cfg.indicator);

        if (btn) {
            try { btn.disabled = !!isTesting; } catch (_) {}
        }

        if (indicator) {
            indicator.style.display = isTesting ? 'flex' : 'none';
        }
    },

    clearAllTestingState() {
        this.setTestingState('llm', false);
        this.setTestingState('xmpp', false);
    },

    async show(options = {}) {
        if (typeof Modal === 'undefined') {
            console.error('Modal component not loaded');
            return;
        }

        await this.loadInitialData();

        // Initialize wizard UI language from the global app config so that
        // the wizard reflects the user's previously chosen language.
        this.currentLang = this.resolveInitialLang();

        // Ensure the language dictionaries are loaded from JSON before any
        // rendering. English is always loaded as the fallback source.
        if (window.i18n && typeof window.i18n.ensureLang === 'function') {
            try {
                await window.i18n.ensureLang('en');
                await window.i18n.ensureLang(this.currentLang);
            } catch (e) {
                console.warn('[InitializationWizard] i18n load failed:', e);
            }
        }

        const auto = !!(options && options.auto);

        if (auto && Number(this.state.status) === 1) {
            return;
        }

        if (Number(this.state.status) === 1) {
            Modal.show({
                title: this.t('title'),
                content: this.renderReadonlySummary(),
                showCancel: false,
                confirmText: this.t('btn.close'),
                width: '820px',
                onOpen: (modal) => {
                    this.modal = modal;
                    this.mountLanguageSelector();
                },
                onClose: () => {
                    this.modal = null;
                }
            });
            return;
        }

        this.step = 0;

        Modal.show({
            title: this.t('title'),
            content: this.renderStep(),
            showCancel: true,
            cancelText: this.t('btn.cancel'),
            confirmText: this.t('btn.next'),
            width: '820px',
            closeOnClickOutside: false,
            onOpen: (modal) => {
                this.modal = modal;
                this.mountLanguageSelector();
                this.bindStepEvents();
            },
            onCancel: async () => {
                if (this.step > 0) {
                    this.collectFormValues();
                    await this.saveDraftSilently();
                    this.step -= 1;
                    this.updateModal();
                    return false;
                }

                this.cleanupCaptchaObjectUrl();
                if (window.electronAPI && typeof window.electronAPI.quitApp === 'function') {
                    window.electronAPI.quitApp();
                } else if (window.electronAPI && typeof window.electronAPI.windowClose === 'function') {
                    window.electronAPI.windowClose();
                } else {
                    window.close();
                }
                return true;
            },
            onConfirm: async () => {
                this.collectFormValues();

                const validateResult = this.validateCurrentStep();
                if (validateResult !== true) {
                    return false;
                }

                if (this.step < 4) {
                    await this.saveDraftSilently();
                    this.step += 1;
                    this.updateModal();
                    return false;
                }

                const captchaCode = (this.state.captcha_code || '').trim();
                if (!this.captcha.id || !captchaCode) {
                    if (typeof Notification !== 'undefined') {
                        Notification.error(this.t('notify.enterCaptcha'));
                    }
                    return false;
                }

                try {
                    const payload = {
                        ...this.state,
                        avatar3d: this.avatar3dSubmitValue(this.state.avatar3d),
                        captcha_id: this.captcha.id,
                        captcha_code: captchaCode
                    };

                    const res = await window.api.post('/api/system/init-wizard/submit', payload);
                    if (res && res.success) {
                        if (typeof Notification !== 'undefined') {
                            Notification.success(this.t('notify.configSaved'));
                        }
                        try {
                            const mapTypeValue = this.state.map === 'Baidu' ? '1' : '0';
                            localStorage.setItem('sns_map_type', mapTypeValue);
                        } catch (e) {
                        }
                        // Persist the chosen wizard language to system config
                        // so the rest of the app picks it up after init.
                        await this.persistLanguage(this.currentLang);
                        this.cleanupCaptchaObjectUrl();
                        return true;
                    }

                    if (typeof Notification !== 'undefined') {
                        Notification.error(res?.message || res?.detail || this.t('notify.submitFailed'));
                    }
                    return false;
                } catch (e) {
                    if (typeof Notification !== 'undefined') {
                        Notification.error(e.message || this.t('notify.submitFailed'));
                    }
                    return false;
                }
            },
            onClose: () => {
                this.cleanupCaptchaObjectUrl();
            }
        });
    },

    // Map an LLM dropdown label to its default API endpoint URL. Returns ''
    // for providers that require user-supplied endpoints (OpenAI Compatible).
    defaultServerForLlm(llm) {
        const urlMap = {
            'OpenAI': 'https://api.openai.com/v1/chat/completions',
            'Claude': 'https://api.anthropic.com/v1/messages',
            'Gemini': 'https://generativelanguage.googleapis.com/v1beta/openai/chat/completions',
            'OpenAI Compatible': ''
        };
        const label = this.normalizeLlmLabel(llm);
        return Object.prototype.hasOwnProperty.call(urlMap, label) ? urlMap[label] : '';
    },

    normalizeLlmLabel(llm) {
        const raw = String(llm || '').trim();
        if (!raw) {
            return 'OpenAI';
        }
        const map = {
            openai: 'OpenAI',
            claude: 'Claude',
            gemini: 'Gemini',
            custom: 'OpenAI Compatible'
        };
        return map[raw.toLowerCase()] || raw;
    },

    async loadInitialData() {
        try {
            const draftRes = await window.api.get('/api/system/init-wizard/draft');
            if (draftRes && draftRes.success && draftRes.data) {
                this.state = { ...this.state, ...draftRes.data };
            }
        } catch (e) {
            console.warn('Failed to load init draft:', e);
        }

        this.state.llm = this.normalizeLlmLabel(this.state.llm);

        // Ensure LLM Server has a sensible default that matches the
        // currently-selected LLM provider. The backend draft may store
        // null/empty llm_server before the user reaches the LLM step, and the
        // draft request itself may fail on first launch.
        if (!String(this.state.llm_server || '').trim()) {
            this.state.llm_server = this.defaultServerForLlm(this.state.llm) || '';
        }

        try {
            const avatarRes = await window.api.get('/api/system/init-wizard/avatar3d');
            if (avatarRes && avatarRes.success && Array.isArray(avatarRes.data)) {
                this.avatar3dItems = avatarRes.data;
            }
        } catch (e) {
            console.warn('Failed to load avatar3d list:', e);
        }
    },

    // Normalize an avatar3d value for submission. Local-host URLs
    // (127.0.0.1/localhost) and plain paths are reduced to just their
    // filename (e.g. "ctboychinese_0_0_0_0_1_0.glb"), matching the behavior
    // of SNSAdvancedDialog. Remote custom URLs are kept as-is.
    avatar3dSubmitValue(value) {
        const raw = String(value || '').trim();
        if (!raw) {
            return '';
        }

        const isWeb = /^(https?:)?\/\//i.test(raw);
        const isLocal = /^https?:\/\/(127\.0\.0\.1|localhost)(:\d+)?(\/|$)/i.test(raw);

        if (isWeb && !isLocal) {
            return raw;
        }

        const cleaned = raw.split('#')[0].split('?')[0];
        return cleaned.split('/').pop().split('\\').pop();
    },

    apiBaseUrl() {
        const raw = (window.api && window.api.baseUrl)
            || (window.appConfig && window.appConfig.agent_server)
            || '';
        if (raw) return String(raw).replace(/\/+$/, '');
        if (typeof window.resolveAgentServerUrl === 'function') {
            try {
                const u = new URL(window.resolveAgentServerUrl('/'));
                return u.origin;
            } catch (e) {
                return '';
            }
        }
        return '';
    },

    renderReadonlySummary() {
        const avatarUrl = this.state.avatar ? `${this.apiBaseUrl()}/images/avatars/${this.state.avatar}` : '';
        return `
            <div class="initialization-wizard">
                <div style="display:flex;gap:16px;align-items:flex-start;">
                    <div style="width:88px;">
                        ${avatarUrl ? `<img src="${avatarUrl}" style="width:70px;height:70px;border-radius:50%;object-fit:cover;display:block;margin:0 auto;"/>` : ''}
                    </div>
                    <div style="flex:1;">
                        <h4 style="margin:0 0 8px 0;">${this.escapeHtml(this.t('summary.complete'))}</h4>
                        <div style="opacity:0.9;">
                            <div><strong>${this.escapeHtml(this.t('summary.nickname'))}:</strong> ${this.escapeHtml(this.state.name || '')}</div>
                            <div><strong>${this.escapeHtml(this.t('summary.account'))}:</strong> ${this.escapeHtml(this.state.account || '')}</div>
                            <div><strong>${this.escapeHtml(this.t('summary.map'))}:</strong> ${this.escapeHtml(this.state.map || '')}</div>
                            <div><strong>${this.escapeHtml(this.t('summary.avatar3d'))}:</strong> ${this.escapeHtml(this.state.avatar3d || '')}</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    renderStep() {
        const steps = [
            { key: 'basic', title: this.t('tab.basic') },
            { key: 'llm', title: this.t('tab.llm') },
            { key: 'xmpp', title: this.t('tab.xmpp') },
            { key: 'map', title: this.t('tab.map') },
            { key: 'submit', title: this.t('tab.submit') }
        ];

        return `
            <div class="initialization-wizard" id="initWizard">
                <div class="settings-tabs" style="margin-bottom:12px;">
                    ${steps.map((s, idx) => `
                        <button class="settings-tab-btn ${idx === this.step ? 'active' : ''}" data-step="${idx}" type="button" disabled>${s.title}</button>
                    `).join('')}
                </div>

                <div class="init-wizard-body">
                    ${this.step === 0 ? this.renderBasicStep() : ''}
                    ${this.step === 1 ? this.renderLlmStep() : ''}
                    ${this.step === 2 ? this.renderXmppStep() : ''}
                    ${this.step === 3 ? this.renderMapStep() : ''}
                    ${this.step === 4 ? this.renderCaptchaStep() : ''}
                </div>
            </div>
        `;
    },

    renderBasicStep() {
        const avatarUrl = this.state.avatar ? `${this.apiBaseUrl()}/images/avatars/${this.state.avatar}` : `${this.apiBaseUrl()}/images/avatar.png`;

        return `
            <div class="init-step init-step-basic">
                <div style="display:flex;gap:16px;align-items:flex-start;">
                    <div style="width:96px;text-align:center;">
                        <img id="initAvatarPreview" src="${avatarUrl}" style="width:70px;height:70px;border-radius:50%;object-fit:cover;border:1px solid rgba(255,255,255,0.2);display:block;margin:0 auto;" />
                        <div style="margin-top:8px;display:flex;flex-direction:column;gap:6px;align-items:center;">
                            <input id="initAvatarFile" type="file" accept="image/*" style="display:none;" />
                            <button class="btn btn-secondary" id="initAvatarSelectBtn" type="button" style="width:92px;display:block;margin:0 auto;">${this.escapeHtml(this.t('btn.upload'))}</button>
                            <div id="initAvatarFileName" style="font-size:11px;opacity:0.75;max-width:96px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"></div>
                        </div>
                    </div>

                    <div style="flex:1;">
                        <div class="form-group">
                            <label>${this.escapeHtml(this.t('basic.nickname'))}</label>
                            <input class="form-input" id="initName" type="text" value="${this.escapeHtml(this.state.name || '')}" />
                        </div>

                        <div class="form-row" style="display:flex;gap:12px;">
                            <div class="form-group" style="flex:1;">
                                <label>${this.escapeHtml(this.t('basic.password'))}</label>
                                <input class="form-input" id="initPassword" type="password" value="${this.escapeHtml(this.state.password || '')}" />
                            </div>
                            <div class="form-group" style="flex:1;">
                                <label>${this.escapeHtml(this.t('basic.confirmPassword'))}</label>
                                <input class="form-input" id="initConfirmPassword" type="password" value="${this.escapeHtml(this.state.confirm_password || '')}" />
                            </div>
                        </div>

                        <div class="form-group">
                            <label>${this.escapeHtml(this.t('basic.bio'))}</label>
                            <textarea class="form-input" id="initProfile" placeholder="${this.escapeHtml(this.t('basic.bioPlaceholder'))}" rows="3">${this.escapeHtml(this.state.profile || '')}</textarea>
                        </div>

                        <div class="form-group">
                            <label>${this.escapeHtml(this.t('basic.snsUrl'))}</label>
                            <input class="form-input" id="initSnsUrl" type="text" placeholder="${this.escapeHtml(this.t('basic.snsUrlPlaceholder'))}" value="${this.escapeHtml(this.state.sns_url || '')}" />
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    renderLlmStep() {
        const llmOptions = [
            'OpenAI',
            'Claude',
            'Gemini',
            'OpenAI Compatible'
        ];

        return `
            <div class="init-step init-step-llm">
                <div class="form-group">
                    <label>${this.escapeHtml(this.t('llm.llm'))}</label>
                    <select class="form-input" id="initLlm">
                        ${llmOptions.map(o => `<option value="${this.escapeHtml(o)}" ${o === this.state.llm ? 'selected' : ''}>${this.escapeHtml(o)}</option>`).join('')}
                    </select>
                </div>

                <div class="form-group">
                    <label>${this.escapeHtml(this.t('llm.server'))}</label>
                    <input class="form-input" id="initLlmServer" type="text" value="${this.escapeHtml(this.state.llm_server || '')}" />
                </div>

                <div class="form-group">
                    <label>${this.escapeHtml(this.t('llm.apiKey'))}</label>
                    <input class="form-input" id="initApiKey" type="text" value="${this.escapeHtml(this.state.api_key || '')}" />
                </div>

                <div class="form-group">
                    <div id="initInlineTestResult" style="display:none; border:1px solid rgba(255,255,255,0.1); border-radius:10px; padding:12px 16px; background:rgba(255,255,255,0.03); font-family:var(--font-mono, monospace); font-size:12px; line-height:1.5;"></div>
                </div>

                <div class="form-group" style="display:flex;justify-content:flex-end;align-items:center;gap:12px;margin-top:16px;">
                    <div id="initLlmTestingIndicator" style="display:none; align-items:center; gap:8px; color:var(--color-primary, #1a73e8); font-size:13px; font-weight:500; transition: all 0.2s;">
                        <div class="spinner" style="width:16px; height:16px; border-width:2px; margin:0;"></div>
                        <span>${this.escapeHtml(this.t('common.testing'))}</span>
                    </div>
                    <button class="btn btn-secondary" id="initTestLlmBtn" type="button" style="min-width:80px; transition: all 0.2s;">${this.escapeHtml(this.t('btn.test'))}</button>
                </div>
            </div>
        `;
    },

    renderXmppStep() {
        return `
            <div class="init-step init-step-xmpp">
                <div class="form-row" style="display:flex;gap:12px;">
                    <div class="form-group" style="flex:1;">
                        <label>${this.escapeHtml(this.t('xmpp.account'))}</label>
                        <input class="form-input" id="initAccount" type="text" value="${this.escapeHtml(this.state.account || '')}" />
                    </div>
                    <div class="form-group" style="flex:1;">
                        <label>${this.escapeHtml(this.t('xmpp.password'))}</label>
                        <input class="form-input" id="initAccountPassword" type="password" value="${this.escapeHtml(this.state.account_password || '')}" />
                    </div>
                </div>

                <div class="form-group" style="display:flex;justify-content:flex-start;">
                    <div style="display:flex;align-items:center;gap:8px;white-space:nowrap;">
                        <label style="white-space:nowrap;margin:0;">${this.escapeHtml(this.t('xmpp.noAccount'))}</label>
                        <a href="#" id="initSnsRegisterLink" style="font-size:12px;white-space:nowrap;display:inline-flex;align-items:center;gap:6px;">${this.escapeHtml(this.t('btn.getOne'))}</a>
                    </div>
                </div>

                <div class="form-group">
                    <div id="initInlineTestResult" style="display:none; border:1px solid rgba(255,255,255,0.1); border-radius:10px; padding:12px 16px; background:rgba(255,255,255,0.03); font-family:var(--font-mono, monospace); font-size:12px; line-height:1.5;"></div>
                </div>

                <div class="form-group" style="display:flex;justify-content:flex-end;align-items:center;gap:12px;margin-top:16px;">
                    <div id="initXmppTestingIndicator" style="display:none; align-items:center; gap:8px; color:var(--color-primary, #1a73e8); font-size:13px; font-weight:500; transition: all 0.2s;">
                        <div class="spinner" style="width:16px; height:16px; border-width:2px; margin:0;"></div>
                        <span>${this.escapeHtml(this.t('common.testing'))}</span>
                    </div>
                    <button class="btn btn-secondary" id="initTestXmppBtn" type="button" style="min-width:80px; transition: all 0.2s;">${this.escapeHtml(this.t('btn.test'))}</button>
                </div>
            </div>
        `;
    },

    renderMapStep() {
        const avatarGrid = this.avatar3dItems.map(item => {
            const selected = this.avatar3dSubmitValue(item.glb_url) === this.avatar3dSubmitValue(this.state.avatar3d);
            return `
                <div class="avatar3d-item" data-glb-url="${this.escapeHtml(item.glb_url)}" style="cursor:pointer;border:1px solid ${selected ? '#1a73e8' : 'rgba(255,255,255,0.2)'};border-radius:10px;padding:6px;flex:0 0 auto;width:86px;">
                    <img src="${this.escapeHtml(item.png_url)}" style="width:72px;height:72px;object-fit:cover;border-radius:8px;display:block;margin:0 auto;" />
                    <div style="font-size:11px;opacity:0.85;margin-top:6px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${this.escapeHtml(item.key)}</div>
                </div>
            `;
        }).join('');

        const mapIdReadOnly = this.state.map === 'Baidu';
        const mapIdValue = mapIdReadOnly ? 'do_not_need_map_id' : (this.state.map_id || '');

        return `
            <div class="init-step init-step-map">
                <div class="form-group">
                    <div style="display:flex;align-items:baseline;gap:2ch;">
                        <label style="margin:0;">${this.escapeHtml(this.t('map.chooseAvatar'))}</label>
                        <a href="#" id="initAvatar3dLicensesLink" style="font-size:12px;white-space:nowrap;">${this.escapeHtml(this.t('btn.licenses'))}</a>
                    </div>
                    <div style="display:flex;align-items:center;gap:8px;">
                        <button class="btn btn-secondary" id="avatar3dPrevBtn" type="button" style="padding:6px 10px;">◀</button>
                        <div id="avatar3dGrid" style="display:flex;gap:10px;overflow-x:auto;overflow-y:hidden;scrollbar-width:thin;padding:6px 2px;flex:1;min-width:0;">
                            ${avatarGrid}
                        </div>
                        <button class="btn btn-secondary" id="avatar3dNextBtn" type="button" style="padding:6px 10px;">▶</button>
                    </div>
                    <input type="hidden" id="initAvatar3d" value="${this.escapeHtml(this.state.avatar3d || '')}" />
                </div>

                <div class="form-row" style="display:flex;gap:12px;align-items:center;">
                    <div class="form-group" style="flex:1;min-width:0;">
                        <label>${this.escapeHtml(this.t('map.mapType'))}</label>
                        <select class="form-input" id="initMapType">
                            <option value="Google" ${this.state.map === 'Google' ? 'selected' : ''}>Google</option>
                            <option value="Baidu" ${this.state.map === 'Baidu' ? 'selected' : ''}>Baidu</option>
                        </select>
                    </div>
                    <div class="form-group" style="flex:1;min-width:0;">
                        <div style="display:flex;align-items:center;gap:6px;white-space:nowrap;">
                            <span style="font-size:14px;opacity:0.9;">${this.escapeHtml(this.t('map.noApiKey'))}</span>
                            <a href="#" id="initMapRegisterLink" style="font-size:14px;white-space:nowrap;display:inline-flex;align-items:center;gap:6px;">${this.escapeHtml(this.t('btn.getOne'))}</a>
                        </div>
                    </div>
                </div>

                <div class="form-row" style="display:flex;gap:12px;">
                    <div class="form-group" style="flex:1;">
                        <label>${this.escapeHtml(this.t('map.apiKey'))}</label>
                        <input class="form-input" id="initMapApiKey" type="text" value="${this.escapeHtml(this.state.map_api_key || '')}" />
                    </div>
                    <div class="form-group" style="flex:1;min-width:0;">
                        <label>${this.escapeHtml(this.t('map.mapId'))}</label>
                        <input class="form-input" id="initMapId" type="text" value="${this.escapeHtml(mapIdValue)}" ${mapIdReadOnly ? 'readonly' : ''} />
                    </div>
                </div>

                <div class="form-group">
                    <div id="initInlineTestResult" style="display:none; border:1px solid rgba(255,255,255,0.1); border-radius:10px; padding:12px 16px; background:rgba(255,255,255,0.03); font-family:var(--font-mono, monospace); font-size:12px; line-height:1.5;"></div>
                </div>

                <div class="form-group" style="display:flex;justify-content:flex-end;margin-top:16px;">
                    <button class="btn btn-secondary" id="initTestMapBtn" type="button" style="min-width:80px; transition: all 0.2s;">${this.escapeHtml(this.t('btn.test'))}</button>
                </div>
            </div>
        `;
    },

    renderCaptchaStep() {
        return `
            <div class="init-step init-step-captcha">
                <div class="form-group">
                    <label>${this.escapeHtml(this.t('captcha.enter'))}</label>
                    <div style="display:flex;gap:12px;align-items:center;">
                        <input class="form-input" id="initCaptchaCode" type="text" value="${this.escapeHtml(this.state.captcha_code || '')}" style="flex:1;" />
                        <div id="initCaptchaImgWrap" style="position:relative;width:140px;height:56px;border:1px solid rgba(255,255,255,0.2);border-radius:6px;overflow:hidden;flex:0 0 auto;">
                            <img id="initCaptchaImg" style="width:100%;height:100%;object-fit:contain;display:none;" />
                            <div id="initCaptchaLoading" style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;gap:6px;font-size:12px;line-height:1.2;color:rgba(255,255,255,0.7);text-align:center;padding:4px 6px;box-sizing:border-box;">
                                <span id="initCaptchaSpinner" style="flex:0 0 auto;width:14px;height:14px;border:2px solid rgba(255,255,255,0.25);border-top-color:rgba(255,255,255,0.9);border-radius:50%;display:inline-block;animation:initCaptchaSpin 0.8s linear infinite;"></span>
                                <span id="initCaptchaLoadingText" style="flex:1 1 auto;min-width:0;white-space:normal;word-break:break-word;">${this.escapeHtml(this.t('captcha.loading'))}</span>
                            </div>
                        </div>
                        <button class="btn btn-secondary" id="initCaptchaRefresh" type="button">${this.escapeHtml(this.t('btn.refresh'))}</button>
                    </div>
                    <style>@keyframes initCaptchaSpin{to{transform:rotate(360deg);}}</style>
                </div>


            </div>
        `;
    },

    updateModal() {
        if (!this.modal || !this.modal.element) {
            return;
        }

        this.clearAllTestingState();

        const readonly = Number(this.state.status) === 1;
        const body = this.modal.element.querySelector('.modal-body');
        if (body) {
            body.innerHTML = readonly ? this.renderReadonlySummary() : this.renderStep();
        }

        const title = this.modal.element.querySelector('.modal-title');
        if (title) {
            title.textContent = this.t('title');
        }

        const cancelBtn = this.modal.element.querySelector('[data-action="cancel"]');
        const confirmBtn = this.modal.element.querySelector('[data-action="confirm"]');

        if (cancelBtn) {
            cancelBtn.textContent = this.step === 0 ? this.t('btn.cancel') : this.t('btn.previous');
        }

        if (confirmBtn) {
            confirmBtn.textContent = readonly ? this.t('btn.close') : (this.step < 4 ? this.t('btn.next') : this.t('btn.submit'));
        }

        // Re-mount the language selector so it reflects the current language
        // label and stays in the bottom-left of the footer after re-render.
        this.mountLanguageSelector();

        if (!readonly) {
            this.bindStepEvents();
        }
    },

    bindStepEvents() {
        if (!this.modal || !this.modal.element) {
            return;
        }

        this.clearAllTestingState();

        const closeBtn = this.modal.element.querySelector('[data-action="close"]');
        if (closeBtn && !closeBtn.dataset.initWizardBound) {
            closeBtn.dataset.initWizardBound = '1';
            closeBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopImmediatePropagation();
                this.cleanupCaptchaObjectUrl();

                if (window.electronAPI && typeof window.electronAPI.quitApp === 'function') {
                    window.electronAPI.quitApp();
                    return;
                }
                if (window.electronAPI && typeof window.electronAPI.windowClose === 'function') {
                    window.electronAPI.windowClose();
                    return;
                }
                window.close();
            }, true);
        }

        const root = this.modal.element.querySelector('#initWizard');
        if (!root) {
            return;
        }

        root.querySelectorAll('.settings-tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });

        const testLlmBtn = root.querySelector('#initTestLlmBtn');
        if (testLlmBtn) {
            testLlmBtn.addEventListener('click', async () => {
                this.collectFormValues();
                this.setInlineTestResult(null, '');
                try {
                    this.setTestingState('llm', true);

                    const providerMap = {
                        'OpenAI': 'openai',
                        'Claude': 'claude',
                        'Gemini': 'gemini',
                        'OpenAI Compatible': 'custom'
                    };

                    const modelCandidatesMap = {
                        openai: ['gpt-4o-mini', 'gpt-4o', 'gpt-4.1-mini'],
                        gemini: ['gemini-3.1-flash-lite-preview'],
                        claude: ['claude-sonnet-4-6', 'claude-haiku-4-5']
                    };

                    // For OpenAI-compatible (custom) endpoints, auto-detect the
                    // upstream provider from the endpoint URL so we only test a
                    // small set of relevant model names. Falls back to generic
                    // candidates when the endpoint is unrecognized.
                    const detectCustomCandidates = (rawEndpoint) => {
                        const u = String(rawEndpoint || '').toLowerCase();
                        if (u.includes('deepseek.com'))                       return ['deepseek-v4-flash', 'deepseek-v4-pro'];
                        if (u.includes('dashscope') || u.includes('aliyuncs')) return ['qwen-plus', 'qwen-turbo'];
                        if (u.includes('api.x.ai') || u.includes('//x.ai'))    return ['grok-4-fast', 'grok-3-mini'];
                        if (u.includes('bigmodel.cn'))                         return ['glm-4-flash', 'glm-4-plus'];
                        if (u.includes('minimax'))                             return ['MiniMax-M1', 'abab6.5s-chat'];
                        if (u.includes('moonshot'))                            return ['kimi-k2-0711-preview', 'moonshot-v1-8k'];
                        if (u.includes('mistral'))                             return ['mistral-small-latest'];
                        if (u.includes('volces') || u.includes('ark.cn'))      return ['doubao-seed-1-6', 'doubao-1-5-pro-32k-250115'];
                        if (u.includes('hunyuan') || u.includes('tencent'))    return ['hunyuan-turbos-latest', 'hunyuan-lite'];
                        if (u.includes('qianfan') || u.includes('baidubce'))   return ['ernie-speed-128k', 'ernie-4.5-turbo-128k'];
                        if (u.includes('openrouter'))                          return ['openrouter/auto'];
                        return ['gpt-4o-mini', 'deepseek-v4-flash'];
                    };

                    const provider = providerMap[this.state.llm] || 'custom';
                    const endpoint = String(this.state.llm_server || '').trim();
                    const apiKey = String(this.state.api_key || '').trim();

                    const candidates = (provider === 'custom')
                        ? detectCustomCandidates(endpoint)
                        : (modelCandidatesMap[provider] || ['gpt-4o-mini']);

                    let lastErr = null;
                    let okResult = null;
                    for (const modelName of candidates) {
                        try {
                            const res = await window.api.post('/api/agent/llm-configs/test', {
                                api_endpoint: endpoint,
                                api_key: apiKey,
                                model_name: modelName,
                                provider
                            });

                            if (res && res.success && res.data && String(res.data.status || '').toLowerCase() === 'success') {
                                okResult = res.data;
                                break;
                            }

                            lastErr = res?.error || res?.data?.message || res?.message || res?.detail || 'Test failed';
                        } catch (innerErr) {
                            lastErr = innerErr?.message || 'Test failed';
                        }
                    }

                    if (okResult) {
                        const messageLines = [
                            `${this.t('test.status')}: ${okResult.status || 'success'}`,
                            okResult.model ? `${this.t('test.model')}: ${okResult.model}` : '',
                            okResult.base_url ? `${this.t('test.baseUrl')}: ${okResult.base_url}` : '',
                            okResult.latency_ms != null ? `${this.t('test.latency')}: ${okResult.latency_ms} ${this.t('test.latencyMs')}` : '',
                            okResult.reply ? `${this.t('test.reply')}: ${okResult.reply}` : ''
                        ].filter(Boolean);
                        this.setInlineTestResult('success', messageLines.join('\n'));
                    } else {
                        this.setInlineTestResult('error', String(lastErr || this.t('test.failed')));
                    }
                } catch (e) {
                    this.setInlineTestResult('error', e.message || this.t('test.failed'));
                } finally {
                    this.setTestingState('llm', false);
                }
            });
        }

        const openUrlInDefaultBrowser = (url) => {
            const u = String(url || '').trim();
            if (!u) {
                return;
            }
            if (window.electronAPI && typeof window.electronAPI.openUrl === 'function') {
                window.electronAPI.openUrl(u);
            } else {
                window.open(u, '_blank');
            }
        };

        const testXmppBtn = root.querySelector('#initTestXmppBtn');
        if (testXmppBtn) {
            testXmppBtn.addEventListener('click', async () => {
                this.collectFormValues();
                this.setInlineTestResult(null, '');
                try {
                    this.setTestingState('xmpp', true);
                    const res = await window.api.post('/api/system/init-wizard/test-xmpp', {
                        account: this.state.account,
                        account_password: this.state.account_password
                    });
                    if (res && res.success) {
                        this.setInlineTestResult('success', res.message || this.t('test.passed'));
                    } else {
                        this.setInlineTestResult('error', res?.message || res?.detail || this.t('test.failed'));
                    }
                } catch (e) {
                    this.setInlineTestResult('error', e.message || this.t('test.failed'));
                } finally {
                    this.setTestingState('xmpp', false);
                }
            });
        }

        const snsRegisterLink = root.querySelector('#initSnsRegisterLink');
        if (snsRegisterLink) {
            snsRegisterLink.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                openUrlInDefaultBrowser('https://guide.ai-sns.org/docs.html#xmpp');
            });
        }

        const testMapBtn = root.querySelector('#initTestMapBtn');
        if (testMapBtn) {
            testMapBtn.addEventListener('click', async () => {
                this.collectFormValues();
                this.setInlineTestResult(null, '');
                const mapType = String(this.state.map || '').trim();
                const apiKey = String(this.state.map_api_key || '').trim();
                const mapId = String(this.state.map_id || '').trim();
                const qs = new URLSearchParams();
                if (apiKey) qs.set('api_key', apiKey);
                // Baidu test page no longer takes a Style ID, so map_id is
                // only forwarded for Google.
                if (mapType === 'Google' && mapId) qs.set('map_id', mapId);
                const query = qs.toString();
                const base = mapType === 'Google'
                    ? 'http://localhost:8788/static/googlemap3d_test.html'
                    : 'http://localhost:8788/static/map_test.html';
                const url = query ? `${base}?${query}` : base;
                openUrlInDefaultBrowser(url);
            });
        }

        const mapRegisterLink = root.querySelector('#initMapRegisterLink');
        if (mapRegisterLink) {
            mapRegisterLink.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                openUrlInDefaultBrowser('https://guide.ai-sns.org/docs.html#map');
            });
        }

        const avatar3dLicensesLink = root.querySelector('#initAvatar3dLicensesLink');
        if (avatar3dLicensesLink) {
            avatar3dLicensesLink.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                openUrlInDefaultBrowser('https://ai-sns.gitbook.io/docs/documentation/more/3d-assets-licenses');
            });
        }

        const fileInput = root.querySelector('#initAvatarFile');
        const fileSelectBtn = root.querySelector('#initAvatarSelectBtn');
        const fileNameEl = root.querySelector('#initAvatarFileName');
        if (fileSelectBtn && fileInput) {
            fileSelectBtn.addEventListener('click', () => {
                fileInput.click();
            });
        }
        if (fileInput) {
            fileInput.addEventListener('change', async () => {
                const file = fileInput.files && fileInput.files[0];
                if (!file) {
                    return;
                }

                if (fileNameEl) {
                    fileNameEl.textContent = file.name || '';
                }

                try {
                    const form = new FormData();
                    form.append('avatar_file', file);

                    const resp = await fetch(`${this.apiBaseUrl()}/api/system/init-wizard/avatar`, {
                        method: 'POST',
                        body: form
                    });
                    if (!resp.ok) {
                        const text = await resp.text();
                        throw new Error(text || resp.statusText);
                    }

                    const json = await resp.json();
                    if (!json.success) {
                        throw new Error(json.message || json.detail || this.t('notify.uploadFailed'));
                    }

                    this.state.avatar = json.data.avatar;
                    await this.saveDraftSilently();

                    const preview = root.querySelector('#initAvatarPreview');
                    if (preview) {
                        preview.src = `${this.apiBaseUrl()}/images/avatars/${this.state.avatar}`;
                    }

                    if (typeof Notification !== 'undefined') {
                        Notification.success(this.t('notify.avatarUpdated'));
                    }
                } catch (e) {
                    if (typeof Notification !== 'undefined') {
                        Notification.error(e.message || this.t('notify.avatarUploadFailed'));
                    }
                } finally {
                    fileInput.value = '';
                }
            });
        }

        const llmSelect = root.querySelector('#initLlm');
        if (llmSelect) {
            llmSelect.addEventListener('change', () => {
                const llm = llmSelect.value;
                const serverInput = root.querySelector('#initLlmServer');
                if (serverInput) {
                    serverInput.value = this.defaultServerForLlm(llm);
                }
            });
        }

        const mapType = root.querySelector('#initMapType');
        if (mapType) {
            mapType.addEventListener('change', () => {
                const mapId = root.querySelector('#initMapId');
                if (!mapId) {
                    return;
                }

                if (mapType.value === 'Baidu') {
                    mapId.value = 'do_not_need_map_id';
                    mapId.setAttribute('readonly', 'readonly');
                } else {
                    mapId.removeAttribute('readonly');
                    if (mapId.value === 'do_not_need_map_id') {
                        mapId.value = '';
                    }
                }
            });
        }

        const avatarGrid = root.querySelector('#avatar3dGrid');
        const prevBtn = root.querySelector('#avatar3dPrevBtn');
        const nextBtn = root.querySelector('#avatar3dNextBtn');
        if (avatarGrid) {
            if (typeof this._avatar3dScrollLeft === 'number') {
                avatarGrid.scrollLeft = this._avatar3dScrollLeft;
                this._avatar3dScrollLeft = null;
            }
            const scrollByAmount = (dir) => {
                const amount = Math.max(120, Math.floor((avatarGrid.clientWidth || 0) * 0.7));
                avatarGrid.scrollBy({ left: dir * amount, behavior: 'smooth' });
            };

            if (prevBtn) {
                prevBtn.addEventListener('click', () => scrollByAmount(-1));
            }
            if (nextBtn) {
                nextBtn.addEventListener('click', () => scrollByAmount(1));
            }

            avatarGrid.addEventListener('wheel', (e) => {
                if (Math.abs(e.deltaY) > Math.abs(e.deltaX)) {
                    avatarGrid.scrollLeft += e.deltaY;
                    e.preventDefault();
                }
            }, { passive: false });

            avatarGrid.querySelectorAll('.avatar3d-item').forEach(item => {
                item.addEventListener('click', async () => {
                    this._avatar3dScrollLeft = avatarGrid.scrollLeft;
                    // Store only the filename (e.g. "name.glb") for local/preset
                    // avatars so the submitted avatar3d stays consistent with
                    // SNSAdvancedDialog.
                    const glbUrl = this.avatar3dSubmitValue(item.dataset.glbUrl);
                    // Preserve other inputs the user has typed on this step
                    // (Map API Key / Map ID / Map Type) before we re-render.
                    this.collectFormValues();
                    this.state.avatar3d = glbUrl;
                    const hidden = root.querySelector('#initAvatar3d');
                    if (hidden) {
                        hidden.value = glbUrl;
                    }
                    await this.saveDraftSilently();
                    this.updateModal();
                });
            });
        }

        const captchaImg = root.querySelector('#initCaptchaImg');
        const captchaRefresh = root.querySelector('#initCaptchaRefresh');
        if (captchaImg && captchaRefresh) {
            captchaRefresh.addEventListener('click', async () => {
                try {
                    await this.loadCaptcha();
                } catch (e) {
                }
            });

            this.loadCaptcha().catch(() => {});
        }
    },

    collectFormValues() {
        if (!this.modal || !this.modal.element) {
            return;
        }

        const root = this.modal.element.querySelector('#initWizard');
        if (!root) {
            return;
        }

        const get = (sel) => {
            const el = root.querySelector(sel);
            return el ? el.value : '';
        };

        if (this.step === 0) {
            this.state.name = get('#initName');
            this.state.password = get('#initPassword');
            this.state.confirm_password = get('#initConfirmPassword');
            this.state.profile = get('#initProfile');
            this.state.sns_url = get('#initSnsUrl');
        } else if (this.step === 1) {
            this.state.llm = get('#initLlm');
            this.state.llm_server = get('#initLlmServer');
            this.state.api_key = get('#initApiKey');
        } else if (this.step === 2) {
            this.state.account = get('#initAccount');
            this.state.account_password = get('#initAccountPassword');
        } else if (this.step === 3) {
            this.state.avatar3d = get('#initAvatar3d');
            this.state.map = get('#initMapType');
            this.state.map_api_key = get('#initMapApiKey');
            this.state.map_id = get('#initMapId');
        } else if (this.step === 4) {
            this.state.captcha_code = get('#initCaptchaCode');
        }
    },

    validateCurrentStep() {
        const fail = (key) => {
            if (typeof Notification !== 'undefined') {
                Notification.error(this.t(key));
            }
            return false;
        };

        if (this.step === 0) {
            if (!this.state.name) return fail('notify.enterName');
            if (!this.state.avatar) return fail('notify.uploadAvatar');
            if (!this.state.password) return fail('notify.enterPassword');
            if (!this.state.confirm_password) return fail('notify.confirmPassword');
            if (!this.state.profile) return fail('notify.enterBio');

            if (this.state.password !== this.state.confirm_password) {
                return fail('notify.passwordMismatch');
            }

            if (!this.isPasswordValid(this.state.password)) {
                return fail('notify.passwordRule');
            }
        }

        if (this.step === 1) {
            if (!this.state.llm) return fail('notify.selectLlm');
            if (!this.state.llm_server) return fail('notify.enterLlmServer');
            if (!this.state.api_key) return fail('notify.enterApiKey');
        }

        if (this.step === 2) {
            if (!this.state.account) return fail('notify.enterXmppAccount');
            if (!this.state.account_password) return fail('notify.enterXmppPassword');
        }

        if (this.step === 3) {
            if (!this.state.avatar3d) return fail('notify.selectAvatar3d');
            if (!this.state.map) return fail('notify.selectMapType');
            if (!this.state.map_api_key) return fail('notify.enterMapKey');

            if (this.state.map === 'Baidu') {
                if (this.state.map_id !== 'do_not_need_map_id') {
                    this.state.map_id = 'do_not_need_map_id';
                }
            } else if (!this.state.map_id) {
                return fail('notify.enterMapId');
            }
        }

        return true;
    },

    isPasswordValid(password) {
        if (!password || password.length < 8) return false;
        const hasUpper = /[A-Z]/.test(password);
        const hasLower = /[a-z]/.test(password);
        const hasDigit = /[0-9]/.test(password);
        const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(password);
        return hasUpper && hasLower && hasDigit && hasSpecial;
    },

    async saveDraftSilently() {
        try {
            const payload = { ...this.state };
            delete payload.captcha_code;
            await window.api.put('/api/system/init-wizard/draft', payload);
        } catch (e) {
            console.warn('Save draft failed:', e);
        }
    },

    setCaptchaStatus(status) {
        if (!this.modal || !this.modal.element) {
            return;
        }
        const root = this.modal.element;
        const loading = root.querySelector('#initCaptchaLoading');
        const spinner = root.querySelector('#initCaptchaSpinner');
        const text = root.querySelector('#initCaptchaLoadingText');
        const img = root.querySelector('#initCaptchaImg');
        const refresh = root.querySelector('#initCaptchaRefresh');

        const isLoaded = status === 'loaded';
        if (loading) {
            loading.style.display = isLoaded ? 'none' : 'flex';
        }
        if (img) {
            img.style.display = isLoaded ? 'block' : 'none';
        }
        if (spinner) {
            spinner.style.display = status === 'loading' ? 'inline-block' : 'none';
        }
        if (text) {
            if (status === 'error') {
                text.textContent = this.t('captcha.loadFailed');
                text.style.color = 'rgba(255,120,120,0.95)';
                text.title = this.t('captcha.refreshTip');
            } else {
                text.textContent = this.t('captcha.loading');
                text.style.color = '';
                text.title = '';
            }
        }
        if (refresh) {
            refresh.disabled = status === 'loading';
            refresh.style.opacity = status === 'loading' ? '0.6' : '';
            refresh.style.cursor = status === 'loading' ? 'not-allowed' : '';
        }
    },

    async loadCaptcha() {
        const requestSeq = ++this.captchaRequestSeq;
        this.cleanupCaptchaObjectUrl();
        this.setCaptchaStatus('loading');

        try {
            const resp = await fetch(`${this.apiBaseUrl()}/api/system/init-wizard/captcha`, {
                method: 'GET'
            });
            if (!resp.ok) {
                throw new Error(await resp.text());
            }

            this.captcha.id = resp.headers.get('X-Captcha-ID') || '';
            const blob = await resp.blob();
            if (requestSeq !== this.captchaRequestSeq) {
                return;
            }
            this.captcha.objectUrl = URL.createObjectURL(blob);

            if (!this.modal || !this.modal.element) {
                return;
            }

            const img = this.modal.element.querySelector('#initCaptchaImg');
            if (img) {
                img.onload = () => {
                    if (requestSeq === this.captchaRequestSeq) {
                        this.setCaptchaStatus('loaded');
                    }
                };
                img.onerror = () => {
                    if (requestSeq === this.captchaRequestSeq) {
                        this.setCaptchaStatus('error');
                    }
                };
                img.src = this.captcha.objectUrl;
            }
        } catch (e) {
            if (requestSeq === this.captchaRequestSeq) {
                this.setCaptchaStatus('error');
            }
            throw e;
        }
    },

    cleanupCaptchaObjectUrl() {
        if (this.captcha.objectUrl) {
            try {
                URL.revokeObjectURL(this.captcha.objectUrl);
            } catch (_) {
            }
            this.captcha.objectUrl = '';
        }
    },

    escapeHtml(str) {
        return String(str || '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
};

export default InitializationWizard;
