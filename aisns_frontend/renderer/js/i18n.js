/**
 * Electron Renderer i18n module (classic global script).
 *
 * JSON files under renderer/lang/{en,zh}.json are the single source of
 * truth for all UI strings. This module loads them at runtime and exposes
 * a global `window.i18n` so that both classic scripts (e.g. app.js) and ES
 * modules (e.g. InitializationWizard.js) can consume translations without
 * import/bundling concerns.
 *
 * The renderer is loaded via file:// with webSecurity disabled, so language
 * files are fetched using a path relative to index.html (renderer/), i.e.
 * `lang/<code>.json`.
 *
 * Usage:
 *   await window.i18n.initI18n('en');           // load + set current language
 *   window.i18n.lt('home.config.title', 'Configuration');
 *   await window.i18n.ensureLang('zh');          // preload another language
 *   window.i18n.ltFor('zh', 'home.config.title', 'Configuration');
 */
(function () {
    'use strict';

    // Per-language cache: { en: {...}, zh: {...} }. Each language file is
    // fetched at most once and reused for the lifetime of the renderer.
    const _caches = {};
    // In-flight fetch promises, keyed by language code, to dedupe concurrent
    // ensureLang() calls for the same language.
    const _pending = {};
    let _current = 'en';

    function _normalize(lang) {
        return (String(lang || '').toLowerCase() === 'zh') ? 'zh' : 'en';
    }

    function _resolve(data, key) {
        const parts = String(key || '').split('.');
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

    // Ensure a language file is loaded into the cache. Returns the cached
    // dictionary (possibly {} if the file could not be loaded).
    async function ensureLang(lang) {
        const code = _normalize(lang);
        if (_caches[code]) {
            return _caches[code];
        }
        if (_pending[code]) {
            return _pending[code];
        }
        _pending[code] = (async () => {
            try {
                // Relative to index.html (renderer/) -> renderer/lang/<code>.json
                const resp = await fetch(`lang/${code}.json`, { cache: 'no-store' });
                _caches[code] = resp.ok ? await resp.json() : {};
            } catch (e) {
                console.warn('[i18n] Failed to load language file:', code, e);
                _caches[code] = {};
            } finally {
                delete _pending[code];
            }
            return _caches[code];
        })();
        return _pending[code];
    }

    // Initialize the module: set the current language and load its file.
    async function initI18n(lang) {
        _current = _normalize(lang);
        await ensureLang(_current);
        return _current;
    }

    // Translate a key for a specific language (must be loaded already, via
    // initI18n/ensureLang). Falls back to the provided fallback, then key.
    function ltFor(lang, key, fallback = '') {
        const data = _caches[_normalize(lang)];
        if (!data) {
            return fallback || key;
        }
        const result = _resolve(data, key);
        return (result !== null) ? result : (fallback || key);
    }

    // Translate a key for the current language.
    function lt(key, fallback = '') {
        return ltFor(_current, key, fallback);
    }

    // Set the current language without forcing a (re)load. Returns the
    // normalized code. Use initI18n/ensureLang to guarantee the file loaded.
    function setLang(lang) {
        _current = _normalize(lang);
        return _current;
    }

    function getLangCode() {
        return _current;
    }

    // Whether the current language's dictionary has been loaded.
    function isReady() {
        return !!_caches[_current];
    }

    window.i18n = {
        initI18n,
        ensureLang,
        lt,
        ltFor,
        setLang,
        getLangCode,
        isReady
    };

    // Convenience global shortcut: window.tt('foo.bar') reads the current
    // language's value from the loaded JSON dictionaries. JSON files are
    // the single source of truth; when a key is missing the key itself is
    // returned so missing translations stay visible during development.
    window.tt = function (key) {
        return lt(key);
    };

    // HTML/attribute escape helpers shared by all modules so any string
    // pulled from JSON can be safely interpolated into innerHTML templates.
    window.escHtml = function (s) {
        return String(s == null ? '' : s)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
    };
    window.escAttr = function (s) {
        return String(s == null ? '' : s)
            .replace(/&/g, '&amp;')
            .replace(/"/g, '&quot;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
    };
})();
