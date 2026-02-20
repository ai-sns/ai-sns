/**
 * Storage - local storage wrapper
 * Unified localStorage management
 */

class Storage {
    constructor() {
        this.prefix = 'ai-sns-';
    }

    /**
     * Get stored value
     * @param {string} key - key name
     * @param {*} defaultValue - default value
     * @returns {*}
     */
    get(key, defaultValue = null) {
        try {
            const value = localStorage.getItem(this.prefix + key);
            if (value === null) return defaultValue;
            return JSON.parse(value);
        } catch (error) {
            console.error(`Error getting storage key '${key}':`, error);
            return defaultValue;
        }
    }

    /**
     * Set stored value
     * @param {string} key - key name
     * @param {*} value - value
     */
    set(key, value) {
        try {
            localStorage.setItem(this.prefix + key, JSON.stringify(value));
        } catch (error) {
            console.error(`Error setting storage key '${key}':`, error);
        }
    }

    /**
     * Remove stored value
     * @param {string} key - key name
     */
    remove(key) {
        try {
            localStorage.removeItem(this.prefix + key);
        } catch (error) {
            console.error(`Error removing storage key '${key}':`, error);
        }
    }

    /**
     * Clear all stored data
     */
    clear() {
        try {
            const keys = Object.keys(localStorage);
            keys.forEach(key => {
                if (key.startsWith(this.prefix)) {
                    localStorage.removeItem(key);
                }
            });
        } catch (error) {
            console.error('Error clearing storage:', error);
        }
    }

    /**
     * Get all keys
     * @returns {Array<string>}
     */
    keys() {
        try {
            const keys = Object.keys(localStorage);
            return keys
                .filter(key => key.startsWith(this.prefix))
                .map(key => key.substring(this.prefix.length));
        } catch (error) {
            console.error('Error getting storage keys:', error);
            return [];
        }
    }
}

// Export singleton
const storage = new Storage();
window.storage = storage;
