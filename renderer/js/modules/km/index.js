/**
 * KM Module - Index
 * 知识库管理模块入口
 */

import KMPage from './KMPage.js';
import KMSidebar from './KMSidebar.js';
import kmHandlers from './kmHandlers.js';

export default {
    name: 'km',
    version: '1.0.0',

    /**
     * 渲染主内容区
     */
    renderPage() {
        return KMPage.render();
    },

    /**
     * 渲染侧边栏
     */
    renderSidebar() {
        return KMSidebar.render();
    },

    /**
     * 初始化模块
     */
    init() {
        kmHandlers.init();
    },

    /**
     * 销毁模块
     */
    destroy() {
        kmHandlers.destroy();
    }
};
