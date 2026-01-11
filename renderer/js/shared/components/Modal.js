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
        this.confirmText = options.confirmText || '确认';
        this.cancelText = options.cancelText || '取消';
        this.showCancel = options.showCancel !== false;
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
                this.onOpen();
            }, 0);
        }

        return this;
    }

    bindEvents() {
        this.element.addEventListener('click', (e) => {
            const action = e.target.dataset.action;

            if (action === 'close' || action === 'cancel') {
                this.close();
                if (this.onCancel) this.onCancel();
            } else if (action === 'confirm') {
                if (this.onConfirm) {
                    const result = this.onConfirm(this);
                    if (result !== false) {
                        this.close();
                    }
                } else {
                    this.close();
                }
            }
        });

        // 点击遮罩层关闭
        this.element.addEventListener('click', (e) => {
            if (e.target === this.element) {
                this.close();
                if (this.onCancel) this.onCancel();
            }
        });

        // ESC键关闭
        this.handleKeydown = (e) => {
            if (e.key === 'Escape') {
                this.close();
                if (this.onCancel) this.onCancel();
            }
        };
        document.addEventListener('keydown', this.handleKeydown);
    }

    close() {
        if (this.element) {
            this.element.remove();
            if (this.handleKeydown) {
                document.removeEventListener('keydown', this.handleKeydown);
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
