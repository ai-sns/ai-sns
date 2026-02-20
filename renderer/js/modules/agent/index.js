/**
 * Agent Module - Index (multi-agent version)
 * AI chat agent module entry
 */

import AgentPage from './AgentPage.js';
import AgentSidebar from './AgentSidebar.js';
import agentHandlers from './agentHandlers.js';
import multiAgentHandlers from './multiAgentHandlers.js';
import ModelManagementPage from './ModelManagementPage.js';
import RoleManagementPage from './RoleManagementPage.js';

export default {
    name: 'agent',
    version: '2.0.0', // Upgraded to 2.0.0 to indicate multi-agent version

    /**
     * Render main content area
     */
    renderPage() {
        return AgentPage.render();
    },

    /**
     * Render sidebar
     */
    renderSidebar() {
        return AgentSidebar.render();
    },

    /**
     * Initialize module (multi-agent version)
     */
    async init() {
        console.log('[AgentModule] 初始化多Agent系统...');

        try {
            // Initialize using multi-agent handlers
            await multiAgentHandlers.init();
            console.log('[AgentModule] 多Agent系统初始化完成');
        } catch (error) {
            console.error('[AgentModule] 初始化失败:', error);
            // Fallback to legacy mode
            console.warn('[AgentModule] 降级到传统单Agent模式');
            agentHandlers.init();
        }
    },

    /**
     * Destroy module
     */
    destroy() {
        if (agentHandlers && agentHandlers.destroy) {
            agentHandlers.destroy();
        }
    },

    /**
     * Export management pages
     */
    ModelManagementPage,
    RoleManagementPage,

    /**
     * Export handlers for external use
     */
    agentHandlers,
    multiAgentHandlers
};
