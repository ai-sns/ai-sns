/**
 * Notification Component - notification component
 */

class Notification {
    static container = null;
    static timeout = 5000;

    static init() {
        this.container = document.getElementById('notificationContainer');
        if (!this.container) {
            console.error('Notification container not found');
        }
    }

    static show(message, type = 'info', duration = this.timeout) {
        const safeMessage = this.sanitizeMessage(message);
        try {
            if (typeof window !== 'undefined' && window.Toast && typeof window.Toast.show === 'function') {
                return window.Toast.show(safeMessage, type, duration);
            }
        } catch (e) {
        }

        if (!this.container) this.init();
        if (!this.container) return null;

        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <span class="notification-message">${this.escapeHtml(safeMessage)}</span>
            <button class="notification-close">&times;</button>
        `;

        this.container.appendChild(notification);

        // Bind close button
        notification.querySelector('.notification-close').addEventListener('click', () => {
            this.remove(notification);
        });

        // Auto remove
        if (duration > 0) {
            setTimeout(() => {
                this.remove(notification);
            }, duration);
        }

        return notification;
    }

    static sanitizeMessage(message, maxLength = 420) {
        if (typeof window !== 'undefined' && window.Toast && typeof window.Toast.sanitizeMessage === 'function') {
            return window.Toast.sanitizeMessage(message, maxLength);
        }
        let text = String(message ?? '').trim();
        text = text.replace(/\bsk-proj-[A-Za-z0-9_\-*]{12,}\b/g, (v) => `${v.slice(0, 6)}...${v.slice(-4)}`);
        text = text.replace(/\bsk-svcac[A-Za-z0-9_\-*]{12,}\b/g, (v) => `${v.slice(0, 6)}...${v.slice(-4)}`);
        text = text.replace(/\bsk-[A-Za-z0-9_\-*]{12,}\b/g, (v) => `${v.slice(0, 6)}...${v.slice(-4)}`);
        text = text.replace(/[ \t\r\n]+/g, ' ').trim();
        return text.length > maxLength ? `${text.slice(0, maxLength).trim()}...` : text;
    }

    static escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = String(text ?? '');
        return div.innerHTML;
    }

    static remove(notification) {
        notification.style.animation = 'slideOut 0.3s ease forwards';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 300);
    }

    static success(message, duration) {
        return this.show(message, 'success', duration);
    }

    static error(message, duration) {
        return this.show(message, 'error', duration);
    }

    static warning(message, duration) {
        return this.show(message, 'warning', duration);
    }

    static info(message, duration) {
        return this.show(message, 'info', duration);
    }
}

// Export to global
window.Notification = Notification;
