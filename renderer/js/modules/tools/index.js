/**
 * Tools Module - Index
 * Tools management module entry
 */

import ToolsPage from './ToolsPage.js';
import ToolsSidebar from './ToolsSidebar.js';
import toolsHandlers from './toolsHandlers.js';

export default {
    name: 'tools',
    version: '1.0.0',

    /**
     * Render main content area
     */
    renderPage() {
        return ToolsPage.render();
    },

    /**
     * Render sidebar
     */
    renderSidebar() {
        return ToolsSidebar.render();
    },

    /**
     * Initialize module
     */
    init() {
        toolsHandlers.init();
    },

    /**
     * Destroy module
     */
    destroy() {
        toolsHandlers.destroy();
    }
};
