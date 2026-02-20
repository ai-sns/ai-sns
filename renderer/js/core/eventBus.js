/**
 * Event Bus - inter-module communication
 * Used to decouple direct dependencies between modules
 */

class EventBus {
    constructor() {
        this.events = {};
    }

    /**
     * Subscribe to an event
     * @param {string} event - event name
     * @param {Function} handler - event handler
     */
    on(event, handler) {
        if (!this.events[event]) {
            this.events[event] = [];
        }
        this.events[event].push(handler);
    }

    /**
     * Unsubscribe from an event
     * @param {string} event - event name
     * @param {Function} handler - event handler
     */
    off(event, handler) {
        if (!this.events[event]) return;

        if (!handler) {
            // If handler is not specified, remove all handlers for this event
            delete this.events[event];
        } else {
            this.events[event] = this.events[event].filter(h => h !== handler);
        }
    }

    /**
     * Emit an event
     * @param {string} event - event name
     * @param {*} data - event data
     */
    emit(event, data) {
        if (!this.events[event]) return;

        this.events[event].forEach(handler => {
            try {
                handler(data);
            } catch (error) {
                console.error(`Error in event handler for '${event}':`, error);
            }
        });
    }

    /**
     * Subscribe to an event once
     * @param {string} event - event name
     * @param {Function} handler - event handler
     */
    once(event, handler) {
        const onceHandler = (data) => {
            handler(data);
            this.off(event, onceHandler);
        };
        this.on(event, onceHandler);
    }

    /**
     * Clear all events
     */
    clear() {
        this.events = {};
    }
}

// Export singleton
const eventBus = new EventBus();
window.eventBus = eventBus;
