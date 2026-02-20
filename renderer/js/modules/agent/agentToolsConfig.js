/**
 * Agent Tools Config Event Handler
 * Handles click events for the tool configuration button
 */

// Use event delegation to handle dynamically created tool configuration buttons
document.addEventListener('click', function(e) {
    // Check whether the tool configuration button (or its child) was clicked
    const configBtn = e.target.closest('.config-tools-btn');

    if (configBtn) {
        e.preventDefault();
        e.stopPropagation();

        const agentId = configBtn.dataset.agentId;
        console.log('[AgentToolsConfig] Opening tools dialog for agent:', agentId);

        const page = document.getElementById(`page-agent-${agentId}`);
        const agentType = (page && page.dataset && page.dataset.agentType) ? String(page.dataset.agentType).toLowerCase() : '';
        if (agentType === 'remote') {
            const msg = 'This feature is not available for Remote agents.';
            if (typeof Notification !== 'undefined' && Notification.error) {
                Notification.error(msg);
            } else {
                alert(msg);
            }
            return;
        }

        // Open tool configuration dialog
        if (window.AgentToolsDialog) {
            window.AgentToolsDialog.open(agentId);
        } else {
            console.error('[AgentToolsConfig] AgentToolsDialog not loaded');
        }
    }
});

console.log('[AgentToolsConfig] Event handler initialized');
