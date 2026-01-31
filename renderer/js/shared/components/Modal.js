/**
 * Modal Component - 模态对话框
 */

class Modal {
    constructor(options = {}) {
        this.title = options.title || '';
        this.content = options.content || '';
        this.onConfirm = options.onConfirm || null;
        this.onCancel = options.onCancel || null;
        this.onOpen = options.onOpen || null;
        this.onClose = options.onClose || null;
        this.confirmText = options.confirmText || '确认';
        this.cancelText = options.cancelText || '取消';
        this.showCancel = options.showCancel !== false;
        this.closeOnClickOutside = options.closeOnClickOutside !== false; // 默认允许点击外部关闭
        this.width = options.width || '500px';
        this.element = null;
        this.handleKeydown = null;
    }

    render() {
        const html = `
            <div class="modal-overlay">
                <div class="modal" style="max-width: ${this.width};">
                    <div class="modal-header">
                        <h3 class="modal-title">${this.title}</h3>
                        <button class="modal-close" data-action="close">&times;</button>
                    </div>
                    <div class="modal-body">
                        ${this.content}
                    </div>
                    <div class="modal-footer">
                        ${this.showCancel ? `<button class="btn btn-secondary" data-action="cancel">${this.cancelText}</button>` : ''}
                        <button class="btn btn-primary" data-action="confirm">${this.confirmText}</button>
                    </div>
                </div>
            </div>
        `;

        const container = document.getElementById('modalContainer');
        if (!container) {
            console.error('Modal container not found');
            return this;
        }

        container.innerHTML = html;
        this.element = container.querySelector('.modal-overlay');

        this.bindEvents();

        // 调用 onOpen 回调(在 DOM 元素已经渲染后)
        if (this.onOpen) {
            // 使用 setTimeout 确保 DOM 完全渲染
            setTimeout(() => {
                this.onOpen(this);
            }, 0);
        }

        return this;
    }

    bindEvents() {
        this.element.addEventListener('click', async (e) => {
            const action = e.target.dataset.action;
            console.log('[Modal] Button clicked, action:', action);

            if (action === 'close' || action === 'cancel') {
                console.log('[Modal] Close/Cancel button clicked');
                if (this.onCancel) {
                    try {
                        const result = await this.onCancel(this);
                        if (result !== false) {
                            this.close();
                        }
                    } catch (error) {
                        console.error('[Modal] Error in onCancel:', error);
                    }
                } else {
                    this.close();
                }
            } else if (action === 'confirm') {
                console.log('[Modal] Confirm button clicked');
                if (this.onConfirm) {
                    console.log('[Modal] Calling onConfirm...');
                    try {
                        const result = await this.onConfirm(this);
                        console.log('[Modal] onConfirm result:', result);
                        if (result !== false) {
                            console.log('[Modal] Result is not false, calling close()');
                            this.close();
                        } else {
                            console.log('[Modal] Result is false, not closing');
                        }
                    } catch (error) {
                        console.error('[Modal] Error in onConfirm:', error);
                    }
                } else {
                    console.log('[Modal] No onConfirm callback, closing directly');
                    this.close();
                }
            }
        });

        // 点击遮罩层关闭（如果允许）
        if (this.closeOnClickOutside) {
            this.element.addEventListener('click', async (e) => {
                if (e.target === this.element) {
                    console.log('[Modal] Clicked outside, closing...');
                    if (this.onCancel) {
                        try {
                            const result = await this.onCancel(this);
                            if (result !== false) {
                                this.close();
                            }
                        } catch (error) {
                            console.error('[Modal] Error in onCancel:', error);
                        }
                    } else {
                        this.close();
                    }
                }
            });
        }

        // ESC键关闭
        this.handleKeydown = async (e) => {
            if (e.key === 'Escape') {
                console.log('[Modal] ESC pressed, closing...');
                if (this.onCancel) {
                    try {
                        const result = await this.onCancel(this);
                        if (result !== false) {
                            this.close();
                        }
                    } catch (error) {
                        console.error('[Modal] Error in onCancel:', error);
                    }
                } else {
                    this.close();
                }
            }
        };
        document.addEventListener('keydown', this.handleKeydown);
    }

    close() {
        console.log('[Modal] Closing modal...');
        if (this.element) {
            this.element.remove();
            if (this.handleKeydown) {
                document.removeEventListener('keydown', this.handleKeydown);
            }
            // 调用 onClose 回调
            if (this.onClose) {
                console.log('[Modal] Calling onClose callback');
                this.onClose();
            } else {
                console.log('[Modal] No onClose callback defined');
            }
        }
    }

    getFormData() {
        const form = this.element.querySelector('form');
        if (!form) return {};

        const formData = new FormData(form);
        const data = {};
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        return data;
    }

    static show(options) {
        return new Modal(options).render();
    }

    static confirm(message, onConfirm) {
        return Modal.show({
            title: '确认',
            content: `<p>${message}</p>`,
            onConfirm
        });
    }

    static alert(message, title = '提示') {
        return Modal.show({
            title,
            content: `<p>${message}</p>`,
            showCancel: false
        });
    }
}

// 导出到全局
window.Modal = Modal;
