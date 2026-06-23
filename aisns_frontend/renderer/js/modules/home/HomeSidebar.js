/**
 * Home Sidebar - sidebar rendering
 */

const HomeSidebar = {
    render() {
        return `
            <div class="sidebar-section">
                <div class="sidebar-header-row">
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="#1a73e8">
                        <path d="M19.14 12.94c.04-.31.06-.63.06-.94 0-.31-.02-.63-.06-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.04.31-.06.63-.06.94s.02.63.06.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/>
                    </svg>
                    <span class="sidebar-section-title">${window.escHtml(window.tt('home.sidebar.setting'))}</span>
                </div>
                <div class="setting-buttons">
                    <button class="setting-btn" data-action="initialization">
                        <div class="setting-btn-icon">
                            <svg viewBox="0 0 48 48" width="48" height="48">
                                <rect x="8" y="8" width="32" height="32" rx="4" fill="none" stroke="#1a73e8" stroke-width="2"/>
                                <line x1="16" y1="18" x2="32" y2="18" stroke="#1a73e8" stroke-width="2"/>
                                <line x1="16" y1="24" x2="28" y2="24" stroke="#1a73e8" stroke-width="2"/>
                                <line x1="16" y1="30" x2="24" y2="30" stroke="#1a73e8" stroke-width="2"/>
                                <circle cx="30" cy="30" r="6" fill="none" stroke="#1a73e8" stroke-width="2"/>
                                <line x1="34" y1="34" x2="38" y2="38" stroke="#1a73e8" stroke-width="2"/>
                            </svg>
                        </div>
                        <span class="setting-btn-text">${window.escHtml(window.tt('home.sidebar.configuration'))}</span>
                    </button>
                    <button class="setting-btn" data-action="devtools">
                        <div class="setting-btn-icon">
                            <svg viewBox="0 0 48 48" width="48" height="48" fill="none" stroke="#1a73e8" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                                <polyline points="18,16 8,24 18,32"/>
                                <polyline points="30,16 40,24 30,32"/>
                                <line x1="27" y1="12" x2="21" y2="36"/>
                            </svg>
                        </div>
                        <span class="setting-btn-text">${window.escHtml(window.tt('home.sidebar.devtools'))}</span>
                    </button>
                </div>
            </div>
        `;
    }
};

export default HomeSidebar;
