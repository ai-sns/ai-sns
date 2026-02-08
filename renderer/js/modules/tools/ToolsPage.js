/**
 * Tools Page - 主内容渲染
 */

const ToolsPage = {
    render() {
        return `
            <div class="tools-page tools-page-ref">
                <main class="tools-main-ref">
                    <div class="tools-main-ref__container">
                        <header class="tools-main-ref__header plugin-list-header">
                            <div>
                                <h1 class="plugin-list-title">Tools Plugin List</h1>
                                <p class="tools-main-ref__subtitle">Manage and test your Model Context Protocol servers</p>
                            </div>
                            <button class="tools-add-btn" onclick="toolsHandlers.showAddDialog(toolsHandlers.currentCategory)">
                                <span class="material-icons-round tools-main-ref__add-icon">add</span>
                                Add Tool
                            </button>
                        </header>
                        <div class="plugin-grid" id="pluginGrid">
                            ${this.renderPluginCards()}
                        </div>
                        <div class="plugin-more-section">
                            <button class="plugin-more-btn" type="button">More...</button>
                        </div>
                    </div>
                </main>
            </div>
        `;
    },

    renderPluginCards() {
        const plugins = [
            { name: 'OpenAI', icon: 'openai', desc: 'OpenAI is an AI research organization known for GPT-4 and GPT-4o, which excel in natural language understanding and generation.', badge: 'LLM Connector' },
            { name: 'Claude', icon: 'claude', desc: 'Claude is an AI language model by Anthropic, featuring Claude 3.5, designed for safe, reliable, and user-friendly communication tasks.', badge: 'LLM Connector' },
            { name: 'DeepSeek', icon: 'deepseek', desc: 'DeepSeek\'s DeepSeek-R1 model excels in reasoning, code generation, and cost efficiency, rivaling OpenAI\'s offerings in performance.', badge: 'LLM Connector' },
            { name: 'Mistral', icon: 'mistral', desc: 'Mistral AI is a Paris-based startup specializing in open-source large language models, founded by ex-Google DeepMind and Meta researchers.', badge: 'LLM Connector' },
            { name: 'Gemini', icon: 'gemini', desc: 'Gemini is Google DeepMind\'s advanced multimodal AI model, designed to intuitively understand and integrate text, code, audio, images, and video.', badge: 'LLM Connector' },
            { name: 'Llama', icon: 'llama', desc: 'Llama is developed by Meta, featuring multiple model sizes for diverse applications, enabling efficient and effective natural language processing tasks.', badge: 'LLM Connector' },
        ];

        return plugins.map(plugin => `
            <div class="plugin-card">
                <div class="plugin-card-header">
                    <div class="plugin-icon-lg">
                        ${this.getPluginIcon(plugin.icon)}
                    </div>
                    <div class="plugin-header-info">
                        <span class="plugin-name">${plugin.name}</span>
                        <span class="plugin-badge-connector">${plugin.badge}</span>
                    </div>
                </div>
                <div class="plugin-author">
                    <span class="author-label">AI-SNS</span>
                    <span class="author-official">Official</span>
                </div>
                <div class="plugin-desc">${plugin.desc}</div>
                <button class="plugin-download-btn">Download</button>
            </div>
        `).join('');
    },

    getPluginIcon(icon) {
        const icons = {
            'openai': '<svg viewBox="0 0 24 24" width="32" height="32"><path fill="#10a37f" d="M22.2 8.3c-.5-1.4-1.5-2.5-2.7-3.3-.9-.6-1.9-.9-3-1-.3 0-.5 0-.8.1-.5-1.3-1.4-2.4-2.6-3.2C11.9.2 10.5-.1 9.2.1c-1.1.1-2.1.5-2.9 1.1-.8.6-1.5 1.4-1.9 2.3-.8-.2-1.6-.2-2.4 0-1.1.3-2.1.9-2.8 1.8-.6.8-1 1.8-1.1 2.8-.1 1 .1 2 .5 2.9-.8.8-1.3 1.8-1.5 2.9-.2 1.3.1 2.6.7 3.8.5.9 1.2 1.7 2.1 2.2.9.6 1.9.9 3 1 .3 0 .5 0 .8-.1.5 1.3 1.4 2.4 2.6 3.2 1.2.7 2.6 1 4 .8 1.1-.1 2.1-.5 2.9-1.1.8-.6 1.5-1.4 1.9-2.3.8.2 1.6.2 2.4 0 1.1-.3 2.1-.9 2.8-1.8.6-.8 1-1.8 1.1-2.8.1-1-.1-2-.5-2.9.8-.8 1.3-1.8 1.5-2.9.2-1.3-.1-2.7-.7-3.8zM12 18.9c-3.8 0-6.9-3.1-6.9-6.9s3.1-6.9 6.9-6.9 6.9 3.1 6.9 6.9-3.1 6.9-6.9 6.9z"/></svg>',
            'claude': '<svg viewBox="0 0 24 24" width="32" height="32"><rect fill="#d97706" x="2" y="2" width="20" height="20" rx="4"/><text x="12" y="16" text-anchor="middle" font-size="12" font-weight="bold" fill="white">A</text></svg>',
            'deepseek': '<svg viewBox="0 0 24 24" width="32" height="32"><rect fill="#1a73e8" x="2" y="2" width="20" height="20" rx="4"/><path fill="white" d="M7 8h10v2H7zM7 12h8v2H7zM7 16h6v2H7z"/></svg>',
            'mistral': '<svg viewBox="0 0 24 24" width="32" height="32"><rect fill="#ff6b35" x="2" y="2" width="20" height="20" rx="4"/><path fill="white" d="M6 6h4v4H6zM14 6h4v4h-4zM6 10h4v4H6zM10 10h4v4h-4zM14 14h4v4h-4zM6 14h4v4H6z"/></svg>',
            'gemini': '<svg viewBox="0 0 24 24" width="32" height="32"><defs><linearGradient id="gemGrad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#4285f4"/><stop offset="50%" style="stop-color:#9b72cb"/><stop offset="100%" style="stop-color:#d96570"/></linearGradient></defs><circle fill="url(#gemGrad)" cx="12" cy="12" r="10"/><path fill="white" d="M12 6l2 4h4l-3 3 1 5-4-2-4 2 1-5-3-3h4z"/></svg>',
            'llama': '<svg viewBox="0 0 24 24" width="32" height="32"><circle fill="#1877f2" cx="12" cy="12" r="10"/><text x="12" y="15" text-anchor="middle" font-size="8" font-weight="bold" fill="white">Meta</text></svg>',
            'grok': '<svg viewBox="0 0 24 24" width="32" height="32"><rect fill="#000" x="2" y="2" width="20" height="20" rx="4"/><text x="12" y="16" text-anchor="middle" font-size="12" font-weight="bold" fill="white">X</text></svg>',
            'kimi': '<svg viewBox="0 0 24 24" width="32" height="32"><rect fill="#ff4081" x="2" y="2" width="20" height="20" rx="4"/><text x="12" y="16" text-anchor="middle" font-size="12" font-weight="bold" fill="white">K</text></svg>',
            'aisns': '<svg viewBox="0 0 24 24" width="32" height="32"><path fill="#1a73e8" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>',
        };
        return icons[icon] || icons['aisns'];
    }
};

export default ToolsPage;
