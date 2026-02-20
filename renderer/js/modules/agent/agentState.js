/**
 * Agent State - multi-agent state management
 * Manages chat history, streaming state, etc. for multiple agents
 */

const agentState = {
    // Current active agent ID
    currentAgentId: null,

    // List of all agents
    agents: [],

    // Per-agent state { agent_id: { chatHistory, conversationId, modelConfig, roleConfig, ... } }
    agentStates: {},

    // Current request ID (for streaming responses)
    currentRequestId: null,

    // Current streaming content
    currentStreamingContent: '',

    // Model list
    models: [],

    // Role list
    roles: [],

    /**
     * Set current active agent
     */
    setCurrentAgent(agentId) {
        this.currentAgentId = agentId;
        // Initialize state if this agent does not have one yet
        if (!this.agentStates[agentId]) {
            this.agentStates[agentId] = {
                chatHistory: [],
                conversationId: null,
                currentModelConfig: null,
                currentRoleConfig: null,
                streamingContent: '',
                requestId: null,
                attachments: []
            };
        }
    },

    ensureAgentState(agentId) {
        if (!this.agentStates[agentId]) {
            this.agentStates[agentId] = {
                chatHistory: [],
                conversationId: null,
                currentModelConfig: null,
                currentRoleConfig: null,
                streamingContent: '',
                requestId: null,
                attachments: []
            };
        }
        return this.agentStates[agentId];
    },

    getAgentState(agentId) {
        return this.agentStates[agentId] || null;
    },

    /**
     * Get current agent
     */
    getCurrentAgent() {
        if (!this.currentAgentId) return null;
        return this.agents.find(a => a.id === this.currentAgentId);
    },

    /**
     * Get current agent state
     */
    getCurrentAgentState() {
        if (!this.currentAgentId || !this.agentStates[this.currentAgentId]) {
            return null;
        }
        return this.agentStates[this.currentAgentId];
    },

    /**
     * Set agents list
     */
    setAgents(agents) {
        this.agents = agents;
        // If there is no current agent yet, set the first one
        if (!this.currentAgentId && agents.length > 0) {
            this.setCurrentAgent(agents[0].id);
        }
    },

    /**
     * Get agents list
     */
    getAgents() {
        return this.agents;
    },

    /**
     * Add a message to the current agent chat history
     */
    addMessage(role, content) {
        const state = this.getCurrentAgentState();
        if (state) {
            state.chatHistory.push({ role, content });
        }
    },

    /**
     * Get current agent chat history
     */
    getChatHistory() {
        const state = this.getCurrentAgentState();
        return state ? [...state.chatHistory] : [];
    },

    /**
     * Clear current agent chat history
     */
    clearChatHistory() {
        const state = this.getCurrentAgentState();
        if (state) {
            state.chatHistory = [];
        }
    },

    /**
     * Set current agent conversation ID
     */
    setConversationId(id) {
        const state = this.getCurrentAgentState();
        if (state) {
            state.conversationId = id;
        }
    },

    /**
     * Get current agent conversation ID
     */
    getConversationId() {
        const state = this.getCurrentAgentState();
        return state ? state.conversationId : null;
    },

    /**
     * Generate a new conversation ID
     */
    generateConversationId() {
        return 'conv_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    },

    /**
     * Set current agent model config
     */
    setModel(configId) {
        const state = this.getCurrentAgentState();
        if (state) {
            if (!state.currentModelConfig) {
                state.currentModelConfig = {};
            }
            state.currentModelConfig.config_id = configId;
        }
    },

    /**
     * Get current agent model config
     */
    get currentModelConfig() {
        const state = this.getCurrentAgentState();
        return state ? state.currentModelConfig : null;
    },

    set currentModelConfig(config) {
        const state = this.getCurrentAgentState();
        if (state) {
            state.currentModelConfig = config;
        }
    },

    /**
     * Set current agent role config
     */
    setRole(roleId) {
        const state = this.getCurrentAgentState();
        if (state) {
            if (!state.currentRoleConfig) {
                state.currentRoleConfig = {};
            }
            state.currentRoleConfig.role_id = roleId;
        }
    },

    /**
     * Get current agent role config
     */
    get currentRoleConfig() {
        const state = this.getCurrentAgentState();
        return state ? state.currentRoleConfig : null;
    },

    set currentRoleConfig(config) {
        const state = this.getCurrentAgentState();
        if (state) {
            state.currentRoleConfig = config;
        }
    },

    /**
     * Get current agent system prompt
     */
    getSystemPrompt() {
        const roleConfig = this.currentRoleConfig;
        if (roleConfig && roleConfig.system_prompt) {
            return roleConfig.system_prompt;
        }
        // Fallback to default prompt
        return '你是一个有帮助的AI助手。';
    },

    /**
     * Set request ID (for streaming responses)
     */
    setRequestId(id) {
        this.currentRequestId = id;
        const state = this.getCurrentAgentState();
        if (state) {
            state.requestId = id;
        }
    },

    /**
     * Get request ID
     */
    getRequestId() {
        return this.currentRequestId;
    },

    /**
     * Clear request ID
     */
    clearRequestId() {
        this.currentRequestId = null;
        const state = this.getCurrentAgentState();
        if (state) {
            state.requestId = null;
        }
    },

    /**
     * Append streaming content
     */
    appendStreamingContent(content) {
        this.currentStreamingContent += content;
        const state = this.getCurrentAgentState();
        if (state) {
            state.streamingContent += content;
        }
    },

    /**
     * Get streaming content
     */
    getStreamingContent() {
        return this.currentStreamingContent;
    },

    /**
     * Clear streaming content
     */
    clearStreamingContent() {
        this.currentStreamingContent = '';
        const state = this.getCurrentAgentState();
        if (state) {
            state.streamingContent = '';
        }
    },

    /**
     * Set model list
     */
    setModels(models) {
        this.models = models;
    },

    /**
     * Get model list
     */
    getModels() {
        return this.models;
    },

    /**
     * Set role list
     */
    setRoles(roles) {
        this.roles = roles;
    },

    /**
     * Get role list
     */
    getRoles() {
        return this.roles;
    },

    /**
     * Reset all state
     */
    reset() {
        this.currentAgentId = null;
        this.agents = [];
        this.agentStates = {};
        this.currentRequestId = null;
        this.currentStreamingContent = '';
    }
};

export default agentState;
