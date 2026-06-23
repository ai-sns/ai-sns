/**
 * Tools Sidebar - sidebar rendering
 */

const ToolsSidebar = {
    render() {
        return `
            <aside class="tools-sidebar-ref">
                <h2 class="tools-sidebar-ref__title">${window.escHtml(window.tt('tools.sidebar.title'))}</h2>
                <button class="tools-category-item active" data-category="mcp" type="button">
                    <svg class="tools-sidebar-ref__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="2" y="2" width="20" height="8" rx="2" ry="2"></rect>
                        <rect x="2" y="14" width="20" height="8" rx="2" ry="2"></rect>
                        <line x1="6" y1="6" x2="6.01" y2="6"></line>
                        <line x1="6" y1="18" x2="6.01" y2="18"></line>
                    </svg>
                    <span class="tools-sidebar-ref__label">${window.escHtml(window.tt('tools.sidebar.mcp'))}</span>
                    <svg class="category-arrow ml-auto" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round">
                        <polyline points="9 18 15 12 9 6"></polyline>
                    </svg>
                </button>
                <button class="tools-category-item" data-category="skill" type="button">
                    <svg class="tools-sidebar-ref__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round">
  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
  <polyline points="14 2 14 8 20 8"/>
  <polyline points="10 13 8 15 10 17"/>
  <polyline points="14 13 16 15 14 17"/>
                    </svg>
                    <span class="tools-sidebar-ref__label">${window.escHtml(window.tt('tools.sidebar.skills'))}</span>
                    <svg class="category-arrow ml-auto" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round">
                        <polyline points="9 18 15 12 9 6"></polyline>
                    </svg>
                </button>
            </aside>
        `;
    }
};

export default ToolsSidebar;
