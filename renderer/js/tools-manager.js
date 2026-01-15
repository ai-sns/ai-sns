/**
 * Tools Module - Frontend JavaScript
 * Manages Plugins, MCP, Functions, and Computer Use tools
 */

class ToolsManager {
    constructor() {
        this.apiBaseUrl = '';
        this.currentTab = 'plugins'; // plugins, mcp, functions, skills
        this.currentItems = [];
        this.init();
    }

    async init() {
        // Get API base URL
        if (window.electronAPI) {
            this.apiBaseUrl = await window.electronAPI.getApiUrl();
        } else {
            this.apiBaseUrl = 'http://127.0.0.1:8788';
        }
        console.log('Tools Manager initialized with API:', this.apiBaseUrl);
    }

    // ==================== Plugin Methods ====================

    async getAllPlugins() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/tools/plugins`);
            if (!response.ok) throw new Error('Failed to fetch plugins');
            return await response.json();
        } catch (error) {
            console.error('Error fetching plugins:', error);
            this.showNotification('Failed to load plugins', 'error');
            return [];
        }
    }

    async createPlugin(data) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/tools/plugins`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (!response.ok) throw new Error('Failed to create plugin');
            const result = await response.json();
            this.showNotification('Plugin created successfully', 'success');
            return result;
        } catch (error) {
            console.error('Error creating plugin:', error);
            this.showNotification('Failed to create plugin', 'error');
            throw error;
        }
    }

    async updatePlugin(pluginId, data) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/tools/plugins/${pluginId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (!response.ok) throw new Error('Failed to update plugin');
            const result = await response.json();
            this.showNotification('Plugin updated successfully', 'success');
            return result;
        } catch (error) {
            console.error('Error updating plugin:', error);
            this.showNotification('Failed to update plugin', 'error');
            throw error;
        }
    }

    async deletePlugin(pluginId) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/tools/plugins/${pluginId}`, {
                method: 'DELETE'
            });
            if (!response.ok) throw new Error('Failed to delete plugin');
            this.showNotification('Plugin deleted successfully', 'success');
            return true;
        } catch (error) {
            console.error('Error deleting plugin:', error);
            this.showNotification('Failed to delete plugin', 'error');
            throw error;
        }
    }

    // ==================== MCP Methods ====================

    async getAllMCPs() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/tools/mcp`);
            if (!response.ok) throw new Error('Failed to fetch MCPs');
            return await response.json();
        } catch (error) {
            console.error('Error fetching MCPs:', error);
            this.showNotification('Failed to load MCPs', 'error');
            return [];
        }
    }

    async createMCP(data) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/tools/mcp`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (!response.ok) throw new Error('Failed to create MCP');
            const result = await response.json();
            this.showNotification('MCP created successfully', 'success');
            return result;
        } catch (error) {
            console.error('Error creating MCP:', error);
            this.showNotification('Failed to create MCP', 'error');
            throw error;
        }
    }

    async updateMCP(mcpId, data) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/tools/mcp/${mcpId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (!response.ok) throw new Error('Failed to update MCP');
            const result = await response.json();
            this.showNotification('MCP updated successfully', 'success');
            return result;
        } catch (error) {
            console.error('Error updating MCP:', error);
            this.showNotification('Failed to update MCP', 'error');
            throw error;
        }
    }

    async deleteMCP(mcpId) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/tools/mcp/${mcpId}`, {
                method: 'DELETE'
            });
            if (!response.ok) throw new Error('Failed to delete MCP');
            this.showNotification('MCP deleted successfully', 'success');
            return true;
        } catch (error) {
            console.error('Error deleting MCP:', error);
            this.showNotification('Failed to delete MCP', 'error');
            throw error;
        }
    }

    // ==================== Function Methods ====================

    async getAllFunctions() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/tools/functions`);
            if (!response.ok) throw new Error('Failed to fetch functions');
            return await response.json();
        } catch (error) {
            console.error('Error fetching functions:', error);
            this.showNotification('Failed to load functions', 'error');
            return [];
        }
    }

    async createFunction(data) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/tools/functions`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (!response.ok) throw new Error('Failed to create function');
            const result = await response.json();
            this.showNotification('Function created successfully', 'success');
            return result;
        } catch (error) {
            console.error('Error creating function:', error);
            this.showNotification('Failed to create function', 'error');
            throw error;
        }
    }

    async updateFunction(functionId, data) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/tools/functions/${functionId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (!response.ok) throw new Error('Failed to update function');
            const result = await response.json();
            this.showNotification('Function updated successfully', 'success');
            return result;
        } catch (error) {
            console.error('Error updating function:', error);
            this.showNotification('Failed to update function', 'error');
            throw error;
        }
    }

    async deleteFunction(functionId) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/tools/functions/${functionId}`, {
                method: 'DELETE'
            });
            if (!response.ok) throw new Error('Failed to delete function');
            this.showNotification('Function deleted successfully', 'success');
            return true;
        } catch (error) {
            console.error('Error deleting function:', error);
            this.showNotification('Failed to delete function', 'error');
            throw error;
        }
    }

    // ==================== Skill (Computer Use) Methods ====================

    async getAllSkills() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/tools/skills`);
            if (!response.ok) throw new Error('Failed to fetch skills');
            return await response.json();
        } catch (error) {
            console.error('Error fetching skills:', error);
            this.showNotification('Failed to load computer use tools', 'error');
            return [];
        }
    }

    async createSkill(data) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/tools/skills`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (!response.ok) throw new Error('Failed to create skill');
            const result = await response.json();
            this.showNotification('Computer use tool created successfully', 'success');
            return result;
        } catch (error) {
            console.error('Error creating skill:', error);
            this.showNotification('Failed to create computer use tool', 'error');
            throw error;
        }
    }

    async updateSkill(skillId, data) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/tools/skills/${skillId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (!response.ok) throw new Error('Failed to update skill');
            const result = await response.json();
            this.showNotification('Computer use tool updated successfully', 'success');
            return result;
        } catch (error) {
            console.error('Error updating skill:', error);
            this.showNotification('Failed to update computer use tool', 'error');
            throw error;
        }
    }

    async deleteSkill(skillId) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/tools/skills/${skillId}`, {
                method: 'DELETE'
            });
            if (!response.ok) throw new Error('Failed to delete skill');
            this.showNotification('Computer use tool deleted successfully', 'success');
            return true;
        } catch (error) {
            console.error('Error deleting skill:', error);
            this.showNotification('Failed to delete computer use tool', 'error');
            throw error;
        }
    }

    // ==================== UI Helper Methods ====================

    showNotification(message, type = 'info') {
        // Use the global notification system if available
        if (window.showNotification) {
            window.showNotification(message, type);
        } else {
            console.log(`[${type}] ${message}`);
        }
    }

    async loadCurrentTab() {
        let items = [];
        switch (this.currentTab) {
            case 'plugins':
                items = await this.getAllPlugins();
                break;
            case 'mcp':
                items = await this.getAllMCPs();
                break;
            case 'functions':
                items = await this.getAllFunctions();
                break;
            case 'skills':
                items = await this.getAllSkills();
                break;
        }
        this.currentItems = items;
        return items;
    }

    switchTab(tabName) {
        this.currentTab = tabName;
        this.loadCurrentTab();
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ToolsManager;
}

// Make available globally
window.ToolsManager = ToolsManager;
