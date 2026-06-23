/**
 * AI-SNS Main Application
 * Application entry point and initialization
 */

const App = {
    currentPage: null,  // Initially null to ensure first navigation runs
    initialized: false,
    sidebarCollapsed: false,
    _snsEngineStartupStopAttempted: false,

    async init() {
        if (this.initialized) return;

        console.log('Initializing AI-SNS...');

        // Initialize theme
        this.initTheme();

        // Bind navigation events (high priority, non-blocking)
        this.bindNavigationEvents();

        // Bind sidebar collapse events
        this.bindSidebarToggle();

        // Bind window control buttons
        this.bindWindowControls();

        // Bind keyboard shortcuts
        this.bindKeyboardShortcuts();

        // Listen for Electron events
        this.bindElectronEvents();

        // Decide initial landing page by system_init.status: not initialized -> Home, initialized -> SNS.
        // Awaiting navigateTo ensures the initial page module's data load
        // completes before the bootstrap hides the global loading overlay.
        const initialPage = await this.getInitialPage();

        // Load the language dictionary (renderer/lang/*.json) before applying
        // any localized labels. window.appConfig.language was populated by
        // api.init() during bootstrap.
        await this.initI18n();

        // Localize the left navigation rail module names based on the
        // configured language.
        this.applyModuleLabels();

        // Reload the dictionary and re-apply localized module names whenever
        // the system config changes (e.g. user switches language in
        // Home > Configuration or completes the initialization wizard).
        window.addEventListener('app-config-updated', async (ev) => {
            const detailLang = ev && ev.detail && ev.detail.language;
            const langChanged = detailLang && window.i18n &&
                typeof window.i18n.getLangCode === 'function' &&
                String(detailLang).toLowerCase() !== window.i18n.getLangCode();

            await this.initI18n();
            this.applyModuleLabels();

            // When the active language changes, drop every cached page and
            // sidebar DOM so the next navigateTo() rebuilds them from the
            // newly loaded JSON dictionaries. Module-level state (open chat,
            // selected agent, etc.) is intentionally sacrificed for correctness
            // because the rendered HTML is the only place the translated text
            // lives at runtime.
            if (langChanged && window.router) {
                this.rerenderForLanguageChange();
            }
        });

        await this.navigateTo(initialPage);

        // Initialize API client asynchronously (non-blocking).
        // Health check is already done by the bootstrap; this only handles
        // WebSocket connection and engine-status side effects.
        this.initApiAsync();

        // Fix the issue where inputs cannot be edited in Windows frameless windows
        this.fixInputFocus();

        this.initialized = true;
        console.log('AI-SNS initialized successfully');
    },

    // Fix input focus issue
    fixInputFocus() {
        setTimeout(() => {
            // Create a temporary input to capture focus, then remove it
            const tempInput = document.createElement('input');
            tempInput.style.position = 'absolute';
            tempInput.style.opacity = '0';
            tempInput.style.pointerEvents = 'none';
            document.body.appendChild(tempInput);
            tempInput.focus();
            tempInput.blur();
            document.body.removeChild(tempInput);
        }, 200);
    },

    // Initialize API asynchronously (non-blocking)
    initApiAsync() {
        // Use Promise rather than await to avoid blocking
        Promise.resolve().then(async () => {
            try {
                await this.checkApiConnection();
                await this.ensureSnsEngineStoppedOnStartup();
                await this.initWebSocket();
            } catch (error) {
                console.warn('API initialization failed:', error);
            }
        });
    },

    async ensureSnsEngineStoppedOnStartup() {
        if (this._snsEngineStartupStopAttempted) return;
        this._snsEngineStartupStopAttempted = true;

        try {
            if (!window.api || typeof window.api.get !== 'function') {
                return;
            }

            const status = await window.api.get('/api/sns/engine-status');
            const taskStatus = String(status?.task_status || '').toLowerCase();
            const shouldStop = !!(
                status &&
                status.success &&
                (status.running || status.started || taskStatus === 'started' || taskStatus === 'paused')
            );

            if (!shouldStop) return;

            console.log('[App] Backend SNS engine is active on startup, stopping it...');
            await window.api.post('/api/sns/stop-engine', {});
        } catch (e) {
            console.warn('[App] Failed to stop SNS engine on startup:', e);
        }
    },

    async getInitialPage() {
        try {
            if (window.api && typeof window.api.init === 'function') {
                await window.api.init();
            }

            const res = await window.api.get('/api/system/init-wizard/draft');
            const status = Number(res?.data?.status);
            if (res && res.success && status !== 1) {
                return 'home';
            }
        } catch (e) {
            console.warn('[App] Failed to resolve initial page, fallback to sns:', e);
        }
        return 'sns';
    },

    async checkApiConnection() {
        try {
            // Set a timeout to avoid waiting too long
            const timeoutPromise = new Promise((_, reject) =>
                setTimeout(() => reject(new Error('Connection timeout')), 3000)
            );
            await Promise.race([api.healthCheck(), timeoutPromise]);
            console.log('API server connected');
        } catch (error) {
            console.error('API server connection failed:', error);
        }
    },

    async initWebSocket() {
        if (!api.connectWebSocket) return;

        const clientId = this.generateId();
        try {
            await api.connectWebSocket(clientId);

            // Listen for chat responses
            api.onWebSocketMessage('chat_response', (message) => {
                console.log('Received chat response:', message);
            });

            // Listen for map chat messages
            api.onWebSocketMessage('map_chat_message', (message) => {
                console.log('Received map chat message:', message);
                // TODO: Handle map chat messages, e.g. show in map chat UI
            });

            // Listen for notifications
            api.onWebSocketMessage('notification', (message) => {
                if (typeof Notification !== 'undefined' && Notification.info) {
                    Notification.info(message.content);
                }
            });

        } catch (error) {
            console.warn('WebSocket connection failed:', error);
        }
    },

    generateId() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    },

    bindNavigationEvents() {
        // Left navigation bar icon click events
        document.querySelectorAll('.nav-icon-item').forEach(item => {
            item.addEventListener('click', () => {
                const page = item.dataset.page;
                if (page) {
                    this.navigateTo(page);
                }
            });
        });
    },

    // Resolve the current UI language from system config (window.appConfig).
    currentLang() {
        return (window.appConfig && window.appConfig.language)
            ? String(window.appConfig.language).toLowerCase()
            : 'en';
    },

    // Load the current language dictionary from renderer/lang/*.json via the
    // global i18n module. JSON is the single source of truth for all labels.
    async initI18n() {
        if (window.i18n && typeof window.i18n.initI18n === 'function') {
            try {
                await window.i18n.initI18n(this.currentLang());
            } catch (e) {
                console.warn('[App] i18n init failed:', e);
            }
        }
    },

    // Apply localized module names to the left navigation rail. Strings come
    // from renderer/lang/{en,zh}.json -> "nav.<page>". The existing DOM text
    // is used as the fallback so the rail never goes blank if a key/file is
    // missing.
    applyModuleLabels() {
        const hasI18n = window.i18n && typeof window.i18n.ltFor === 'function';
        const lang = this.currentLang();
        document.querySelectorAll('.nav-icon-item[data-page]').forEach(item => {
            const page = item.dataset.page;
            const label = item.querySelector('.nav-label');
            if (!page || !label) return;
            const fallback = label.textContent;
            label.textContent = hasI18n
                ? window.i18n.ltFor(lang, `nav.${page}`, fallback)
                : fallback;
        });
    },

    // Rebuild every previously rendered page and sidebar after a language
    // switch. The router caches DOM under #mainContent/#secondarySidebar,
    // so we strip those caches and re-navigate to the current page; the
    // router's renderOrShowMainContent()/renderSidebar() will then call
    // module.renderPage()/renderSidebar() again and pick up the new JSON
    // strings. Module-level state (selected agent, scroll position, etc.)
    // is intentionally rebuilt by each module's init() hook.
    rerenderForLanguageChange() {
        try {
            const router = window.router;
            if (!router) return;
            const currentPage = (typeof router.getCurrentPage === 'function')
                ? router.getCurrentPage()
                : router.currentPage;

            const mainContent = document.getElementById('mainContent');
            if (mainContent) {
                mainContent.querySelectorAll('.page-container').forEach(el => el.remove());
            }
            const sidebarContainer = document.getElementById('secondarySidebar');
            if (sidebarContainer) {
                sidebarContainer.querySelectorAll('.sidebar-page-container').forEach(el => el.remove());
            }

            // Force navigateTo() to take the "first render" branch by clearing
            // the cached page id on the router.
            router.currentPage = null;
            if (currentPage) {
                router.navigateTo(currentPage);
            }
        } catch (e) {
            console.warn('[App] rerenderForLanguageChange failed:', e);
        }
    },

    bindSidebarToggle() {
        const resizer = document.getElementById('sidebarResizer');
        const collapseBtn = document.getElementById('sidebarCollapseBtn');
        const sidebar = document.getElementById('secondarySidebar');

        if (!resizer || !sidebar) return;

        // Sidebar width bounds
        const minWidth = 200;
        const maxWidth = 450;
        const defaultWidth = 280;
        let currentWidth = defaultWidth;
        let isResizing = false;
        let lastClickTime = 0;

        // Collapse button click
        if (collapseBtn) {
            collapseBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleSidebar();
            });
        }

        // Double click to collapse
        resizer.addEventListener('dblclick', () => {
            if (!this.sidebarCollapsed) {
                this.toggleSidebar();
            }
        });

        // Click to expand when collapsed
        resizer.addEventListener('click', () => {
            if (this.sidebarCollapsed) {
                this.toggleSidebar();
            }
        });

        // Drag to resize width
        resizer.addEventListener('mousedown', (e) => {
            if (this.sidebarCollapsed) return;
            if (e.target === collapseBtn || collapseBtn.contains(e.target)) return;

            isResizing = true;
            resizer.classList.add('resizing');
            document.body.style.cursor = 'col-resize';
            document.body.style.userSelect = 'none';

            // Disable iframe pointer events to avoid lag while dragging
            const iframes = document.querySelectorAll('iframe');
            iframes.forEach(iframe => {
                iframe.style.pointerEvents = 'none';
            });

            const startX = e.clientX;
            const startWidth = sidebar.offsetWidth;

            const onMouseMove = (e) => {
                if (!isResizing) return;

                const deltaX = e.clientX - startX;
                let newWidth = startWidth + deltaX;

                // Clamp width to bounds
                newWidth = Math.max(minWidth, Math.min(maxWidth, newWidth));

                // If dragged small enough, auto-collapse
                if (newWidth < minWidth + 20 && deltaX < -50) {
                    this.toggleSidebar();
                    onMouseUp();
                    return;
                }

                currentWidth = newWidth;
                sidebar.style.width = `${newWidth}px`;
            };

            const onMouseUp = () => {
                isResizing = false;
                resizer.classList.remove('resizing');
                document.body.style.cursor = '';
                document.body.style.userSelect = '';

                // Restore iframe pointer events
                iframes.forEach(iframe => {
                    iframe.style.pointerEvents = '';
                });

                document.removeEventListener('mousemove', onMouseMove);
                document.removeEventListener('mouseup', onMouseUp);
            };

            document.addEventListener('mousemove', onMouseMove);
            document.addEventListener('mouseup', onMouseUp);
        });

        // Save and restore sidebar state
        this.restoreSidebarState = () => {
            const savedWidth = localStorage.getItem('sidebarWidth');
            const savedCollapsed = localStorage.getItem('sidebarCollapsed');

            if (savedCollapsed === 'true') {
                this.sidebarCollapsed = true;
                sidebar.classList.add('collapsed');
                resizer.classList.add('collapsed');
            } else if (savedWidth) {
                currentWidth = parseInt(savedWidth, 10);
                sidebar.style.width = `${currentWidth}px`;
            }
        };

        this.saveSidebarState = () => {
            localStorage.setItem('sidebarWidth', currentWidth);
            localStorage.setItem('sidebarCollapsed', this.sidebarCollapsed);
        };

        // Restore initial state
        this.restoreSidebarState();
    },

    bindWindowControls() {
        // Window control buttons
        const closeBtn = document.getElementById('windowClose');
        const minimizeBtn = document.getElementById('windowMinimize');
        const maximizeBtn = document.getElementById('windowMaximize');

        if (closeBtn && window.electronAPI) {
            closeBtn.addEventListener('click', () => {
                window.electronAPI.windowClose();
            });
        }

        if (minimizeBtn && window.electronAPI) {
            minimizeBtn.addEventListener('click', () => {
                window.electronAPI.windowMinimize();
            });
        }

        if (maximizeBtn && window.electronAPI) {
            maximizeBtn.addEventListener('click', async () => {
                window.electronAPI.windowMaximize();
                // Update button icon state
                const isMaximized = await window.electronAPI.windowIsMaximized();
                maximizeBtn.classList.toggle('maximized', isMaximized);
            });
        }

        // Theme toggle button
        const themeToggleBtn = document.getElementById('themeToggleBtn');
        if (themeToggleBtn) {
            themeToggleBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                const currentTheme = this.getCurrentTheme();
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                console.log(`Switching theme from ${currentTheme} to ${newTheme}`);
                this.applyTheme(newTheme);
            });
        }
    },

    toggleSidebar() {
        this.sidebarCollapsed = !this.sidebarCollapsed;
        const sidebar = document.getElementById('secondarySidebar');
        const resizer = document.getElementById('sidebarResizer');
        const mainContent = document.getElementById('mainContent');

        if (this.sidebarCollapsed) {
            sidebar.classList.add('collapsed');
            resizer.classList.add('collapsed');
            mainContent.classList.add('sidebar-collapsed');
        } else {
            sidebar.classList.remove('collapsed');
            resizer.classList.remove('collapsed');
            mainContent.classList.remove('sidebar-collapsed');
        }

        // Update BrowserView bounds
        if (window.electronAPI && window.electronAPI.updateBrowserViewBounds) {
            window.electronAPI.updateBrowserViewBounds(this.sidebarCollapsed);
        }

        // Save state
        if (this.saveSidebarState) {
            this.saveSidebarState();
        }
    },

    bindKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + B: collapse/expand sidebar
            if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
                e.preventDefault();
                this.toggleSidebar();
            }

            // Ctrl/Cmd + K: search
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                this.showSearchModal();
            }

            // Ctrl/Cmd + 1-6: quick navigation
            if ((e.ctrlKey || e.metaKey) && e.key >= '1' && e.key <= '6') {
                e.preventDefault();
                const pages = ['sns', 'agent', 'km', 'tools', 'web', 'home'];
                const pageIndex = parseInt(e.key) - 1;
                if (pages[pageIndex]) {
                    this.navigateTo(pages[pageIndex]);
                }
            }
        });
    },

    bindElectronEvents() {
        if (!window.electronAPI) return;

        // Listen for menu actions
        window.electronAPI.onMenuAction((action) => {
            switch (action) {
                case 'about':
                    this.showAboutModal();
                    break;
                case 'help':
                    this.showHelpModal();
                    break;
            }
        });

        // Listen for navigation events
        window.electronAPI.onNavigate((page) => {
            this.navigateTo(page);
        });
    },

    navigateTo(page) {
        if (window.router) {
            // Return the underlying promise so callers (e.g. App.init / bootstrap)
            // can await the initial page module's data load.
            return window.router.navigateTo(page);
        }
        console.error('[App] Router not available, cannot navigate to:', page);
        return Promise.resolve();
    },

    // Resolve a UI string from renderer/lang/*.json via the global i18n
    // module. JSON files are the single source of truth; if i18n is
    // unavailable or a key is missing, the key itself is returned.
    _t(key) {
        if (window.i18n && typeof window.i18n.lt === 'function') {
            return window.i18n.lt(key);
        }
        return key;
    },

    // Build a placeholder-safe attribute value (no raw quotes/backticks
    // in template injection points).
    _escAttr(s) {
        return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    },

    _escHtml(s) {
        return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    },

    showSearchModal() {
        Modal.show({
            title: this._t('app.search.title'),
            content: `
                <div class="search-modal">
                    <input type="text" class="search-input-field" placeholder="${this._escAttr(this._t('app.search.placeholder'))}" autofocus>
                    <div class="search-results"></div>
                </div>
            `,
            showCancel: false,
            confirmText: this._t('app.search.close')
        });
    },

    getCurrentTheme() {
        if (document.body.classList.contains('theme-dark')) return 'dark';
        if (document.body.classList.contains('theme-light')) return 'light';
        return localStorage.getItem('theme') || 'light';
    },

    applyTheme(theme) {
        console.log(`Applying theme: ${theme}`);
        document.body.classList.remove('theme-light', 'theme-dark');
        document.body.classList.add(`theme-${theme}`);
        localStorage.setItem('theme', theme);
        window.dispatchEvent(new CustomEvent('theme-changed', { detail: { theme } }));
        console.log(`Body classes: ${document.body.className}`);
    },

    initTheme() {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            this.applyTheme(savedTheme);
        } else {
            // Detect system theme preference
            if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
                this.applyTheme('dark');
            } else {
                this.applyTheme('light');
            }
        }

        // Listen for system theme changes
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
                if (!localStorage.getItem('theme')) {
                    this.applyTheme(e.matches ? 'dark' : 'light');
                }
            });
        }
    },

    showAboutModal() {
        const t = (k) => this._escHtml(this._t(k));
        Modal.show({
            title: this._t('app.about.title'),
            content: `
                <div class="about-modal">
                    <div class="about-logo">
                        <svg viewBox="0 0 24 24" width="64" height="64" fill="#1a73e8">
                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                        </svg>
                    </div>
                    <h2>${t('app.about.name')}</h2>
                    <p class="about-subtitle">${t('app.about.subtitle')}</p>
                    <p class="about-version">${t('app.about.version')}</p>
                    <p class="about-desc">${t('app.about.description')}</p>
                    <p class="about-link">
                        <a href="https://www.ai-sns.net" target="_blank">www.ai-sns.net</a>
                    </p>
                </div>
            `,
            showCancel: false,
            confirmText: this._t('app.about.close')
        });
    },

    showHelpModal() {
        const t = (k) => this._escHtml(this._t(k));
        // Module list is rendered from the same nav.* keys as the sidebar,
        // paired with module-specific help descriptions, so labels stay in
        // sync with the navigation rail.
        const modulePages = ['sns', 'agent', 'km', 'tools', 'web', 'home'];
        const moduleItems = modulePages.map(p => {
            const name = t(`nav.${p}`);
            const desc = t(`app.help.module.${p}`);
            return `<li><strong>${name}</strong>${desc ? ` - ${desc}` : ''}</li>`;
        }).join('');

        Modal.show({
            title: t('app.help.title'),
            content: `
                <div class="help-modal">
                    <h4>${t('app.help.shortcutsHeading')}</h4>
                    <ul class="help-list">
                        <li><kbd>Ctrl/Cmd + B</kbd> ${t('app.help.shortcut.sidebar')}</li>
                        <li><kbd>Ctrl/Cmd + K</kbd> ${t('app.help.shortcut.search')}</li>
                        <li><kbd>Ctrl/Cmd + 1-6</kbd> ${t('app.help.shortcut.quickNav')}</li>
                        <li><kbd>Enter</kbd> ${t('app.help.shortcut.send')}</li>
                        <li><kbd>Shift + Enter</kbd> ${t('app.help.shortcut.newline')}</li>
                    </ul>
                    <h4>${t('app.help.sidebarHeading')}</h4>
                    <ul class="help-list">
                        <li><strong>${t('app.help.sidebar.dragTitle')}</strong> - ${t('app.help.sidebar.dragDesc')}</li>
                        <li><strong>${t('app.help.sidebar.doubleClickTitle')}</strong> - ${t('app.help.sidebar.doubleClickDesc')}</li>
                        <li><strong>${t('app.help.sidebar.floatingTitle')}</strong> - ${t('app.help.sidebar.floatingDesc')}</li>
                    </ul>
                    <h4>${t('app.help.modulesHeading')}</h4>
                    <ul class="help-list">
                        ${moduleItems}
                    </ul>
                </div>
            `,
            showCancel: false,
            confirmText: this._t('app.help.close')
        });
    }
};

// App initialization is driven by the startup bootstrap
// (renderer/js/core/bootstrap.js). The bootstrap waits for the backend
// to be ready, then calls `window.App.init()` and hides the global
// loading overlay once the initial landing page has finished loading.

// Export for global access
window.App = App;
