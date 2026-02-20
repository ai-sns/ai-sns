/**
 * KM Module - Index
 * Knowledge base management module entry
 */

import KMPage from './KMPage.js';
import KMSidebar from './KMSidebar.js';
import kmHandlers from './kmHandlers.js';
import KMManagementDialog from './KMManagementDialog.js';

export default {
    name: 'km',
    version: '1.0.0',

    /**
     * Render main content area
     */
    renderPage() {
        // Return initial container, content will be rendered dynamically based on KB type
        return `
            <div id="km-main-content" class="km-main-content-wrapper">
                <div class="km-empty-state">
                    <p style="text-align: center; color: #999; padding: 40px;">
                        Please select a knowledge base from the sidebar
                    </p>
                </div>
            </div>
        `;
    },

    /**
     * Render sidebar
     */
    renderSidebar() {
        return KMSidebar.render();
    },

    /**
     * Initialize module
     */
    async init() {
        // Initialize handlers first so the initial kb switch event is not missed
        kmHandlers.init();

        // Initialize sidebar to load KB list (this will trigger initial kb selection)
        await KMSidebar.init();

        // Ensure KMManagementDialog is available globally
        if (!window.KMManagementDialog) {
            window.KMManagementDialog = KMManagementDialog;
        }
    },

    /**
     * Destroy module
     */
    destroy() {
        kmHandlers.destroy();
    }
};
