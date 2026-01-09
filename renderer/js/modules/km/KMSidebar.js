/**
 * KM Sidebar - 侧边栏渲染
 */

const KMSidebar = {
    render() {
        return `
            <!-- 顶部标题区 -->
            <div class="km-sidebar-header">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="#1a73e8">
                    <path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm4 18H6V4h7v5h5v11z"/>
                </svg>
                <span class="km-sidebar-title">My Note</span>
            </div>

            <!-- 操作按钮 -->
            <div class="km-action-buttons">
                <button class="km-action-btn" id="newNoteBtn">
                    <div class="km-action-icon">
                        <svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="#1a73e8" stroke-width="1.5">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                            <polyline points="14 2 14 8 20 8"/>
                            <line x1="12" y1="11" x2="12" y2="17"/>
                            <line x1="9" y1="14" x2="15" y2="14"/>
                        </svg>
                    </div>
                    <span>New Note</span>
                </button>
                <button class="km-action-btn" id="kmSettingBtn">
                    <div class="km-action-icon">
                        <svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="#1a73e8" stroke-width="1.5">
                            <circle cx="12" cy="12" r="3"/>
                            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
                        </svg>
                    </div>
                    <span>Setting</span>
                </button>
            </div>

            <!-- 搜索框 -->
            <div class="km-search-box">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="#999">
                    <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
                </svg>
                <input type="text" placeholder="Keyword+Enter,Blank+Enter to reset" class="km-search-input" id="kmSearchInput">
            </div>

            <!-- 标签页切换 -->
            <div class="km-tabs">
                <button class="km-tab active" data-tab="all">All</button>
                <button class="km-tab" data-tab="tag">Tag</button>
            </div>

            <!-- 笔记列表树 -->
            <div class="km-note-tree" id="noteTree">
                <div class="km-tree-node">
                    <div class="km-tree-item">
                        <span class="tree-icon">📋</span>
                        <span class="tree-text">Memo</span>
                    </div>
                </div>
                <div class="km-tree-node">
                    <div class="km-tree-item">
                        <span class="tree-icon">✅</span>
                        <span class="tree-text">Todo</span>
                    </div>
                </div>
                <div class="km-tree-node expandable">
                    <div class="km-tree-item">
                        <span class="tree-expand">▶</span>
                        <span class="tree-icon">📁</span>
                        <span class="tree-text">amazon</span>
                    </div>
                </div>
                <div class="km-tree-node expandable expanded">
                    <div class="km-tree-item">
                        <span class="tree-expand">▼</span>
                        <span class="tree-icon">📁</span>
                        <span class="tree-text">ai coding</span>
                    </div>
                    <div class="km-tree-children">
                        <div class="km-tree-node">
                            <div class="km-tree-item active">
                                <span class="tree-icon">📄</span>
                                <span class="tree-text">codex</span>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="km-tree-node expandable">
                    <div class="km-tree-item">
                        <span class="tree-expand">▶</span>
                        <span class="tree-icon">📁</span>
                        <span class="tree-text">baidu</span>
                    </div>
                </div>
                <div class="km-tree-node expandable">
                    <div class="km-tree-item">
                        <span class="tree-expand">▶</span>
                        <span class="tree-icon">📁</span>
                        <span class="tree-text">Resource</span>
                    </div>
                </div>
                <div class="km-tree-node">
                    <div class="km-tree-item">
                        <span class="tree-icon">📄</span>
                        <span class="tree-text">moonlight stream</span>
                    </div>
                </div>
            </div>

            <!-- 底部知识库列表 -->
            <div class="km-kb-section">
                <div class="km-kb-item" data-kb="pinecone">
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="#1a73e8"><path d="M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-1 9h-4v4h-2v-4H9V9h4V5h2v4h4v2z"/></svg>
                    <span>KB on Pinecone</span>
                </div>
                <div class="km-kb-item" data-kb="3d-design">
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="#1a73e8"><path d="M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-1 9h-4v4h-2v-4H9V9h4V5h2v4h4v2z"/></svg>
                    <span>3D Design</span>
                </div>
                <div class="km-kb-item" data-kb="code-kb">
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="#1a73e8"><path d="M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-1 9h-4v4h-2v-4H9V9h4V5h2v4h4v2z"/></svg>
                    <span>Code KB</span>
                </div>
                <div class="km-kb-item" data-kb="testpinecone">
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="#1a73e8"><path d="M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-1 9h-4v4h-2v-4H9V9h4V5h2v4h4v2z"/></svg>
                    <span>testpinecone</span>
                </div>
                <div class="km-kb-item km-kb-setting" data-kb="setting">
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="#666"><path d="M19.14 12.94c.04-.31.06-.63.06-.94 0-.31-.02-.63-.06-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.04.31-.06.63-.06.94s.02.63.06.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58z"/></svg>
                    <span>KM Setting</span>
                </div>
            </div>
        `;
    }
};

export default KMSidebar;
