/**
 * SNS Module - Index
 * SNS module entry
 */

import SNSPage from './SNSPage.js';
import SNSSidebar from './SNSSidebar.js';
import snsHandlers from './snsHandlers.js';

export default {
    name: 'sns',
    version: '1.0.0',

    /**
     * Render main content area
     */
    renderPage() {
        return SNSPage.render();
    },

    /**
     * Render sidebar
     */
    renderSidebar() {
        return SNSSidebar.render();
    },

    /**
     * Initialize module
     */
    async init() {
        snsHandlers.init();
        // Initialize sidebar charts and contacts
        await SNSSidebar.init();
        // Initialize SNS page (load model info)
        await SNSPage.init();
    },

    /**
     * Destroy module
     */
    destroy() {
        snsHandlers.destroy();
    }
};
