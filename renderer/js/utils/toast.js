/**
 * Toast Notification System
 * Provides elegant toast notifications as a replacement for alert/confirm
 */

const Toast = {
    container: null,

    /**
     * Initialize toast container
     */
    init() {
        if (this.container) return;

        // Create toast container
        this.container = document.createElement('div');
        this.container.id = 'toast-container';
        this.container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 100000;
            display: flex;
            flex-direction: column;
            gap: 10px;
            pointer-events: none;
        `;
        document.body.appendChild(this.container);
    },

    /**
     * Show a toast notification
     * @param {string} message - Message to display
     * @param {string} type - Type: 'success', 'error', 'warning', 'info'
     * @param {number} duration - Duration in milliseconds (0 = no auto-hide)
     */
    show(message, type = 'info', duration = 3000) {
        this.init();

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;

        // Get icon and colors based on type
        const config = this.getToastConfig(type);

        toast.innerHTML = `
            <div class="toast-icon">${config.icon}</div>
            <div class="toast-message">${this.escapeHtml(message)}</div>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
                    <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                </svg>
            </button>
        `;

        // Apply styles
        toast.style.cssText = `
            display: flex;
            align-items: center;
            gap: 12px;
            min-width: 300px;
            max-width: 500px;
            padding: 16px 20px;
            background: white;
            border-left: 4px solid ${config.color};
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
            pointer-events: auto;
            animation: slideInRight 0.3s ease-out;
            transition: all 0.3s ease;
        `;

        // Add animation styles if not exists
        if (!document.getElementById('toast-animations')) {
            const style = document.createElement('style');
            style.id = 'toast-animations';
            style.textContent = `
                @keyframes slideInRight {
                    from {
                        transform: translateX(400px);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }
                @keyframes slideOutRight {
                    from {
                        transform: translateX(0);
                        opacity: 1;
                    }
                    to {
                        transform: translateX(400px);
                        opacity: 0;
                    }
                }
                .toast:hover {
                    box-shadow: 0 6px 28px rgba(0, 0, 0, 0.25);
                    transform: translateY(-2px);
                }
                .toast-icon {
                    flex-shrink: 0;
                    width: 24px;
                    height: 24px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .toast-message {
                    flex: 1;
                    font-size: 14px;
                    color: #333;
                    line-height: 1.5;
                    word-wrap: break-word;
                }
                .toast-close {
                    flex-shrink: 0;
                    background: none;
                    border: none;
                    padding: 4px;
                    cursor: pointer;
                    color: #999;
                    border-radius: 4px;
                    transition: all 0.2s;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .toast-close:hover {
                    background: #f0f0f0;
                    color: #333;
                }
            `;
            document.head.appendChild(style);
        }

        this.container.appendChild(toast);

        // Auto-hide
        if (duration > 0) {
            setTimeout(() => {
                this.hideToast(toast);
            }, duration);
        }

        return toast;
    },

    /**
     * Hide a toast with animation
     */
    hideToast(toast) {
        toast.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => {
            toast.remove();
        }, 300);
    },

    /**
     * Get toast configuration based on type
     */
    getToastConfig(type) {
        const configs = {
            success: {
                color: '#4caf50',
                icon: `<svg viewBox="0 0 24 24" width="24" height="24" fill="#4caf50">
                    <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                </svg>`
            },
            error: {
                color: '#f44336',
                icon: `<svg viewBox="0 0 24 24" width="24" height="24" fill="#f44336">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
                </svg>`
            },
            warning: {
                color: '#ff9800',
                icon: `<svg viewBox="0 0 24 24" width="24" height="24" fill="#ff9800">
                    <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/>
                </svg>`
            },
            info: {
                color: '#2196f3',
                icon: `<svg viewBox="0 0 24 24" width="24" height="24" fill="#2196f3">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
                </svg>`
            }
        };
        return configs[type] || configs.info;
    },

    /**
     * Shorthand methods
     */
    success(message, duration = 3000) {
        return this.show(message, 'success', duration);
    },

    error(message, duration = 5000) {
        return this.show(message, 'error', duration);
    },

    warning(message, duration = 4000) {
        return this.show(message, 'warning', duration);
    },

    info(message, duration = 3000) {
        return this.show(message, 'info', duration);
    },

    /**
     * Show confirmation dialog
     * @param {string} message - Message to display
     * @param {object} options - Options {confirmText, cancelText, onConfirm, onCancel}
     * @returns {Promise} - Resolves to true if confirmed, false if cancelled
     */
    confirm(message, options = {}) {
        return new Promise((resolve) => {
            const {
                title = '确认',
                confirmText = '确定',
                cancelText = '取消',
                type = 'warning',
                onConfirm = null,
                onCancel = null
            } = options;

            // Create modal backdrop
            const backdrop = document.createElement('div');
            backdrop.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.5);
                z-index: 100001;
                display: flex;
                align-items: center;
                justify-content: center;
                animation: fadeIn 0.2s ease-out;
            `;

            // Create dialog
            const dialog = document.createElement('div');
            const config = this.getToastConfig(type);

            dialog.style.cssText = `
                background: white;
                border-radius: 12px;
                padding: 24px;
                min-width: 360px;
                max-width: 480px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
                animation: slideInDown 0.3s ease-out;
            `;

            dialog.innerHTML = `
                <div style="display: flex; align-items: flex-start; gap: 16px; margin-bottom: 24px;">
                    <div style="flex-shrink: 0;">${config.icon}</div>
                    <div style="flex: 1;">
                        <div style="font-size: 18px; font-weight: 600; color: #333; margin-bottom: 8px;">
                            ${this.escapeHtml(title)}
                        </div>
                        <div style="font-size: 14px; color: #666; line-height: 1.5;">
                            ${this.escapeHtml(message)}
                        </div>
                    </div>
                </div>
                <div style="display: flex; gap: 12px; justify-content: flex-end;">
                    <button id="confirmCancelBtn" style="
                        padding: 10px 20px;
                        border: 1px solid #ddd;
                        background: white;
                        border-radius: 6px;
                        cursor: pointer;
                        font-size: 14px;
                        color: #666;
                        transition: all 0.2s;
                    ">${this.escapeHtml(cancelText)}</button>
                    <button id="confirmOkBtn" style="
                        padding: 10px 20px;
                        border: none;
                        background: ${config.color};
                        color: white;
                        border-radius: 6px;
                        cursor: pointer;
                        font-size: 14px;
                        transition: all 0.2s;
                    ">${this.escapeHtml(confirmText)}</button>
                </div>
            `;

            backdrop.appendChild(dialog);

            // Add animation styles if not exists
            if (!document.getElementById('confirm-animations')) {
                const style = document.createElement('style');
                style.id = 'confirm-animations';
                style.textContent = `
                    @keyframes fadeIn {
                        from { opacity: 0; }
                        to { opacity: 1; }
                    }
                    @keyframes slideInDown {
                        from {
                            transform: translateY(-50px);
                            opacity: 0;
                        }
                        to {
                            transform: translateY(0);
                            opacity: 1;
                        }
                    }
                    #confirmCancelBtn:hover {
                        background: #f5f5f5;
                        border-color: #ccc;
                    }
                    #confirmOkBtn:hover {
                        opacity: 0.9;
                        transform: translateY(-1px);
                        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                    }
                `;
                document.head.appendChild(style);
            }

            document.body.appendChild(backdrop);

            // Handle confirm
            const confirmBtn = dialog.querySelector('#confirmOkBtn');
            confirmBtn.addEventListener('click', () => {
                backdrop.remove();
                resolve(true);
                if (onConfirm) onConfirm();
            });

            // Handle cancel
            const cancelBtn = dialog.querySelector('#confirmCancelBtn');
            cancelBtn.addEventListener('click', () => {
                backdrop.remove();
                resolve(false);
                if (onCancel) onCancel();
            });

            // Handle backdrop click
            backdrop.addEventListener('click', (e) => {
                if (e.target === backdrop) {
                    backdrop.remove();
                    resolve(false);
                    if (onCancel) onCancel();
                }
            });

            // Handle ESC key
            const handleEsc = (e) => {
                if (e.key === 'Escape') {
                    backdrop.remove();
                    resolve(false);
                    if (onCancel) onCancel();
                    document.removeEventListener('keydown', handleEsc);
                }
            };
            document.addEventListener('keydown', handleEsc);
        });
    },

    /**
     * Show loading indicator
     * @param {string} message - Loading message
     * @returns {object} - Object with close() method
     */
    loading(message = 'Loading...') {
        this.init();

        const loading = document.createElement('div');
        loading.className = 'toast toast-loading';

        loading.innerHTML = `
            <div class="loading-spinner">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#2196f3" stroke-width="2">
                    <circle cx="12" cy="12" r="10" opacity="0.25"/>
                    <path d="M12 2 A10 10 0 0 1 22 12" opacity="1">
                        <animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur="1s" repeatCount="indefinite"/>
                    </path>
                </svg>
            </div>
            <div class="toast-message">${this.escapeHtml(message)}</div>
        `;

        loading.style.cssText = `
            display: flex;
            align-items: center;
            gap: 12px;
            min-width: 200px;
            padding: 16px 20px;
            background: white;
            border-left: 4px solid #2196f3;
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
            pointer-events: auto;
            animation: slideInRight 0.3s ease-out;
        `;

        this.container.appendChild(loading);

        return {
            close: () => {
                this.hideToast(loading);
            },
            update: (newMessage) => {
                const messageEl = loading.querySelector('.toast-message');
                if (messageEl) {
                    messageEl.textContent = this.escapeHtml(newMessage);
                }
            }
        };
    },

    /**
     * Clear all toasts
     */
    clearAll() {
        if (this.container) {
            this.container.querySelectorAll('.toast').forEach(toast => {
                this.hideToast(toast);
            });
        }
    },

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};

// Export for ES modules
export default Toast;

// Also expose globally for convenience
if (typeof window !== 'undefined') {
    window.Toast = Toast;
}
