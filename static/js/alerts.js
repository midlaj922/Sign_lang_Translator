// Custom Alert Notification System
class AlertNotification {
    constructor() {
        this.container = null;
        this.init();
    }

    init() {
        // Create container if it doesn't exist
        if (!document.querySelector('.alert-container')) {
            this.container = document.createElement('div');
            this.container.className = 'alert-container';
            document.body.appendChild(this.container);
        } else {
            this.container = document.querySelector('.alert-container');
        }
    }

    show(message, type = 'info', duration = 5000) {
        const alert = document.createElement('div');
        alert.className = `custom-alert ${type}`;

        const icons = {
            success: '✓',
            error: '✕',
            info: 'ℹ',
            warning: '⚠'
        };

        const titles = {
            success: 'Success',
            error: 'Error',
            info: 'Info',
            warning: 'Warning'
        };

        alert.innerHTML = `
            <div class="alert-icon">${icons[type]}</div>
            <div class="alert-content">
                <div class="alert-title">${titles[type]}</div>
                <div class="alert-message">${message}</div>
            </div>
            <button class="alert-close" onclick="this.parentElement.remove()">×</button>
            <div class="alert-progress"></div>
        `;

        this.container.appendChild(alert);

        // Auto remove after duration
        setTimeout(() => {
            alert.classList.add('hiding');
            setTimeout(() => {
                if (alert.parentElement) {
                    alert.remove();
                }
            }, 500);
        }, duration);

        return alert;
    }

    success(message, duration) {
        return this.show(message, 'success', duration);
    }

    error(message, duration) {
        return this.show(message, 'error', duration);
    }

    info(message, duration) {
        return this.show(message, 'info', duration);
    }

    warning(message, duration) {
        return this.show(message, 'warning', duration);
    }
}

// Initialize global alert instance
const alert = new AlertNotification();

// Handle Flask flash messages
document.addEventListener('DOMContentLoaded', function() {
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(function(message) {
        const category = message.classList.contains('success') ? 'success' :
                        message.classList.contains('error') ? 'error' :
                        message.classList.contains('warning') ? 'warning' : 'info';
        
        alert.show(message.textContent.trim(), category);
        message.remove(); // Remove original flash message
    });
});
