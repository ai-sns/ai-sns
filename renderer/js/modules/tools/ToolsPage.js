/**
 * Tools Page - 主内容渲染
 */

const ToolsPage = {
    render() {
        return `
            <div class="tools-page">
                <!-- 顶部导航栏 -->
                <div class="tools-top-nav">
                    <div class="tools-nav-brand">
                        <svg viewBox="0 0 24 24" width="24" height="24" fill="#fff">
                            <path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm4 18H6V4h7v5h5v11z"/>
                        </svg>
                        <span>AI-SNS</span>
                    </div>
                    <div class="tools-nav-links">
                        <a href="#" class="tools-nav-link">About</a>
                        <a href="#" class="tools-nav-link">Ecosystem</a>
                        <a href="#" class="tools-nav-link">Docs</a>
                        <a href="#" class="tools-nav-link">Blog</a>
                        <a href="#" class="tools-nav-link">Community</a>
                        <button class="tools-nav-btn">Try AI-SNS</button>
                    </div>
                </div>

                <!-- 插件列表区域 -->
                <div class="plugin-market">
                    <div class="plugin-list-header">
                        <h1 class="plugin-list-title">Plugin List</h1>
                        <button class="tools-add-btn" onclick="toolsHandlers.showAddDialog(toolsHandlers.currentCategory)">
                            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="12" y1="5" x2="12" y2="19"/>
                                <line x1="5" y1="12" x2="19" y2="12"/>
                            </svg>
                            Add Tool
                        </button>
                    </div>
                    <div class="plugin-grid" id="pluginGrid">
                        ${this.renderPluginCards()}
                    </div>
                    <div class="plugin-more-section">
                        <button class="plugin-more-btn">More...</button>
                    </div>
                </div>

                <!-- 底部导航 -->
                <div class="tools-footer">
                    <div class="tools-footer-links">
                        <a href="#">AI-Nation</a>
                        <a href="#">Plugin</a>
                        <a href="#">Network Service</a>
                        <a href="#">Application Service</a>
                        <a href="#">Memberlist</a>
                        <a href="#">Source Code</a>
                        <a href="#">Contact</a>
                        <a href="#">Support</a>
                    </div>
                    <div class="tools-footer-icons">
                        <a href="#" class="footer-icon"><svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg></a>
                        <a href="#" class="footer-icon"><svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M20.317 4.3698a19.7913 19.7913 0 00-4.8851-1.5152.0741.0741 0 00-.0785.0371c-.211.3753-.4447.8648-.6083 1.2495-1.8447-.2762-3.68-.2762-5.4868 0-.1636-.3933-.4058-.8742-.6177-1.2495a.077.077 0 00-.0785-.037 19.7363 19.7363 0 00-4.8852 1.515.0699.0699 0 00-.0321.0277C.5334 9.0458-.319 13.5799.0992 18.0578a.0824.0824 0 00.0312.0561c2.0528 1.5076 4.0413 2.4228 5.9929 3.0294a.0777.0777 0 00.0842-.0276c.4616-.6304.8731-1.2952 1.226-1.9942a.076.076 0 00-.0416-.1057c-.6528-.2476-1.2743-.5495-1.8722-.8923a.077.077 0 01-.0076-.1277c.1258-.0943.2517-.1923.3718-.2914a.0743.0743 0 01.0776-.0105c3.9278 1.7933 8.18 1.7933 12.0614 0a.0739.0739 0 01.0785.0095c.1202.099.246.1981.3728.2924a.077.077 0 01-.0066.1276 12.2986 12.2986 0 01-1.873.8914.0766.0766 0 00-.0407.1067c.3604.698.7719 1.3628 1.225 1.9932a.076.076 0 00.0842.0286c1.961-.6067 3.9495-1.5219 6.0023-3.0294a.077.077 0 00.0313-.0552c.5004-5.177-.8382-9.6739-3.5485-13.6604a.061.061 0 00-.0312-.0286z"/></svg></a>
                        <a href="#" class="footer-icon"><svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/></svg></a>
                        <a href="#" class="footer-icon"><svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/></svg></a>
                        <a href="#" class="footer-icon"><svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg></a>
                    </div>
                </div>
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
