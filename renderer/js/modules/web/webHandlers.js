/**
 * Web Handlers - event handling
 */

const webHandlers = {
    webPage: null,
    webSidebar: null,

    init(webPage, webSidebar) {
        this.webPage = webPage;
        this.webSidebar = webSidebar;
        this.bindEvents();
    },

    bindEvents() {
        // Section header click - toggle expand/collapse
        document.addEventListener('click', (e) => {
            const header = e.target.closest('.web-section-header');
            if (header) {
                this.toggleSection(header);
            }
        });

        // Icon click - load URL in BrowserView
        document.addEventListener('click', (e) => {
            const iconItem = e.target.closest('.web-icon-item');
            if (iconItem && !e.ctrlKey && !e.metaKey && e.button === 0) {
                const url = iconItem.dataset.url;
                if (url) {
                    this.webPage.loadUrl(url);
                }
            }
        });

        // Icon right-click - show context menu
        document.addEventListener('contextmenu', (e) => {
            const iconItem = e.target.closest('.web-icon-item');
            if (iconItem) {
                e.preventDefault();
                this.showContextMenu(e, iconItem);
            }
        });

        // Add/Manage buttons
        document.addEventListener('click', (e) => {
            if (e.target.closest('#addLLMBtn')) {
                this.webSidebar.showAddDialog('LLM');
            } else if (e.target.closest('#manageLLMBtn')) {
                this.webSidebar.showManageDialog('LLM');
            } else if (e.target.closest('#addToolBtn')) {
                this.webSidebar.showAddDialog('Tool');
            } else if (e.target.closest('#manageToolBtn')) {
                this.webSidebar.showManageDialog('Tool');
            }
        });

        // Search functionality
        document.addEventListener('input', (e) => {
            if (e.target.id === 'llmSearchInput') {
                this.webSidebar.handleLLMSearch(e.target.value);
            } else if (e.target.id === 'toolSearchInput') {
                this.webSidebar.handleToolSearch(e.target.value);
            }
        });
    },

    toggleSection(header) {
        const section = header.closest('.web-section');
        const sectionType = header.dataset.section;

        if (sectionType === 'llm') {
            this.webSidebar.llmExpanded = !this.webSidebar.llmExpanded;
            this.webSidebar.toolExpanded = !this.webSidebar.llmExpanded;
        } else if (sectionType === 'tool') {
            this.webSidebar.toolExpanded = !this.webSidebar.toolExpanded;
            this.webSidebar.llmExpanded = !this.webSidebar.toolExpanded;
        }

        // Re-render sidebar - only update the web module's sidebar container
        const sidebar = document.getElementById('sidebar-web');
        if (sidebar) {
            sidebar.innerHTML = this.webSidebar.render();
        }
    },

    showContextMenu(e, iconItem) {
        const url = iconItem.dataset.url;
        const name = iconItem.dataset.name;

        const copyTextToClipboard = async (text) => {
            if (!text) return false;

            try {
                if (window.electronAPI && typeof window.electronAPI.writeClipboardText === 'function') {
                    const res = await window.electronAPI.writeClipboardText(text);
                    if (res && res.success) return true;
                }
            } catch (e) {
            }

            try {
                if (navigator.clipboard && typeof navigator.clipboard.writeText === 'function') {
                    await navigator.clipboard.writeText(text);
                    return true;
                }
            } catch (e) {
            }

            try {
                const textarea = document.createElement('textarea');
                textarea.value = text;
                textarea.setAttribute('readonly', '');
                textarea.style.position = 'fixed';
                textarea.style.top = '-9999px';
                textarea.style.left = '-9999px';
                document.body.appendChild(textarea);
                textarea.focus();
                textarea.select();
                const ok = document.execCommand('copy');
                document.body.removeChild(textarea);
                return !!ok;
            } catch (e) {
                return false;
            }
        };

        // Remove existing context menu
        const existingMenu = document.querySelector('.web-context-menu');
        if (existingMenu) {
            existingMenu.remove();
        }

        // Create context menu
        const menu = document.createElement('div');
        menu.className = 'web-context-menu';
        menu.style.left = e.pageX + 'px';
        menu.style.top = e.pageY + 'px';
        menu.style.flexDirection = 'column';
        menu.innerHTML = `
            <div class="web-context-menu-item" data-action="open-browser" title="Open in Default Browser">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                    <polyline points="15 3 21 3 21 9"/>
                    <line x1="10" y1="14" x2="21" y2="3"/>
                </svg>
            </div>
            <div class="web-context-menu-item" data-action="copy-url" title="Copy URL">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                </svg>
            </div>
        `;

        document.body.appendChild(menu);

        // Handle menu item clicks
        menu.addEventListener('click', async (e) => {
            const item = e.target.closest('.web-context-menu-item');
            if (item) {
                const action = item.dataset.action;
                if (action === 'open-browser') {
                    this.webPage.openInBrowser(url);
                } else if (action === 'copy-url') {
                    const ok = await copyTextToClipboard(url);
                    if (ok) {
                        console.log('URL copied to clipboard');
                    } else {
                        console.error('Copy failed');
                    }
                }
                menu.remove();
            }
        });

        // Close menu on outside click
        setTimeout(() => {
            document.addEventListener('click', function closeMenu() {
                menu.remove();
                document.removeEventListener('click', closeMenu);
            });
        }, 0);
    },

    filterIcons(type, searchTerm) {
        const section = document.querySelector(`.web-section[data-section="${type}"]`);
        if (!section) return;

        const icons = section.querySelectorAll('.web-icon-item');
        const term = searchTerm.toLowerCase();

        icons.forEach(icon => {
            const name = icon.dataset.name.toLowerCase();
            icon.style.display = name.includes(term) ? '' : 'none';
        });
    },

    // showAddModal() is deprecated; use WebSidebar.showAddDialog instead
    // Keep this note for future reference

    destroy() {
        // Cleanup if needed
    }
};

export default webHandlers;
