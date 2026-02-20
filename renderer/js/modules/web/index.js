/**
 * Web Module - Index
 * Web service module entry
 */

import WebPage from './WebPage.js';
import WebSidebar from './WebSidebar.js';
import webHandlers from './webHandlers.js';

export default {
    name: 'web',
    version: '1.0.0',

    /**
     * Render main content area
     */
    renderPage() {
        return WebPage.render();
    },

    /**
     * Render sidebar
     */
    renderSidebar() {
        return WebSidebar.render();
    },

    /**
     * Initialize module
     */
    async init() {
        console.log('[Web Module] Initializing...');
        await WebSidebar.init();

        // Re-render sidebar after data is loaded
        const sidebarContainer = document.getElementById('sidebar-web');
        console.log('[Web Module] Sidebar container:', sidebarContainer);
        if (sidebarContainer) {
            console.log('[Web Module] Re-rendering sidebar with data...');
            sidebarContainer.innerHTML = WebSidebar.render();
        } else {
            console.warn('[Web Module] Sidebar container not found!');
        }

        webHandlers.init(WebPage, WebSidebar);

        // Listen for page changes to hide/show BrowserView
        if (window.eventBus) {
            window.eventBus.on('page:changed', (data) => {
                if (data.from === 'web' && data.to !== 'web') {
                    console.log('[Web Module] Leaving web page, hiding BrowserView');
                    WebPage.hideBrowserView();
                } else if (data.to === 'web' && data.from !== 'web') {
                    console.log('[Web Module] Returning to web page, showing BrowserView');
                    WebPage.showBrowserView();
                }
            });
        }

        console.log('[Web Module] Initialization complete');
    },

    /**
     * Destroy module
     */
    destroy() {
        console.log('[Web Module] Destroying...');
        WebPage.closeBrowserView();
        webHandlers.destroy();
        
        // Clean up sidebar state
        const sidebarContainer = document.getElementById('secondarySidebar');
        if (sidebarContainer) {
            sidebarContainer.innerHTML = '';
        }
    }
};
