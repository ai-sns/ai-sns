/**
 * Home Module - Index
 * Home module entry
 */

import HomePage from './HomePage.js';
import HomeSidebar from './HomeSidebar.js';
import homeHandlers from './homeHandlers.js';

export default {
    name: 'home',
    version: '1.0.0',

    /**
     * Render main content area
     */
    renderPage() {
        return HomePage.render();
    },

    /**
     * Render sidebar
     */
    renderSidebar() {
        return HomeSidebar.render();
    },

    /**
     * Initialize module
     */
    init() {
        homeHandlers.init();
    },

    /**
     * Destroy module
     */
    destroy() {
        homeHandlers.destroy();
    }
};
