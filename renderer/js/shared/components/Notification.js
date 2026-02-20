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
        if (!this.container) this.init();
        if (!this.container) return null;

        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <span class="notification-message">${message}</span>
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
