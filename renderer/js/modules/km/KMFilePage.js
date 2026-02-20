/**
 * KM Page - File Search (kmtype=0) - optimized version
 */

const KMFilePage = {
    render(kbId) {
        return `
            <div class="km-page-layout km-file-page-layout">            

                <!-- 右侧: 向量搜索区域 -->
                <div class="km-vector-search-panel">
                    <div class="km-search-header">
                        <h3>
                            <svg viewBox="0 0 24 24" width="24" height="24" fill="var(--color-primary)" style="vertical-align: middle; margin-right: 8px;">
                                <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
                            </svg>
                            智能语义搜索
                        </h3>
                        <p>使用AI向量技术，从已上传的文档中精准检索相关内容</p>
                    </div>
                    <div class="km-search-input-area">
                        <input type="text" id="vectorSearchInput-${kbId}" class="km-search-input-large" placeholder="输入您想搜索的内容，例如：如何配置数据库连接...">
                        <button class="km-search-btn" id="vectorSearchBtn-${kbId}">
                            <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor" style="vertical-align: middle; margin-right: 4px;">
                                <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
                            </svg>
                            搜索
                        </button>
                    </div>
                    <div class="km-search-results" id="searchResults-${kbId}">
                        <div class="empty-state">
                            <svg viewBox="0 0 24 24" width="64" height="64" fill="#ddd" style="margin-bottom: 16px;">
                                <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
                            </svg>
                            <p>输入关键词开始搜索文档内容</p>
                            <p style="font-size: 12px; color: #aaa; margin-top: 8px;">支持自然语言搜索，AI会找到最相关的内容</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    init() {
        // Bind search button events
        document.querySelectorAll('[id^="vectorSearchBtn-"]').forEach(btn => {
            const kbId = btn.id.replace('vectorSearchBtn-', '');
            btn.addEventListener('click', () => {
                if (window.kmHandlers) {
                    window.kmHandlers.performVectorSearch(parseInt(kbId));
                }
            });
        });

        // Bind Enter key to search
        document.querySelectorAll('[id^="vectorSearchInput-"]').forEach(input => {
            const kbId = input.id.replace('vectorSearchInput-', '');
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && window.kmHandlers) {
                    window.kmHandlers.performVectorSearch(parseInt(kbId));
                }
            });
        });

        // Bind add-file button
        document.querySelectorAll('[id^="fileAddBtn-"]').forEach(btn => {
            const kbId = btn.id.replace('fileAddBtn-', '');
            btn.addEventListener('click', () => {
                if (window.kmHandlers) {
                    window.kmHandlers.showAddFileDialog(parseInt(kbId));
                }
            });
        });

        console.log('[KMFilePage] Initialized');
    },

    destroy() {
        // Clean up event listeners if needed
    }
};

export default KMFilePage;
