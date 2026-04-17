/**
 * Electron Renderer i18n module.
 * Usage:
 *   import { lt, initI18n } from './i18n.js';
 *   await initI18n('en'); // or 'zh'
 *   lt('home.config.title', 'Configuration');
 */

let _langCache = null;
let _langCode = 'en';

function _resolve(data, key) {
    const parts = key.split('.');
    let current = data;
    for (const part of parts) {
        if (current && typeof current === 'object' && part in current) {
            current = current[part];
        } else {
            return null;
        }
    }
    return (typeof current === 'string') ? current : null;
}

/**
 * Initialize the i18n module with a language code.
 * @param {string} langCode - 'en' or 'zh'
 */
export async function initI18n(langCode) {
    _langCode = langCode || 'en';
    _langCache = null;
    try {
        const resp = await fetch(`/renderer/lang/${_langCode}.json`);
        if (resp.ok) {
            _langCache = await resp.json();
        } else {
            _langCache = {};
        }
    } catch (e) {
        console.warn('[i18n] Failed to load language file:', e);
        _langCache = {};
    }
}

/**
 * Translate a key.
 * @param {string} key - Dotted key, e.g. 'home.config.title'
 * @param {string} fallback - Default if key not found
 * @returns {string}
 */
export function lt(key, fallback = '') {
    if (!_langCache) {
        return fallback || key;
    }
    const result = _resolve(_langCache, key);
    return (result !== null) ? result : (fallback || key);
}

/**
 * Get current language code.
 * @returns {string}
 */
export function getLangCode() {
    return _langCode;
}
