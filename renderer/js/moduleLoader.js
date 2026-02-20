/**
 * Module Loader - load all modules
 * This file is responsible for importing and registering all modules to router
 */

// Import all modules (note: HTML must set type="module")
import homeModule from './modules/home/index.js';
import snsModule from './modules/sns/index.js';
import agentModule from './modules/agent/index.js';
import kmModule from './modules/km/index.js';
import toolsModule from './modules/tools/index.js';
import webModule from './modules/web/index.js';

/**
 * Initialize and register all modules
 */
function initializeModules() {
    if (!window.router) {
        console.error('Router not initialized');
        return false;
    }

    // Register all modules
    const modules = [
        { name: 'home', module: homeModule },
        { name: 'sns', module: snsModule },
        { name: 'agent', module: agentModule },
        { name: 'km', module: kmModule },
        { name: 'tools', module: toolsModule },
        { name: 'web', module: webModule }
    ];

    modules.forEach(({ name, module }) => {
        const success = window.router.register(name, module);
        if (success) {
            console.log(`✓ Module '${name}' registered successfully`);
        } else {
            console.error(`✗ Failed to register module '${name}'`);
        }
    });

    return true;
}

// Export init function
window.initializeModules = initializeModules;

// Auto-initialize in browser environment
if (typeof window !== 'undefined') {
    // Initialize after router is ready
    if (window.router) {
        initializeModules();
    } else {
        // If router isn't loaded yet, wait for DOMContentLoaded
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(initializeModules, 100);
        });
    }
}
